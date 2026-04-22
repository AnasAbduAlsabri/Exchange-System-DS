# socket_routes.py
from flask import request, session
from . import socketio
from flask_socketio import send, emit
from flask_login import current_user

# Global dictionary to map usernames to SIDs
user_sids = {}

@socketio.on("connect")
def handle_connect():
    if current_user.is_authenticated:
        user_sids[current_user.username] = request.sid
    session["sid"] = request.sid

@socketio.on("disconnect")
def handle_disconnect():
    if current_user.is_authenticated:
        user_sids.pop(current_user.username, None)
