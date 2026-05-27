from flask import Flask, render_template, request, redirect, session, url_for
from tinydb import TinyDB, Query

# Flask app
app = Flask(__name__, template_folder="templates1")

# Secret key
app.secret_key = "cebronjonbombon"

# Baza
db = TinyDB("db.json")

# Tabela uporabnikov
users = db.table("users")

# Query objekt
User = Query()


# HOME
@app.route("/")
def home():

    # Če je uporabnik prijavljen
    if "user" in session:

        return redirect("/dashboard")

    # Če ni prijavljen
    return redirect("/login")


# REGISTER
@app.route("/register", methods=["GET", "POST"])
def register():

    if request.method == "POST":

        username = request.form["username"]

        password = request.form["password"]

        # Preveri če uporabnik obstaja
        if users.search(User.username == username):

            return "Uporabnik obstaja"

        # Dodaj uporabnika
        users.insert({

            "username": username,

            "password": password,

            "notes": []

        })

        return redirect("/login")

    return render_template("register.html")


# LOGIN
@app.route("/login", methods=["GET", "POST"])
def login():

    if request.method == "POST":

        username = request.form["username"]

        password = request.form["password"]

        # Poišče uporabnika
        user = users.get(User.username == username)

        # Preveri geslo
        if user and user["password"] == password:

            # Shrani v session
            session["user"] = username

            return redirect("/dashboard")

    return render_template("login.html")


# DASHBOARD
@app.route("/dashboard")
def dashboard():

    # Če ni prijavljen
    if "user" not in session:

        return redirect("/login")

    # Najde uporabnika
    user = users.get(

        User.username == session["user"]

    )

    # Pridobi zapiske
    notes = user.get("notes", [])

    return render_template(

        "dashboard.html",

        notes=notes,

        uporabnik=session["user"]

    )


# SHRANI NOTE
@app.route("/saveNote", methods=["POST"])
def saveNote():

    # Naslov
    note_title = request.form["title"]

    # Vsebina
    note_content = request.form["note"]

    # Najde uporabnika
    user = users.get(

        User.username == session["user"]

    )

    # Obstoječi notes
    notes = user.get("notes", [])

    # Dodaj nov note
    notes.append({

        "title": note_title,

        "content": note_content

    })

    # Posodobi bazo
    users.update(

        {"notes": notes},

        User.username == session["user"]

    )

    return redirect("/dashboard")


# EDIT NOTE
@app.route("/editNote/<int:note_index>", methods=["GET", "POST"])
def editNote(note_index):

    # Če ni prijavljen
    if "user" not in session:

        return redirect("/login")

    # Najde uporabnika
    user = users.get(

        User.username == session["user"]

    )

    # Vsi notes
    notes = user.get("notes", [])

    # Izbran note
    note = notes[note_index]

    # Če shrani spremembe
    if request.method == "POST":

        note["title"] = request.form["title"]

        note["content"] = request.form["note"]

        # Posodobi bazo
        users.update(

            {"notes": notes},

            User.username == session["user"]

        )

        return redirect("/dashboard")

    return render_template(

        "edit_note.html",

        note=note,

        note_index=note_index

    )


# CLEAR NOTE
@app.route("/clearNoteContent/<int:note_index>", methods=["POST"])
def clearNoteContent(note_index):

    # Najde uporabnika
    user = users.get(

        User.username == session["user"]

    )

    # Vsi notes
    notes = user.get("notes", [])

    # Počisti content
    notes[note_index]["content"] = ""

    # Posodobi bazo
    users.update(

        {"notes": notes},

        User.username == session["user"]

    )

    return redirect(

        url_for(

            "editNote",

            note_index=note_index

        )
    )


# DELETE NOTE
@app.route("/deleteNote/<int:note_index>", methods=["POST"])
def deleteNote(note_index):

    # Če ni prijavljen
    if "user" not in session:

        return {"success": False}

    # Najde uporabnika
    user = users.get(

        User.username == session["user"]

    )

    # Vsi notes
    notes = user.get("notes", [])

    # Če note obstaja
    if note_index < len(notes):

        # Izbriši note
        notes.pop(note_index)

        # Posodobi bazo
        users.update(

            {"notes": notes},

            User.username == session["user"]

        )

    return {"success": True}


# LOGOUT
@app.route("/logout")
def logout():

    # Počisti session
    session.clear()

    return redirect("/login")


# Zagon aplikacije
app.run(debug=True)