import os
from flask import Flask, render_template
from .extensions import db, bcrypt, login_manager
from .models import User


def create_app():
    app = Flask(
        __name__,
        template_folder=os.path.join(os.path.dirname(__file__), "..", "..", "templates"),
        static_folder=os.path.join(os.path.dirname(__file__), "..", "..", "static"),
    )

    app.secret_key = os.environ.get("SECRET_KEY", os.urandom(24))

    database_url = os.environ.get("DATABASE_URL")
    if not database_url:
        raise RuntimeError("DATABASE_URL environment variable is not set.")

    app.config["SQLALCHEMY_DATABASE_URI"] = database_url
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

    db.init_app(app)
    bcrypt.init_app(app)
    login_manager.init_app(app)

    from .routes import main_bp, auth_bp, content_bp, products_bp, legal_bp, admin_bp

    app.register_blueprint(main_bp)
    app.register_blueprint(auth_bp)
    app.register_blueprint(content_bp)
    app.register_blueprint(products_bp)
    app.register_blueprint(legal_bp)
    app.register_blueprint(admin_bp)

    with app.app_context():
        from .models import PasswordResetToken, Product, Paper, Offer

    @app.errorhandler(403)
    def forbidden(e):
        return render_template("errors/403.html"), 403

    @app.errorhandler(404)
    def not_found(e):
        return render_template("errors/404.html"), 404

    @app.errorhandler(500)
    def server_error(e):
        return render_template("errors/500.html"), 500

    return app


def init_db():
    app = create_app()
    with app.app_context():
        from .models import PasswordResetToken, Product, Paper, Offer
        db.create_all()
        from .seed import seed_products
        seed_products()