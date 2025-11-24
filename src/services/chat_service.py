import itertools
import json
from datetime import datetime

from models import db
from models.chat_models import Message, User

# Conexiones activas
_clients = set()
_usernames_by_ws = {}

# Generador de IDs para nombres automáticos (solo para conexiones sin login)
_username_counter = itertools.count(1)


def _generate_username():
    return f"Usuario_{next(_username_counter):03d}"


def register_client(ws, desired_username=None):
    """
    Registra un cliente WebSocket y le asigna un nombre único
    dentro de la sala (aunque el username en BD pueda repetirse).
    """
    if desired_username:
        base = desired_username.strip() or "Usuario"
    else:
        base = None

    if base:
        username = base
        existing = set(_usernames_by_ws.values())
        suffix = 1
        # Asegurar que el nombre sea único SOLO en esta sala de chat
        while username in existing:
            suffix += 1
            username = f"{base}_{suffix}"
    else:
        username = _generate_username()

    _clients.add(ws)
    _usernames_by_ws[ws] = username
    return username


def unregister_client(ws):
    """Elimina al cliente de los registros."""
    _usernames_by_ws.pop(ws, None)
    _clients.discard(ws)


def add_message(user: User, text: str):
    """
    Añade un mensaje a la BD y lo devuelve en formato dict
    para mandarlo por WebSocket.
    """
    # Crear y guardar en BD
    msg = Message(text=text, user_id=user.id, timestamp=datetime.now())
    db.session.add(msg)
    db.session.commit()

    # Convertir a dict usando el método del modelo
    return msg.to_dict()


def get_history(limit: int = 50):
    """
    Obtiene el historial de mensajes desde la BD
    (por ejemplo, los últimos 50).
    """
    messages = (
        Message.query.order_by(Message.timestamp.asc())
        .limit(limit)
        .all()
    )
    return [m.to_dict() for m in messages]


def _safe_send(ws, data_dict):
    try:
        ws.send(json.dumps(data_dict))
    except Exception:
        pass


def broadcast_chat_message(message_dict):
    """Envía un mensaje de chat a todos los clientes conectados."""
    for ws in list(_clients):
        _safe_send(ws, message_dict)


def broadcast_system_message(text, exclude_ws=None):
    payload = {
        "type": "system",
        "text": text,
    }
    for ws in list(_clients):
        if ws is exclude_ws:
            continue
        _safe_send(ws, payload)


def get_user_list():
    return list(_usernames_by_ws.values())


def broadcast_user_list():
    """Envía la lista de usuarios conectados a todos."""
    payload = {
        "type": "user_list",
        "users": get_user_list(),
    }
    for ws in list(_clients):
        _safe_send(ws, payload)
