from datetime import datetime
from flask_login import UserMixin
from .extensions import db, bcrypt, login_manager


# ── User ──────────────────────────────────────────────────────────────────────

class User(UserMixin, db.Model):
    __tablename__ = "users"

    id            = db.Column(db.Integer, primary_key=True)
    email         = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    name          = db.Column(db.String(120))
    is_admin      = db.Column(db.Boolean, default=False, nullable=False)
    is_verified   = db.Column(db.Boolean, default=True,  nullable=False)  # set False when email is wired up
    newsletter    = db.Column(db.Boolean, default=False, nullable=False)
    created_at    = db.Column(db.DateTime, default=datetime.utcnow)
    deleted_at    = db.Column(db.DateTime, nullable=True)

    def set_password(self, password):
        self.password_hash = bcrypt.generate_password_hash(password).decode("utf-8")

    def check_password(self, password):
        return bcrypt.check_password_hash(self.password_hash, password)

    @property
    def is_active(self):
        # Flask-Login hook — soft-deleted users cannot log in
        return self.deleted_at is None


@login_manager.user_loader
def load_user(user_id):
    user = User.query.get(int(user_id))
    if user and user.deleted_at is not None:
        return None
    return user


# ── Password Reset Token ──────────────────────────────────────────────────────

class PasswordResetToken(db.Model):
    __tablename__ = "password_reset_tokens"

    id         = db.Column(db.Integer, primary_key=True)
    token      = db.Column(db.String(100), unique=True, nullable=False)
    user_id    = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    expires_at = db.Column(db.DateTime, nullable=False)
    used       = db.Column(db.Boolean, default=False, nullable=False)

    user = db.relationship("User", backref="reset_tokens")


# ── Product ───────────────────────────────────────────────────────────────────

class Product(db.Model):
    __tablename__ = "products"

    id          = db.Column(db.Integer, primary_key=True)
    slug        = db.Column(db.String(50), unique=True, nullable=False)   # URL key, e.g. "converter"
    name        = db.Column(db.String(120), nullable=False)
    description = db.Column(db.Text)
    icon        = db.Column(db.String(10))
    features    = db.Column(db.Text)   # JSON array stored as string
    specs       = db.Column(db.Text)   # JSON array stored as string
    support     = db.Column(db.Text)   # JSON array stored as string
    is_active   = db.Column(db.Boolean, default=True, nullable=False)

    def features_list(self):
        import json
        try:
            return json.loads(self.features or "[]")
        except Exception:
            return []

    def specs_list(self):
        import json
        try:
            return json.loads(self.specs or "[]")
        except Exception:
            return []

    def support_list(self):
        import json
        try:
            return json.loads(self.support or "[]")
        except Exception:
            return []


# ── Research Paper ────────────────────────────────────────────────────────────

class Paper(db.Model):
    __tablename__ = "papers"

    id          = db.Column(db.Integer, primary_key=True)
    pdf_path    = db.Column(db.String(255), unique=True, nullable=False)  # relative to research/
    title       = db.Column(db.String(255), nullable=False)
    authors     = db.Column(db.String(255))
    date        = db.Column(db.Date)
    description = db.Column(db.Text)
    notified    = db.Column(db.Boolean, default=False, nullable=False)    # newsletter sent?
    created_at  = db.Column(db.DateTime, default=datetime.utcnow)
