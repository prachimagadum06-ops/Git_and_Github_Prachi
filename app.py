from flask import Flask, render_template, request, jsonify
from pymongo import MongoClient
import os
import json

app = Flask(__name__)

# -----------------------------
# MongoDB Connection
# -----------------------------
MONGO_URI = os.getenv("MONGO_URI")

if not MONGO_URI:
    print("WARNING: MONGO_URI is not set.")

client = MongoClient(MONGO_URI) if MONGO_URI else None

if client:
    db = client["todo_database"]
    todos = db["todos"]
else:
    todos = None


# -----------------------------
# Home / To-Do Page
# -----------------------------
@app.route("/")
def home():
    return render_template("todo.html")


# -----------------------------
# To-Do Page
# -----------------------------
@app.route("/todo")
def todo():
    return render_template("todo.html")


# -----------------------------
# API Route
# -----------------------------
@app.route("/api", methods=["GET"])
def api():
    try:
        with open("data.json", "r") as file:
            data = json.load(file)

        return jsonify(data)

    except FileNotFoundError:
        return jsonify({
            "error": "data.json file not found"
        }), 404

    except json.JSONDecodeError:
        return jsonify({
            "error": "Invalid JSON format"
        }), 500


# -----------------------------
# Submit To-Do Item
# -----------------------------
@app.route("/submittodoitem", methods=["POST"])
def submit_todo_item():

    # Accept form data
    item_name = request.form.get("itemName")
    item_description = request.form.get("itemDescription")

    # Also accept JSON data
    if not item_name and request.is_json:
        data = request.get_json()
        item_name = data.get("itemName")
        item_description = data.get("itemDescription")

    # Validate data
    if not item_name or not item_description:
        return jsonify({
            "error": "itemName and itemDescription are required"
        }), 400

    # MongoDB
    if todos is None:
        return jsonify({
            "error": "MongoDB is not connected. Set MONGO_URI."
        }), 500

    todo_item = {
        "itemName": item_name,
        "itemDescription": item_description
    }

    todos.insert_one(todo_item)

    # If request came as JSON, return JSON
    if request.is_json:
        return jsonify({
            "message": "To-Do item stored successfully",
            "item": todo_item
        }), 201

    # If submitted from HTML form
    return """
    <h2>To-Do item submitted successfully!</h2>
    <p>Item Name: {}</p>
    <p>Item Description: {}</p>
    <a href="/todo">Back to To-Do</a>
    """.format(item_name, item_description)


# -----------------------------
# Run Application
# -----------------------------
if __name__ == "__main__":
    app.run(debug=True)