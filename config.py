import datetime as dt
import os
from random import randbytes
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
    # App Config
    app = Flask(__name__)
    app.config["PERMANENT_SESSION_LIFETIME"] = dt.timedelta(hours=1)
    bootstrap = Bootstrap5(app)
    app.config["SECRET_KEY"] = randbytes(128)

    # Database Config
    if not os.path.isfile("quote.db"):
        with open("quote.db", "w") as file:
            pass # the whole with open() as file: pass is for to force python to garbage collect
        db = QuoteDb("quote.db")
        db.multi_query(open("quote.sql").read())
        db.reload_tables()
    else:
        db = QuoteDb("quote.db")
        
    def log(request: str):
        if request.strip() == "COMMIT" or request.strip() == "BEGIN":
            return
        request = request.replace("\n", "").strip().replace("   ", "")
        app.logger.info(f"[Database] {request}")

    db.query_logging(True, log)
    db.backup("/backups")

    crypt = Bcrypt(app)
    User.db = db
    User.crypt = crypt
    return app, db, crypt