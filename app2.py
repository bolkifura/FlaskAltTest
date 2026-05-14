from flask import Flask, render_template, request, redirect, session, url_for # url_for omogoča ustvarjanje URL-jev za funkcije, kar je uporabno pri preusmerjanju in povezavah v HTML-ju
from tinydb import TinyDB, Query
import base64

app = Flask(__name__, template_folder="templates2") # Ustvari flask app
app.secret_key = "vilisesmili" # Za sessione, cookies, varnost

db = TinyDB("db2.json")
users = db.table("users") # V bazi ustvarimo tabelo "users"

User = Query() # Omogoča iskanje po tabeli "users" z Query

@app.route("/")
def home():
    if "user" in session: # Preveri, če je uporabnik v sessionu
        return redirect("/dashboard") # Preusmeri na dashboard, če je prijavljen
    return redirect("/login") # Preusmeri na login, če ni prijavljen

@app.route("/register", methods=["GET", "POST"]) # Get prikaže stran in zahteva podatke, Post pošlje podatke v bazo
def register():
    if request.method == "POST": # Če submitaš
        username = request.form["username"] # Pridobi username iz html
        password = request.form["password"] # Pridobi password iz html

        if users.search(User.username == username): # Preveri, če uporabnik že obstaja v bazi
            return "Uporabnik obstaja"

        users.insert({ "username": username, "password": password, "posts": [] }) # Vstavi novega uporabnika v bazo, s praznim seznamom posts
        return redirect("/login") # Preusmeri na login
    return render_template("register.html") # Prikaže register.html

@app.route("/login", methods=["GET", "POST"]) # Get prikaže stran in zahteva podatke, Post pošlje podatke v bazo
def login():
    if request.method == "POST": # Če submitaš
        username = request.form["username"] # Pridobi username iz html
        password = request.form["password"] # Pridobi password iz html

        user = users.get(User.username == username) # Poišče uporabnika v bazi po usernameu
        if user and user["password"] == password: # Preveri, če uporabnik obstaja in če je geslo pravilno
            session["user"] = username # Shrani username v session, da lahko preverjamo, če je uporabnik prijavljen
            return redirect("/dashboard") # Preusmeri na dashboard
    return render_template("login.html") # Prikaže login.html

@app.route("/dashboard")
def dashboard():
    if "user" not in session: # Preveri, če je uporabnik v sessionu
        return redirect("/login") # Preusmeri na login
    all_users = users.all() # Pridobi vse uporabnike iz baze, da lahko prikažemo njihove poste na dashboardu
    all_posts = [] # Ustvari prazen seznam, kamor bomo shranili vse poste vseh uporabnikov, da jih lahko prikažemo na dashboardu
    for u in all_users: # Za vsakega uporabnika v seznamu vseh uporabnikov
        for i, p in enumerate(u.get("posts", [])): # Za vsak post trenutnega uporabnika, pridobi indeks posta in post, da lahko prikažemo post na dashboardu in omogočimo like in delete funkcionalnost
            all_posts.append({ "author": u["username"], "text": p["text"], "image": p["image"], "likes": p.get("likes", 0), "index": i}) # Doda post v seznam vseh postov, skupaj z avtorjem, tekstom, sliko, 
                                                                                                                                         #številom lajkov in indeksom posta, da lahko prikažemo post na dashboardu
                                                                                                                                         # in omogočimo like in delete funkcionalnost
    return render_template("dashboard.html", posts=all_posts, uporabnik=session["user"]) # Prikaže dashboard.html in pošlje seznam vseh postov in username, da jih lahko uporabimo v html

@app.route("/addPost", methods=["POST"]) # Post pošlje podatke v bazo
def addPost():
    if "user" not in session: # Preveri, če je uporabnik v sessionu
        return redirect("/login") # Preusmeri na login
    text = request.form["text"] # Pridobi text posta iz html
    image_file = request.files["image"] # Pridobi sliko posta iz html, request.files se uporablja za pridobivanje datotek, ki jih uporabnik naloži preko form, v tem primeru slika posta, ki jo bomo shranili v bazo
                                        # kot base64 string, da jo lahko prikažemo na dashboardu brez potrebe po shranjevanju datoteke na strežnik
    image_data = "" # Ustvari prazen string, kamor bomo shranili base64 kodirano sliko, če uporabnik naloži sliko, sicer ostane prazen string
    if image_file: # Preveri, če je uporabnik naložil sliko, da preprečimo napake pri kodiranju prazne datoteke
        image_data = base64.b64encode(image_file.read()).decode("utf-8") # Prebere naloženo datoteko, kodira jo v base64 in dekodira v utf-8 string, da jo lahko shranimo v bazo in prikažemo na dashboardu
    user = users.get(User.username == session["user"]) # Poišče uporabnika v bazi po usernameu, da lahko dodamo post v njegov seznam postov
    posts = user.get("posts", []) # Pridobi seznam postov iz baze za trenutnega uporabnika, če nima postov, vrne prazen seznam, da lahko dodamo prvi post
    posts.append({"text": text,"image": image_data,"likes": 0}) # V seznam doda lajke postov, z začetno vrednostjo 0
    users.update({"posts": posts}, User.username == session["user"]) # Posodobi seznam postov v bazi za trenutnega uporabnika, da shranimo novi post v bazo
    return redirect("/dashboard") # Preusmeri na dashboard, da lahko uporabnik vidi svoj novi post na dashboardu

@app.route("/likePost", methods=["POST"]) # Post pošlje podatke v bazo
def likePost():
    index = int(request.form["index"]) # Pridobi indeks posta iz html, da lahko povečamo število lajkov za pravilen post
    author = request.form["author"] # Pridobi avtorja posta iz html, da lahko najdemo pravilen post v bazi, author je username avtorja posta, ki ga lajkaš, da lahko najdemo pravilen post v bazi
    user = users.get(User.username == author) # Poišče avtorja posta v bazi po usernameu, da lahko najdemo pravilen post v bazi
    posts = user.get("posts", []) # Pridobi seznam postov iz baze za avtorja posta, če nima postov, vrne prazen seznam
    posts[index]["likes"] += 1 # Poveča število lajkov za post
    users.update({"posts": posts}, User.username == author) # Posodobi seznam postov v bazi za avtorja posta, da shranimo novo število lajkov v bazo
    return {"success": True, "likes": posts[index]["likes"]} # Vrne JSON odgovor z uspehom in novim številom lajkov, da lahko uporabnik vidi novo število lajkov na dashboardu brez osveževanja strani 
@app.route("/deletePost", methods=["POST"]) # Post pošlje podatke v bazo
def deletePost():
    if "user" not in session: # Preveri, če je uporabnik v sessionu
        return {"success": False} # Vrne JSON odgovor z neuspehom
    index = int(request.form["index"]) # Pridobi indeks posta z html, da lahko izbrišemo pravilen post
    user = users.get(User.username == session["user"]) # Poišče trenutnega uporabnika v bazi po usernameu, da lahko najdemo pravilen post v bazi
    if index < len(posts): # Preveri, če je indeks posta manjši od dolžine seznama postov, da preprečimo napake pri brisanju neobstoječega posta
        posts.pop(index) # Odstrani post iz seznama postov na podlagi indeksa, da izbrišemo post iz seznama postov
    users.update({"posts": posts}, User.username == session["user"]) # Posodobi seznam postov v bazi za trenutnega uporabnika
    return {"success": True} # Vrne JSON odgovor z uspehom, da lahko uporabnik vidi, da je post izbrisan na dashboardu brez osveževanja strani

@app.route("/logout")
def logout():
    session.clear() # Počisti session, da odjavimo uporabnika
    return redirect("/login") # Preusmeri na login

app.run(debug=True) # Zažene flask app v debug načinu, da lahko vidimo napake in avtomatsko osvežuje stran ob spremembah v kodi
