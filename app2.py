from flask import Flask, render_template, request, redirect, session, url_for
from tinydb import TinyDB, Query
import base64

app = Flask(__name__, template_folder="templates2")
app.secret_key = "vilisesmili"

db = TinyDB("db2.json")
users = db.table("users")

User = Query()

@app.route("/")
def home():
    if "user" in session:
        return redirect("/dashboard")
    return redirect("/login")

@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]

        if users.search(User.username == username):
            return "Uporabnik obstaja"

        users.insert({
            "username": username,
            "password": password,
            "posts": []
        })
        return redirect("/login")
    return render_template("register.html")

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]

        user = users.get(User.username == username)
        if user and user["password"] == password:
            session["user"] = username
            return redirect("/dashboard")
    return render_template("login.html")

@app.route("/dashboard")
def dashboard():
    if "user" not in session:
        return redirect("/login")

    all_users = users.all()
    all_posts = []

    for u in all_users:
        for p in u.get("posts", []):
            all_posts.append({
                "author": u["username"],
                "text": p["text"],
                "image": p["image"],
                "likes": p.get("likes", 0)
            })

    return render_template("dashboard.html", posts=all_posts, uporabnik=session["user"])

@app.route("/addPost", methods=["POST"])
def addPost():
    if "user" not in session:
        return redirect("/login")

    text = request.form["text"]
    image_file = request.files["image"]

    image_data = ""
    if image_file:
        image_data = base64.b64encode(image_file.read()).decode("utf-8")

    user = users.get(User.username == session["user"])
    posts = user.get("posts", [])

    posts.append({
        "text": text,
        "image": image_data,
        "likes": 0
    })

    users.update({"posts": posts}, User.username == session["user"])
    return redirect("/dashboard")


@app.route("/logout")
def logout():
    session.clear()
    return redirect("/login")

app.run(debug=True)
