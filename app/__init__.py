from random import randbytes
import datetime as dt

from flask import Flask, render_template
from flask_bootstrap import Bootstrap5

from app.accounts import blueprint as account
from app.admin import blueprint as admin
from app.chat import blueprint as chat
from app.quotes import blueprint as quotes
from app.utils import db

app = Flask(__name__)
app = Flask(__name__)
app.config["PERMANENT_SESSION_LIFETIME"] = dt.timedelta(hours=1)
bootstrap = Bootstrap5(app)
app.config["SECRET_KEY"] = randbytes(128)

@app.route("/")
def landing():
    return render_template("landing.html")

if __name__ == "__main__":
    app.run()