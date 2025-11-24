import json
from flask import session
from simple_websocket import ConnectionClosed

from models.chat_models import User
from services.chat_service import (
    register_client,
    unregister_client,
    add_message,
    get_history,
    broadcast_chat_message,
    broadcast_system_message,
    broadcast_user_list,
)


def handle_websocket(ws):
    """
    Controla la vida de una conexión WebSocket:
    - Obtiene el usuario desde la sesión (Google login).
    - Recibe el mensaje de JOIN y registra al usuario.
    - Recibe mensajes de chat.
    - Maneja desconexiones.
    """
    username = None
    user = None

    # Intentamos recuperar el usuario de la sesión (login Google)
    user_id = session.get("user_id")
    if user_id:
        user = User.query.get(user_id)

    try:
        while True:
            raw = ws.receive()

            # None suele significar que el cliente se desconectó.
            if raw is None:
                break

            try:
                data = json.loads(raw)
            except json.JSONDecodeError:
                # Ignorar paquetes que no son JSON
                continue

            msg_type = data.get("type")

            # Primer mensaje: JOIN
            if msg_type == "join" and username is None:
                # Si tenemos usuario logueado, usamos su username,
                # si no, permitimos que el cliente envíe un nombre.
                if user is not None:
                    desired_username = user.username
                else:
                    desired_username = data.get("username")

                username = register_client(ws, desired_username)

                # Enviar bienvenida solo a este usuario
                ws.send(
                    json.dumps(
                        {
                            "type": "welcome",
                            "username": username,
                        }
                    )
                )

                # Enviar historial solo a este usuario (desde BD)
                history = get_history()
                ws.send(
                    json.dumps(
                        {
                            "type": "history",
                            "messages": history,
                        }
                    )
                )

                # Notificar a todos los demás
                broadcast_system_message(
                    f"{username} se ha unido al chat.", exclude_ws=ws
                )

                # Actualizar lista de usuarios conectados
                broadcast_user_list()

            # Mensaje de chat normal
            elif msg_type == "chat" and username is not None:
                text = (data.get("text") or "").strip()
                if text:
                    if user is not None:
                        # Guardar mensaje para usuario logueado
                        message = add_message(user, text)
                    else:
                        # Si no hay usuario logueado en BD, podrías:
                        # - Ignorar el mensaje, o
                        # - Crear un usuario temporal en BD
                        # Aquí, por simplicidad, NO guardamos en BD.
                        timestamp = datetime.now().strftime("%H:%M:%S")
                        message = {
                            "type": "chat",
                            "username": username,
                            "text": text,
                            "timestamp": timestamp,
                        }

                    broadcast_chat_message(message)

            # Puedes agregar otros tipos (typing, etc.) si quieres

    except ConnectionClosed:
        # El cliente cerró la conexión
        pass
    finally:
        if username:
            unregister_client(ws)
            broadcast_system_message(f"{username} se ha desconectado.")
            broadcast_user_list()
