from flask import Blueprint, render_template, request, redirect, url_for, flash, session, jsonify
from app import db, socketio
from app.models import User, Chat, Message, ChatWithBotMessage
from datetime import datetime
from flask_socketio import emit, join_room
from openai import OpenAI
from config import Config


main = Blueprint('main', __name__)

# Главная страница
@main.route('/')
def index():
    if 'user_id' in session:
        user_id = session['user_id']
        user = User.query.get(user_id)
        chats = Chat.query.filter(Chat.participants.contains(user)).all()
        return render_template('index.html', chats=chats)
    else:
        return render_template('index.html')

# Регистрация
@main.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']

        if User.query.filter_by(email=email).first():
            flash('Email is already registered', 'error')
            return redirect(url_for('main.register'))

        if User.query.filter_by(username=username).first():
            flash('Username is already taken', 'error')
            return redirect(url_for('main.register'))

        new_user = User(username=username, email=email)
        new_user.set_password(password)

        db.session.add(new_user)
        db.session.commit()

        flash('Registration successful! Please login.', 'success')
        return redirect(url_for('main.login'))

    return render_template('register.html')

# Вход в систему
@main.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']

        user = User.query.filter_by(email=email).first()
        if user and user.check_password(password):
            session['user_id'] = user.id
            flash('Login successful!', 'success')
            return redirect(url_for('main.index'))
        else:
            flash('Invalid credentials. Please try again.', 'error')
            return redirect(url_for('main.login'))

    return render_template('login.html')

# Выход из системы
@main.route('/logout')
def logout():
    session.pop('user_id', None)
    flash('You have been logged out.', 'success')
    return redirect(url_for('main.index'))

# Поиск пользователей
@main.route('/search', methods=['GET'])
def search():
    query = request.args.get('query')
    users = []
    if query:
        users = User.query.filter(User.username.ilike(f'%{query}%')).all()
    return render_template('search.html', users=users, query=query)

# Начало нового чата или открытие существующего с пользователем по его user_id
@main.route('/start_chat/<int:user_id>', methods=['GET', 'POST'])
def start_chat(user_id):
    current_user_id = session.get('user_id')
    if not current_user_id:
        flash('Please log in to start a chat.', 'error')
        return redirect(url_for('main.login'))

    user = User.query.get_or_404(user_id)
    if current_user_id == user_id:
        flash('You cannot start a chat with yourself.', 'error')
        return redirect(url_for('main.index'))

    chat = Chat.query.filter(
        Chat.participants.any(User.id == current_user_id),
        Chat.participants.any(User.id == user_id)
    ).first()

    if not chat:
        chat = Chat(participants=[user, User.query.get(current_user_id)])
        db.session.add(chat)
        db.session.commit()

    return redirect(url_for('main.chat', chat_id=chat.id))

# Чат с проверкой прав доступа
@main.route('/chat/<int:chat_id>', methods=['GET', 'POST'])
def chat(chat_id):
    user_id = session.get('user_id')
    if not user_id:
        flash('Please log in to access the chat.', 'error')
        return redirect(url_for('main.login'))

    chat = Chat.query.get_or_404(chat_id)

    user = User.query.get(user_id)
    if user not in chat.participants:
        flash('You do not have access to this chat.', 'error')
        return redirect(url_for('main.index'))

    messages = Message.query.filter_by(chat_id=chat_id).order_by(Message.timestamp.asc()).all()
    return render_template('chat.html', chat=chat, messages=messages)

# Отправка сообщения с проверкой прав доступа
@main.route('/chat/<int:chat_id>/send_message', methods=['POST'])
def send_message(chat_id):
    user_id = session.get('user_id')
    content = request.form['content']

    if user_id and content:
        chat = Chat.query.get_or_404(chat_id)

        user = User.query.get(user_id)
        if user not in chat.participants:
            flash('You do not have access to send messages in this chat.', 'error')
            return redirect(url_for('main.index'))

        message = Message(chat_id=chat_id, sender_id=user_id, content=content, timestamp=datetime.utcnow())
        db.session.add(message)
        db.session.commit()

        socketio.emit(
            'receive_message',
            {
                'message': message.content,
                'username': message.sender.username,
                'timestamp': message.timestamp.strftime('%d.%m.%Y %H:%M'),
                'user_id': user_id
            },
            room=f'chat_{chat_id}'
        )

    return redirect(url_for('main.chat', chat_id=chat_id))

# SocketIO событие для присоединения к комнате чата
@socketio.on('join_chat')
def handle_join_chat(data):
    chat_id = data['chat_id']
    join_room(f'chat_{chat_id}')

# Обработчик события отправки сообщения
@socketio.on('send_message')
def handle_send_message(data):
    user_id = data['user_id']
    chat_id = data['chat_id']
    message_content = data['message']

    chat = Chat.query.get_or_404(chat_id)

    user = User.query.get(user_id)
    if user not in chat.participants:
        emit('access_denied', {'error': 'Access to this chat is denied.'})
        return

    message = Message(chat_id=chat_id, sender_id=user_id, content=message_content, timestamp=datetime.utcnow())
    db.session.add(message)
    db.session.commit()

    socketio.emit('receive_message', {
        'message': message_content,
        'username': user.username,
        'timestamp': message.timestamp.strftime('%d.%m.%Y %H:%M'),
        'user_id': user_id
    }, room=f'chat_{chat_id}')

# Чат пользователя с ботом ChatGPT
@main.route('/chatgpt', methods=['GET', 'POST'])
def chatgpt():
    user_id = session.get('user_id')
    if not user_id:
        flash('Please log in to access the chat.', 'error')
        return redirect(url_for('main.login'))

    messages = ChatWithBotMessage.query.filter_by(user_id=user_id).order_by(ChatWithBotMessage.timestamp).all()

    if request.method == 'POST':
        user_message = request.json.get('message')

        bot_response = get_bot_response(user_message)

        new_message = ChatWithBotMessage(user_id=user_id, message=user_message, bot_response=bot_response,
                                         timestamp=datetime.utcnow())
        db.session.add(new_message)
        db.session.commit()

        return jsonify({"response": bot_response})

    return render_template('chatgpt.html', messages=messages)

# Получения ответа от чат-бота на основе модели GPT
def get_bot_response(user_message):
    client = OpenAI(
        api_key=Config.OPENAI_API_KEY
    )

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": user_message}]
    )
    return response.choices[0].message.content

# Присоединяем пользователя к его комнате c чат-ботом
@socketio.on('join')
def handle_join(data):
    user_id = data['user_id']
    join_room(f'user_{user_id}')

# SocketIO обработчик для отправки сообщений ChatGPT
@socketio.on('send_message_bot')
def handle_send_message_bot(data):
    # Получаем данные из сообщения
    user_id = data['user_id']
    message_content = data['message']
    chat_type = data['chat_type']  # 'bot'

    if chat_type == 'bot':
        bot_response = get_bot_response(message_content)

        new_message = ChatWithBotMessage(
            user_id=user_id,
            message=message_content,
            bot_response=bot_response,
            timestamp=datetime.utcnow()
        )
        db.session.add(new_message)
        db.session.commit()

        emit('receive_message_bot', {
            'message': bot_response,
            'timestamp': datetime.utcnow().isoformat() + "Z",
            'user_id': 'ChatGPT'
        }, room=f'user_{user_id}')