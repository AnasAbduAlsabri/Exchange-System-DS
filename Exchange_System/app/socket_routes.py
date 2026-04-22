# socket_routes.py
from flask import request, session
from . import socketio
from flask_socketio import send, emit


# @socketio.on("transfer_notification")
# def handle_transfer_notification(data):
#     print("Transfer Notification:", data["message"])
#     # استلام رقم جلسة العميل المستهدف
#     recipient_sid = request.sid
#     print("/////////-----------------///////////", request.sid)
#     # إرسال الإشعار إلى العميل المستهدف
#     emit("response", {"data": "Transfer successful!"}, room=recipient_sid)


@socketio.on("connect")
def handle_connect():
    # عندما يتصل العميل بالخادم
    session["sid"] = request.sid


def ack():
    print("message was received!")


# @socketio.on("transfer_notification")
# def handle_transfer_notification(json):
#     emit("response", json, callback=ack)


# @socketio.on("all_transfer_notification")
# def handle_all_transfer_notification(json):
#     emit("response", json, callback=ack)
