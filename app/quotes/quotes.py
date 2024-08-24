from flask import Blueprint, render_template
from flask_wtf import FlaskForm
from wtforms.fields import StringField, SubmitField

from ..utils import QuoteManager, qm

qm: QuoteManager = qm

blueprint = Blueprint("quotes", __name__, template_folder="templates", url_prefix="/quotes")

class Submit(FlaskForm):
    author = StringField("name", render_kw={"placeholder": "name"})
    year = StringField("year", render_kw={"placeholder": "year"})
    quote = StringField("quote", render_kw={"placeholder": "quote"})
    submit = SubmitField("Submit Field")

@blueprint.route("/home")
def home():
    random_quote = qm.get_quote(-1)
    qotd = qm.qotd()
    best_quote = qm.orderd_by_likes()[0]
    return render_template("quote.html", random_quote=random_quote, qotd=qotd, best_quote=best_quote)

@blueprint.route("/all")
def all():
    quotes = qm.search("")
    return render_template("all.html", quotes=quotes)

@blueprint.route("/submit", methods=["GET", "POST"])
def submit():
    form: Submit = Submit()
    quotes = qm.search("")
    # TODO: make form functional
    if form.validate_on_submit():
        qm.create_quote(form.author.data, form.year.data, form.quote.data)
    
    return render_template("submit.html", form=form, quotes=quotes)
