import os
from flask import Flask
from flask_sock import Sock

from services.auth_service import init_oauth

sock = Sock()


def create_app():
    app = Flask(__name__)
    app.config["SECRET_KEY"] = "dev-secret-key"

    # Configuración de Google OAuth (mejor usar variables de entorno)
    app.config["GOOGLE_CLIENT_ID"] = "25146429800-e49i74fe7fudcpnvk477ajp3gnleblu2.apps.googleusercontent.com"
    app.config["GOOGLE_CLIENT_SECRET"] = "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"

    # Inicializar OAuth (Google)
    init_oauth(app)

    # Inicializar WebSocket
    sock.init_app(app)

    # Rutas de chat (HTTP + WebSocket)
    from routes.chat_routes import chat_bp, register_ws_routes
    app.register_blueprint(chat_bp)
    register_ws_routes(sock)

    # Rutas de autenticación
    from routes.auth_routes import auth_bp
    app.register_blueprint(auth_bp)

    return app


app = create_app()

if __name__ == "__main__":
    app.run(debug=True)
