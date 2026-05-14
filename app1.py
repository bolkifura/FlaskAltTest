from flask import Flask, render_template, request, redirect, session, url_for # url_for omogoča ustvarjanje URL-jev za funkcije, kar je uporabno pri preusmerjanju in povezavah v HTML-ju
from tinydb import TinyDB, Query # Query omogoča iskanje po bazi podatkov

app = Flask(__name__, template_folder="templates1") # Ustvari flask app
app.secret_key = "cebronjonbombon" # Za sessione, cookies, varnost

db = TinyDB("db.json")
users = db.table("users") # V bazi ustvarimo tabelo "users"

User = Query() # Omogoča iskanje po tabeli "users" z Query

@app.route("/") 
def home():
    if "user" in session: # Preveri, če je uporabnik v sessionu
        return redirect ("/dashboard") # Preusmeri na dashboard, če je prijavljen
    return redirect("/login") # Preusmeri na login, če ni prijavljen

@app.route("/register", methods=["GET", "POST"]) # Get prikaže stran in zahteva podatke, Post pošlje podatke v bazo
def register():
    if request.method == "POST": # Če submitaš 
        username = request.form["username"] # Pridobi username iz html
        password = request.form["password"] # Pridobi password iz html

        if users.search(User.username == username): # Preveri, če uporabnik že obstaja v bazi
            return "Uporabnik obstaja"

        users.insert({"username": username, "password": password, "note": ""}) # Vstavi novega uporabnika v bazo
        return redirect("/login") # Preusmeri na login
    return render_template("register.html") # Prikaže register.html

@app.route("/login", methods=["GET", "POST"]) # Get prikaže stran in zahteva podatke, Post pošlje podatke v bazo
def login():
    if request.method == "POST": # Če submitaš 
        username = request.form["username"] # Pridobi username iz html
        password = request.form["password"] # Pridobi password iz html

        user = users.get(User.username == username) # Pooišče uporabnika v bazi po usernameu
        if user and user["password"] == password: # Preveri, če uporabnik obstaja in če je geslo pravilno
            session["user"] = username # Shrani username v session, da lahko preverjamo, če je uporabnik prijavljen
            return redirect("/dashboard") # Preusmeri na dashboard
    return render_template("login.html") # Prikaže login.html
    
@app.route("/dashboard")
def dashboard():
    if "user" not in session: # Preveri, če je uporabnik v sessionu
        return redirect("/login") # Preusmeri na login
    user = users.get(User.username == session["user"]) # Poišče uporabnika v bazi po usernameu
    notes = user.get("notes", []) # Pridobi note iz baze, če ni note, vrne prazen seznam
    return render_template("dashboard.html", notes=notes, uporabnik=session["user"]) # Prikaže dashboard.html in pošlje notes in username, da jih lahko uporabimo v html

@app.route("/saveNote", methods=["POST"]) # Post pošlje podatke v bazo
def saveNote():
    note_title = request.form["title"] # Pridobi title iz html
    note_content = request.form["note"] # Pridobi content iz html
    user = users.get(User.username == session["user"]) # Poišče uporabnika v bazi po usernameu
    notes = user.get("notes", [])  # Pridobi note iz baze, če ni note, vrne prazen seznam
    notes.append({"title": note_title, "content": note_content}) # Doda nov note v seznam notes
    users.update({"notes": notes}, User.username == session["user"]) # Posodobi notes v bazi za trenutnega uporabnika
    return redirect("/dashboard") # Preusmeri na dashboard

@app.route("/editNote/<int:note_index>", methods=["GET", "POST"]) # Get prikaže stran in zahteva podatke, Post pošlje podatke v bazo    #note_index je indeks nota, ki ga želimo urediti
def editNote(note_index):
    if "user" not in session: # Preveri, če je uporabnik v sessionu
        return redirect("/login") # Preusmeri na login
    
    user = users.get(User.username == session["user"]) # Poišče uporabnika v bazi po usernameu
    notes = user.get("notes", []) # Pridobi note iz baze, če ni note, vrne prazen seznam
    note = notes[note_index] # Pridobi note, ki ga želimo urediti iz seznama notes po indeksu

    if request.method == "POST": # Če shraniš
        note["title"] = request.form["title"] # Posodobi title nota z novim titleom iz html
        note["content"] = request.form["note"] # Posodobi content nota z novim contentom iz html
        users.update({"notes": notes}, User.username == session["user"]) # Shrani v bazo posodobljen seznam notes za trenutnega uporabnika
        return redirect("/dashboard") # Preusmeri na dashboard

    return render_template("edit_note.html", note=note, note_index=note_index) # Prikaže edit_note.html in pošlje note, da jih lahko uporabimo v html

@app.route("/clearNoteContent/<int:note_index>", methods=["POST"]) # Post pošlje podatke v bazo
def clearNoteContent(note_index):
    user = users.get(User.username == session["user"]) # Poišče uporabnika v bazi po usernameu
    notes = user.get("notes", []) # Pridobi note iz baze, če ni note, vrne prazen seznam
    notes[note_index]["content"] = "" # Počisti content nota, ki ga želimo urediti iz seznama notes po indeksu
    users.update({"notes": notes}, User.username == session["user"]) # Posodobi notes v bazi za trenutnega uporabnika
    return redirect(url_for('editNote', note_index=note_index)) # Preusmeri nazaj na editNote, da lahko uporabnik vidi, da je content počisten

@app.route("/deleteNote/<int:note_index>", methods=["POST"]) # Post pošlje podatke v bazo, note_index je indeks nota, ki ga želimo izbrisati
def deleteNote(note_index):
    if "user" not in session: # Preveri, če je uporabnik v sessionu
        return {"success": False} # Vrne JSON odgovor, da brisanje ni uspelo, lahko ga uporabimo v JavaScriptu, da prikažemo napako
    user = users.get(User.username == session["user"]) # Poišče uporabnika v bazi po usernameu
    notes = user.get("notes", []) # Pridobi note iz baze, če ni note, vrne prazen seznam
    if note_index < len(notes): # Preveri, če je indeks nota, ki ga želimo izbrisati, manjši od dolžine seznama notes, da preprečimo napake
        notes.pop(note_index) # Odstrani note, ki ga želimo izbrisati iz seznama notes po indeksu
        users.update({"notes": notes}, User.username == session["user"]) # Posodobi notes v bazi za trenutnega uporabnika
    return {"success": True} # Vrne JSON odgovor, da je brisanje uspelo, lahko ga uporabimo v JavaScriptu, da odstranimo note iz strani brez osveževanja
    
@app.route("/logout")
def logout():
    session.clear() # Počisti session, da se uporabnik odjavi
    return redirect("/login") # Preusmeri na login

app.run(debug=True) # Zaženi flask app, tako da lahko vidimo napake in avtomatsko osveževanje strani pri spremembah v kodi

