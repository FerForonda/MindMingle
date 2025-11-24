import os 
from flask import Flask
from flask_sock import Sock

from services.auth_service import init_oauth
from models import init_db  # <- añadimos esto

sock = Sock()


def create_app():
    app = Flask(__name__)

    # Clave secreta
    app.config["SECRET_KEY"] = os.environ.get("SECRET_KEY", "dev-secret-key")

    # Config OAuth Google (mejor por variables de entorno en producción)
    app.config["GOOGLE_CLIENT_ID"] = os.environ.get(
        "GOOGLE_CLIENT_ID",
        "933030651532-8csikv5i46a2ruraas6rv8aii6jds14j.apps.googleusercontent.com",
    )
    app.config["GOOGLE_CLIENT_SECRET"] = os.environ.get(
        "GOOGLE_CLIENT_SECRET",
        "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",
    )

    # 🔸 Configuración de BASE DE DATOS (MySQL + PyMySQL)
    # Puedes cambiar usuario, password y nombre de BD según lo que creaste en phpMyAdmin
    app.config["SQLALCHEMY_DATABASE_URI"] = os.environ.get(
        "DATABASE_URL",
        "mysql+pymysql://root:@localhost/web_sis_colab",
    )
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

    # Inicializar OAuth (Google)
    init_oauth(app)

    # 🔸 Inicializar SQLAlchemy y crear tablas
    init_db(app)

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
   
    app.run(debug=True, threaded=True)
