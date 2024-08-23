"""
All the classes used for errors
"""


class FortifySQLError(Exception):
    """Used for all errors in FortifySQL"""

    def __init__(self, msg):
        super().__init__(f"FortifySQL Error: {msg}")


class SQLTypeError(Exception):
    """used for type errors in SQLite datatypes"""

    def __init__(self, msg):
        super().__init__(f"Error with SQL Datatypes: {msg}")


class DatabaseConfigError(FortifySQLError):
    """used for errors while importing a Database configuration JSON"""

    def __init__(self, msg):
        super().__init__(f"Error while importing Database configuration JSON: {msg}")


class SecurityError(FortifySQLError):
    """Used when a security rule is broken"""

    def __init__(self, msg):
        super().__init__(f"Error, Broken Security Rule: {msg}")
