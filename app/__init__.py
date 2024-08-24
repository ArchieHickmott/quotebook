# stdlib
from random import randbytes
import datetime as dt

# ext. Libraries
from flask import Flask, render_template, session, request, abort
from flask_bootstrap import Bootstrap5
from werkzeug.exceptions import HTTPException

# Local
from app.utils import db
from app.utils import qm
from app.errors import error_codes

# Blueprints
from app.accounts import blueprint as account
from app.admin import blueprint as admin
from app.chat import blueprint as chat
from app.quotes import blueprint as quotes

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
    if not "style" in session:
        session["style"] = "light"
    if request.args.get("style"):
        session["style"] = request.args.get("style")

@app.route("/")
def landing():
    quotes = []
    for i in range(15):
        quotes.append(qm.get_quote(-1))
    return render_template("landing.html", quotes=quotes)

@app.route("/abort")
def testing_only_remove_before_deployment():
    return abort(int(request.args.get("code")))

@app.errorhandler(Exception)
def error(e):
    msg = "OOPS something went wrong"
    if isinstance(e, HTTPException):
        if e.code == 500 or (not e.code in error_codes):
            return render_template("error.html", message=msg)
        msg = error_codes[e.code]
        render_template("error.html", message=msg)
    return render_template("error.html", message=msg)

if __name__ == "__main__":
    app.run()