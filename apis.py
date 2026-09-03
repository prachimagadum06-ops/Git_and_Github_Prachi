from flask import Flask, jsonify
import json

app = Flask(__name__)


@app.route("/api")
def api():

    # Read data from backend JSON file
    with open("app.json", "r") as file:
        data = json.load(file)

    # Return data as JSON
    return jsonify(data)


if __name__ == "__main__":
    app.run(debug=True)


















