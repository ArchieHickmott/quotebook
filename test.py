'''
Database structure is as follows:
users(id, name, email, password_hash, created_at, plevel)
quotes(id, author, year, quote, likes)
reports(id, user_id, quote_id, reason, details, status)
logs(id, user_id, action, message)
likes(user_id, quote_id)
comments(user_id, quote_id, comment)
'''

from utils import DatabaseManager

dbm = DatabaseManager()

dbm.reset_db()

# Check all tables are queried correctly
print(dbm.query('SELECT * FROM quotes'))

# Insert data into the users table
dbm.query('INSERT INTO users (id, name, email, password_hash, created_at, plevel) VALUES (?, ?, ?, ?, ?, ?)', ('0', 'test', 'test@email.com', 'password', '0', 1))

# Check the data was inserted correctly
print(dbm.query('SELECT * FROM users'))

# reset the database
dbm.reset_db()