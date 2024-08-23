from flask import Blueprint

blueprint = Blueprint("quotes", __name__, template_folder="templates", url_prefix="/quotes")