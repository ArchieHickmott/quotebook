from typing import Any, List, Self
from datetime import date
from sqlite3 import IntegrityError
from os import getenv, path

from flask import redirect, url_for, session
from fortifysql import Database, Table, Column, max
from flask_bcrypt import Bcrypt

from app_errors import UserError, AuthError, DatabaseIntegrityError
if path.isfile("env.py"):
    from env import PEPPER
else:
    PEPPER = input("pepper: ")

def protected(func):
    def wrapper(self, *args, **kw):
        if self.is_logged_in:
            return func(self, *args, **kw)
        return
    return wrapper

class User:
    user_details = ["id", "first_name", "last_name" "email"]
    PEPPER = PEPPER
 
    db: Database
    crypt: Bcrypt
    
    __is_logged_in = False
    
    def __init__(self, id: str, password: str=""):
        info = self.db.users.get().filter(userid=id).first() 
        if info == []: UserError("User does not exist")
        self.__id = id
        self.__first_name, self.__last_name, self.__email = info[1], info[2], info[3]
        self.__is_logged_in = False
        if password != "":
            self.log_in(password) 
    
    def __setattr__(self, name: str, value: Any) -> None:
        if name in self.user_details:
            name_val_dict = {name:value}
            self.db.users.replace(**name_val_dict)
        self.__dict__[name] = value  
    
    def __vars__(self):
        self.db = None
        self.crypt = None
        return self.__dict__   
    
    def has_liked(self, quoteid) -> bool:
        return self.user_has_liked(self.__id, quoteid)
    
    def user_has_liked(self, userid, quoteid) -> bool:
        if self.db.likes.get().filter(quoteid=int(quoteid), userid=int(userid)).all():
            return True
        return False    
   
    def create_user(db: Database, first_name: str, last_name: str, email: str, password: str):
        users: Table = db.users
        passwords: Table = db.passwords
        self = User.__new__(User)
        self.db = db
        if users.get().all() == []:
            self.__id = 1
        else:
            self.__id = users.get(max("userid") + 1).first()[0]
        self.__email = email
        self.__first_name = first_name
        self.__last_name = last_name
        hashed_pw = self.crypt.generate_password_hash(self.PEPPER + password)
        try:
            passwords.append(userid=self.__id, hash=hashed_pw)
        except IntegrityError as e:
            try:
                users.append(userid=self.__id, 
                            first_name=first_name, 
                            last_name=last_name,
                            email=email,
                            date_created=date.today())
            except IntegrityError as e2:
                raise UserError("tried creating a user with ID that already exists")
            raise DatabaseIntegrityError(f"major integrity error, password exists without a user {e}", e)
        users.append(userid=self.__id, 
                    first_name=first_name, 
                    last_name=last_name,
                    email=email,
                    date_created=date.today())
        return self       
    
    def load(**kw):
        self = User.__new__(User)
        for key, value in kw.items():
            self.__dict__[key] = value
        return self
            
    def log_in(self, password: str):
        pw: Table = self.db.passwords
        hash: Column = pw.hash
        truepw = pw.get(hash).filter(userid=self.__id).first()[0]
        if self.crypt.check_password_hash(truepw, self.PEPPER + password):
            self.__is_logged_in = True
            return True
        raise AuthError("Incorrect Password") 
    
    @protected 
    def name(self):
        return self.__first_name, self.__last_name
    
    def is_admin(self) -> bool:
        if self.db.users.get("PLEVEL").filter(userid=self.__id).first()[0] != 0:
            return True
        else:
            return False
     
    def id(self):
        return self.__id
    
    @protected 
    def email(self):
        return self.__email
    
    def is_logged_in(self):
        return self.__is_logged_in