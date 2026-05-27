from flask import Flask, render_template, request, redirect, session
from tinydb import TinyDB, Query
import base64

# Flask app
app = Flask(__name__, template_folder="templates2")

# Secret key za session
app.secret_key = "vilisesmili"

# TinyDB baza
db = TinyDB("db2.json")

# Tabela users
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

    # Ko uporabnik pošlje formo
    if request.method == "POST":

        username = request.form["username"]

        password = request.form["password"]

        # Preveri če uporabnik obstaja
        if users.search(User.username == username):

            return "Uporabnik že obstaja"

        # Dodaj novega uporabnika
        users.insert({

            "username": username,
            "password": password,
            "posts": []

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

    # Vsi uporabniki
    all_users = users.all()

    # Seznam vseh postov
    all_posts = []

    # Gre skozi vse uporabnike
    for u in all_users:

        # Gre skozi vse poste
        for i, p in enumerate(u.get("posts", [])):

            all_posts.append({

                "author": u["username"],

                "text": p["text"],

                "image": p["image"],

                "likes": p.get("likes", 0),

                "liked_by": p.get("liked_by", []),

                "index": i

            })

    return render_template(

        "dashboard.html",

        posts=all_posts,

        uporabnik=session["user"]

    )


# DODAJ POST
@app.route("/addPost", methods=["POST"])
def addPost():

    # Če ni prijavljen
    if "user" not in session:

        return redirect("/login")

    # Text posta
    text = request.form["text"]

    # Slika
    image_file = request.files["image"]

    image_data = ""

    # Če obstaja slika
    if image_file:

        image_data = base64.b64encode(

            image_file.read()

        ).decode("utf-8")

    # Trenutni uporabnik
    user = users.get(

        User.username == session["user"]

    )

    # Obstoječi posti
    posts = user.get("posts", [])

    # Dodaj nov post
    posts.append({

        "text": text,

        "image": image_data,

        "likes": 0,

        # Seznam uporabnikov ki so dali like
        "liked_by": []

    })

    # Shrani v bazo
    users.update(

        {"posts": posts},

        User.username == session["user"]

    )

    return redirect("/dashboard")


# LIKE / UNLIKE
@app.route("/likePost", methods=["POST"])
def likePost():

    # Če ni prijavljen
    if "user" not in session:

        return {"success": False}

    # Trenutni uporabnik
    current_user = session["user"]

    # Podatki posta
    index = int(request.form["index"])

    author = request.form["author"]

    # Najde avtorja
    user = users.get(

        User.username == author

    )

    # Vsi posti
    posts = user.get("posts", [])

    # Če liked_by ne obstaja
    if "liked_by" not in posts[index]:

        posts[index]["liked_by"] = []

    # Če je uporabnik že lajkal
    if current_user in posts[index]["liked_by"]:

        # Odstrani like
        posts[index]["liked_by"].remove(current_user)

        # Zmanjša število lajkov
        posts[index]["likes"] -= 1

        liked = False

    else:

        # Dodaj like
        posts[index]["liked_by"].append(current_user)

        # Povečaj število lajkov
        posts[index]["likes"] += 1

        liked = True

    # Shrani v bazo
    users.update(

        {"posts": posts},

        User.username == author

    )

    # Vrne odgovor
    return {

        "success": True,

        "likes": posts[index]["likes"],

        "liked": liked

    }


# DELETE POST
@app.route("/deletePost", methods=["POST"])
def deletePost():

    # Če ni prijavljen
    if "user" not in session:

        return {"success": False}

    # Index posta
    index = int(request.form["index"])

    # Trenutni uporabnik
    user = users.get(

        User.username == session["user"]

    )

    # Posti uporabnika
    posts = user.get("posts", [])

    # Če post obstaja
    if index < len(posts):

        # Izbriše post
        posts.pop(index)

    # Posodobi bazo
    users.update(

        {"posts": posts},

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