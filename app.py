from flask import Flask, render_template, request, jsonify
from pymongo import MongoClient
from dotenv import load_dotenv
import certifi
import os
import json

app = Flask(__name__)

load_dotenv()

MONGO_URI = os.getenv("MONGO_URI")

client = None
todos = None

if not MONGO_URI:
    print("WARNING: MONGO_URI is not set.")
else:
    try:
        client = MongoClient(
            MONGO_URI,
            tls=True,
            tlsCAFile=certifi.where(),
            serverSelectionTimeoutMS=30000
        )

        client.admin.command("ping")

        print("MongoDB connected successfully!")

        db = client["todo_database"]
        todos = db["todo_items"]

    except Exception as e:
        print("MongoDB connection failed:")
        print(e)


@app.route("/")
def home():
    return render_template("todo.html")


@app.route("/todo")
def todo():
    return render_template("todo.html")


@app.route("/api", methods=["GET"])
def api():
    try:
        with open("apps.json", "r") as file:
            data = json.load(file)

        return jsonify(data)

    except FileNotFoundError:
        return jsonify({
            "error": "apps.json file not found"
        }), 404

    except json.JSONDecodeError:
        return jsonify({
            "error": "Invalid JSON format"
        }), 500


@app.route("/submittodoitem", methods=["POST"])
def submit_todo_item():
    try:
        if not request.is_json:
            return jsonify({
                "error": "Request must contain JSON data"
            }), 400

        data = request.get_json()

        if not data:
            return jsonify({
                "error": "No data received"
            }), 400

        item_name = data.get("itemName")
        item_id = data.get("itemId")
        item_uuid = data.get("itemUuid")
        item_hash = data.get("itemHash")
        item_description = data.get("itemDescription")

        if item_name:
            item_name = item_name.strip()

        if item_id:
            item_id = item_id.strip()

        if item_uuid:
            item_uuid = item_uuid.strip()

        if item_hash:
            item_hash = item_hash.strip()

        if item_description:
            item_description = item_description.strip()

        if not item_name:
            return jsonify({
                "error": "Item Name is required"
            }), 400

        if not item_id:
            return jsonify({
                "error": "Item ID is required"
            }), 400

        if not item_uuid:
            return jsonify({
                "error": "Item UUID is required"
            }), 400

        if not item_hash:
            return jsonify({
                "error": "Item Hash is required"
            }), 400

        if not item_description:
            return jsonify({
                "error": "Item Description is required"
            }), 400

        if todos is None:
            return jsonify({
                "error": "MongoDB is not connected. Check MONGO_URI in .env"
            }), 500

        todo_item = {
            "itemName": item_name,
            "itemId": item_id,
            "itemUuid": item_uuid,
            "itemHash": item_hash,
            "itemDescription": item_description
        }

        result = todos.insert_one(todo_item)

        print("Todo inserted successfully:", result.inserted_id)

        # Build a fresh dict for the response instead of reusing
        # todo_item — insert_one() mutates todo_item in place by
        # adding an ObjectId "_id" key, which jsonify() cannot
        # serialize. Using a separate dict avoids that entirely.
        response_item = {
            "itemName": item_name,
            "itemId": item_id,
            "itemUuid": item_uuid,
            "itemHash": item_hash,
            "itemDescription": item_description
        }

        return jsonify({
            "message": "To-Do item stored successfully!",
            "id": str(result.inserted_id),
            "item": response_item
        }), 201

    except Exception as e:
        print("Error while submitting TODO:")
        print(e)

        return jsonify({
            "error": str(e)
        }), 500


if __name__ == "__main__":
    app.run(
        debug=True,
        host="127.0.0.1",
        port=5000
    )