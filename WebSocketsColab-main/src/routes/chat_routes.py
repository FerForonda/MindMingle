from flask import Blueprint, render_template, session, redirect, url_for
from controllers.chat_controller import handle_websocket

chat_bp = Blueprint("chat", __name__)


@chat_bp.route("/")
def index():
    username = session.get("username")
    # Si no ha iniciado sesión, lo mandamos a login
    if not username:
        return redirect(url_for("auth.login"))
    return render_template("index.html", username=username)


def register_ws_routes(sock):
    @sock.route("/ws/chat")
    def chat_socket(ws):
        handle_websocket(ws)
