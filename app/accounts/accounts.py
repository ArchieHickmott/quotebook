from flask import Blueprint, render_template
from flask_wtf import FlaskForm
from wtforms.fields import StringField, SubmitField, EmailField, PasswordField

blueprint = Blueprint("accounts", __name__, template_folder="templates", url_prefix="/accounts")

class Register(FlaskForm):
    name = StringField("name")
    email = EmailField("email")
    password = PasswordField("password")
    submit = SubmitField("Register Account")

class Login(FlaskForm):
    email = EmailField("email")
    password = PasswordField("password")
    submit = SubmitField("Login")

@blueprint.route("/")
def account():
    return render_template("account_page.html")

@blueprint.route('/login')
def login():
    form = Login()
    return render_template("login.html", form=form)

@blueprint.route("/register")
def register():
    form = Register()
    return render_template("register.html", form=form)