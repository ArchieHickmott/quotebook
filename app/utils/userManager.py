'''
Database structure is as follows:
users(id, name, email, password_hash, created_at, plevel)
quotes(id, author, year, quote, likes)
reports(id, user_id, quote_id, reason, details, status)
logs(id, user_id, action, message)
likes(user_id, quote_id)
comments(user_id, quote_id, comment)
'''

from time import time
from .databaseManager import db, DatabaseManager

class UserManager:
    def __init__(self):
        self.db: DatabaseManager = db

    def get_user(self, user_id: int):
        '''
        Get a user from the database.
        :param user_id: The ID of the user.
        '''
        user = self.db.query('SELECT * FROM users WHERE id = ?', (user_id,))[0]
        return {"id": user[0], "name": user[1], "email": user[2], "hash": user[3], "created": user[4], "style": user[5], "plevel": user[6]}

    def create_user(self, name: str, email: str, password_hash: str):
        '''
        Create a user in the database.
        :param name: The name of the user.
        :param email: The email of the user.
        :param password_hash: The password hash of the user.
        '''
        
        print(self.db.query('INSERT INTO users (name, email, password_hash, created_at, plevel) VALUES (?, ?, ?, ?, ?)', (name, email, password_hash, int(time()), 1)))

        return self.db.query('SELECT * FROM users WHERE email = ?', (email,))[0]

    def update_user(self, user_id: int, name: str=None, email: str=None, password_hash: str=None, plevel: int=None, style: str=None):
        '''
        Update a user in the database.
        :param user_id: The ID of the user.
        :param name: The name of the user.
        :param email: The email of the user.
        :param password_hash: The password hash of the user.
        '''
        if not (style == "dark" or style == "light"):
            style = None
        for item in [name, email, password_hash, plevel, style]:
            if item is None:
                item = self.get_user(user_id)[[name, email, password_hash, plevel].index(item)]
        
        self.db.query('UPDATE users SET name = ?, email = ?, password_hash = ? WHERE id = ? ', (name, email, password_hash, user_id))

        return self.db.query('SELECT * FROM users WHERE id = ?', (user_id,))[0]

    def delete_user(self, user_id: int):
        '''
        Delete a user from the database.
        :param user_id: The ID of the user.
        '''
        self.db.query('DELETE FROM users WHERE id = ?', (user_id,))

        return True

um = UserManager()

    
    