from flask import Blueprint, render_template

blueprint = Blueprint("chat", __name__, template_folder="templates", url_prefix="/chat")

@blueprint.route("/")
def home():
    return render_template("chat.html")