import hashlib
import hmac
import secrets
from functools import wraps

from flask import abort, current_app, session
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
# Stateless HMAC approach: only a short random seed is stored in the session
# cookie; the actual token is HMAC(secret_key, seed) — never stored server-side.
# This avoids all session-persistence edge cases and works across all Gunicorn workers.

def _csrf_key() -> bytes:
    key = current_app.secret_key
    return key.encode("utf-8") if isinstance(key, str) else key


def generate_csrf_token() -> str:
    """Return the CSRF token for this session, generating the seed if needed."""
    if "_cs" not in session:
        session["_cs"] = secrets.token_hex(16)
    session.modified = True  # ensure the session cookie is always written
    seed = session["_cs"]
    return hmac.new(_csrf_key(), seed.encode("utf-8"), hashlib.sha256).hexdigest()


def validate_csrf_token(token: str) -> bool:
    """Return True iff token matches the expected HMAC for this session."""
    if not token:
        return False
    seed = session.get("_cs")
    if not seed:
        return False
    expected = hmac.new(_csrf_key(), seed.encode("utf-8"), hashlib.sha256).hexdigest()
    return hmac.compare_digest(expected, token)


# Decorators

def admin_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if not current_user.is_authenticated or not current_user.is_admin:
            abort(403)
        return f(*args, **kwargs)
    return decorated