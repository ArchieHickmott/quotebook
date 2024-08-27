from flask import Blueprint, render_template, redirect, url_for, session, abort
from ..utils.userManager import check_logged_in, um, User
from ..utils.databaseManager import db
from ..utils.quoteManager import qm
from ..utils.logger import logger
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField

blueprint = Blueprint("admin", __name__, template_folder="templates", url_prefix="/admin")

class DeleteQuote(FlaskForm):
    quote_id = StringField("Quote Id")
    submit = SubmitField("DELETE QUOTE", render_kw={"class": "btn-warning"})

class UpdateQuote(FlaskForm):
    # IT IS SUPER!!! important that the quoteid attribute name does not match the
    # attribute name in DeleteQuote, this is how flask differentiates between the two forms in
    # the /quotes endpoint
    quoteid = StringField("Quote Id")
    author = StringField("name")
    year = StringField("year")
    quote = StringField("quote")
    submit = SubmitField("Update Quote")

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
    vals = {}
    if plevel == 1:
        vals["reports"] = db.query("SELECT * FROM reports")
    if plevel > 1:
        vals["recent_logins"] = db.query("SELECT * FROM logs WHERE action = 'login' ORDER BY id DESC LIMIT 10")
    if plevel > 2:
        vals["logs"] = db.query('SELECT * FROM logs ORDER BY id DESC LIMIT 50')
    return render_template("portal.html", plevel=plevel, **vals)

@blueprint.route("/security")
def security():
    user = User(**session["user"])
    plevel = user.plevel
    if plevel <= 2:
        return redirect(url_for("admin.portal"))
    logs = db.query('SELECT * FROM logs ORDER BY id DESC LIMIT 50')
    return render_template("security.html", plevel=plevel, logs=logs)

@blueprint.route("/reports")
def reports():
    user = User(**session["user"])
    plevel = user.plevel
    reports = db.query("SELECT * FROM reports")
    return render_template("reports.html", plevel=plevel, reports=reports)

@blueprint.route("/users")
def users():
    user = User(**session["user"])
    plevel = user.plevel
    if plevel <= 1:
        return redirect(url_for("admin.portal"))
    users = db.query("SELECT id, name, email, created_at, style, plevel FROM users")
    return render_template("users.html", plevel=plevel, users=users)

@blueprint.route("/quotes", methods=["GET", "POST"])
def quotes():
    user = User(**session["user"])
    plevel = user.plevel
    update_form: UpdateQuote = UpdateQuote()
    delete_form: DeleteQuote = DeleteQuote()
    if update_form.validate_on_submit() and update_form.quoteid.data:
        logger.info(update_form.data)
        logger.info(delete_form.data)
        logger.warning(f"updating quote {update_form.quoteid.data}")
        qm.update_quote(int(update_form.quoteid.data), 
                        update_form.author.data, 
                        update_form.quote.data,
                        update_form.year.data)
        update_form.quoteid.data = None
        update_form.author.data = None 
        update_form.quote.data = None
        update_form.year.data = None
    if delete_form.validate_on_submit() and delete_form.quote_id.data:
        logger.warning(f"deleting quote {delete_form.quote_id.data}")
        qm.delete_quote(int(delete_form.quote_id.data))   
        delete_form.quote_id.data = None
    quotes = db.query("SELECT id, author, year, quote, likes FROM quotes")
    return render_template("quotes.html", plevel=plevel, quotes=quotes, delete_form=delete_form, update_form=update_form)