"""
Classes for all the data types in SQLite
"""
from numbers import Number
from typing import Any, Self

from .errors import SQLTypeError

class LogicalString(str):
    """instead of logical operators such as and returning a bool, a and b will return the string f"{a} AND {b}"

    Args:
        string (str): any string
    """
    def __and__(self, other):
        return LogicalString(f" {self} AND {other} ")
    
    def __rand__(self, other):
        return LogicalString(f" {self} AND {other} ")
    
    def __or__(self, other):
        return LogicalString(f" {self} or {other} ")
    
    def __not__(self, other):
        return LogicalString(f" {self} not {other} ")
    
    def __add__(self, other):
        return LogicalString(f"{self} + {other}")
    
    def __sub__(self, other):
        return LogicalString(f"{self} - {other}")
    
    def __mul__(self, other):
        return LogicalString(f"{self} * {other}")
    
    def __truediv__(self, other):
        return LogicalString(f"{self} / {other}")
    
    def __iadd__(self, other):
        return LogicalString(str(self) + other)
    
    def __bool__(self):
        if self == "":
            return False
        return True

class SQLDataType: # used for typing
    """Do not use class SQLDataType on it's own, for typechecking only
    """
    python_equiv = ...
    sql_text = ...
    value = ...
    
    def __init__(self, value):
        if isinstance(value, Literal):
            self.value = value 
    
    def __str__(self): ...

class Null(SQLDataType):
    """
    SQLite NULL datatype
    """
    python_equiv = None
    sql_text = "NULL"
    value = "NULL"
    
    def __str__(self):
        return self.value

class Integer(SQLDataType):
    """
    SQLite3 INTEGER datatype
    """
    sql_text = "INTEGER"
    python_equiv = int
    def __init__(self, number: Number | str) -> None:
        if isinstance(number, str): # check if given string is valid
            for char in number:
                try:
                    int(char)
                except ValueError:
                    raise SQLTypeError(f"Error in converting string to INTEGER, value {char} failed")

        if isinstance(number, complex):
            number = number.real    

        self.value: int = int(number)
        
        super().__init__(number)

    def __str__(self) -> str:
        return str(self.value)

class Real(SQLDataType):
    """
    SQLite3 REAL datatype
    """
    sql_text = "REAL"
    python_equiv = float
    def __init__(self, number: Number | str):
        if isinstance(number, str):
            try:
                number = float(number)
            except ValueError as e:
                raise SQLTypeError(f"Error in converting string to REAL, value failed: {e}")

        if isinstance(number, complex):
            number = number.real
        
        self.value = float(number)
        super().__init__(number)

    def __str__(self):
        return str(self.value)

class Text(SQLDataType):
    """
    SQLite3 TEXT datatype
    """
    python_equiv = str
    sql_text = "TEXT"
    def __init__(self, text) -> None:
        try:
            self.value = str(text)
            super().__init__(text)     
        except ValueError as e:
            raise SQLTypeError(f"Error in converting {text} to TEXT: {e}")
    
    def __str__(self):
        return f"'{self.value}'"

class Blob(SQLDataType):
    """
    SQLite3 BLOB datatype (bytes)
    """
    python_equiv = bytes
    sql_text = "BLOB"
    def __init__(self, bites: bytes=None, bytes_like: Any=None, encoding: str="") -> None:
        if bites is not None and bytes_like is not None:
            raise SQLTypeError(f"Blob() cannot have two inputs: {bites} and {bytes_like}")
        elif bites is not None and isinstance(bites, bytes):
            self.value = bites
            value = bites
        elif bytes_like is not None:
            try:
                self.value = bytes(bytes_like)
                value = bytes_like
            except Exception as e:
                raise SQLTypeError(f"Error in converting to bytes {e}")
        else:
            raise SQLTypeError(f"Invalid inputs to Blob() {bites}, {bytes_like}")
        
        self.encoding = encoding
        super().__init__(value)

    def __str__(self) -> str:
        if self.encoding != "":
            return "'" + str(self.value.decode(self.encoding)) + "'"
        else:
            return str(self.value)[1:]

class Literal(Text):
    """special data type for parameterisation and subqueries"""
    def __str__(self):
        return self.value

ALL_SQL_DATA_TYPES = [Null, Integer, Real, Text, Blob, Literal]
ALL_SQL_DATA_TYPE_NAMES = [dtype.sql_text for dtype in ALL_SQL_DATA_TYPES]
primitives = (bool, str, int, float, type(None), complex) 

def get_dtype(text: str):
    if "(" in text:
        text = text.rsplit('(')[0]
    match text.upper().strip():
        case "NULL":
            return Null
        case "INTEGER":
            return Integer
        case "REAL":
            return Real
        case "TEXT":
            return Text
        case "BLOB":
            return Blob
        case "":
            return Text
 
def cast_sql_dtype(value: Any) -> SQLDataType:
    """assinges a SQL datatype to any value passed through

    Args:
        value (Any): to be turned into 

    Returns:
        _type_: _description_
    """
    if isinstance(value, str):
        if value == '?':
            return Literal(value)
        return Text(value)
    if isinstance(value, int):
        return Integer(value)
    if isinstance(value, Number):
        return Real(value)
    if isinstance(value, bool):
        return Integer(1) if value else Integer(0)
    if isinstance(value, bytes):
        return Blob(value)
    if value is None:
        return Null()
    for dtype in ALL_SQL_DATA_TYPES:
        try:
            return dtype(value)
        except:
            pass
    raise SQLTypeError(f"can't cast type: {type(value)}, value: {value}")