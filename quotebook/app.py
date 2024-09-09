# stdlib
from random import randbytes
import datetime as dt
import traceback as tb
from typing import Tuple

# ext. Libraries
from flask import Flask, render_template, session, request, redirect, url_for
from flask_socketio import SocketIO
from flask_bootstrap import Bootstrap5
from jinja2 import Template
from werkzeug.exceptions import HTTPException
from werkzeug.middleware.proxy_fix import ProxyFix

# Local
from .utils import User, um, db
from .errors import error_codes
from .utils import logger
from .config import load_config

class App:
    config: dict = dict()

    def __new__(self) -> Tuple[SocketIO, Flask]:
        if not self.config:
            self.config = load_config()
        flask_app = Flask(__name__)
        flask_app.config["PERMANENT_SESSION_LIFETIME"] = self.config["session_time"]
        flask_app.config["RECAPTCHA_PRIVATE_KEY"] = "6LeBKyQqAAAAAMrpRiM9BQETvmAmn5C48u3bEi9N"
        flask_app.config["RECAPTCHA_PUBLIC_KEY"] = "6LeBKyQqAAAAAMwRSIkHrPhDnACK6_aj3YO1sA2C"
        flask_app.config["SECRET_KEY"] = self.config["secret_key"]
        bootstrap = Bootstrap5(flask_app)
        
        flask_app.wsgi_app = ProxyFix( # used to fix errors when running NGINX with werkzueg
            flask_app.wsgi_app
        )

        # Blueprints
        from .accounts import blueprint as account
        from .admin import blueprint as admin
        from .chat import blueprint as chat, socket
        from .quotes import blueprint as quotes

        flask_app.register_blueprint(account)
        flask_app.register_blueprint(admin)
        flask_app.register_blueprint(quotes)
        flask_app.register_blueprint(chat)
        socket.init_app(flask_app, cors_allowed_origins="*")

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
            user.check_banned()
            if not user.active:
                reason = db.query(f"SELECT reason FROM bans WHERE user_id = {user.id}")[0][0]
                escaped_reason = flask_app.jinja_env.from_string("{{reason|e}}").render(reason=reason)
                message = f"""
                <h1>You Are Banned!</h1>
                <p>You are banned! because {escaped_reason} </p>
                <p>If this is a mistake please contact at [Insert Email Here]
                """
                return render_template("message_page.html", message=message)
            session["style"] = user.style
            if "style" in request.args:
                session["style"] = request.args.get("style")
                um.update_user(user.id, style=session["style"])
                session["user"]["style"] = session["style"]
                
        @flask_app.route("/")
        def landing():
            return render_template("landing.html")

        @flask_app.route("/logout")
        def logout():
            session.pop("user")
            return redirect(url_for("landing"))
        
        @flask_app.route("/terms-of-use")
        def terms():
            return render_template("terms_of_use.html")
        
        @flask_app.route("/privacy-policy")
        def privacy():
            return render_template("privacy_policy.html")

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