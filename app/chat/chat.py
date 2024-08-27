from flask import Blueprint, render_template, session
from ..utils import login_required, User
from flask_socketio import SocketIO, emit, join_room, leave_room

blueprint = Blueprint("chat", __name__, template_folder="templates", url_prefix="/chat")
socket = SocketIO()

@socket.on('send_message')
def handle_send_message(data):
    room = data['room']
    message = data['message']
    emit('receive_message', message, room=room)

@socket.on('join')
def on_join(data):
    user = User(**session["user"])
    username = user.name
    room = data['room']
    join_room(room)
    emit('receive_message', f'{username} has entered the room.', room=room)

@socket.on('leave')
def on_leave(data):
    user = User(**session["user"])
    username = user.name
    room = data['room']
    leave_room(room)
    emit('receive_message', f'{username} has left the room.', room=room)

@blueprint.route("/")
@login_required
def home():
    user = User(**session["user"])
    return render_template("chat.html", user=user.name)