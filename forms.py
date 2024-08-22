from flask_wtf import FlaskForm, RecaptchaField
from wtforms import StringField, PasswordField, SubmitField, ValidationError
from wtforms.validators import InputRequired, DataRequired, Email

# form displayed when logging in
class LoginForm(FlaskForm):
    email = StringField("Email", [InputRequired("Please enter your email"), Email("Please enter your email")], render_kw={"placeholder": "Email"})
    password = PasswordField("Password", [InputRequired("please enter your password")], render_kw={"placeholder": "Password"})
    submit = SubmitField("Log-In", render_kw={"class": "btn btn-light"})
    
# form displayed when registering
class RegisterForm(FlaskForm):
    first_name = StringField("First Name | Required",[InputRequired("please enter a first name")], render_kw={"placeholder": "First Name", "required":True})
    last_name = StringField("Last Name", render_kw={"placeholder": "Last Name"})
    email = StringField("Email | Required", [InputRequired("please enter an email"), Email("not a valid email")], render_kw={"placeholder": "Email", "required":True})
    password = PasswordField("Password | Required", [InputRequired("please enter a password")], render_kw={"placeholder": "Password", "required":True})
    confirm_password = PasswordField("Confirm Password | Required", [InputRequired("please confirm your password")], render_kw={"placeholder": "Confirm Password", "required":True})
    # recaptcha = RecaptchaField()
    submit = SubmitField("Register", render_kw={"class": "btn btn-light"})      

    def validate_confirm_password(self, field: PasswordField):
        psw1 = self.password.data
        psw2 = field.data
        if not psw1 == psw2:
            raise ValidationError("passwords do not match")

class UpdateDataForm(FlaskForm):
    first_name = StringField("First Name", render_kw={"placeholder": "First Name", "required":True})
    last_name = StringField("Last Name", render_kw={"placeholder": "Last Name"})
    password = PasswordField("Password", [InputRequired("please enter your password")], render_kw={"placeholder": "Password", "required":True})
    # recaptcha = RecaptchaField()
    submit = SubmitField("Update", render_kw={"class": "btn btn-light"})

class ConfirmDelete(FlaskForm):
    submit = SubmitField("DELTE ACCOUNT", render_kw={"class": "btn btn-warning"})

class QuoteForm(FlaskForm):
    name = StringField("Name", [InputRequired()])
    date = StringField("Date")
    quote = StringField("Quote", [InputRequired()])
    submit = SubmitField("submit quote", render_kw={"class": "button button-dark"})

class SearchForm(FlaskForm):
    search = StringField("search", [InputRequired()])
    submit = SubmitField("search", render_kw={"class": "button button-dark"})