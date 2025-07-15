from flask import Flask, render_template, request, redirect, url_for
from flask_socketio import SocketIO, join_room, leave_room, emit, disconnect
from flask import request as socket_request
import uuid
import random
import time
import threading

app = Flask(__name__)
app.secret_key = "secret"
socketio = SocketIO(app)

rooms = {}
room_last_active = {}
user_map = {}

CHARACTER_NAMES = [
    "Naruto", "Luffy", "Goku", "Saitama", "Doraemon", "Shinchan",
    "Itachi", "Levi", "Gojo", "Tanjiro", "Killua", "Light", "Zoro",
    "Sasuke", "Rem", "Nezuko", "SpongeBob", "Dexter", "Pikachu", "Chopper"
]

def monitor_rooms():
    while True:
        now = time.time()
        to_delete = []
        for room_id, last_active in list(room_last_active.items()):
            if now - last_active > 300:
                to_delete.append(room_id)
        for room_id in to_delete:
            rooms.pop(room_id, None)
            room_last_active.pop(room_id, None)
            socketio.emit('room_deleted', room=room_id)
        time.sleep(30)

threading.Thread(target=monitor_rooms, daemon=True).start()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/create_room', methods=['POST'])
def create_room():
    room_name = request.form.get('room_name')
    password = request.form.get('password') or ''
    room_id = str(uuid.uuid4())[:8]

    rooms[room_id] = {
        'name': room_name,
        'password': password,
        'messages': [],
        'users': []
    }
    room_last_active[room_id] = time.time()
    return redirect(url_for('chat', room_id=room_id))

@app.route('/join_room', methods=['POST'])
def join_existing():
    room_id = request.form.get('access_key')
    password = request.form.get('password') or ''
    room = rooms.get(room_id)
    if room and room['password'] == password:
        return redirect(url_for('chat', room_id=room_id))
    else:
        return "Room not found or incorrect password.", 403

@app.route('/room/<room_id>')
def chat(room_id):
    room = rooms.get(room_id)
    if not room:
        return "Room not found", 404
    return render_template('chatroom.html', room_id=room_id, room_name=room['name'])

@socketio.on('join')
def handle_join(data):
    room_id = data['room']
    join_room(room_id)
    room_last_active[room_id] = time.time()

    username = random.choice(CHARACTER_NAMES) + str(random.randint(100, 999))
    avatar = f"https://api.dicebear.com/7.x/adventurer/svg?seed={username}"
    user_map[socket_request.sid] = {
        'username': username,
        'room_id': room_id,
        'avatar': avatar
    }

    emit('self_name', {'name': username, 'avatar': avatar})
    emit('user_joined', {'name': username, 'avatar': avatar}, room=room_id)

@socketio.on('send_message')
def handle_message(data):
    room_id = data['room']
    msg = data['msg']
    user_info = user_map.get(socket_request.sid, {})
    room_last_active[room_id] = time.time()

    emit('message', {
        'name': user_info.get('username', 'Unknown'),
        'text': msg,
        'avatar': user_info.get('avatar', '')
    }, room=room_id)

@socketio.on('send_file')
def handle_file(data):
    room_id = data['room']
    file_data = data['file']
    filename = data['filename']
    user_info = user_map.get(socket_request.sid, {})
    room_last_active[room_id] = time.time()

    emit('file_shared', {
        'name': user_info.get('username', 'Unknown'),
        'filename': filename,
        'url': f"/static/uploads/{filename}",
        'avatar': user_info.get('avatar', '')
    }, room=room_id)

@socketio.on('disconnect')
def handle_disconnect():
    sid = socket_request.sid
    user_info = user_map.pop(sid, None)
    if user_info:
        username = user_info['username']
        room_id = user_info['room_id']
        leave_room(room_id)
        emit('user_left', {'name': username}, room=room_id)
        room_last_active[room_id] = time.time()

if __name__ == '__main__':
    socketio.run(app, debug=True)
