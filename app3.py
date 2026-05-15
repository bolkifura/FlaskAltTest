from flask import Flask, render_template, request, redirect, session
from tinydb import TinyDB, Query

app = Flask(__name__, template_folder="templates3")  # Ustvari flask app
app.secret_key = "sigmabolka" # Za sessione, cookies, varnost

DB = TinyDB("chatdb.json") 
users = DB.table("users") # V bazi ustvarimo tabelo "users"

messages = DB.table("messages") # V bazi ustvarimo tabelo "messages", kamor bomo shranjevali vsa sporočila
User = Query() # Omogoča iskanje po tabeli "users" z Query

@app.route("/")
def home():
    if "user" in session: # Preveri, če je uporabnik v sessionu
        return redirect("/chat") # Preusmeri na chat, če je prijavljen
    return redirect("/login") # Preusmeri na login, če ni prijavljen

@app.route("/register", methods=["GET", "POST"]) # Get prikaže stran in zahteva podatke, Post pošlje podatke v bazo
def register():
    if request.method == "POST": # Če submitaš
        username = request.form["username"] # Pridobi username z html
        password = request.form["password"] # Pridobi password z html
        if users.search(User.username == username): # Preveri, če uporabnik že obstaja v bazi
            return "Uporabnik že obstaja" 
        
        users.insert({"username": username,"password": password}) # Vstavi novega uporabnika v bazo
        return redirect("/login") # Preusmeri na login
    return render_template("register.html") # Prikaže register.html

@app.route("/login", methods=["GET", "POST"]) # Get prikaže stran in zahteva podatke, Post pošlje podatke v bazo
def login():
    if request.method == "POST": # Če submitaš
        username = request.form["username"] # Pridobi username z html
        password = request.form["password"] # Pridobi password z html

        user = users.get(User.username == username) # Poišče uporabnika v bazi po usernameu
        if user and user["password"] == password: # Preveri, če uporabnik obstaja in če je geslo pravilno
            session["user"] = username # Shrani username v session, da lahko preverjamo, če je uporabnik prijavljen
            return redirect("/chat") # Preusmeri na chat
    return render_template("login.html") # Prikaže login.html

@app.route("/chat")
def chat():
    if "user" not in session: # Preveri, če je uporabnik v sessionu
        return redirect("/login") # Preusmeri na login
    all_messages = messages.all() # Pridobi vsa sporočila iz baze, da jih lahko prikažemo na chat strani
    return render_template("chat.html", messages=all_messages, uporabnik=session["user"]) # Prikaže chat.html in pošlje vsa sporočila in username, da jih lahko uporabimo v html

@app.route("/sendMessage", methods=["POST"]) # Post pošlje podatke v bazo
def sendMessage():
    if "user" not in session: # Preveri, če je uporabnik v sessionu
        return {"success": False} # Vrne JSON odgovor z neuspehom, če ni prijavljen
    text = request.form["text"] # Pridobi text sporočila z html
    messages.insert({ "author": session["user"], "text": text }) # Vstavi novo sporočilo v bazo, skupaj z avtorjem in tekstom sporočila
    return {"success": True} # Vrne JSON odgovor z uspehom, da lahko uporabnik vidi, da je sporočilo poslano na chat strani brez osveževanja strani

@app.route("/getMessages")
def getMessages():
    all_messages = messages.all() # Pridobi vsa sporočila iz baze, da jih lahko prikažemo na chat strani, to funkcijo bomo klicali z JavaScriptom vsake 3 sekundi, da dobimo nova sporočila brez osveževanja strani
    return {"messages": all_messages} # Vrne JSON odgovor z vsemi sporočili, da dobimo nova sporočila brez osveževanja strani

@app.route("/deleteMessage", methods=["POST"]) # Post pošlje podatke v bazo
def deleteMessage():
    if "user" not in session: # Preveri, če je uporabnik v sessionu
        return {"success": False} # Vrne JSON odgovor z neuspehom, če ni prijavljen
    index = int(request.form["index"]) # Pridobi indeks sporočila z html, da lahko izbrišemo pravilen post, ki ga dobimo z getMessages funkcijo
    all_messages = messages.all() # Pridobi vsa sporočila z baze, da lahko najdemo pravilen post na podlagi indeksa, ki ga dobimo z getMessages funkcijo
    if index < len(all_messages): # Preveri, če je indeks sporočila manjši od dolžine seznama sporočil, da preprečimo napake pri brisanju neobstoječega sporočila
        if all_messages[index]["author"] == session["user"]: # Preveri, če je avtor sporočila enak trenutnemu uporabniku, da lahko izbrišemo samo svoja sporočila
            messages.remove(doc_ids=[all_messages[index].doc_id]) # Odstrani sporočilo z baze na podlagi doc_ids, ki ga dobimo z getMessages funkcijo
            return {"success": True} # Vrne JSON odgovor z uspehom, da lahko uporabnik vidi, da je sporočilo izbrisan na chat strani brez osveževanja strani
    return {"success": False} # Vrne JSON odgovor z neuspehom, če indeks sporočila je večji od dolžine seznama sporočil ali če avtor sporočila ni enak trenutnemu uporabniku, da preprečimo brisanje neobstoječega sporočila nebo tujih sporočil

@app.route("/logout")
def logout():
    session.clear() # Počisti session, da odjavimo uporabnika
    return redirect("/login") # Preusmeri na login

app.run(debug=True) # Zažene flask app v debug načinu, da lahko vidimo napake in avtomatsko osvežuje stran ob spremembah v kodi