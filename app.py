from flask import Flask, render_template, request, abort, Response
from flask_bootstrap import Bootstrap5
from flask_wtf import FlaskForm
from wtforms import StringField, DateField, SubmitField, HiddenField
from wtforms.validators import InputRequired
from fortifysql import Database, Table
from random import randint
from cryptography.hazmat.primitives.asymmetric import padding
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.serialization import load_pem_private_key
import base64

# Hardcoded RSA private key
public_key_str = b'-----BEGIN PUBLIC KEY-----\nMIIBIjANBgkqhkiG9w0BAQEFAAOCAQ8AMIIBCgKCAQEAx+FOnwiQWcF775osIvIW\nscOhUKfyGLi/X7VDVIVv/vqweeiiHRayz+PXoBTlhxnTbkVulKDpX07kZqJJH12g\nGMEdJnRTCFS/X9IXKaMVf1zeTtRvJfc6xskTaVb5PNT/FLiZWp4YSP8XtPhNT/ec\nxso8WqBFH9mOBaFEJwZvbGuf/yhMlpovGlPFl4a61gttMpFHGTalZNgjvC6wAUB4\n/lK4jG2UQbEqFq1vH5PVmBLYeeHIVuWj8UY2wFIRWPGu3QBK90e9AC1cQQj3JB1i\nSkbF1NKlsrpAWOhyrNRG4Ge4wSzmxSg5whB+JYop0knQQUYSbX7sadOxq/kgQ2Yb\n7QIDAQAB\n-----END PUBLIC KEY-----\n'

# Hardcoded RSA public key
private_key_str = b'-----BEGIN RSA PRIVATE KEY-----\nMIIEpAIBAAKCAQEAx+FOnwiQWcF775osIvIWscOhUKfyGLi/X7VDVIVv/vqweeii\nHRayz+PXoBTlhxnTbkVulKDpX07kZqJJH12gGMEdJnRTCFS/X9IXKaMVf1zeTtRv\nJfc6xskTaVb5PNT/FLiZWp4YSP8XtPhNT/ecxso8WqBFH9mOBaFEJwZvbGuf/yhM\nlpovGlPFl4a61gttMpFHGTalZNgjvC6wAUB4/lK4jG2UQbEqFq1vH5PVmBLYeeHI\nVuWj8UY2wFIRWPGu3QBK90e9AC1cQQj3JB1iSkbF1NKlsrpAWOhyrNRG4Ge4wSzm\nxSg5whB+JYop0knQQUYSbX7sadOxq/kgQ2Yb7QIDAQABAoIBAAiI+/D5jiRvCSpJ\nlJHncYWku2o0ybc5iF5/YIEm84nZTZjfELEaS4dqDMaWrdhvh2JBj7/EAUMjHMiv\nLF0tA82azXJbbEJCUCu4zmlmP+BA6HNISfi+jmF3q58HajwpQj0xxsaiUponXm1J\nXw/HnIe2kg4yotEB2rkt0jmyYiaofGrrUWSUuk8uqRSVAzH0Hz1Znd0rtNIocJkF\ngYNSCW9yfb/K8tBIBHHNLaVWm412RCWm8i61cSSfRg5iTeB74XRUQKvBrsjL2vJF\nK8JOrBKIpGDzUyaboI3W27WIjXABxfFcKiHT+serc6KUi+uMfmbAOG0NqcLR3r8k\nnsWb4JcCgYEA/Tjw2LCMYAOsToqUAdBHLm9vwQrccYbcw+hdHKUKDjr7SY3a4pi6\ndNAKUIUwqKt/HB+x1WS6wfJvI3DlwESY0MAk6kEuKQILsqQEx2XXDfgPQIF3rBWm\nc4BJl07OxRMKea6GMBeqNofiQjmEKX/HuxsS5/NFSGrZ+uV+jQzvRi8CgYEAyhKU\nLrSB/tkXrxqpSWCTJlcb7IfIS/ApgFnqUTEq9X2BT/Uh+99/8xXqBPzitIiEZz1o\nudmMdQow491dBB7X74UfWHo9wPSyT+h5gPoy5sIHUfPVi7WdF9xhDzMAzHFF1Szl\nPT3s0+txZX7fw3shzpj+Ot9kJh/Zgf3VvYALVKMCgYAFmj7p7G4OqcYkLri7mYoZ\noumMEdtyv5Me2oNE4Pnp+rAYnoTbQpnNf9TalzfOY4z6aFEc8Y+YPu7qj9LlgB8J\nb1bhv/NvgNYVa7+XUc+CRZzAxpyJOClooMwABwRYI+W1b4EUi1F+x17gLDmaWXNn\n1l+CtkUwJv0Pqgg0wraAjQKBgQCz1rEWmAORoffYGSxMZ6zOVHw/l+CE5OqqlltZ\ngx6ueNIbLRjfptuipgAuDDpfXZgooZiQvrKofzdftGTSA/k97AYnojNPhPck8ssg\nJIwkns4Q+6czvaBf2fxvoH63dKAnxtsGFBSvzjyPjcjrmqxNyA+KqcHhxDq53ATb\nsBdlbQKBgQDMkAk2GLOG2UGlh7fHa4tIcrtSUNgnu46mZ+zcPowDRrMw7dc5WoLI\nPlT7b8ToylrXHKK30lYTd20sgLIxufDlVpcPln8WAqiHuLctuoEI2JNwhIEEF/3D\n56HIRFap7aqFZlG3VVSVm+JwXYeAPlsWXhNCfu7VPBKGcOjPUQFJCA==\n-----END RSA PRIVATE KEY-----\n'

private_key = load_pem_private_key(private_key_str, password=None)

app = Flask(__name__)
bootstrap = Bootstrap5(app)
app.config["SECRET_KEY"] = "attendance is the biggest indicator for success"
db = Database("quote.db")
def log(request):
    app.logger.info(f"[Database] {request}")
db.query_logging(True, log)
db.backup("C:/Users/25hickmar/OneDrive - St Patricks College/Digital Solutions/small projects/quotebook")
        
class QuoteForm(FlaskForm):
    name = StringField("Name", [InputRequired()])
    date = StringField("Date")
    quote = StringField("Quote")
    submit = SubmitField("submit quote", render_kw={"class": "button button-dark"})

@app.route('/submit', methods=["GET", "POST"])
def submit():
    form: QuoteForm = QuoteForm()
    quotes: Table = db.quotes
    if form.validate_on_submit():
        name = form.name.data
        date = form.date.data
        if not date:
            date = "2024"
        quote = form.quote.data
        if len(quote) > 300 or len(name) > 300 or len(date) > 300:
            form.quote.errors.append(ValueError("too long"))
        else:
            quotes.append(name=name, year=date, quote=quote)
    quotes = quotes()
    return render_template("submit.html", form=form, quotes=quotes)

@app.route("/")
def home():
    num = db.query("SELECT max(rowid) FROM quotes")[0][0]
    while True:
        id = randint(1, num)
        try:
            quote = db.query(f"SELECT * FROM quotes WHERE rowid = {id}")[0]
        except IndexError:
            pass
        else:
            break
    return render_template("quote.html", quote=quote)

@app.route("/quotes")
def quotes():
    quotes: Table = db.quotes
    quotes = quotes()
    return render_template("home.html", quotes=quotes)

if __name__ == '__main__':
    app.run(host="0.0.0.0", debug=True)