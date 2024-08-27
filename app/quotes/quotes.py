from flask import Blueprint, render_template, request, redirect, url_for, session
from flask_wtf import FlaskForm
from wtforms.fields import StringField, SubmitField, SelectField
from wtforms.validators import DataRequired
import random
import datetime

from ..utils import qm, db, User, login_required

qm = qm

blueprint = Blueprint("quotes", __name__, template_folder="templates", url_prefix="/quotes")

get_liked_sql = "CASE WHEN id IN (SELECT quote_id FROM likes WHERE user_id={id}) THEN 2 ELSE 1 END"


class Submit(FlaskForm):
    author = StringField("name", [DataRequired()], render_kw={"placeholder": "name"})
    year = StringField("year", [DataRequired()], render_kw={"placeholder": "year"})
    quote = StringField("quote", [DataRequired()], render_kw={"placeholder": "quote"})
    submit = SubmitField("Submit Quote")

class Report(FlaskForm):
    reason = SelectField("reason", [DataRequired()], 
                         choices=[("needs updating", "needs updating"),
                                  ("personal reasons", "personal reasons"),
                                  ("not funny", "not funny"),
                                  ("joke taken too far", "joke taken too far"),
                                  ("not a quote", "not a quote"),
                                  ("other", "other")])
    details = StringField("details")
    submit = SubmitField("submit a report")

@blueprint.before_request
def before():
    if "like" in request.form and "user" in session:
        user = User(**session["user"])
        qm.like_quote(user.id, int(request.form["like"]))
    elif "unlike" in request.form and "user" in session:
        user = User(**session["user"])
        qm.unlike_quote(user.id, int(request.form["unlike"]))

@blueprint.route("/", methods=["GET", "POST"])
def index():
    return redirect(url_for("quotes.all"))

@blueprint.route("/home", methods=["GET", "POST"])
def home():
    if "user" in session:
        user = User(**session["user"])
        random_quote = db.query(f"""SELECT id, author, year, quote, likes, {get_liked_sql.format(id=user.id)} 
                                    FROM quotes 
                                    ORDER BY RANDOM()
                                    LIMIT 1""")[0]
        quotes = db.query(f"""SELECT id, author, year, quote, likes, {get_liked_sql.format(id=user.id)} 
                              FROM quotes""")
        random.seed(datetime.datetime.now().day)
        qotd = quotes[random.randint(0, len(quotes) - 1)]
        best_quote = db.query(f"""SELECT id, author, year, quote, likes, {get_liked_sql.format(id=user.id)}
                                  FROM quotes 
                                  ORDER BY likes DESC""")[0]
    else:
        random_quote = qm.get_quote(-1)
        qotd = qm.qotd()
        best_quote = qm.orderd_by_likes()[0]
    return render_template("home.html", random_quote=random_quote, qotd=qotd, best_quote=best_quote)

@blueprint.route("/all", methods=["GET", "POST"])
def all():
    quotes = qm.search("", order_by="likes DESC")
    return render_template("all.html", quotes=quotes)

@blueprint.route("/search", methods=["GET", "POST"])
def search():
    if request.args.get("query"):
        query = request.args.get("query")
    else:
        query = ""
    if request.args.get("field"):
        field = request.args.get("field")
        if not field in ["name", "year", "quote", "author"]: field=None
        if field == "name": field = "author"
    else:
        field = None
    if request.args.get("order"):
        order = request.args.get("order")
        if order == "default": order = None
        if order == "name": order = "author"
    else:
        order = None
    quotes = qm.search(query, field, order)
    return render_template("search.html", quotes=quotes)

@blueprint.route("/submit", methods=["GET", "POST"])
def submit():
    form: Submit = Submit()
    quotes = qm.search("")
    # TODO: make form functional
    if form.validate_on_submit():
        fields = (form.author, form.year, form.quote)
        qm.create_quote(*(field.data for field in fields))
        quotes = qm.search("", order_by="id DESC")
        for field in fields:
            setattr(field, "data", None)
    return render_template("submit.html", form=form, quotes=quotes)

@blueprint.route("/report", methods=["GET", "POST"])
@login_required
def report():
    form: Report = Report()
    quote = request.args.get("quote", False)
    if not quote:
        return redirect(url_for("quotes.all"))
    quote = int(quote)
    if form.validate_on_submit():
        user = User(**session["user"])
        reason = form.reason
        details = form.details
        db.query(f"INSERT INTO reports (user_id, quote_id, reason, details, status) VALUES ({user.id}, {quote}, ?, ?, 0)",
                 (reason, details))
        # yeah ik and don't care that this is bad practice, fight me about it
        message = \
        """
        <h2>Success</h2>
        <p>
            your report will be view by our admin team <br> if they deem suitable, action will be taken
        </p>
        """
        return render_template("message_page.html", message=message)
    quote = db.query(f"SELECT author, year, quote FROM quotes WHERE id={quote}")[0]
    return render_template("report.html", quote=quote, form=form)

@blueprint.route("/<int:quoteid>")
def quote_page(quoteid):
    quote = qm.get_quote(quoteid)
    return render_template("quote.html", quote=quote)
    