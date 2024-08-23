from flask import Blueprint

blueprint = Blueprint("accounts", __name__, template_folder="templates", url_prefix="/accounts")