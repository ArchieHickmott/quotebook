__version__ = "0.4.1"
__author__ = "Archie Hickmott"
import sqlite3

from .orm import Database, Table, Column
from .sql_data_types import (
    Null,
    Integer,
    Real,
    Text,
    Blob,
    ALL_SQL_DATA_TYPE_NAMES,
    ALL_SQL_DATA_TYPES,
)
from .sql_functions import *
from .sql_functions import __all__
import sqlparse

# print(f"""\033[93mWARNING FortifySQL is in BETA {__version__},
# do not use in a production environment until full release \033[0m""")

__all__ = [
    "Database",
    "Table",
    "column",
    "sqlite3",
    "sqlparse",
    "Null",
    "Integer",
    "Real",
    "Text",
    "Blob",
    "ALL_SQL_DATA_TYPE_NAMES",
    "ALL_SQL_DATA_TYPES",
    *__all__,
]
