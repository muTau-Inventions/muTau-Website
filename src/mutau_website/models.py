import uuid
from datetime import datetime, timezone
from flask_login import UserMixin
from .extensions import db, bcrypt, login_manager


def _now():
    return datetime.now(timezone.utc)


def _uuid():
    return str(uuid.uuid4())


class User(UserMixin, db.Model):
    __tablename__ = "users"

    id                = db.Column(db.Integer, primary_key=True)
    email             = db.Column(db.String(120), unique=True, nullable=False)
    password_hash     = db.Column(db.String(255), nullable=False)
    name              = db.Column(db.String(120))
    is_admin          = db.Column(db.Boolean, default=False, nullable=False)
    is_verified       = db.Column(db.Boolean, default=False, nullable=False)
    newsletter        = db.Column(db.Boolean, default=False, nullable=False)
    unsubscribe_token = db.Column(db.String(36), unique=True, nullable=False, default=_uuid)
    created_at        = db.Column(db.DateTime(timezone=True), default=_now)

    offers = db.relationship("Offer", backref="user", cascade="all, delete-orphan", passive_deletes=True)

    def set_password(self, password: str) -> None:
        self.password_hash = bcrypt.generate_password_hash(password).decode("utf-8")

    def check_password(self, password: str) -> bool:
        return bcrypt.check_password_hash(self.password_hash, password)


@login_manager.user_loader
def load_user(user_id):
    return db.session.get(User, int(user_id))


class EmailVerificationToken(db.Model):
    __tablename__ = "email_verification_tokens"

    id         = db.Column(db.Integer, primary_key=True)
    token      = db.Column(db.String(100), unique=True, nullable=False)
    user_id    = db.Column(db.Integer, db.ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    expires_at = db.Column(db.DateTime(timezone=True), nullable=False)
    used       = db.Column(db.Boolean, default=False, nullable=False)
    mail_sent  = db.Column(db.Boolean, default=False, nullable=False)

    user = db.relationship("User", backref=db.backref("verification_tokens", cascade="all, delete-orphan", passive_deletes=True))


class PasswordResetToken(db.Model):
    __tablename__ = "password_reset_tokens"

    id         = db.Column(db.Integer, primary_key=True)
    token      = db.Column(db.String(100), unique=True, nullable=False)
    user_id    = db.Column(db.Integer, db.ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    expires_at = db.Column(db.DateTime(timezone=True), nullable=False)
    used       = db.Column(db.Boolean, default=False, nullable=False)

    user = db.relationship("User", backref=db.backref("reset_tokens", cascade="all, delete-orphan", passive_deletes=True))


class Product(db.Model):
    __tablename__ = "products"

    id          = db.Column(db.Integer, primary_key=True)
    slug        = db.Column(db.String(50), unique=True, nullable=False)
    name        = db.Column(db.String(120), nullable=False)
    description = db.Column(db.Text)
    icon        = db.Column(db.String(10))
    features    = db.Column(db.Text)
    specs       = db.Column(db.Text)
    support     = db.Column(db.Text)
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


class Paper(db.Model):
    __tablename__ = "papers"

    id          = db.Column(db.Integer, primary_key=True)
    pdf_path    = db.Column(db.String(255), unique=True, nullable=False)
    title       = db.Column(db.String(255), nullable=False)
    authors     = db.Column(db.String(255))
    date        = db.Column(db.Date)
    description = db.Column(db.Text)
    notified    = db.Column(db.Boolean, default=False, nullable=False)
    created_at  = db.Column(db.DateTime(timezone=True), default=_now)


class Offer(db.Model):
    __tablename__ = "offers"

    id               = db.Column(db.Integer, primary_key=True)
    user_id          = db.Column(db.Integer, db.ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    name             = db.Column(db.String(120), nullable=False)
    email            = db.Column(db.String(120), nullable=False)
    company          = db.Column(db.String(120))
    product_interest = db.Column(db.String(120))
    message          = db.Column(db.Text, nullable=False)
    created_at       = db.Column(db.DateTime(timezone=True), default=_now)
    status           = db.Column(db.String(20), default="new", nullable=False)


class ContactMessage(db.Model):
    __tablename__ = "contact_messages"

    id         = db.Column(db.Integer, primary_key=True)
    name       = db.Column(db.String(120), nullable=False)
    email      = db.Column(db.String(120), nullable=False)
    subject    = db.Column(db.String(200))
    message    = db.Column(db.Text, nullable=False)
    read       = db.Column(db.Boolean, default=False, nullable=False)
    answered   = db.Column(db.Boolean, default=False, nullable=False)
    created_at = db.Column(db.DateTime(timezone=True), default=_now)