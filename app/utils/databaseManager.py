from typing import Any, List, Tuple, Dict

import sqlparse

import logging

logger = logging.getLogger()
class DatabaseManager:
    def __init__(self, path):
        import sqlite3
        
        self.conn = sqlite3.connect(path, check_same_thread=False)

    # for security reasons, if you're planning on using a single statement in a query
    def query(self, 
              query: str, 
              values: Tuple[Any, ...] | Dict[str, Any] = tuple()
        ) -> List[Tuple[Any, ...]] | Exception | bool:
        """executes a query on the database, NOTE: query must have one and only one statement
        for security reasons, if you're planning on using a single statement in a query it is recommended
        to use query as if there is some SQLi vulnerability then they won't be able to execute a statement other than
        the default statement. Principle of least privilege 

        :param query: query to execute
        :type query: str
        :param values: parameters for the query, defaults to tuple()
        :type values: tuple | dict, optional
        :return: results if there are results, True if it's not a SELECT statement and is successful, Exception if something went wrong
        :rtype: Any[List[Tuple[Any]], Exception, bool]
        """
        parsed = sqlparse.parse(query)
        if len(parsed) > 1:
            return False #TODO: decide a better return value
        return self.multi_query(query, values)
        
    def multi_query(self, 
              query: str, 
              values: Tuple[Any, ...] | Dict[str, Any] = tuple()
        ) -> List[Tuple[Any, ...]] | Exception | bool:
        """executes a query on the database

        :param query: query to execute
        :type query: str
        :param values: parameters for the query, defaults to tuple()
        :type values: tuple | dict, optional
        :return: results if there are results, True if it's not a SELECT statement and is successful, Exception if something went wrong
        :rtype: Any[List[Tuple[Any]], Exception, bool]
        """
        if query.lower().startswith('select'):
            return self.select(query, values)
        else:
            return self.execute(query, values)
        
    def select(self, 
               query: str, 
              values: Tuple[Any, ...] | Dict[str, Any] = tuple()
        ) -> List[Tuple[Any, ...]] | Exception | bool:
        '''
        Execute a select query on the database.
        :param query: The query to execute.
        :param values: The values to insert into the query.
        '''
        if values is None: values = ()
        
        with self.conn:
            cursor = self.conn.cursor()

            try:
                cursor.execute(query, values)
                return cursor.fetchall()
            except Exception as e:
                logger.error(f"{type(e)} error in database {e.__dict__.get("msg")}")
                return e
        
    def execute(self, 
                query: str,
              values: Tuple[Any, ...] | Dict[str, Any] = tuple()
        ) -> List[Tuple[Any, ...]] | Exception | bool:
        """executes a non-SELECT query

        :param query: SQL to execute
        :type query: str
        :param values: parameters for query, defaults to tuple()
        :type values: Tuple | Dict, optional
        :return: True if successful, Exception if something went wrong
        :rtype: Any[bool, Exception]
        """
        with self.conn:
            cursor = self.conn.cursor()
            try:
                cursor.execute(query, values)
                cursor.connection.commit()
                return True
            except Exception as exception:
                logger.error(f"{type(exception).__name__} error in database")
                return exception
            
    def reset_db(self):
        '''
        Reset the database.
        '''
        with self.conn:
            cursor = self.conn.cursor()
            with open('database_query.sql', 'r') as f:
                cursor.executescript(f.read())

db = DatabaseManager("database.db")