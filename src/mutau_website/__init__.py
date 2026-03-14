"""Application factory."""
import logging
import os

from flask import Flask, render_template, request, abort
from .extensions import db, bcrypt, login_manager, generate_csrf_token, validate_csrf_token
from .models import User  # noqa: F401


def _configure_logging(app: Flask) -> None:
    from .config import get_log_level
    level = get_log_level()
    gunicorn_logger = logging.getLogger("gunicorn.error")
    if gunicorn_logger.handlers:
        root = logging.getLogger()
        root.handlers = gunicorn_logger.handlers
        root.setLevel(level)
    else:
        logging.basicConfig(
            level=level,
            format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
        )
    app.logger.setLevel(level)


def create_app() -> Flask:
    app = Flask(
        __name__,
        template_folder=os.path.join(os.path.dirname(__file__), "..", "..", "templates"),
        static_folder=os.path.join(os.path.dirname(__file__), "..", "..", "static"),
    )

    # LOGGING (needs config loaded first)
    _configure_logging(app)
    logger = logging.getLogger(__name__)

    # SECRET KEY — must be set via the SECRET_KEY environment variable.
    # Set it in docker-compose.yml under web.environment.
    secret_key = os.environ.get("SECRET_KEY", "").strip()
    if not secret_key:
        raise RuntimeError(
            "Die Umgebungsvariable SECRET_KEY ist nicht gesetzt. "
            "Bitte in docker-compose.yml unter web.environment eintragen."
        )
    app.secret_key = secret_key

    # DATABASE — always from the DATABASE_URL environment variable.
    # Docker Compose sets this automatically from the db service definition.
    database_url = os.environ.get("DATABASE_URL", "").strip()
    if not database_url:
        raise RuntimeError(
            "Die Umgebungsvariable DATABASE_URL ist nicht gesetzt. "
            "Sie wird von Docker Compose automatisch aus dem db-Service uebernommen."
        )
    app.config["SQLALCHEMY_DATABASE_URI"] = database_url
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

    # SESSION COOKIE — secure defaults that work on localhost and behind a proxy
    app.config["SESSION_COOKIE_HTTPONLY"] = True
    app.config["SESSION_COOKIE_SAMESITE"] = "Lax"
    # SESSION_COOKIE_SECURE is deliberately left at default (False).
    # Enable it in production by setting the env var COOKIE_SECURE=1.
    if os.environ.get("COOKIE_SECURE", "").strip() == "1":
        app.config["SESSION_COOKIE_SECURE"] = True

    # EXTENSIONS
    db.init_app(app)
    bcrypt.init_app(app)
    login_manager.init_app(app)

    # JINJA GLOBALS
    app.jinja_env.globals["csrf_token"] = generate_csrf_token

    # CSRF PROTECTION
    # Applied to every state-changing request except static files and unrouted 404s.
    _CSRF_EXEMPT_ENDPOINTS: set = set()

    @app.before_request
    def enforce_csrf():
        if request.method not in ("POST", "PUT", "PATCH", "DELETE"):
            return
        # Static files and unmatched routes don't need CSRF protection.
        if request.endpoint is None or request.endpoint == "static":
            return
        if request.endpoint in _CSRF_EXEMPT_ENDPOINTS:
            return
        submitted = request.form.get("csrf_token", "")
        if not validate_csrf_token(submitted):
            logger.warning(
                "CSRF validation failed | endpoint=%s | token_in_form=%s | "
                "token_in_session=%s",
                request.endpoint,
                bool(submitted),
                "csrf_token" in request.cookies or bool(submitted),
            )
            abort(403)

    # BLUEPRINTS
    from .routes import main_bp, auth_bp, content_bp, products_bp, legal_bp, admin_bp
    app.register_blueprint(main_bp)
    app.register_blueprint(auth_bp)
    app.register_blueprint(content_bp)
    app.register_blueprint(products_bp)
    app.register_blueprint(legal_bp)
    app.register_blueprint(admin_bp)

    # DB INIT
    with app.app_context():
        from .models import (  # noqa: F401
            EmailVerificationToken, PasswordResetToken,
            Product, Paper, Offer, ContactMessage,
        )
        db.create_all()
        logger.info("Database tables verified / created.")
        from .seed import seed_products
        seed_products()

    # ERROR HANDLERS
    @app.errorhandler(403)
    def forbidden(e):
        return render_template("errors/403.html"), 403

    @app.errorhandler(404)
    def not_found(e):
        return render_template("errors/404.html"), 404

    @app.errorhandler(500)
    def server_error(e):
        return render_template("errors/500.html"), 500

    logger.info("muTau app created successfully.")
    return app