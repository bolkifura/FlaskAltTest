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
        return redirect ("/dashboard")
    return redirect("/login")

@app.route("/register", methods =["GET", "POST"])
def register():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]

        if users.search(User.username == username):
            return "Uporabnik obstaja"

        users.insert({"username": username, "password": password, "note": ""})
        return redirect("/login")
    return render_template("register.html")

@app.route("/login.html")
def login():


app.run(debug=True)

