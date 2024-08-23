from flask import Blueprint

blueprint = Blueprint("chat", __name__, template_folder="templates", url_prefix="/chat")