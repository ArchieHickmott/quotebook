from flask import Blueprint, render_template, session, redirect, url_for
from flask_wtf import FlaskForm, RecaptchaField
from wtforms.validators import ValidationError, DataRequired
from wtforms.fields import StringField, SubmitField, EmailField, PasswordField, BooleanField 
from ..utils import um, login_required, User, generate_password_hash, db, qm

blueprint = Blueprint("accounts", __name__, template_folder="templates", url_prefix="/accounts")

class Register(FlaskForm):
    name = StringField("name", [DataRequired()])
    email = EmailField("email", [DataRequired()])
    password = PasswordField("password", [DataRequired()])
    privacy = BooleanField('I agree to the Privacy Policy and the Terms & Conditions', validators=[DataRequired()])
    recaptcha = RecaptchaField()
    submit = SubmitField("Register Account")
    
    def validate_privacy(form: FlaskForm, field: BooleanField):
        if not field.data:
            raise ValidationError("You must agree to the privacy policy to create account")
    
    def validate_name(form: FlaskForm, name: StringField):
        if not name.data.replace(" ", "").isalpha():
            raise ValidationError("name must contain alphabetical characters only")
    
    def validate_email(form: FlaskForm, email: StringField):
        email: str = email.data
        results = db.query("SELECT * FROM users WHERE email = ?", (email,))
        if len(results) > 0:
            raise ValidationError("email already exists")
        try:
            int(email[0])
            int(email[1])
            if email.split("@")[1] != "stpatricks.qld.edu.au": raise Exception("doesn't end in stpatricks.qld.edu.au")
            if not email.split("@")[0][2:].isalpha() or len(email.split("@")[0][2:]) > 7: raise Exception("not a valid student email")
        except Exception as e:
            raise ValidationError(f"email must be a student email")
        
class Login(FlaskForm):
    email = EmailField("email")
    password = PasswordField("password")
    submit = SubmitField("Login")

@blueprint.route("/")
@login_required
def home():
    return redirect(url_for("accounts.account"))

@blueprint.route("/logout")
def logout():
    session.pop("user")
    return redirect(url_for("landing"))

@blueprint.route("/account")
@login_required
def account():
    user = User(**session["user"])
    liked_quotes = db.query(f"SELECT id, author, year, quote, likes {qm.get_liked_sql.format(id=user.id)} FROM quotes WHERE id in (SELECT quote_id FROM likes WHERE user_id={user.id})")
    return render_template("account_page.html", plevel=user.plevel, name=user.name, email=user.email, likes=liked_quotes)

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
