from flask import Blueprint

blueprint = Blueprint("chat", __name__, template_folder="templates", url_prefix="/chat")

@blueprint.route("/")
def home():
    return "CHAT"