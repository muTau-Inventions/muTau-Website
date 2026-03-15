import logging
import os

from flask import Flask, render_template, request, abort
from .extensions import db, bcrypt, login_manager, generate_csrf_token, validate_csrf_token
from .models import User


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


def _seed_admin(logger: logging.Logger) -> None:
    email    = os.environ.get("ADMIN_EMAIL", "").strip()
    name     = os.environ.get("ADMIN_NAME", "Admin").strip()
    password = os.environ.get("ADMIN_PASSWORD", "").strip()

    if not email or not password:
        return

    if User.query.filter_by(is_admin=True).first():
        return

    if User.query.filter_by(email=email).first():
        logger.warning("ADMIN_EMAIL '%s' already registered but is not admin.", email)
        return

    admin = User(email=email, name=name, is_admin=True, is_verified=True)
    admin.set_password(password)
    db.session.add(admin)
    db.session.commit()
    logger.info("First admin account created: %s", email)


def create_app() -> Flask:
    app = Flask(
        __name__,
        template_folder=os.path.join(os.path.dirname(__file__), "..", "..", "templates"),
        static_folder=os.path.join(os.path.dirname(__file__), "..", "..", "static"),
    )

    # LOGGING
    _configure_logging(app)
    logger = logging.getLogger(__name__)

    # SECRET KEY
    secret_key = os.environ.get("SECRET_KEY", "").strip()
    if not secret_key:
        raise RuntimeError(
            "Die Umgebungsvariable SECRET_KEY ist nicht gesetzt. "
            "Bitte in docker-compose.yml unter web.environment eintragen."
        )
    app.secret_key = secret_key

    # DATABASE
    database_url = os.environ.get("DATABASE_URL", "").strip()
    if not database_url:
        raise RuntimeError(
            "Die Umgebungsvariable DATABASE_URL ist nicht gesetzt. "
            "Sie wird von Docker Compose automatisch aus dem db-Service uebernommen."
        )
    app.config["SQLALCHEMY_DATABASE_URI"] = database_url
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

    # SESSION COOKIE
    app.config["SESSION_COOKIE_HTTPONLY"] = True
    app.config["SESSION_COOKIE_SAMESITE"] = "Lax"
    if os.environ.get("COOKIE_SECURE", "").strip() == "1":
        app.config["SESSION_COOKIE_SECURE"] = True

    # BASE URL
    from .config import get_base_url
    _base_url = get_base_url()
    if _base_url and _base_url != "http://localhost":
        from urllib.parse import urlparse
        _parsed = urlparse(_base_url)
        app.config["SERVER_NAME"] = _parsed.netloc
        app.config["PREFERRED_URL_SCHEME"] = _parsed.scheme or "https"

    # EXTENSIONS
    db.init_app(app)
    bcrypt.init_app(app)
    login_manager.init_app(app)

    # JINJA GLOBALS
    app.jinja_env.globals["csrf_token"] = generate_csrf_token

    # CSRF PROTECTION
    _CSRF_EXEMPT_ENDPOINTS: set = set()

    @app.before_request
    def enforce_csrf():
        if request.method not in ("POST", "PUT", "PATCH", "DELETE"):
            return
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
        from .models import (
            EmailVerificationToken, PasswordResetToken,
            Product, Paper, Offer, ContactMessage,
        )
        db.create_all()
        logger.info("Database tables verified / created.")
        from .seed import seed_products
        seed_products()
        _seed_admin(logger)

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