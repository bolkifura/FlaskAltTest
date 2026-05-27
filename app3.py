from flask import Flask, render_template, request, redirect, session
from tinydb import TinyDB, Query

# Flask app
app = Flask(__name__, template_folder="templates3")

# Secret key
app.secret_key = "sigmabolka"

# Baza
db = TinyDB("chatdb.json")

# Tabele
users = db.table("users")

messages = db.table("messages")

# Query
User = Query()


# HOME
@app.route("/")
def home():

    # Če je prijavljen
    if "user" in session:

        return redirect("/chat")

    # Če ni prijavljen
    return redirect("/login")


# REGISTER
@app.route("/register", methods=["GET", "POST"])
def register():

    if request.method == "POST":

        username = request.form["username"]

        password = request.form["password"]

        # Preveri če obstaja
        if users.search(User.username == username):

            return "Uporabnik že obstaja"

        # Dodaj uporabnika
        users.insert({

            "username": username,

            "password": password

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
        user = users.get(

            User.username == username

        )

        # Preveri geslo
        if user and user["password"] == password:

            # Shrani v session
            session["user"] = username

            return redirect("/chat")

    return render_template("login.html")


# CHAT
@app.route("/chat")
def chat():

    # Če ni prijavljen
    if "user" not in session:

        return redirect("/login")

    # Vsa sporočila
    all_messages = messages.all()

    return render_template(

        "chat.html",

        messages=all_messages,

        uporabnik=session["user"]

    )


# SEND MESSAGE
@app.route("/sendMessage", methods=["POST"])
def sendMessage():

    # Če ni prijavljen
    if "user" not in session:

        return {"success": False}

    # Besedilo
    text = request.form["text"]

    # Dodaj message
    messages.insert({

        "author": session["user"],

        "text": text

    })

    return {"success": True}


# GET MESSAGES
@app.route("/getMessages")
def getMessages():

    # Vsa sporočila
    all_messages = messages.all()

    return {

        "messages": all_messages

    }


# DELETE MESSAGE
@app.route("/deleteMessage", methods=["POST"])
def deleteMessage():

    # Če ni prijavljen
    if "user" not in session:

        return {"success": False}

    # Index sporočila
    index = int(request.form["index"])

    # Vsa sporočila
    all_messages = messages.all()

    # Če obstaja
    if index < len(all_messages):

        # Če je avtor isti uporabnik
        if all_messages[index]["author"] == session["user"]:

            # Izbriši message
            messages.remove(

                doc_ids=[

                    all_messages[index].doc_id

                ]
            )

            return {"success": True}

    return {"success": False}


# LOGOUT
@app.route("/logout")
def logout():

    # Počisti session
    session.clear()

    return redirect("/login")


# Zagon aplikacije
app.run(debug=True)