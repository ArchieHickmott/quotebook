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
    yn = input("Would you like to install the required libraries? (y/n): ")
    if yn.lower() == "y":
        os.system("pip install -r requirements.txt")

# Local Imports
from users import User
from forms import LoginForm, RegisterForm, UpdateDataForm, ConfirmDelete, QuoteForm, ReportForm
from app_errors import AuthError, AppError, error_codes
from config import create_app
from data_classes import Quote
 
app, db, crypt = create_app()

# NOTE: userid and quoteid are safe variables, no need to parameterize
def user_has_liked(userid, quoteid) -> bool:
    count_likes(quoteid)
    if db.query(f"SELECT * FROM likes WHERE quoteid={quoteid} AND userid={userid}"):
        return True
    return False    

def count_likes(quoteid):
    num_likes = db.query(f"SELECT count(quoteid) FROM likes WHERE quoteid={quoteid}")[0][0]
    db.query(f"UPDATE likes WHERE quoteid={quoteid} WHERE numlikes={num_likes}")

def like_quote(quoteid, userid):
    if user_has_liked(userid, quoteid):
        return
    db.query(f"INSERT INTO likes VALUES ({quoteid}, {userid})")
    count_likes(quoteid)
    
def unlike_quote(quoteid, userid):
    db.query(f"DELETE FROM likes WHERE quoteid={quoteid} AND userid={userid}")
    count_likes(quoteid)

@app.before_request
def before():
    if "like" in request.form and "user" in session:
        user = User.load(**session["user"])
        like_quote(request.form["like"], user.id())
    elif "unlike" in request.form and "user" in session:
        user = User.load(**session["user"])
        unlike_quote(request.form["unlike"], user.id())
 
@app.route('/submit', methods=["GET", "POST"])
def submit():
    form: QuoteForm = QuoteForm()
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
            db.query("INSERT INTO quotes (name, year, quote) VALUES (?, ?, ?)", (name, date, quote))
    results = db.query("SELECT name, year, quotes FROM quotes")
    quotes = []
    for quote in results:
        quotes.append(Quote(*quote))
    return render_template("submit.html", form=form, quotes=quotes)

@app.route("/", methods=["GET", "POST"])
def index():
    if "user" in session:
        return redirect(url_for("home"))
    if db.query("SELECT count(*) FROM quotes")[0][0] == 0:
        quote = Quote("No quotes found", "0000", "No quotes found")
        return render_template("index.html", quote=quote, quoteid=0, best_quote=quote)
    
    quote = db.query(f"SELECT name, year, quote FROM quotes ORDER BY RANDOM() LIMIT 1")[0] 
    best_quote = db.query("SELECT name, year, quote FROM quotes ORDER BY numlikes DESC LIMIT 1")[0]
    
    quote = Quote(*quote)
    best_quote = Quote(*best_quote)
    
    return render_template("index.html", quote=quote, quoteid=id, best_quote=best_quote)

@app.route("/quotes", methods=["GET", "POST"])
def quotes():
    if not "user" in session:
        results = db.query("SELECT name, year, quote, numlikes FROM quotes ORDER BY numlikes DESC")
        quotes = []
        for quote in results:
            quotes.append(Quote(*quote))
        return render_template("quotes.html", quotes=quotes)
    user = User.load(**session["user"])
    sql = f"""SELECT  name, year, quote, numlikes, quoteid, 
                        CASE WHEN quoteid IN (SELECT quoteid 
                                                FROM likes 
                                                WHERE userid={user.id()}) 
                        THEN 1 ELSE 0 END
                FROM quotes
                ORDER BY numlikes DESC"""
    quotes = db.query(sql)
    return render_template("quotes.html", quotes=quotes, id=int(user.id()))

@app.route("/search", methods=["GET", "POST"])
def search():
    if request.args.get("search"):
        search = request.args.get("search")
        if not "user" in session:
            sql = """
                    SELECT name, year, quote, numlikes FROM quotes 
                    WHERE name LIKE ?
                    OR year LIKE ?
                    OR quote LIKE ?
                """
            results = db.query(sql, tuple("%" + search.strip() + "%" for _ in range(3)))
            return render_template("quotes.html", quotes=results)
        user = User.load(**session["user"])
        sql =f"""SELECT  name, year, quote, numlikes, quoteid, 
                        CASE WHEN quoteid IN (SELECT quoteid 
                                                FROM likes 
                                                WHERE userid={user.id()}) 
                        THEN 1 ELSE 0 END
                FROM quotes
                WHERE name LIKE ?
                    OR year LIKE ?
                    OR quote LIKE ?
                ORDER BY numlikes DESC"""
        results = db.query(sql, tuple("%" + search.strip() + "%" for _ in range(3)))
        return render_template("quotes.html", user=user, quotes=results, id=int(user.id()))
    return redirect(url_for("/"))

@app.route("/report", methods=["GET", "POST"])
def report():
    if not "user" in session:
        return redirect(url_for("login"))
    user = User.load(**session["user"])
    form: ReportForm = ReportForm()
    extra = ""
    if form.validate_on_submit():
        form.reason.data = None
        form.detials.data = None
        extra="submitted successfully"
    if request.args.get("quoteid"):
        quoteid = int(request.args.get("quoteid"))
        form.userid.data = user.id()
        form.quoteid.data = quoteid
        quote = db.query(f"SELECT name, year, quote WHERE quoteid={quoteid}")[0]
        quote = Quote(quoteid, *quote)
        return render_template("report.html", form=form, quote=quote, extra=extra)        
    else:
        return redirect(url_for("index"))

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
        id = db.query("SELECT userid FROM users WHERE email=?", (email,))[0]
        try:
            id = id[0]
            user = User(id, password)
        except TypeError: form.password.errors.append("Something went wrong, please try again. 😢")
        except AuthError as e:
            app.logger.warning(f"failed loggin for {id}")
            db.query(f"INSERT INTO log_failed_logins VALUES ({id}, ?, ?, ?)", 
                                (request.remote_addr, datetime.now(), str(e)))
            form.password.errors.append("Something went wrong, please try again. 😢")
        else: # SUCCESSFUL LOGIN
            db.query(f"INSERT INTO log_logins VALUES ({id}, ?, ?)", (request.remote_addr, datetime.now()))
            session["user"] = vars(user)
            return redirect(url_for('home'))
    return render_template("login.html", form=form)

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
        
        if db.query("SELECT email FROM users WHERE email=?", (email,))[0]:
            form.email.errors.append(ValueError("email is already in use"))
            return render_template("register.html", form=form)
        
        User.create_user(db, first_name, last_name, email, password)
        return redirect(url_for("login"))
    return render_template("register.html", form=form)

# MARK: Home Page
# home page (logged in users only)
@app.route('/home', methods=["GET", "POST"])
def home():
    if not "user" in session:
        return redirect(url_for("login"))
        
    user = User.load(**session["user"])
    
    if db.query("SELECT count(*) FROM quotes")[0][0] == 0:
        quote = Quote("No quotes found", "0000", "No quotes found")
        return render_template("index.html", quote=quote, quoteid=0, best_quote=quote)
    
    quote = db.query(f"SELECT quoteid, name, year, quote FROM quotes ORDER BY RANDOM() LIMIT 1")[0] 
    best_quote = db.quotes.get("quoteid", "name", "year", "quote").order("numlikes DESC").limit(1)[0]
    
    quote = Quote(*quote)
    best_quote = Quote(*best_quote)
    return render_template("home.html", user=user, id=int(user.id()),
                           quote=quote, best_quote=best_quote)

# MARK: logout/delete
@app.route("/logout")
def logout():
    if "user" in session:
        session.pop("user")
    return redirect(url_for("login"))

@app.errorhandler(Exception)
def errors(e: Exception):
    if isinstance(e, HTTPException):
        if e.code == 404:
            return render_template("404.html", msg=error_codes[e.code])
        else:
            app.logger.warning(f"error in app {e.code}")
    tb = format_exc()  # Capture traceback 
    app.logger.error(f"Exception in app {e}", extra={"error": str(e),"traceback":tb})
    raise e

if __name__ == '__main__':  
    app.run(host="0.0.0.0", debug=True)
