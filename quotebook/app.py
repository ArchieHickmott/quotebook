# stdlib
from random import randbytes
import datetime as dt
import traceback as tb
from typing import Tuple

# ext. Libraries
from flask import Flask, render_template, session, request, redirect, url_for
from flask_socketio import SocketIO
from flask_bootstrap import Bootstrap5
from werkzeug.exceptions import HTTPException

# Local
from .utils import User, um
from .quotes import qm
from .errors import error_codes
from .utils import logger
from .config import load_config

class App:
    config: dict | None = None

    def __new__(self) -> Tuple[SocketIO, Flask]:
        if not self.config:
            self.config = load_config()
        flask_app = Flask(__name__)
        flask_app.config["PERMANENT_SESSION_LIFETIME"] = self.config["session_time"]
        bootstrap = Bootstrap5(flask_app)
        flask_app.config["SECRET_KEY"] = self.config["secret_key"]

        # Blueprints
        from .accounts import blueprint as account
        from .admin import blueprint as admin
        from .chat import blueprint as chat, socket
        from .quotes import blueprint as quotes

        flask_app.register_blueprint(account)
        flask_app.register_blueprint(admin)
        flask_app.register_blueprint(quotes)
        flask_app.register_blueprint(chat)
        socket.init_app(flask_app)

        @flask_app.before_request
        def before():
            if request.endpoint is None or request.endpoint == "static":
                return
            if request.endpoint in self.config["public_endpoints"]:
                if not "style" in session:
                    session["style"] = "light"
                if "style" in request.args:
                    session["style"] = request.args.get("style")
                if not "user" in session:
                    return

            user = session.get("user")
            if not user:
                return redirect(url_for('accounts.login', reason="logging in is now required to view quotes"))
            user = User(**user)
            if not user.is_logged_in:
                return redirect(url_for('accounts.login', reason="logging in is now required to view quotes"))
            session["style"] = user.style
            if "style" in request.args:
                session["style"] = request.args.get("style")
                um.update_user(user.id, style=session["style"])
                session["user"]["style"] = session["style"]

        @flask_app.route("/")
        def landing():
            quotes = []
            for _ in range(15):
                quotes.append(qm.get_quote(-1))
            return render_template("landing.html", quotes=quotes)

        @flask_app.route("/logout")
        def logout():
            session.pop("user")
            return redirect(url_for("landing"))

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
        
        return socket, flask_app