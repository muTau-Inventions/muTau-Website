"""Application factory."""
import logging
import os

from flask import Flask, render_template
from .extensions import db, bcrypt, login_manager
from .models import User  # noqa: F401 — must be imported before create_all()


def _configure_logging(app: Flask) -> None:
    """
    Route all app + library logs through gunicorn's error logger when running
    under gunicorn, or fall back to a basic stderr handler in dev.
    """
    from .config import get_log_level
    level = get_log_level()

    gunicorn_logger = logging.getLogger("gunicorn.error")

    if gunicorn_logger.handlers:
        # Running under gunicorn — reuse its handlers so output lands in
        # the same stream that `docker compose logs` captures.
        root = logging.getLogger()
        root.handlers = gunicorn_logger.handlers
        root.setLevel(level)
    else:
        # Dev / direct flask run — basic stderr output.
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

    # ── Logging (must be early so config loader messages are captured) ────
    _configure_logging(app)
    logger = logging.getLogger(__name__)

    # ── Secret key ────────────────────────────────────────────────────────
    secret_key = os.environ.get("SECRET_KEY", "")
    if not secret_key or secret_key == "change_this_in_production":
        logger.warning(
            "SECRET_KEY environment variable is not set or still uses the default value. "
            "Set a strong random key before running."
        )
    app.secret_key = secret_key

    # ── Database ──────────────────────────────────────────────────────────
    database_url = os.environ.get("DATABASE_URL")
    if not database_url:
        raise RuntimeError("DATABASE_URL environment variable is not set.")

    app.config["SQLALCHEMY_DATABASE_URI"] = database_url
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

    # ── Extensions ────────────────────────────────────────────────────────
    db.init_app(app)
    bcrypt.init_app(app)
    login_manager.init_app(app)

    # ── Blueprints ────────────────────────────────────────────────────────
    from .routes import main_bp, auth_bp, content_bp, products_bp, legal_bp, admin_bp

    app.register_blueprint(main_bp)
    app.register_blueprint(auth_bp)
    app.register_blueprint(content_bp)
    app.register_blueprint(products_bp)
    app.register_blueprint(legal_bp)
    app.register_blueprint(admin_bp)

    # ── DB init (safe with --preload: runs once in gunicorn master) ───────
    with app.app_context():
        from .models import EmailVerificationToken, PasswordResetToken, Product, Paper, Offer  # noqa: F401
        db.create_all()
        logger.info("Database tables verified / created.")
        from .seed import seed_products
        seed_products()

    # ── Error handlers ────────────────────────────────────────────────────
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