import hmac
import secrets
from functools import wraps

from flask import abort, session
from flask_bcrypt import Bcrypt
from flask_login import LoginManager, current_user
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()
bcrypt = Bcrypt()
login_manager = LoginManager()
login_manager.login_view = "auth.login"
login_manager.login_message = "Bitte melde dich an."
login_manager.login_message_category = "warning"


# CSRF
# The token is generated once per session and stored directly in the signed
# Flask session cookie. No server-side state is needed. The session cookie is
# signed with SECRET_KEY by Flask/itsdangerous, so the token cannot be forged.
# hmac.compare_digest is used to prevent timing attacks.

def generate_csrf_token() -> str:
    """Return the session CSRF token, creating it if it doesn't exist yet."""
    if "csrf_token" not in session:
        session["csrf_token"] = secrets.token_hex(32)
    return session["csrf_token"]


def validate_csrf_token(submitted: str) -> bool:
    """Return True iff the submitted token matches the one stored in the session."""
    if not submitted:
        return False
    stored = session.get("csrf_token")
    if not stored:
        return False
    return hmac.compare_digest(stored, submitted)


# Decorators

def admin_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if not current_user.is_authenticated or not current_user.is_admin:
            abort(403)
        return f(*args, **kwargs)
    return decorated