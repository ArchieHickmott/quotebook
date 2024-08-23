from flask import Blueprint, render_template
from flask_wtf import FlaskForm
from wtforms.fields import StringField, SubmitField

blueprint = Blueprint("quotes", __name__, template_folder="templates", url_prefix="/quotes")

class Submit(FlaskForm):
    author = StringField("name", render_kw={"placeholder": "name"})
    year = StringField("year", render_kw={"placeholder": "year"})
    quote = StringField("quote", render_kw={"placeholder": "quote"})
    submit = SubmitField("Submit Field")

@blueprint.route("/home")
def home():
    return render_template("quote.html")

@blueprint.route("/all")
def all():
    return render_template("all.html")

@blueprint.route("/submit")
def submit():
    form: Submit = Submit()
    # TODO: make form functional
    if form.validate_on_submit():
        form.author.data = None
        form.year.data = None
        form.quote.data = None
    return render_template("submit.html", form=form)
