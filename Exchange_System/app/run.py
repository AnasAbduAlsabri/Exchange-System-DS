# __init__.py
import subprocess
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from dotenv import load_dotenv
import os
from flask_migrate import Migrate
from flask_login import LoginManager
from flask_socketio import SocketIO
from openai import OpenAI

app = Flask(__name__)
load_dotenv()

app.config["SECRET_KEY"] = os.getenv("SECRET_KEY")
app.config["SQLALCHEMY_DATABASE_URI"] = os.getenv("SQLALCHEMY_DATABASE_URI")
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config["TEMPLATES_AUTO_RELOAD"] = True

socketio = SocketIO(app)
db = SQLAlchemy(app)
migrate = Migrate(app, db)
login_manager = LoginManager(app)

openai_client = OpenAI(
    organization=os.getenv("OPENAI_ORG_ID"),
    api_key=os.getenv("OPENAI_KEY"),
)

from app.models import User
from . import routes


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


if __name__ == "__main__":
    app.run(debug=True)
    socketio.run(app=app, host="0.0.0.0", port=5000)
print("----------------------------------------------------------------")
# script_path = os.path.abspath(os.path.join(os.path.dirname(__file__), 'getTransfers_mpi.py'))
# # Run the script after starting the Flask app
# subprocess.run(f"mpiexec -n 2 python {script_path}", shell=True)
print("----------------------------------------------------------------")
