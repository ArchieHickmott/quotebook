import re
import sqlite3
import os
import time
import random
import json
from typing import Callable, Iterable, List, Any, Self

import sqlparse
from prettytable import PrettyTable

from .utils import is_drop_query, is_dangerous_delete
from .errors import FortifySQLError, DatabaseConfigError, SecurityError
from .sql_data_types import get_dtype, LogicalString, primitives

class Database:
    # initialise connection to database
    def __init__(self, path: str, check_same_thread: bool=False, name: str = "") -> None:
        """Create a connection to a database, checks if the database exists
            when loading in tables, the table will be an attribute of the database class the attribute name matches the table name
            however if the attribute already exists the table will be renamed to tbl_{table name}

        Args:
            path (str): path to the database
            check_same_thread (bool, optional): used to check if a query is made on the same thread as the __main__ thread. Defaults to False.
            name (str, optional): used to give the database a custom name. Defaults to "".

        Raises:
            FortifySQLError: when the database doesn't exist
        """
        if os.path.isfile(path):
            if name == "":
                if "/" in path:
                    self.__name = path.rsplit('/', 1)[1]
                else:
                    self.__name = path
            else:
                self.__name = name
        elif path == ":memory:":
            self.__name = "memory"
        else:
            raise FortifySQLError(f"SQL error - Database does not exist on path: {path}.")

        self.error = False
        self.allow_dropping = False
        self.check_delete_statements = True
        self.error_logging = False
        self.banned_statements = []
        self.banned_syntax = []

        self.cur = None
        self.path = path
        self.conn = sqlite3.connect(path, check_same_thread=check_same_thread)
        self.recent_data = None
        
        self.reload_tables()

    # to safely close database
    def __del__(self) -> None:
        """
        Rolls back any uncommited transactions on garbage collection
        """
        if self.conn is not None:
            self.conn.rollback()
            self.conn.close()
                
    def reload_tables(self):
        reserved_names = ["error", "allow_dropping", "check_delete_statements", "error_logging", "banned_statements", "banned_syntax",
                          "cur", "path", "conn", "recent_data", "tables", "logging"]
        self.tables = []
        raw_tables = self.query("SELECT name, sql, tbl_name FROM sqlite_master WHERE type='table'")
        for table in raw_tables:
            if table[0] in reserved_names:
                table[0] = f"tbl_{table[0]}"
            table_class = Table(self, table[0], table[1], table[2])
            self.tables.append(table_class)
            
        for table in self.tables:
            setattr(self, str(table), table)
    
    def import_configuration(self, path: str = "", json_string: str = ""):
        """Imports a database configuration from a JSON file or a JSON string \n
        For infromation on how to format the JSON go to: https://archiehickmott.github.io/fortify-sql/

        Args (either path or json not none not both):
            path (str, optional): path to the json config file. Defaults to "".
            json_string (str, optional): JSON formated string. Defaults to "".

        Raises:
            DatabaseConfigError: both a path and JSON string provided
            DatabaseConfigError: neither a path or JSON provided
        """
        is_path = path != ""
        is_json = json_string != ""
        config = None
        if is_path and not is_json:
            with open(path, 'r') as file:
                config = json.load(file)
        elif is_json and not is_path:
            config = json.loads(json_string)
        elif is_path and is_json:
            raise DatabaseConfigError("Can't have import configuration from file and string at the same time")
        else:
            raise DatabaseConfigError("No arguments given to import_configuration()")

        self.error = config["error_catching"]
        self.allow_dropping = config["allow_dropping"]
        self.check_delete_statements = config["check_delete_statements"]
        self.error_logging = config["error_logging"]
        self.banned_statements = config["banned_statements"]
        self.banned_syntax = config["banned_syntax"]

        if config["default_query_logger"]:
            self.query_logging(True)
        if config["default_row_factory"]:
            self.row_factory(sqlite3.Row)

    def logger(self, statement: str) -> None:
        """used to log queries

        Args:
            statement (str): SQL statement
        """
        print(f"[{self.__name}] {statement}")

    # DATABASE CONNECTION CONFIGURATION
    # allow drop
    def allow_drop(self, allow: bool) -> None:
        """allows or bans DROP like statements

        Args:
            allow (bool): wether DROP is banned
        """
        self.allow_dropping = allow

    # enable error catching on queries
    def error_catch(self, enable: bool, logging: bool = False) -> None:
        """enables wether errors are caught on queries

        Args:
            enable (bool): True if errors should be caught False if they should be raised
            logging (bool, optional): True if errors are logged to console False if not. Defaults to False.
        """
        self.error = enable
        self.logging = logging

    def query_logging(self, enable: bool, func: Callable | None = None) -> None:
        """Enables or disables all queries executed on database being logged to console

        Args:
            enable (bool): True if query logging otherwise False
            func (Callable | None, optional): function used to log queries. Defaults to None.
        """
        if not enable:
            self.conn.set_trace_callback(None)
            return None
        if func is None:
            self.conn.set_trace_callback(self.logger)
        else:
            self.conn.set_trace_callback(func)

    #allows dev to set the row factory
    def row_factory(self, factory: sqlite3.Row | Callable = sqlite3.Row) -> None:
        """sets the row factory of the connection \n refer to SQLite3 documentation@https://docs.python.org/3/library/sqlite3.html#sqlite3-howto-row-factory for more info

        Args:
            factory (sqlite3.Row | Callable, optional): function or sqlite3.Row class used for a row factory Defaults to sqlite3.Row.
        """
        self.conn.row_factory = factory

    def delete_checking(self, enable: bool = True) -> None:
        """Delete checking creates a temporary copy of a table before executing a delete statement, it will check that the table still exists after the delete statement \n
        This can be computationally expensive for very large tables.s

        Args:
            enable (bool, optional): True if every DELETE statement is checked for danger otherwise False. Defaults to True.
        """
        self.check_delete_statements = enable

    # add a banned statement
    def add_banned_statement(self, statement: str | Iterable[str]) -> None:
        """If a statement is added it means it cannot be run on the database unless it is removed with remove_banned_statement()

        Args:
            statement (str | Iterable[str]): statement type that is banned
        """
        if isinstance(statement, list) or isinstance(statement, tuple):
            for x in statement:
                self.banned_statements.append(x.upper())
        elif isinstance(statement, str):
            self.banned_statements.append(statement.upper())

    # remove banned statement
    def remove_banned_statement(self, statement: str | Iterable[str]) -> None:
        """Allows a once banned statement to be executed on the database

        Args:
            statement (str | Iterable[str]): statement type to un-ban
        """
        if isinstance(statement, list) or isinstance(statement, tuple):
            for x in statement:
                if x in self.banned_statements:
                    self.banned_statements.remove(x)
        elif isinstance(statement, str):
            if statement in self.banned_statements:
                self.banned_statements.remove(statement)

    # add a banned syntax
    def add_banned_syntax(self, syntax: str | Iterable[str]) -> None:
        """If some syntax is added it means it cannot be run on the database unless it is removed with remove_banned_syntax()

        Args:
            syntax (str | Iterable[str]): syntax to ban
        """
        if isinstance(syntax, list) or isinstance(syntax, tuple):
            for x in syntax:
                if x in self.banned_syntax:
                    self.banned_syntax.append(x)
        elif isinstance(syntax, str):
            if syntax in self.banned_syntax:
                self.banned_syntax.append(syntax)

    # remove banned syntax
    def remove_banned_syntax(self, syntax: str | Iterable[str]) -> None:
        """Allows a once banned SQL syntax to be executed on the database

        Args:
            syntax (str | Iterable[str]): syntax to unban
        """
        if isinstance(syntax, list) or isinstance(syntax, tuple):
            for x in syntax:
                if x in self.banned_syntax:
                    self.banned_syntax.remove(x)
        elif isinstance(syntax, str):
            if syntax in self.banned_syntax:
                self.banned_syntax.remove(syntax)

    def backup(self, path: str = "", extension: str = "db") -> str:
        """Creates a backup of the database as path/time.extension ("/time.db" by default) where time us the time of the backup

        Args:
            path (str, optional): path to save to. Defaults to "".
            extension (str, optional): file extension formated as "extension" NOT ".extension". Defaults to "db".

        Returns:
            str: path it was saved to
        """
        path = path + "/" + str(time.asctime().replace(":", "-") + "." + extension)
        with open(self.path, "rb") as src_file:
            with open(path, "wb") as dst_file:
                dst_file.write(src_file.read())
        return path

    def is_dangerous_delete(self, request: str, parameters=()) -> bool:
        """used to check if a DELETE statement is dangerous (wether it deletes the whole table)

        Args:
            request (str): request to check
            parameters (tuple, optional): request parameters. Defaults to ()

        Returns:
            bool: wether it is dangerous or not
        """
        parsed = sqlparse.parse(request)[0]
        if is_dangerous_delete(request):
            return True

        if not ((parsed.get_type() == "DELETE") and (not self.allow_dropping) and self.check_delete_statements):
            return False
        token_list = sqlparse.sql.TokenList(parsed.tokens)
        for token in token_list:
            if token.value == "FROM":
                from_id = token_list.token_index(token)
                table = token_list.token_next(from_id)[1].value

        cur = self.conn.cursor()
        cur.execute(f"SELECT * FROM {table}")
        if cur.fetchall() != []:
            cur.close()
            self.conn.commit()
            cur = self.conn.cursor()
            key = random.randint(0, 100)
            temp_table = f"check{key}"
            cur.execute(f"CREATE TEMP TABLE {temp_table} AS SELECT * FROM {table}")
            cur.execute(f"INSERT INTO {temp_table} SELECT * FROM {table}")
            query = request.replace(table, temp_table)
            cur.execute(query, parameters)
            cur.execute(f"SELECT * FROM {temp_table}")
            if cur.fetchall == []:
                cur.execute(f"DROP TABLE {temp_table}")
                self.conn.commit()
                cur.close()
                return True
            else:
                cur.execute(f"DROP TABLE {temp_table}")
                self.conn.commit()
                cur.close()
                return False
        else:
            self.conn.commit()
            cur.close()
            return False

    # Excecutes a single query on the database
    def query(self, request: str, parameters: tuple=(), save_data=True) -> List[List[Any]] | None:
        """Handles querying a database, includes paramaterisation for safe user inputing. \n
        SECURITY NOTE: this allows a single statement to be excecuted no more

        Args:
            request (str): SQL request to execute
            parameters (tuple, optional): paramaters to insert into request. Defaults to ().
            save_data (bool, optional): can be used to ignore data returned by SQL. Defaults to True.

        Raises:
            SecurityError: if more than one statement is provided e.g: SELECT * FROM table; SELECT * FROM table2
            SecurityError: if a DROP statement is provided and they're banned
            SecurityError: if a banned statement was provided
            SecurityError: if a banned syntax was provided
            SecurityError: if a dangerous DELETE was provided

        Returns:
            List[List[Any]] | None: None if no data was returned by SQL, returns a table if not
        """
        try:
            with self.conn: \
            request = str(request)
            parsed = sqlparse.parse(request)
            if not len(parsed) == 1:
                raise SecurityError("Multiple statements not allowed in a single query")

            if (not self.allow_dropping) and is_drop_query(request):
                raise SecurityError(f"Dropping is disabled on this database")

            if self.banned_statements != []:
                if parsed[0].get_type().upper() in self.banned_statements:
                    raise SecurityError(f"Attempted to execute banned statement: {request}")

            if self.banned_syntax != []:
                for banned in self.banned_syntax:
                    if banned in request:
                        raise SecurityError(f"Attempted to execute banned syntax: {request}")

            if self.is_dangerous_delete(request, parameters):
                raise SecurityError(f"Attempted to execute dangerous statement: {request}")

            self.cur = self.conn.cursor()
            self.cur.execute(request, parameters)
            data = self.cur.fetchall()
            self.conn.commit()
            self.cur.close()
            self.cur = None
            if save_data:
                self.recent_data = data
                return data

        except Exception as e:
            if self.error:
                if self.logging:
                    print(f"SQL DATABASE ERROR, database: {self.path}, error: {e}")
                    quit()
            else:
                raise e

    # Excecutes multiple queries on the database
    def multi_query(self, request: str, parameters: tuple=(), save_data=True) -> List[List[Any]]:
        """Handles querying a database, includes paramaterisation for safe user inputing. \n
        SECURITY NOTE: this allows a multiple statements to be executed, only use if necessery

        Args:
            request (str): SQL request to execute
            parameters (tuple, optional): paramaters to insert into request. Defaults to ().
            save_data (bool, optional): can be used to ignore data returned by SQL. Defaults to True.

        Raises:
            SecurityError: if a DROP statement is provided and they're banned
            SecurityError: if a banned statement was provided
            SecurityError: if a banned syntax was provided
            SecurityError: if a dangerous DELETE was provided

        Returns:
            List[List[Any]] | None: None if no data was returned by SQL, returns a table if not
        """
        try:
            statements = sqlparse.split(request)
            for statement in statements:
                self.query(statement, parameters, save_data)
            return self.recent_data
        except Exception as e:
            if self.error:
                if self.logging:
                    print(f"SQL DATABASE ERROR, database: {self.path}, error: {e}")
            else:
                raise e
            
class Column: # first defined here for typechecking
    name = ...
    dtype = ...
    table = ...

class Table:
    """Used by FortifySQL ORM to represent a table"""
    def __init__(self, db: Database, name: str, sql, tbl_name=""):
        """Used by FortifySQL ORM to represent a table \n
            If a column name matches one of the Table attributes it will be renamed to col_{name}

        Args:
            db (Database): what database the table is on
            name (str): name of the table
            sql (str): sql statement that creates the table
            tbl_name (str, optional): SQLite tbl_name variable Defaults to "".
        """
        self.reserved_names = ["sql", "tbl_name", "columns", "db", "read_only"]
        self.__name = name
        self.sql = sql
        self.tbl_name = tbl_name
        
        self.read_only = False
        
        if db:
            self.db = db
        
        self.columns = self.__import_columns()
        for column in self.columns:
            if str(column) in self.reserved_names:
                column.name = f"col_{column.name}"
            setattr(self, column.name, column)
         
    def __str__(self) -> str:
        """to convert to str datatype

        Returns:
            (str): table name
        """
        return self.__name
    
    def __call__(self, *args):
        """returns all data in a table"""
        if args == ():
            args = "*"
        else:
            args = "".join(f"{arg}, " for arg in args).strip(", ")
        query = f"SELECT {args} FROM {self.__name}"
        return self.db.query(query)
        
    def __import_columns(self) -> List[Column]:
        """
        imports the columns from the connected Database
        
        Returns:
            List[Columns]: a list of columns in a table
        """
        cursor = self.db.conn.execute(f'PRAGMA table_info({self.__name})')
        data = cursor.fetchall()
        column_info = [[row[1], row[2]] for row in data]
        column_info = [(column_info[n][0], get_dtype(column_info[n][1])) for n, column in enumerate(column_info)]

        columns = []
        for column in column_info:
            columns.append(Column(column[0], column[1], self))  
        return columns    
    
    def __edits_table(func):
        def wrapper(self: Self, *args, **kw):
            if self.read_only:
                raise SecurityError(f"tried to edit a table that is marked as read only, table: {self}, {func}")
            else: 
                return func(self, *args, **kw)
        return wrapper

    def get(self, *cols):
        """gets data from the table, NOTE: use .first(), .all() etc. to return the data

        Returns:
            Select : select class used for method chaining
        """
        return Select(self).select(*cols)
    
    def get_distinct(self, *cols):
        """gets distinct data from the table, NOTE: use .first(), .all() etc. to return the data

        Returns:
            Select : select class used for method chaining
        """
        return Select(self).distinct(*cols)
    
    def filter(self, expr: str = "", **kw):
        """gets data from the table where an expression is true \n
        NOTE: use .first(), .all() etc. to return the data

        Returns:
            Select : select class used for method chaining
        """
        return Select(self).select().filter(expr, **kw)
    
    @__edits_table
    def append(self, **kw) -> None:
        """appends data to the end of a table
        """
        if kw == {}: return 
        cols = []
        values = []
        paramaters = ()
        for col, val in kw.items():
            column = getattr(self, col)
            cols.append(str(col))
            if isinstance(val, Select):
                values.append('(' + str(val) + ')')
            elif isinstance(val, str) or isinstance(val, LogicalString):
                paramaters = (*paramaters, val)
                values.append('?')
            else:  
                values.append(column.dtype(val))  
        cols = '(' + ', '.join(cols) + ')'
        values = '(' + ', '.join(str(value) for value in values) + ')'
        sql = f"INSERT INTO {self.__name} {cols} VALUES {values}"
        self.db.query(sql, paramaters)
    
    @__edits_table
    def replace(self, expr: str = "", **kw) -> None:   
        """used to replace data in a table

        Args:
            expr (str, optional): _description_. Defaults to "".
        """
        if kw == {}: return
        vals = ""
        paramaters=()
        for col, val in kw.items():
            if isinstance(val, str) or isinstance(val, LogicalString):
                vals += f"{col} = ?, "
                paramaters = (*paramaters, val)
                continue
            vals += f"{col} = {val}, "
        vals = vals[:-2]
        where = "" if expr == "" else f"WHERE {expr}"
        sql = f"UPDATE {self.__name} SET {vals} {where}"
        self.db.query(sql, paramaters)
    
    @__edits_table
    def remove(self, expr: str = "", **kw):
        if (not self.db.allow_dropping) and expr=="" and kw=={}:
            raise SecurityError(".remove() was given no arguments and will delete the whole table")
        if expr=="" and kw != {}:
            for col, val in kw.items():
                expr += f"{str(col)} = {val} AND "
            expr = re.sub(r'\s*AND\s*$', "", expr)
        if expr != "":
            expr = "WHERE " + expr
        self.db.query(f"DELETE FROM {self.__name} {expr}")
        
    def pretty_print(self, limit: str | int = None):
        to_print = Select(self).select().pretty_print(limit=limit)
        return to_print
         
class Column:
    used_in_join = False
    def __init__(self, name: str, dtype, table: Table):
        """Used to represent a column in the FortifySQL ORM

        Args:
            name (str): name of the column
            dtype (SQLite data type): data type of the column
            table (Table): FortifySQL Table class
        """
        self.name = name
        self.dtype = dtype
        self.table = table
    
    def __call__(self):
        """returns all the data in a column"""
        data = self.table.get(self.name)
        data = [row[0] for row in data]
        return data
            
    def __str__(self) -> LogicalString:
        """used for str(Column())

        Returns:
            str: name of the column
        """
        if self.used_in_join:
            return repr(self)
        return LogicalString(f"{self.name}")
    
    def __repr__(self) -> LogicalString:
        """used for repr(Column())

        Returns:
            str: name of the column
        """
        return LogicalString(f"{self.table}.{self.name}")
    
    def __eq__(self, value: object) -> str:
        """used for query formatting i.e: table.where(column1 == column2)

        Args:
            value (object): what to test a column equals

        Returns:
            str: returns SQL expression
        """

        if isinstance(value, Column):
            return LogicalString(f"{self} = {value}")
        if isinstance(value, primitives):
            return LogicalString(f"{self} = {self.dtype(value)}")
        if value == "?":
            return LogicalString(f"{self} = ?")

    def __le__(self, value: object):
        """used for query formatting i.e: table.where(column1 <= column2)

        Args:
            value (object): what to test a column <=

        Returns:
            str: returns SQL expression
        """
        if isinstance(value, Column):
            return LogicalString(f"{self} <= {value}")
        if isinstance(value, primitives):
            return LogicalString(f"{self} <= {self.dtype(value)}")
        if value == "?":
            return LogicalString(f"{self} <= ?")

    def __ge__(self, value: object):
        """used for query formatting i.e: table.where(column1 >= column2)

        Args:
            value (object): what to test a column >=

        Returns:
            str: returns SQL expression
        """
        if isinstance(value, Column):
            return LogicalString(f"{self} >= {value}")
        if isinstance(value, primitives):
            return LogicalString(f"{self} >= {self.dtype(value)}")
        if value == "?":
            return LogicalString(f"{self} >= ?")

    def __gt__(self, value: object):
        """used for query formatting i.e: table.where(column1 > column2)

        Args:
            value (object): what to test a column >

        Returns:
            str: returns SQL expression
        """

        if isinstance(value, Column):
            return LogicalString(f"{self} > {value}")
        if isinstance(value, primitives):
            return LogicalString(f"{self} >= {self.dtype(value)}")
        if value == "?":
            return LogicalString(f"{self} > ?")

    def __lt__(self, value: object):
        """used for query formatting i.e: table.where(column1 < column2)

        Args:
            value (object): what to test a column <

        Returns:
            str: returns SQL expression
        """

        if isinstance(value, Column):
            return LogicalString(f"{self} < {value}")
        if isinstance(value, primitives):
            return LogicalString(f"{self} < {self.dtype(value)}")
        if value == "?":
            return LogicalString(f"{self} < ?")

    def __ne__(self, value: object):
        """used for query formatting i.e: table.where(column1 != column2)

        Args:
            value (object): what to test a column !=

        Returns:
            str: returns SQL expression
        """
        if isinstance(value, Column):
            return LogicalString(f"{self} != {value}")
        if isinstance(value, primitives):
            return LogicalString(f"{self} != {self.dtype(value)}")        
        if value == "?":
            return LogicalString(f"{self} != ?")

class BaseStatement:
    """base class that other Statement types are built from"""
    def __init__(self, table: Table) -> None:
        """base class that other Statement types are built from

        Args:
            table (Table): table that the statement is executed on
        """
        self.table = table
        self.statement = ""
    
    def __repr__(self) -> str:
        return self.statement

class Selectable(BaseStatement):
    """base class for all queries that return data"""
    def first(self, *parameters) -> List[Any]:
        """returns the first row of data from a selectable query

        Args:
            *paramaters (optional): parameters to pass through query

        Returns:
            List[Any]: first row of data
        """
        data = self.table.db.query(self.statement, parameters)
        if len(data) >= 1:
            return data[0]
        else:
            return None
    
    def all(self, *parameters) -> List[List[Any]]:
        """returns all data from a query

        Args:
            *paramaters (optional): parameters to pass through query

        Returns:
            List[List[Any]]: data from query
        """
        return self.table.db.query(self.statement, parameters)
    
    def limit(self, limit: str | int, *paramaters):
        """used to limit the amount of data returned
        
        Args:
            args (str, int): the maximum amount of rows that can be returned 
        """
        self.statement += "LIMIT " + str(limit) + " "
        return self.table.db.query(self.statement, paramaters)
    
    def pretty_print(self, *parameters, limit: str | int = None):
        """used to print the data from the request nicely to console, uses pandas 

        Args:
            limit (str | int, optional): how many rows to be returned. Defaults to None.
        """
        if limit:
            self.statement += "LIMIT " + str(limit) + " "
        request = self.statement
        
        db = self.table.db
        parsed = sqlparse.parse(request)
        if not len(parsed) == 1:
            raise SecurityError("Multiple statements not allowed in a single query")

        if db.banned_statements != []:
            if parsed[0].get_type().upper() in db.banned_statements:
                raise SecurityError(f"Attempted to execute banned statement: {request}")

        if db.banned_syntax != []:
            for banned in db.banned_syntax:
                if banned in request:
                    raise SecurityError(f"Attempted to execute banned syntax: {request}")
                
        cur = db.conn.cursor()
        cur.execute(request, parameters)
        data = cur.fetchall()
        col_names = [description[0] for description in cur.description]
        db.conn.commit()
        cur.close()
        prettytable = PrettyTable(col_names)
        prettytable.add_rows(data)
        print(prettytable)
        return data     

class Select(Selectable):
    """used to select data from a table"""
    def select(self, *cols):
        """selects given columns from a table

        Returns:
            self: used for method chain
        """
        if cols == (): # if no columns are given then assume * wildcard
            cols = "*"
        else:
            cols = ", ".join(str(col) for col in cols) # format columns
        self.statement += f"SELECT {cols} FROM {self.table} "
        return self
    
    def distinct(self, *cols):
        """selects distinct data from given columns from a table

        Returns:
            self: used for method chain
        """
        if cols == (): # if no columns are given then assume * wildcard
            cols = "*"
        else:
            cols = ", ".join(str(col) for col in cols) # format columns
        self.statement += f"SELECT DISTINCT {cols} FROM {self.table} "
        return self
    
    def filter(self, expr: str = "", **kw):
        """used to add a WHERE clause to a statement

        Args:
            expr (str): expression for where clause

        Returns:
            Database: returns the Database class NOT the data, use .run() or .paramaters to get the data
        """
        if kw == {}:
            if expr == "": raise FortifySQLError("""expected non "" expression given to .filter()""")
            if isinstance(expr, Select):
                expr = f"({repr(expr)})"
            self.statement += f"WHERE {expr} "
            return self
        assert expr == ""
        for col, val in kw.items():
            if isinstance(val, Select):
                val = f"({repr(val)})"
            column = getattr(self.table, col)
            expr += f"{str(col)} = {column.dtype(val)} AND "
        expr = re.sub(r'\s*AND\s*$', "", expr)
        self.statement += f"WHERE {expr} " 
        return self           
    
    def _and(self, expr: str):
        """used to add a AND operator to a statement

        Args:
            expr (str): expression for AND clause

        Returns:
            self: returns itself class NOT the data, use .all() or similar to get the data
        """
        self.statement += "AND " + expr + " "
        return self  
    
    def _or(self, expr: str):
        """used to add a OR operator to a statement

        Args:
            expr (str): expression for OR clause

        Returns:
            Database: returns itself class NOT the data, use .all() or similar to get the data
        """
        self.statement += "OR " + expr + " "
        return self  
    
    def group(self, *args, having=""):
        """used to group data from a SQL statistical funtion

        Args:
            args (str): columns/aliases to group by
        """
        self.statement += "GROUP BY" + ", ".join(args) + " "
        if having != "":
            self.statement += "HAVING " + having + " "
        return self
    
    def order(self, *args):
        """used to determine the order that data is returned"""
        self.statement += "ORDER BY " + ", ".join(args) + " "
        return self
    