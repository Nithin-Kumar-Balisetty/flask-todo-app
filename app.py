from flask import Flask, render_template, request, redirect, url_for, session, flash
from flask_bcrypt import Bcrypt
from pymongo import MongoClient
from bson.objectid import ObjectId
import os

from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)
app.secret_key = os.urandom(24)

bcrypt = Bcrypt(app)

# MongoDB Cluster URI

MONGO_URI = os.getenv("MONGO_URI")

client = MongoClient(MONGO_URI)
db = client["bhanudb"]
users_collection = db["users"]
todos_collection = db["todos"]

# Routes
@app.route("/")
def home():
    if "user_id" in session:
        return redirect(url_for("todo"))
    return redirect(url_for("login"))

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form["email"]
        password = request.form["password"]

        user = users_collection.find_one({"email": email})
        if user and bcrypt.check_password_hash(user["password"], password):
            session["user_id"] = str(user["_id"])
            session["email"] = user["email"]
            return redirect(url_for("todo"))
        else:
            flash("Invalid credentials, please try again.")
    return render_template("login.html")

@app.route("/register", methods=["POST"])
def register():
    email = request.form["email"]
    password = request.form["password"]

    if users_collection.find_one({"email": email}):
        flash("User already exists. Please login.")
        return redirect(url_for("login"))

    hashed_password = bcrypt.generate_password_hash(password).decode("utf-8")
    users_collection.insert_one({"email": email, "password": hashed_password})
    flash("Registration successful! Please login.")
    return redirect(url_for("login"))

@app.route("/todo", methods=["GET", "POST"])
def todo():
    if "user_id" not in session:
        return redirect(url_for("login"))

    user_id = session["user_id"]
    if request.method == "POST":
        task = request.form["task"]
        todos_collection.insert_one({
            "userId": ObjectId(user_id),
            "task": task,
            "completed": False,
        })
        flash("Task added successfully!")

    tasks = list(todos_collection.find({"userId": ObjectId(user_id)}))
    return render_template("todo.html", tasks=tasks)

@app.route("/complete/<task_id>")
def complete_task(task_id):
    todos_collection.update_one({"_id": ObjectId(task_id)}, {"$set": {"completed": True}})
    return redirect(url_for("todo"))

@app.route("/incomplete/<task_id>")
def incomplete_task(task_id):
    todos_collection.update_one({"_id": ObjectId(task_id)}, {"$set": {"completed": False}})
    return redirect(url_for("todo"))

@app.route("/delete/<task_id>")
def delete_task(task_id):
    todos_collection.delete_one({"_id": ObjectId(task_id)})
    return redirect(url_for("todo"))

@app.route("/logout")
def logout():
    session.clear()
    flash("Logged out successfully.")
    return redirect(url_for("login"))

if __name__ == "__main__":
    app.run()