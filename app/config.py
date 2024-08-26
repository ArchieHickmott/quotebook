# stdlib
import logging.config
from random import randbytes
import datetime as dt
import traceback as tb
import logging

# ext. Libraries
from flask import Flask, render_template, session, request, abort
from flask_bootstrap import Bootstrap5
from werkzeug.exceptions import HTTPException

# Local
from .utils import db
from .quotes import qm
from .errors import error_codes
from .utils.logger import logger

# Blueprints
from .accounts import blueprint as account
from .admin import blueprint as admin
from .chat import blueprint as chat
from .quotes import blueprint as quotes

flask_app = Flask(__name__)
flask_app = Flask(__name__)
flask_app.config["PERMANENT_SESSION_LIFETIME"] = dt.timedelta(hours=1)
bootstrap = Bootstrap5(flask_app)
flask_app.config["SECRET_KEY"] = randbytes(128)

flask_app.register_blueprint(account)
flask_app.register_blueprint(admin)
flask_app.register_blueprint(chat)
flask_app.register_blueprint(quotes)

@flask_app.before_request
def before():
    if not "style" in session:
        session["style"] = "light"
    if request.args.get("style"):
        session["style"] = request.args.get("style")

@flask_app.route("/")
def landing():
    quotes = []
    for _ in range(15):
        quotes.append(qm.get_quote(-1))
    return render_template("landing.html", quotes=quotes)

@flask_app.errorhandler(Exception)
def error(e):
    if flask_app.debug:
        msg = f"{e} {tb.format_exc()}"
    else:
        msg = "OOPS something went wrong"
    if isinstance(e, HTTPException):
        if e.code == 500 or (not e.code in error_codes):
            return render_template("error.html", message=msg)
        msg = error_codes[e.code]
        return render_template("error.html", message=msg)
    logger.error(f"{type(e).__name__} in app")
    return render_template("error.html", message=msg)