'''
Database structure is as follows:
users(id, name, email, password_hash, created_at, plevel)
quotes(id, author, year, quote, likes)
reports(id, user_id, quote_id, reason, details, status)
logs(id, user_id, action, message)
likes(user_id, quote_id)
comments(user_id, quote_id, comment)
'''

from utils import DatabaseManager, UserManager
from hashlib import sha256

dbm = DatabaseManager()
um = UserManager(dbm)

dbm.reset_db()

# Check all tables are queried correctly
print(dbm.query('SELECT * FROM quotes'))

# Insert data into the users table
for i in ['Alice', 'Bob', 'Charlie']:
    um.create_user(i, f"{i}@email.com", sha256('password_hash'.encode()).hexdigest())

# change the email of user with id 1
um.update_user(1, email='new_email@email.com')

# delete the user with id 2
um.delete_user(2)

# create a new user
um.create_user('David', 'david@email.com', sha256('password_hash'.encode()).hexdigest())

# print the user with id 3
print(um.get_user(3))

# Check the data was inserted correctly
print(dbm.query('SELECT * FROM users'))

# reset the database
dbm.reset_db()