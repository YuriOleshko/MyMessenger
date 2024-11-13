from sqlalchemy.orm import relationship
from app import db
from flask_bcrypt import Bcrypt
from datetime import datetime

bcrypt = Bcrypt()

# Вспомогательная таблица для связи многие-ко-многим между пользователями (User) и чатами (Chat)
chat_participants = db.Table('chat_participants',
    db.Column('user_id', db.Integer, db.ForeignKey('user.id'), primary_key=True),
    db.Column('chat_id', db.Integer, db.ForeignKey('chat.id'), primary_key=True)
)

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    password_hash = db.Column(db.String(128), nullable=False)

    # Генерирует хеш из пароля и сохраняет его
    def set_password(self, password):
        self.password_hash = bcrypt.generate_password_hash(password).decode('utf-8')
    # Проверяет, соответствует ли переданный пароль хешу
    def check_password(self, password):
        return bcrypt.check_password_hash(self.password_hash, password)

    bot_messages = db.relationship('ChatWithBotMessage', back_populates='user')


class Chat(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    participants = db.relationship('User', secondary=chat_participants, backref='chats')

class Message(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    chat_id = db.Column(db.Integer, db.ForeignKey('chat.id'), nullable=False)
    sender_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    content = db.Column(db.Text, nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)

    sender = db.relationship('User', backref='sent_messages')


class ChatWithBotMessage(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    message = db.Column(db.Text, nullable=False)
    bot_response = db.Column(db.Text, nullable=True)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)

    # Связь с пользователем
    user = relationship('User', back_populates='bot_messages', foreign_keys=[user_id])