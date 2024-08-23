from random import randbytes
import datetime as dt

from flask import Flask, render_template, session, request
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

app.register_blueprint(account)
app.register_blueprint(admin)
app.register_blueprint(chat)
app.register_blueprint(quotes)

@app.before_request
def before():
    if not "mode" in session:
        session["style"] = "light"
    if request.args.get("style"):
        session["style"] = request.args.get("style")

@app.route("/")
def landing():
    return render_template("landing.html")

if __name__ == "__main__":
    app.run()