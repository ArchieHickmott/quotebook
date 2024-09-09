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
from .logger import logger

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
    active: bool = True
    
    def log_in(self, password) -> bool:
        is_logged_in = check_password_hash(self.hash, password)
        if is_logged_in:
            logger.info(f"\x1b[33muser {self.id} logged in\x1b[0m", extra={"userid": self.id, "action":"login"})
        else:
            logger.info(f"\x1b[33mfailed user {self.id} log in\x1b[0m", extra={"userid": self.id, "action":"failed login"})
        object.__setattr__(self, "is_logged_in", is_logged_in)
        return self.is_logged_in
    
    def check_banned(self):
        if db.query(f"SELECT * FROM bans WHERE user_id = {self.id}"):
            object.__setattr__(self, "active", False)
        else:
            object.__setattr__(self, "active", True)        

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
        user = User(*user)
        if db.query(f"SELECT * FROM bans WHERE user_id = {user.id}"):
            object.__setattr__(user, "active", False)
        return user

    def create_user(self, name: str, email: str, password_hash: str, style: str):
        '''
        Create a user in the database.
        :param name: The name of the user.
        :param email: The email of the user.
        :param password_hash: The password hash of the user.
        '''
        
        self.db.query('INSERT INTO users (name, email, password_hash, style, created_at, plevel) VALUES (?, ?, ?, ?, ?, ?)', (name, email, password_hash, style, int(time()), 0))
        user = User(*self.db.query('SELECT * FROM users WHERE email = ?', (email,))[0])
        logger.info(f"\x1b[33muser created {user.id}\x1b[0m", extra={"userid":user.id, "action":"user created"})
        return user

    def update_user(self, user_id: int, name: str=None, email: str=None, password_hash: str=None, plevel: int=None, style: str=None):
        '''
        Update a user in the database.
        :param user_id: The ID of the user.
        :param name: The name of the user.
        :param email: The email of the user.
        :param password_hash: The password hash of the user.
        '''
        user = self.get_user(user_id)
        if not (style == "dark" or style == "light"):
            style = None
        data_dict = {"name": name, "email": email, "hash": password_hash, "style": style}
        for key, item in data_dict.items():
            if item is None:
               data_dict[key] = getattr(user, key)
            else:
                object.__setattr__(user, key, item)
        logger.info(f"\x1b[33mupdated user info {user_id}\x1b[0m", extra={"userid":user_id, "action":"updated data"})
        parameters = tuple((item[1] for item in data_dict.items()))
        self.db.query(f"UPDATE users SET name=?, email=?, password_hash=?, style=? WHERE id={user_id}", parameters)
        return User(*self.db.query(f'SELECT * FROM users WHERE id = {user_id}')[0])

    def delete_user(self, user_id: int):
        '''
        Delete a user from the database.
        :param user_id: The ID of the user.
        '''
        self.db.query('DELETE FROM users WHERE id = ?', (user_id,))
        logger.warning(f"deleted user {user_id}", extra={"userid":user_id, "action":"deleted"})
        return True
    
um = UserManager()

def check_logged_in() -> bool:
    if not "user" in session:
        return False
    user = User(**session["user"])
    if user.is_logged_in:
        return True
    return True
    
def login_required(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        if check_logged_in():
            return func(*args, **kwargs)
        return redirect(url_for("accounts.login", reason="login required"))
    return wrapper
    