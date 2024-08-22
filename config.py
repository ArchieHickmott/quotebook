import datetime as dt
import os
from typing import Tuple

from flask import Flask
from flask_bootstrap import Bootstrap5
from flask_bcrypt import Bcrypt
from fortifysql import Database, Table

from users import User

class QuoteDb(Database):
    users: Table
    reports: Table
    log_failed_logins: Table
    log_logins: Table
    passwords: Table
    likes: Table
    quotes: Table
    
def create_app() -> Tuple[Flask, QuoteDb, Bcrypt] :
    app = Flask(__name__)
    app.config["PERMANENT_SESSION_LIFETIME"] = dt.timedelta(hours=1)
    Bootstrap5(app)
    app.config["SECRET_KEY"] = "attendance is the biggest indicator for success"
    db: QuoteDb
    if os.path.isfile("fake_quote.db"):
        db = QuoteDb("fake_quote.db")
    else:
        with open("fake_quote.db", "w") as file:
            pass
        db = QuoteDb("fake_quote.db")
        db.multi_query("""
CREATE TABLE users (
    userid       INTEGER PRIMARY KEY,
    first_name   TEXT    NOT NULL,
    last_name    TEXT,
    email        TEXT    NOT NULL
                         UNIQUE,
    date_created TEXT,
    PLEVEL       INTEGER DEFAULT (0) 
);
CREATE TABLE reports (
    reportid INTEGER        PRIMARY KEY,
    reporter                REFERENCES users (userid),
    quoteid  INTEGER        REFERENCES quotes (quoteid),
    reason   TEXT,
    details  TEXT,
    status   INTEGER (0, 2) DEFAULT (0) 
);
CREATE TABLE log_failed_logins (
    userid        INTEGER REFERENCES users (userid),
    ip            TEXT,
    time          TEXT,
    error_message TEXT
);
CREATE TABLE log_logins (
    userid INTEGER REFERENCES users (userid),
    ip     TEXT,
    time   TEXT
);
CREATE TABLE passwords (
    userid INTEGER REFERENCES users (userid) 
                   NOT NULL
                   UNIQUE,
    hash   BLOB
);
CREATE TABLE likes (
    quoteid INTEGER REFERENCES quotes (quoteid),
    userid  INTEGER REFERENCES users (userid) 
);
CREATE TABLE quotes (
    quoteid  INTEGER PRIMARY KEY AUTOINCREMENT,
    name     TEXT,
    year     TEXT,
    quote    TEXT,
    numlikes INTEGER DEFAULT (0) 
);
INSERT INTO quotes VALUES (1, "name", "2024", "example quote 1", 0);
INSERT INTO quotes VALUES (2, "name", "2024", "example quote 2", 0);
INSERT INTO quotes VALUES (3, "name", "2024", "example quote 3", 0);
INSERT INTO quotes VALUES (4, "name", "2024", "example quote 4", 0);
INSERT INTO quotes VALUES (5, "name", "2024", "example quote 5", 0);
INSERT INTO quotes VALUES (6, "name", "2024", "example quote 6", 0);
INSERT INTO quotes VALUES (7, "name", "2024", "example quote 7", 0);
INSERT INTO quotes VALUES (8, "name", "2024", "example quote 8", 0);
INSERT INTO quotes VALUES (9, "name", "2024", "example quote 9", 0);
    """)
        db.reload_tables()
    def log(request: str):
        if request.strip() == "COMMIT" or request.strip() == "BEGIN":
            return
        request = request.replace("\n", "").strip().replace("   ", "")
        app.logger.info(f"[Database] {request}")
    db.query_logging(True, log)
    db.backup("C:/Users/25hickmar/OneDrive - St Patricks College/Digital Solutions/small projects/quotebook")

    crypt = Bcrypt(app)
    User.db = db
    User.crypt = crypt
    return app, db, crypt