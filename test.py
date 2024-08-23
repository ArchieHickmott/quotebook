'''
Database structure is as follows
'''

from utils import DatabaseManager

dbm = DatabaseManager()

dbm.reset_db()
print(dbm.query('SELECT * FROM sqlite_master'))