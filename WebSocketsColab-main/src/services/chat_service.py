import itertools
import json
from datetime import datetime

# Conexiones activas
_clients = set()
_usernames_by_ws = {}

# Historial de mensajes (en memoria)
_history = []

# Generador de IDs para nombres automáticos
_username_counter = itertools.count(1)


def _generate_username():
    return f"Usuario_{next(_username_counter):03d}"


def register_client(ws, desired_username=None):
    if desired_username:
        base = desired_username.strip() or "Usuario"
    else:
        base = None

    if base:
        username = base
        existing = set(_usernames_by_ws.values())
        suffix = 1
        # Asegurar que el nombre sea único
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


def add_message(username, text):
    """Añade un mensaje al historial y lo retorna en formato dict."""
    timestamp = datetime.now().strftime("%H:%M:%S")
    message = {
        "type": "chat",
        "username": username,
        "text": text,
        "timestamp": timestamp,
    }
    _history.append(message)

    if len(_history) > 50:
        _history.pop(0)

    return message


def get_history():
    return list(_history)


def _safe_send(ws, data_dict):
    try:
        ws.send(json.dumps(data_dict))
    except Exception:
        pass


def broadcast_chat_message(message): #Mensaje a todos los usuarios conectados
    for ws in list(_clients):
        _safe_send(ws, message)


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
