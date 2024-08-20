"""
Utils, mainly used by the database class
"""

import sqlparse
from sqlparse.sql import Where
from sqlparse.tokens import Keyword

"""
Query purification
"""
def is_drop_query(query):
    """
    Check if the query contains any potentially DROP statement
    """
    harmful_types = ['DROP', 'TRUNCATE']
    parsed = sqlparse.parse(query)
    for statement in parsed:
        if statement.get_type() in harmful_types:
            return True

def is_delete_without_where(query):
    """
    Check if the DELETE statement has no where statement
    """
    parsed = sqlparse.parse(query)
    for statement in parsed:
        if statement.get_type() == 'DELETE':
            where_found = False
            for token in statement.tokens:
                if isinstance(token, Where):
                    where_found = True
                    break
                if token.ttype is Keyword and token.value.upper() == 'WHERE':
                    where_found = True
                    break
            if not where_found:
                return True
    return False

def is_always_true_where(where_clause):
    """
    IN DEVELOPMENT NOT SUPER SAFE YET!!!\n
    Check if the WHERE clause is always true. This is a simplified check for common always-true conditions. \n
    Only enter in the where clause itself
    """
    always_true_conditions = [
        "1=1",
        "TRUE",
        "1 = 1",
        "true"
    ]
    where_str = str(where_clause).strip().lower()
    for condition in always_true_conditions:
        if condition in where_str:
            return True
    return False

def is_dangerous_delete(query):
    """
    checks if a query contains a dangerous delete statement
    """
    parsed = sqlparse.parse(query)
    where = None
    for statement in parsed:
        if statement.get_type() == "DELETE":
            for token in statement.tokens:
                if "WHERE" in token.value.upper():
                    where = token.value.upper()
            if where is None:
                return True
            if is_always_true_where(where):
                return True
    return False
