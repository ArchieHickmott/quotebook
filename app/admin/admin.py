from flask import Blueprint, render_template, redirect, url_for, session, abort
from ..utils.userManager import check_logged_in, um, User

blueprint = Blueprint("admin", __name__, template_folder="templates", url_prefix="/admin")

@blueprint.before_request
def before():
    if not check_logged_in():
        return redirect(url_for("accounts.login", reason="login required"))
    user = User(**session["user"])
    if user.plevel > 0:
        return
    return abort(401)

@blueprint.route("/")
def portal():
    user = User(**session["user"])
    plevel = user.plevel
    if plevel == 1:
        "get all reports"
    if plevel > 1:
        "get all recent login data"
    if plevel > 2:
        "get security overview aka the entire logs table"
    return render_template("portal.html", plevel=plevel)

@blueprint.route("/security")
def security():
    user = User(**session["user"])
    plevel = user.plevel
    if plevel <= 2:
        return redirect(url_for("admin.portal"))
    return render_template("security.html", plevel=plevel)

@blueprint.route("/reports")
def reports():
    user = User(**session["user"])
    plevel = user.plevel
    return render_template("reports.html", plevel=plevel)

@blueprint.route("/users")
def users():
    user = User(**session["user"])
    plevel = user.plevel
    if plevel <= 1:
        return redirect(url_for("admin.portal"))
    return render_template("users.html", plevel=plevel)

@blueprint.route("/quotes")
def quotes():
    user = User(**session["user"])
    plevel = user.plevel
    return render_template("admin.html", plevel=plevel)