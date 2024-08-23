from flask import Blueprint, redirect, url_for

blueprint = Blueprint("quotes", __name__, template_folder="templates", url_prefix="/quotes")

@blueprint.route("/home")
def home():
    return "HOME OF THE QUOTES"

@blueprint.route("/all")
def all():
    return "ALL OF THE QUOTES"

@blueprint.route("/submit")
def submit():
    return "SUBMIT A QUOTE"
