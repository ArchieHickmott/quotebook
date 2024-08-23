from flask import Blueprint

blueprint = Blueprint("accounts", __name__, template_folder="templates", url_prefix="/accounts")

@blueprint.route("/")
def account():
    return "MY ACCOUNT"

@blueprint.route('/login')
def login():
    return "LOGIN"

@blueprint.route("/register")
def register():
    return "REGISTER"