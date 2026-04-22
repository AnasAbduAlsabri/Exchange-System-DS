# app/run.py
from flask import Flask, jsonify, request
import uuid

app = Flask(__name__)
Banks = [
    "Alkuraimi Bank",
    "Al Tadhamon Bank",
    "Al Qutub Bank",
    "National Bank of Kuwait",
    "Gulf Bank",
    "Commercial Bank of Kuwait",
    "Burgan Bank",
    "Kuwait Finance House",
    "Ahli United Bank",
    "Boubyan Bank",
    "Warba Bank",
    "Kuwait International Bank",
    "Industrial Bank of Kuwait",
    "Boubyan Capital",
    "Kuwait Clearing Company",
    "Kuwait Credit Bank",
    "Al-Mawarid Bank",
    "ABK (Arab Bank for Investment and Foreign Trade)",
    "KIB (Kuwait International Bank)",
    "Kuwait Turkish Participation Bank",
]
tasks = [
    {
        "id": uuid.uuid4().hex,
        "title": "Get Banks Names",
        "BanksNo": 0,
    }
]


@app.route("/", methods=["GET"])
def index():
    return "Web Service"


@app.route("/tasks", methods=["GET"])
def getTasks():
    return jsonify({"tasks": tasks})


@app.route("/tasks", methods=["POST"])
def createTasks():
    new_task = {
        "id": uuid.uuid4().hex,
        "title": request.json["title"],
        "BanksNames": request.json["BanksNames"],
    }
    tasks.append(new_task)
    return jsonify({"tasks": new_task})


@app.route("/get_banks", methods=["POST"])
def get_banks():
    try:
        BankNo = request.json[0]["BanksNo"]

        return jsonify({"BankName": Banks[BankNo]})
    except IndexError:
        return jsonify({"BankName": "NO Bank Avaliable"})


port = 8000
if __name__ == "__main__":
    app.run(debug=True, port=port)
# python app.py -p 8000
