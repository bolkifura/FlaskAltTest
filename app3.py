from flask import Flask, render_template, request, redirect, session
from tinydb import TinyDB, Query

app = Flask(__name__, template_folder="templates3")
app.secret_key = "chatsecret"

DB = TinyDB("chatdb.json")
users = DB.table("users")
messages = DB.table("messages")
User = Query()

@app.route("/")
def home():
    if "user" in session:
        return redirect("/chat")
    return redirect("/login")

@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]
        if users.search(User.username == username):
            return "Uporabnik že obstaja"
        users.insert({
            "username": username,
            "password": password
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
            return redirect("/chat")
    return render_template("login.html")

@app.route("/chat")
def chat():
    if "user" not in session:
        return redirect("/login")
    all_messages = messages.all()
    return render_template(
        "chat.html",
        messages=all_messages,
        uporabnik=session["user"]
    )

@app.route("/sendMessage", methods=["POST"])
def sendMessage():
    if "user" not in session:
        return {"success": False}
    text = request.form["text"]
    messages.insert({
        "author": session["user"],
        "text": text
    })
    return {"success": True}

@app.route("/getMessages")
def getMessages():
    all_messages = messages.all()
    return {"messages": all_messages}

@app.route("/deleteMessage", methods=["POST"])
def deleteMessage():
    if "user" not in session:
        return {"success": False}
    index = int(request.form["index"])
    all_messages = messages.all()
    if index < len(all_messages):
        if all_messages[index]["author"] == session["user"]:
            messages.remove(doc_ids=[all_messages[index].doc_id])
            return {"success": True}
    return {"success": False}

@app.route("/logout")
def logout():
    session.clear()
    return redirect("/login")

app.run(debug=True)