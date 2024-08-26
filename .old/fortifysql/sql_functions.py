from typing import Any
from .sql_data_types import LogicalString

def absolute(x: str) -> str:
    """sqlite absolute value function

    Args:
        x (text): any numeric SQL 'column'

    Returns:
        str: formated as: abs(x)
    """
    return LogicalString(f"abs({x})")

def changes() -> str:
    """The changes() sqlite function returns the number of database rows that were changed or inserted or deleted by the most recently completed INSERT, DELETE, or UPDATE statement, exclusive of statements in lower-level triggers. The changes() SQL function is a wrapper around the sqlite3_changes64() C/C++ function and hence follows the same rules for counting changes.

    Returns:
        str: shanges()
    """
    return LogicalString("changes()")

def char(*args: int) -> str:
    """The sqlite char(X1,X2,...,XN) function returns a string composed of characters having the unicode code point values of integers X1 through XN, respectively.

    Returns:
        str: char(X1,X2,...,XN)
    """
    return LogicalString(f"char({', '.join(args)})")

def iif(x: str, y: str, z: str) -> str:
    """The iif(X,Y,Z) function returns the value Y if X is true, and Z otherwise

    Args:
        x (str): value to check if true
        y (str): value if x is true
        z (str): value if x is false
    
    Returns:
        str: iif(x, y, z)
    """
    return LogicalString(f'iif({x}, {y}, {z})')

def like(x: str, y:str):
    """check if x is like y, aka check similarity

    Args:
        x (str): string to check against y
        y (str): string used to check x
    """
    return LogicalString(f'like({x}, {y})')

def max(x: str):
    """get the max value of x"""
    return LogicalString(f"max({x})")

def min(x: str):
    """get the min value of x"""
    return LogicalString(f"min({x})")

def random():
    """The random() function returns a pseudo-random integer between -9223372036854775808 and +9223372036854775807."""
    return LogicalString("random()")

def round(x: str, y: int=0):
    """rounds x to the y decimal places"""
    return LogicalString(f"round({x}, {y})")

__all__ = ["absolute", "changes", "char", "iif", "like", "max", "min", "random", "round"]