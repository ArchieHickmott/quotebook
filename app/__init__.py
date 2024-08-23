from random import randbytes

from flask import Flask, redirect, url_for

from accounts import blueprint as accounts
from admin import blueprint as admin
from chat import blueprint as chat
from quotes import blueprint as quotes

app = Flask(__name__)

app.register_blueprint(accounts)
app.register_blueprint(admin)
app.register_blueprint(chat)
app.register_blueprint(quotes)

app.config["SECRET_KEY"] = randbytes(128)
# app config
# .
# .
# .

@app.route("/")
def index():
    return redirect(url_for("quotes.index"))

if __name__ == "__main__":
    app.run()