import json
from simple_websocket import ConnectionClosed
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
    - Recibe el mensaje de JOIN y registra al usuario.
    - Recibe mensajes de chat.
    - Maneja desconexiones.
    """
    username = None

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

                # Enviar historial solo a este usuario
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
                broadcast_system_message(f"{username} se unió al chat.", exclude_ws=ws)

                # Actualizar lista de usuarios conectados
                broadcast_user_list()

            # Mensaje de chat normal
            elif msg_type == "chat" and username is not None:
                text = (data.get("text") or "").strip()
                if text:
                    message = add_message(username, text)
                    broadcast_chat_message(message)

            # Puedes agregar otros tipos (typing, etc.) si quieres

    except ConnectionClosed:
        # El cliente cerró la conexión
        pass
    finally:
        if username:
            unregister_client(ws)
            broadcast_system_message(f"{username} se desconectó.")
            broadcast_user_list()
