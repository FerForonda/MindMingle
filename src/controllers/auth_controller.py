from flask import redirect, url_for, session
from services.auth_service import oauth
from datetime import datetime

from models import db
from models.chat_models import User


def start_google_login():
    """
    Inicia el flujo de login con Google.
    (Sin manejo manual de nonce, Authlib valida lo básico)
    """
    redirect_uri = url_for("auth.google_callback", _external=True)
    return oauth.google.authorize_redirect(redirect_uri)


def handle_google_callback():
    """
    Maneja la respuesta de Google:
    - Intercambia el código por tokens
    - Decodifica el ID Token
    - Guarda/actualiza el usuario en la BD
    - Guarda datos básicos en sesión
    """
    # Intercambiamos el código de autorización por tokens
    token = oauth.google.authorize_access_token()

    # 🔸 IMPORTANTE: esta versión de Authlib exige 'nonce' como parámetro,
    # aunque no lo usemos; por eso le pasamos None.
    user_info = oauth.google.parse_id_token(token, None)

    # Datos básicos de Google
    email = user_info.get("email")
    name = user_info.get("name") or email

    if not email:
        # Si por alguna razón Google no devuelve email, no podemos seguir
        return redirect(url_for("auth.login"))

    # Buscar usuario por email (es único)
    user = User.query.filter_by(email=email).first()

    if not user:
        # Crear nuevo usuario
        user = User(
            username=name,
            email=email,
            last_login=datetime.now(),
        )
        db.session.add(user)
    else:
        # Actualizar datos básicos
        user.username = name
        user.last_login = datetime.now()

    db.session.commit()

    # Guardar datos en sesión
    session["user_id"] = user.id
    session["username"] = user.username

    # Redirigimos al chat
    return redirect(url_for("chat.index"))


def perform_logout():
    """
    Cierra la sesión local del usuario.
    """
    session.clear()
    return redirect(url_for("auth.login"))
