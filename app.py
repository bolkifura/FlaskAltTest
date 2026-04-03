from flask import Flask, render_template, request, redirect, session
from tinydb import TinyDB, Query

app = Flask(__name__)
app.secret_key = "cebronjonbombon"

db = TinyDB("db.json")
users = db.table("users")

User = Query()

@app.route("/")
def home():
    if "user" in session:
        return redirect ("/login")
    return redirect("/register")

@app.route("")

app.run(debug=True)