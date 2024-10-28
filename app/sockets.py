from flask_socketio import SocketIO, emit, join_room, leave_room
from app import socketio, db
from app.models import Chat, Message, User
from flask import session
from datetime import datetime


# WebSocket-обработчики

# Обработчик события подключения
@socketio.on('connect')
def handle_connect():
    print(f'Client connected: {session.get("user_id")}')
    emit('connected', {'message': 'Connected to the server'})


# Обработчик события отключения
@socketio.on('disconnect')
def handle_disconnect():
    print(f'Client disconnected: {session.get("user_id")}')
    emit('disconnected', {'message': 'Disconnected from the server'})


# Присоединение к чату
@socketio.on('join_chat')
def handle_join_chat(data):
    chat_id = data['chat_id']
    join_room(chat_id)
    print(f'User joined chat: {chat_id}')
    emit('status', {'message': f'Joined chat {chat_id}'}, room=chat_id)


# Выход из чата
@socketio.on('leave_chat')
def handle_leave_chat(data):
    chat_id = data['chat_id']
    leave_room(chat_id)
    print(f'User left chat: {chat_id}')
    emit('status', {'message': f'Left chat {chat_id}'}, room=chat_id)


# Отправка сообщения в чат
@socketio.on('send_message')
def handle_send_message(data):
    chat_id = data['chat_id']
    user_id = data['user_id']
    content = data['content']

    # Сохраняем сообщение в базе данных
    message = Message(chat_id=chat_id, sender_id=user_id, content=content, timestamp=datetime.utcnow())
    db.session.add(message)
    db.session.commit()

    print(f'User {user_id} sent a message in chat {chat_id}: {content}')

    # Отправляем сообщение в чат
    emit('receive_message', {
        'chat_id': chat_id,
        'user_id': user_id,
        'content': content,
        'timestamp': message.timestamp.strftime('%Y-%m-%d %H:%M:%S')
    }, room=chat_id)

