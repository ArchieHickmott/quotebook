# Standard Imports
from traceback import format_exc, print_exc
from datetime import datetime
import datetime as dt
from random import randint, randbytes
import json
import os

# External Imports
try:
    from flask import render_template, redirect, url_for, request, session
    from fortifysql import Database, Table
    from flask import Flask, render_template, request, abort, Response
    from flask_bootstrap import Bootstrap5
    from flask_wtf import FlaskForm
    from flask_bcrypt import Bcrypt
    from werkzeug.exceptions import HTTPException
    from wtforms import StringField, DateField, SubmitField, HiddenField
    from wtforms.validators import InputRequired
except ImportError as e:
    print(e)
    yn = input("Would you like to install the required libraries? (Y,n): ")
    if yn.lower() == "y":
        os.system("pip install -r requirements.txt")

# Local Imports
from users import User
from forms import LoginForm, RegisterForm, UpdateDataForm, ConfirmDelete, QuoteForm, SearchForm
from app_errors import AuthError, AppError, error_codes
from config import create_app

# create a pre-configured app
app, db, crypt = create_app()

def user_has_liked(userid, quoteid) -> bool:
    count_likes(quoteid)
    if db.likes.get().filter(quoteid=int(quoteid), userid=int(userid)).all():
        return True
    return False    

def count_likes(quoteid):
    num_likes = db.query(f"SELECT count(quoteid) FROM likes WHERE quoteid={quoteid}")[0][0]
    db.quotes.replace(f"quoteid={quoteid}", numlikes=num_likes)

def like_quote(quoteid, userid):
    if user_has_liked(userid, quoteid):
        return
    db.likes.append(quoteid=int(quoteid), userid=int(userid))
    count_likes(quoteid)
    
def unlike_quote(quoteid, userid):
    db.likes.remove(quoteid=int(quoteid), userid=int(userid))
    count_likes(quoteid)

@app.before_request
def before():
    if "like" in request.form and "user" in session:
        user = User.load(**session["user"])
        print(request.form["like"])
        like_quote(request.form["like"], user.id())
    elif "unlike" in request.form and "user" in session:
        user = User.load(**session["user"])
        print(request.form["unlike"])
        unlike_quote(request.form["unlike"], user.id())
 
@app.route('/submit', methods=["GET", "POST"])
def submit():
    form: QuoteForm = QuoteForm()
    quotes: Table = db.quotes
    if form.validate_on_submit():
        name = form.name.data
        date = form.date.data
        form.date.data = ""
        form.name.data = ""

        if not date:
            date = dt.datetime.now().strftime("%Y")
        quote = form.quote.data
        form.quote.data = ""
        if len(quote) > 300 or len(name) > 300 or len(date) > 300:
            form.quote.errors.append(ValueError("too long"))
        else:
            quotes.append(name=name, year=date, quote=quote)
    quotes = quotes("name", "year", "quote")
    return render_template("submit.html", form=form, quotes=quotes, search_form=SearchForm())

@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST" and "user" in session:
        user = User.load(**session["user"])
        like_quote(request.form["id"], user.id())
    
    if db.query("SELECT count(*) FROM quotes")[0][0] == 0:
        quote = ("No quotes found", "0000", "No quotes found")
        return render_template("index.html", quote=quote, quoteid=0, best_quote=quote, search_form=SearchForm())
    
    quote = db.query(f"SELECT name, year, quote FROM quotes ORDER BY RANDOM() LIMIT 1")[0] 
    best_quote = db.quotes.get("name", "year", "quote").order("numlikes DESC").limit(1)[0]
    
    return render_template("index.html", quote=quote, quoteid=id, best_quote=best_quote, search_form=SearchForm())

@app.route("/quotes", methods=["GET", "POST"])
def quotes():
    quotes: Table = db.quotes
    
    if not "user" in session:
        quotes = quotes.get("name", "year", "quote", "numlikes").order("numlikes DESC").all()
        return render_template("quotes.html", quotes=quotes, search_form=SearchForm())
    
    quotes_ls = db.query("""SELECT name, year, quote, numlikes, rowid FROM quotes
                      ORDER BY numlikes DESC""") 
    
    displayed_quotes = []
    for quote in quotes_ls:
        likes = quotes.get("likes").filter(f"rowid={quote[4]}").first()[0]
        likes = json.loads(likes)
        displayed_quotes.append((*quote, likes))
        
    user = User.load(**session["user"])
    return render_template("quotes.html", quotes=displayed_quotes, id=int(user.id()), search_form=SearchForm())
    
# MARK: Login Page
@app.route('/login', methods=['GET', 'POST'])
def login():
    if "user" in session:
        return redirect(url_for('home'))
    form: LoginForm = LoginForm()
    if form.validate_on_submit() and request.method == "POST":
        # get relevent user data
        email = form.email.data
        password = form.password.data
        id = db.users.get(db.users.userid).filter(email=email).first()
        
        # log in algorithm
        try:
            id = id[0]
            user = User(id, password)
        except TypeError: form.submit.errors.append("Something went wrong, please try again. 😢")
        except AuthError as e:
            app.logger.warning(f"failed loggin for {id}")
            db.log_failed_logins.append(userid=id, 
                                        ip=request.remote_addr, 
                                        time=datetime.now(), 
                                        error_message=str(e))
            form.submit.errors.append("Something went wrong, please try again. 😢")
        else: # SUCCESSFUL LOGIN
            db.log_logins.append(userid=id, ip=request.remote_addr, time=datetime.now())
            session["user"] = vars(user)
            return redirect(url_for('home'))
    return render_template("login.html", form=form, search_form=SearchForm())

# MARK: Register Page
@app.route('/register', methods=['GET', 'POST'])
def register():
    if "user" in session:
        return redirect(url_for('home'))
    form: RegisterForm = RegisterForm()
    if form.validate_on_submit() and request.method == "POST":
        first_name = form.first_name.data
        last_name = form.last_name.data
        email = form.email.data 
        password = form.password.data
        
        if db.users.get("email").filter(email=email).first():
            form.email.errors.append(ValueError("email is already in use"))
            return render_template("register.html", form=form)
        
        User.create_user(db, first_name, last_name, email, password)
        return redirect(url_for("login"))
    return render_template("register.html", form=form, search_form=SearchForm())

# MARK: Home Page
# home page (logged in users only)
@app.route('/home', methods=["GET", "POST"])
def home():
    quotes: Table = db.quotes
    num = db.query("SELECT max(rowid) FROM quotes")[0][0]
    while True:
        id = randint(1, num)
        try:
            quote = db.query(f"SELECT name, year, quote FROM quotes WHERE rowid = {id}")[0]
            likes = quotes.get("likes").filter(f"rowid={id}").first()[0]
            likes = json.loads(likes)
            quote = (*quote, likes)
        except IndexError:
            pass
        else:
            break
    if not "user" in session:
        return redirect(url_for("login")), 401
    user = User.load(**session["user"])
    if not user.is_logged_in():
        return redirect(url_for("login"))
    best_quote = db.query("SELECT name, year, quote, rowid FROM quotes ORDER BY numlikes DESC LIMIT 1")[0]
    print(best_quote)
    b_likes = quotes.get("likes").filter(f"rowid={best_quote[3]}").first()[0]
    b_likes = json.loads(b_likes)
    best_quote = (*best_quote, b_likes)
    bid = best_quote[3]
    return render_template("home.html", user=user, id=int(user.id()),
                           quote=quote, quoteid=id, 
                           best_quote=best_quote, best_quote_id=bid, search_form=SearchForm())

# MARK: logout/delete
@app.route("/logout")
def logout():
    if "user" in session:
        session.pop("user")
    return redirect(url_for("login"))

@app.route("/delete", methods=["GET", "POST"])
def delete_account():
    form = ConfirmDelete()
    if not "user" in session:
        return redirect(url_for("index"))
    user = User.load(**session["user"])
    if not user.is_logged_in():
        return redirect(url_for("index"))
    if not form.validate_on_submit():
        return render_template("confirm_delete.html", form=form, search_form=SearchForm())
    id = user.id()
    session.pop("user")
    db.log_detail_changes.remove(userid=id)
    db.log_failed_logins.remove(userid=id)
    db.log_logins.remove(userid=id)
    db.passwords.remove(userid=id)
    db.users.remove(userid=id)
    return redirect(url_for("login"))

# MARK: Admin
@app.route('/admin')
def admin():
    # office_open = dt.time(9, 0)
    # office_close = dt.time(17, 0)
    # current_time = datetime.now().time()
    # if not office_open <= current_time <= office_close:
        # app.logger.warning("attempted access of admin portal outside of office hours")
        # return "Admin portal can only accessed during office hours"
    if not "user" in session:
        return redirect(url_for('login'))
    users = db.users
    user = User.load(**session["user"])
    permission_level = users.get("PLEVEL").filter(userid=user.id()).first()[0]
    if (not isinstance(permission_level, int)) or permission_level < 0:
        app.logger.critical("There exists a user with an invalid permission level")
        raise AppError("Invalid permission level")
    requested_user_data = request.args.get("user")
    if requested_user_data and permission_level != 0:
        id = requested_user_data
        return render_template("user_data_lookup.html", 
                                id=requested_user_data,
                                first_name=users.get(users.first_name).filter(userid=id).first()[0],
                                last_name=users.get(users.last_name).filter(userid=id).first()[0],
                                email=users.get(users.email).filter(userid=id).first()[0],
                                date_created=users.get(users.date_created).filter(userid=id).first()[0],
                                plevel=users.get(users.PLEVEL).filter(userid=id).first()[0],
                                logins=db.log_logins.get("ip", "time").filter(userid=id).order("time DESC").all(),
                                fails=db.log_failed_logins.get("ip", "time").filter(userid=id).order("time DESC").all(),
                                search_form=SearchForm())
    if not user.is_logged_in():
        return redirect(url_for("login")) 
    if permission_level != 0:
        users_table = users.get().all()
        fails = db.query(f"""SELECT fails.userid, users.email, fails.ip, fails.time
                            FROM log_failed_logins as fails, users WHERE fails.userid = users.userid
                            LIMIT 5""")
        logins = db.query(f"""SELECT fails.userid, users.email, fails.ip, fails.time
                            FROM log_logins as fails, users WHERE fails.userid = users.userid
                            ORDER BY time DESC
                            LIMIT 5""")
        return render_template('admin.html', 
                                user=user, 
                                users=users_table, 
                                fails=fails, 
                                logins=logins,
                                plevel = permission_level, 
                                search_form=SearchForm())
    return "NOT ADMIN", 401

@app.errorhandler(Exception)
def errors(e: Exception):
    if isinstance(e, HTTPException):
        if e.code == 404:
            return render_template("404.html", msg=error_codes[e.code], search_form=SearchForm())
        else:
            app.logger.warning(f"error in app {e.code}")
    tb = format_exc()  # Capture traceback 
    app.logger.error(f"Exception in app {e}", extra={"error": str(e),"traceback":tb})
    raise e

if __name__ == '__main__':  
    app.run(host="0.0.0.0", debug=True)
