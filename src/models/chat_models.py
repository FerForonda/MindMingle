from datetime import datetime
from . import db


class User(db.Model):
    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)

    # Nombre visible en el chat (DE GOOGLE o generado)
    # 🔸 Ya NO es único, puede repetirse
    username = db.Column(db.String(120), unique=False, nullable=False)

    # Correo del usuario (Google) → ÚNICO
    email = db.Column(db.String(255), unique=True, nullable=False)

    # Fecha y hora del último inicio de sesión
    last_login = db.Column(db.DateTime, nullable=True)

    messages = db.relationship("Message", backref="user", lazy=True)

    def __repr__(self):
        return f"<User {self.username} ({self.email})>"


class Message(db.Model):
    __tablename__ = "messages"

    id = db.Column(db.Integer, primary_key=True)
    text = db.Column(db.Text, nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.now, nullable=False)

    # Relación con usuario
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)

    def __repr__(self):
        return f"<Message {self.id} by {self.user_id}>"

    def to_dict(self):
        """
        Convierte el mensaje a dict para mandarlo por WebSocket.
        """
        return {
            "type": "chat",
            "username": self.user.username if self.user else "Desconocido",
            "text": self.text,
            "timestamp": self.timestamp.strftime("%H:%M:%S"),
        }
