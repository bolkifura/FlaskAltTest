from flask import Flask, render_template, request, redirect, session
from tinydb import TinyDB, Query

app = Flask(__name__)
app.secret_key = "cebronjonbombon"

db = TinyDB("db.json")
users = db.table("users")

User = Query()