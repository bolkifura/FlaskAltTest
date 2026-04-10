from flask import Flask, render_template, request, redirect, session
from tinydb import TinyDB, Query

app = Flask(__name__, template_folder="templates1")
app.secret_key = "cebronjonbombon"

db = TinyDB("db.json")
users = db.table("users")

User = Query()

@app.route("/")
def home():
    if "user" in session:
        return redirect ("/dashboard")
    return redirect("/login")

@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]

        if users.search(User.username == username):
            return "Uporabnik obstaja"

        users.insert({"username": username, "password": password, "note": ""})
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
    user = users.get(User.username == session["user"])
    notes = user.get("notes", [])
    return render_template("dashboard.html", notes=notes, uporabnik=session["user"])

@app.route("/saveNote", methods=["POST"])
def saveNote():
    note_title = request.form["title"]
    note_content = request.form["note"]
    user = users.get(User.username == session["user"])
    notes = user.get("notes", [])  
    notes.append({"title": note_title, "content": note_content})
    users.update({"notes": notes}, User.username == session["user"])
    return redirect("/dashboard")
    return "Saved"

@app.route("/editNote/<int:note_index>", methods=["GET", "POST"])
def editNote(note_index):
    if "user" not in session:
        return redirect("/login")
    
    user = users.get(User.username == session["user"])
    notes = user.get("notes", [])
    note = notes[note_index]

    if request.method == "POST":
        note["title"] = request.form["title"]
        note["content"] = request.form["note"]
        users.update({"notes": notes}, User.username == session["user"])
        return redirect("/dashboard")

    return render_template("edit_note.html", note=note, note_index=note_index)

@app.route("/logout")
def logout():
    session.clear()
    return redirect("/login")

app.run(debug=True)

