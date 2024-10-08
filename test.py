'''
Database structure is as follows:
users(id, name, email, password_hash, created_at, plevel)
quotes(id, author, year, quote, likes)
reports(id, user_id, quote_id, reason, details, status)
logs(id, user_id, action, message)
likes(user_id, quote_id)
comments(user_id, quote_id, comment)
'''

from quotebook.utils import db, um, qm
from hashlib import sha256

dbm = db
um = um
qm = qm

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

# add a quote
for i in range(10):
    qm.create_quote(f'Author {i}', f'Quote {i}')

# list all quotes
print(qm.search(""))

# like a quote
qm.like_quote(1, 1)

# update a quote
qm.update_quote(2, author='New Author', quote='New Quote 1')

# delete a quote
qm.delete_quote(3)

# search for quotes with "1" in them
print(qm.search('1'))





