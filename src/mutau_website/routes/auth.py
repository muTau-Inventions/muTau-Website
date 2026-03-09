import secrets
from datetime import datetime, timedelta

from flask import Blueprint, render_template, request, flash, redirect, url_for
from flask_login import login_user, logout_user, login_required, current_user

from ..extensions import db
from ..models import User, PasswordResetToken
from ..mail import send_verification_email, send_password_reset_email

auth_bp = Blueprint("auth", __name__)


@auth_bp.route("/register", methods=["GET", "POST"])
def register():
    if current_user.is_authenticated:
        return redirect(url_for("main.index"))

    if request.method == "POST":
        first_name = request.form.get("first_name", "").strip()
        last_name  = request.form.get("last_name", "").strip()
        email      = request.form.get("email", "").strip().lower()
        password   = request.form.get("password", "")
        confirm    = request.form.get("confirm_password", "")
        agb        = request.form.get("agb")
        newsletter = request.form.get("newsletter") == "on"

        if not agb:
            flash("Bitte akzeptiere die AGB.", "danger")
            return render_template("auth/register.html")

        if password != confirm:
            flash("Die Passwörter stimmen nicht überein.", "danger")
            return render_template("auth/register.html")

        if len(password) < 8:
            flash("Das Passwort muss mindestens 8 Zeichen lang sein.", "danger")
            return render_template("auth/register.html")

        if User.query.filter_by(email=email).first():
            flash("Diese E-Mail-Adresse ist bereits registriert.", "danger")
            return render_template("auth/register.html")

        user = User(
            email=email,
            name=f"{first_name} {last_name}".strip(),
            is_verified=True, # FIXME: Set to False when verification code is in place
            newsletter=newsletter,
        )
        user.set_password(password)

        try:
            db.session.add(user)
            db.session.commit()
            # send_verification_email(user) # FIXME: Send Email to verify EMAIL Adress
            flash("Registrierung erfolgreich. Du kannst dich jetzt anmelden.", "success")
            return redirect(url_for("auth.login"))
        except Exception:
            db.session.rollback()
            flash("Ein Fehler ist aufgetreten. Bitte versuche es erneut.", "danger")

    return render_template("auth/register.html")


@auth_bp.route("/login", methods=["GET", "POST"])
def login():
    if current_user.is_authenticated:
        return redirect(url_for("main.index"))

    if request.method == "POST":
        email    = request.form.get("email", "").strip().lower()
        password = request.form.get("password", "")
        remember = request.form.get("remember") == "on"

        user = User.query.filter_by(email=email).first()

        if not user or not user.check_password(password):
            flash("E-Mail oder Passwort ist falsch.", "danger")
            return render_template("auth/login.html")

        if user.deleted_at is not None:
            flash("Dieser Account wurde gelöscht.", "danger")
            return render_template("auth/login.html")

        if not user.is_verified:
            flash("Bitte bestätige zuerst deine E-Mail-Adresse.", "warning")
            return render_template("auth/login.html")

        login_user(user, remember=remember)
        next_page = request.args.get("next")
        return redirect(next_page or url_for("main.index"))

    return render_template("auth/login.html")

@auth_bp.route("/logout")
@login_required
def logout():
    logout_user()
    flash("Du wurdest ausgeloggt.", "info")
    return redirect(url_for("main.index"))


@auth_bp.route("/forgot-password", methods=["GET", "POST"])
def forgot_password():
    if request.method == "POST":
        email = request.form.get("email", "").strip().lower()
        user  = User.query.filter_by(email=email).first()

        flash("Falls diese E-Mail registriert ist, wurde ein Reset-Link gesendet.", "info")

        if user and user.deleted_at is None:
            token_str = secrets.token_urlsafe(48)
            token = PasswordResetToken(
                token=token_str,
                user_id=user.id,
                expires_at=datetime.utcnow() + timedelta(hours=1),
            )
            db.session.add(token)
            db.session.commit()
            # send_password_reset_email(user, token_str)  # FIXME: Uncomment when reset mechanic is implemented

        return redirect(url_for("auth.login"))

    return render_template("auth/forgot_password.html")

@auth_bp.route("/account")
@login_required
def account():
    return render_template("auth/account.html")


@auth_bp.route("/account/newsletter", methods=["POST"])
@login_required
def toggle_newsletter():
    current_user.newsletter = not current_user.newsletter
    db.session.commit()
    state = "aktiviert" if current_user.newsletter else "deaktiviert"
    flash(f"Newsletter {state}.", "success")
    return redirect(url_for("auth.account"))


@auth_bp.route("/account/delete", methods=["POST"])
@login_required
def delete_account():
    confirm = request.form.get("confirm", "")
    if confirm != "LÖSCHEN":
        flash("Bitte gib LÖSCHEN ein, um deinen Account zu löschen.", "danger")
        return redirect(url_for("auth.account"))

    current_user.deleted_at = datetime.utcnow()
    current_user.email      = f"deleted_{current_user.id}@deleted"
    current_user.name       = "Gelöschter Nutzer"
    db.session.commit()
    logout_user()
    flash("Dein Account wurde gelöscht.", "info")
    return redirect(url_for("main.index"))
