from flask import Flask, render_template, request
from pymongo import MongoClient

app = Flask(__name__)



# @app.route("/")
# def home():
#     return "Flask is connected successfully!"

# if __name__ == "__main__":
#     app.run(debug=True)





# Connect to MongoDB
client = MongoClient("mongodb+srv://mtanvi528_db_user:BPIh4Up4UTyh6vXq@cluster0.ye0o5h5.mongodb.net/?appName=Cluster0")

# Select database
db = client["student_database"]

# Select collection
collection = db["students"]


@app.route("/")
def home():
    return render_template("index.html")


@app.route("/submit", methods=["POST"])
def submit():

    # Receive form data
    name = request.form.get("name")
    email = request.form.get("email")
    message = request.form.get("message")

    # Validate input
    if not name or not email or not message:
        return "Please fill all fields!"

    # Store data in MongoDB
    student_data = {
        "name": name,
        "email": email,
        "message": message
    }

    collection.insert_one(student_data)

    # Show success page
    return render_template(
        "success.html",
        name=name
    )


if __name__ == "__main__":
    app.run(debug=True)