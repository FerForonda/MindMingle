from flask_sqlalchemy import SQLAlchemy

# Objeto global de SQLAlchemy
db = SQLAlchemy()

def init_db(app):
    """
    Inicializa la extensión de SQLAlchemy con la app Flask.
    """
    db.init_app(app)

    # Crear las tablas si no existen
    with app.app_context():
        
        from .chat_models import User, Message  # noqa: F401

        db.create_all()