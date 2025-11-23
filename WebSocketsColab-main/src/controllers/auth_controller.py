from flask import redirect, url_for, session
from services.auth_service import oauth
import secrets


def start_google_login():
    """
    Inicia el flujo de login con Google.
    Genera un 'nonce' y lo guarda en sesión.
    """
    # Generamos un nonce aleatorio y lo guardamos en la sesión
    nonce = secrets.token_urlsafe(16)
    session["oauth_nonce"] = nonce

    # URL de retorno (callback)
    redirect_uri = url_for("auth.google_callback", _external=True)

    # Importante: mandamos el nonce en la request a Google
    return oauth.google.authorize_redirect(redirect_uri, nonce=nonce)


def handle_google_callback():
    """
    Maneja la respuesta de Google:
    - Recupera el nonce de la sesión
    - Autoriza el token
    - Valida y decodifica el ID Token usando el nonce
    - Guarda los datos básicos del usuario en sesión
    """
    # Recuperamos el nonce que enviamos antes
    nonce = session.get("oauth_nonce")

    # Intercambiamos el código de autorización por tokens
    token = oauth.google.authorize_access_token()

    # Ahora SÍ pasamos el nonce a parse_id_token
    user_info = oauth.google.parse_id_token(token, nonce=nonce)

    # Por si quieres limpiar el nonce
    session.pop("oauth_nonce", None)

    # Obtenemos un nombre de usuario (name o email)
    username = user_info.get("name") or user_info.get("email")
    session["username"] = username

    # Redirigimos al chat
    return redirect(url_for("chat.index"))


def perform_logout():
    """
    Cierra la sesión local del usuario.
    """
    session.clear()
    return redirect(url_for("auth.login"))
