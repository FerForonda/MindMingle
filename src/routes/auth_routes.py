from flask import Blueprint
from controllers.auth_controller import (
    start_google_login,
    handle_google_callback,
    perform_logout,
)

auth_bp = Blueprint("auth", __name__)


@auth_bp.route("/login")
def login():
    # Inicia flujo de login con Google
    return start_google_login()


@auth_bp.route("/auth/callback")
def google_callback():
    # Google redirige aquí después del login
    return handle_google_callback()


@auth_bp.route("/logout")
def logout():
    # Cerrar sesión local
    return perform_logout()
