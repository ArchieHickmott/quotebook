'''
Database structure is as follows:
users(id, name, email, password_hash, created_at, style, plevel)
quotes(id, author, year, quote, likes)
reports(id, user_id, quote_id, reason, details, status)
logs(id, user_id, action, message)
likes(user_id, quote_id)
comments(user_id, quote_id, comment)
'''
from time import time
from dataclasses import dataclass
from functools import wraps

from flask import session, redirect, url_for

from .databaseManager import db, DatabaseManager
from .crypt import check_password_hash

@dataclass(frozen=True) 
class User:
    id: int
    name: str
    email: str
    hash: str
    created: int
    style: str
    plevel: int
    is_logged_in: bool = False
    
    def log_in(self, password) -> bool:
        object.__setattr__(self, "is_logged_in", check_password_hash(self.hash, password))
        return self.is_logged_in
        
class UserManager:
    def __init__(self):
        self.db: DatabaseManager = db

    def get_user(self, user_id: int=None, email: str=None):
        '''
        Get a user from the database.
        :param user_id: The ID of the user.
        '''
        assert user_id or email, "email or id must be given to UserManager().get_user()"
        if user_id:
            try:
                user_id = int(user_id)
            except Exception as e:
                e.add_note("for security reasons id must be an int")
            user = self.db.query('SELECT * FROM users WHERE id = ?', (user_id,))[0]
        if email:
            user = self.db.query('SELECT * FROM users WHERE email = ?', (email,))[0]
        user = list(user)
        user[3] = str(user[3])
        return User(*user)

    def create_user(self, name: str, email: str, password_hash: str, style: str):
        '''
        Create a user in the database.
        :param name: The name of the user.
        :param email: The email of the user.
        :param password_hash: The password hash of the user.
        '''
        
        print(self.db.query('INSERT INTO users (name, email, password_hash, style, created_at, plevel) VALUES (?, ?, ?, ?, ?, ?)', (name, email, password_hash, style, int(time()), 0)))

        return User(*self.db.query('SELECT * FROM users WHERE email = ?', (email,))[0])

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

        return User(*self.db.query('SELECT * FROM users WHERE id = ?', (user_id,))[0])

    def delete_user(self, user_id: int):
        '''
        Delete a user from the database.
        :param user_id: The ID of the user.
        '''
        self.db.query('DELETE FROM users WHERE id = ?', (user_id,))

        return True
    
um = UserManager()

def login_required(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        if not "user" in session:
            return redirect(url_for("accounts.login", reason="login required for this"))
        user = User(**session["user"])
        if user.is_logged_in:
            return func(*args, **kwargs)
        return redirect(url_for("accounts.login", reason="login required for this"))
    return wrapper
    