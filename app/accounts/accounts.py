from flask import Blueprint, render_template, session, redirect, url_for
from flask_wtf import FlaskForm
from wtforms.validators import ValidationError
from wtforms.fields import StringField, SubmitField, EmailField, PasswordField
from ..utils import um, login_required, User, generate_password_hash, db

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
def home():
    return redirect(url_for("accounts.account"))

@blueprint.route("/account")
@login_required
def account():
    user = User(**session["user"])
    liked_quotes = db.query(f"SELECT author, year, quote, likes FROM quotes WHERE id in (SELECT quote_id FROM likes WHERE user_id={user.id})")
    return render_template("account_page.html", plevel=user.plevel, name=user.name, email=user.email, likes=liked_quotes)

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