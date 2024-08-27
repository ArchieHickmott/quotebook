from flask import Blueprint, render_template, session, redirect, url_for
from flask_wtf import FlaskForm
from wtforms.validators import ValidationError
from wtforms.fields import StringField, SubmitField, EmailField, PasswordField
from ..utils.userManager import um, login_required
from ..utils import db
from ..utils.crypt import generate_password_hash
import logging

blueprint = Blueprint("accounts", __name__, template_folder="templates", url_prefix="/accounts")

class Register(FlaskForm):
    name = StringField("name")
    email = EmailField("email")
    password = PasswordField("password")
    submit = SubmitField("Register Account")
    
    def validate_name(form: FlaskForm, name: StringField):
        if not name.data.replace(" ", "").isalpha():
            raise ValidationError("name must contain alphabetical characters only")
    
    def validate_email(form: FlaskForm, email: StringField):
        results = db.query("SELECT * FROM users WHERE email = ?", (email.data,))
        if len(results) > 0:
            raise ValidationError("email already exists")           

class Login(FlaskForm):
    email = EmailField("email")
    password = PasswordField("password")
    submit = SubmitField("Login")

@blueprint.route("/")
@login_required
def account():
    return render_template("account_page.html")

@blueprint.route("/logout")
def logout():
    if "user" in session:
        session.pop("user")
    return redirect(url_for("landing"))

@blueprint.route('/login', methods=["GET", "POST"])
def login():
    form: Login = Login()
    if form.validate_on_submit():
        email = form.email.data
        password = form.password.data
        try:
            user = um.get_user(email=email)
            if user.log_in(password):
                session["user"] = user
                return redirect(url_for("accounts.account"))
        except:
            pass
        form.password.errors.append("Incorrect Email or Password")
    return render_template("login.html", form=form)

@blueprint.route("/register", methods=["GET", "POST"])
def register():
    form: Register = Register()
    if form.validate_on_submit():
        name = form.name.data
        email = form.email.data
        password = form.password.data
        style = session["style"] if "style" in session else "light"
        user = um.create_user(name, email, generate_password_hash(password), style)
        user.log_in(password)
        session["user"] = user
        return redirect(url_for("accounts.account"))
    return render_template("register.html", form=form)