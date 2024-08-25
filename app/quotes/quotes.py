from flask import Blueprint, render_template, request, redirect, url_for
from flask_wtf import FlaskForm
from wtforms.fields import StringField, SubmitField

from ..utils.quoteManager import QuoteManager, qm

qm: QuoteManager = qm

blueprint = Blueprint("quotes", __name__, template_folder="templates", url_prefix="/quotes")

class Submit(FlaskForm):
    author = StringField("name", render_kw={"placeholder": "name"})
    year = StringField("year", render_kw={"placeholder": "year"})
    quote = StringField("quote", render_kw={"placeholder": "quote"})
    submit = SubmitField("Submit Quote")

@blueprint.route("/")
def index():
    return redirect(url_for("quotes.all"))

@blueprint.route("/home")
def home():
    random_quote = qm.get_quote(-1)
    qotd = qm.qotd()
    best_quote = qm.orderd_by_likes()[0]
    return render_template("quote.html", random_quote=random_quote, qotd=qotd, best_quote=best_quote)

@blueprint.route("/all")
def all():
    quotes = qm.search("", order_by="likes DESC")
    return render_template("all.html", quotes=quotes)

@blueprint.route("/search")
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
