from flask import Blueprint, render_template, redirect, url_for, session, abort, request
from ..utils.userManager import check_logged_in, um, User
from ..utils import db, qm, logger
from flask_wtf import FlaskForm, RecaptchaField
from wtforms import StringField, SubmitField, HiddenField

blueprint = Blueprint("admin", __name__, template_folder="templates", url_prefix="/admin")

class DeleteQuote(FlaskForm):
    quote_id = StringField("Quote Id | Enter ID manually to confirm delete")
    submit = SubmitField("DELETE QUOTE", render_kw={"class": "btn-warning"})

class UpdateQuote(FlaskForm):
    # IT IS SUPER!!! important that the quoteid attribute name does not match the
    # attribute name in DeleteQuote, this is how flask differentiates between the two forms in
    # the /quotes endpoint
    recaptcha = RecaptchaField()
    quoteid = StringField("Quote Id")
    author = StringField("name")
    year = StringField("year")
    quote = StringField("quote")
    recaptcha = RecaptchaField()
    submit = SubmitField("Update Quote")
    
class BanUser(FlaskForm):
    user_id = HiddenField()
    reason = StringField("Reason")    
    submit = SubmitField("Ban User", render_kw={"class": "btm btn-danger"})

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
    if plevel > 0:
        vals["reports"] = db.query("SELECT * FROM reports")
        logger.info(vals["reports"])
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

@blueprint.route("/reports/<int:id>", methods=["GET", "POST"])
def report(id: int):
    user = User(**session["user"])
    plevel = user.plevel
    report = db.query(f"SELECT * FROM reports WHERE id={id}")[0]
    try: quote = qm.get_quote(int(report[2]))
    except: quote = (1, "n/a", "n/a", "QUOTE DOES NOT EXIST", 0)
    update_form, delete_form = _update_quote_logic()
    update_form.quoteid.data = quote[0]
    update_form.author.data = quote[1]
    update_form.year.data = quote[2]
    update_form.quote.data = quote[3]
    if update_form.is_submitted() or delete_form.is_submitted():
        db.query(f"UPDATE reports SET status=1 WHERE id={id}")
    return render_template("report.html", plevel=plevel, id=id, update_form=update_form, delete_form=delete_form, quote=quote, report=report)

@blueprint.route("/users")
def users():
    if request.args.get("id"):
        try: id = int(request.args.get("id"))
        except: return abort(400)
        return redirect(f"/users/{id}")
    user = User(**session["user"])
    plevel = user.plevel
    if plevel <= 1:
        return redirect(url_for("admin.portal"))
    users = db.query("SELECT id, name, email, created_at, style, plevel FROM users")
    return render_template("users.html", plevel=plevel, users=users)

@blueprint.route("/users/<int:id>", methods=["GET", "POST"])
def user_info(id: int):
    admin = User(**session["user"])
    plevel = admin.plevel
    try: user = um.get_user(id)
    except IndexError: return redirect(url_for("admin.users"))
    logs = db.query(f'SELECT * FROM logs WHERE user_id = {user.id} ORDER BY id DESC LIMIT 50')
    form: BanUser = BanUser()
    if form.validate_on_submit():
        if user.active:
            db.query(f"INSERT INTO bans VALUES ({id}, ?)", (form.reason.data,))
        else:
            db.query(f"DELETE FROM bans WHERE user_id = {id}")
        user.check_banned()
    form.user_id.data = id
    if not user.active:
        form._fields.pop("reason")
        form.submit.label.text = "Un-ban"
    return render_template("user_info.html", plevel=plevel, user=user, user_logs=logs, form=form)

@blueprint.route("/quotes", methods=["GET", "POST"])
def quotes():
    user = User(**session["user"])
    plevel = user.plevel
    update_form, delete_form = _update_quote_logic()
    quotes = db.query("SELECT id, author, year, quote, likes FROM quotes")
    return render_template("quotes.html", plevel=plevel, quotes=quotes, delete_form=delete_form, update_form=update_form)

def _update_quote_logic():
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
    return update_form, delete_form