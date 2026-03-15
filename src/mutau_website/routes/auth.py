import logging
import secrets
from datetime import datetime, timezone, timedelta

from flask import Blueprint, render_template, request, flash, redirect, url_for
from flask_login import login_user, logout_user, login_required, current_user

from ..extensions import db
from ..models import User, EmailVerificationToken, PasswordResetToken
from ..mail import send_verification_email, send_password_reset_email

logger = logging.getLogger(__name__)
auth_bp = Blueprint("auth", __name__)


# REGISTER

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
            flash("Die Passw\u00f6rter stimmen nicht \u00fcberein.", "danger")
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
            is_verified=False,
            newsletter=newsletter,
        )
        user.set_password(password)

        try:
            db.session.add(user)
            db.session.flush()

            # Deduplication: if an unused token with >23h55m remaining already
            # exists, a mail was just sent (within the last ~5 minutes).
            # Skip creating a new token to prevent duplicate sends when the
            # browser retries a slow POST or the user clicks submit twice.
            dedup_threshold = datetime.now(timezone.utc) + timedelta(hours=23, minutes=55)
            existing = EmailVerificationToken.query.filter(
                EmailVerificationToken.user_id == user.id,
                EmailVerificationToken.used == False,  # noqa: E712
                EmailVerificationToken.expires_at >= dedup_threshold,
            ).first()

            if not existing:
                token_str = secrets.token_urlsafe(48)
                token = EmailVerificationToken(
                    token=token_str,
                    user_id=user.id,
                    expires_at=datetime.now(timezone.utc) + timedelta(hours=24),
                )
                db.session.add(token)
                db.session.commit()

                verify_url = url_for("auth.verify_email", token=token_str, _external=True)
                send_verification_email(user, verify_url)
            else:
                db.session.commit()

            flash("Registrierung erfolgreich. Bitte best\u00e4tige deine E-Mail-Adresse.", "success")
            return redirect(url_for("auth.login"))
        except Exception:
            db.session.rollback()
            logger.exception("Error during registration for %s", email)
            flash("Ein Fehler ist aufgetreten. Bitte versuche es erneut.", "danger")

    return render_template("auth/register.html")


# EMAIL VERIFICATION

@auth_bp.route("/verify-email/<token>")
def verify_email(token):
    record = EmailVerificationToken.query.filter_by(token=token, used=False).first()

    if not record:
        flash("Ung\u00fcltiger oder bereits verwendeter Best\u00e4tigungslink.", "danger")
        return redirect(url_for("auth.login"))

    if datetime.now(timezone.utc) > record.expires_at:
        flash("Der Best\u00e4tigungslink ist abgelaufen. Bitte registriere dich erneut.", "danger")
        return redirect(url_for("auth.register"))

    record.used             = True
    record.user.is_verified = True
    db.session.commit()

    logger.info("E-mail verified for user %s", record.user.email)
    flash("E-Mail-Adresse erfolgreich best\u00e4tigt. Du kannst dich jetzt anmelden.", "success")
    return redirect(url_for("auth.login"))


# LOGIN

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

        if not user.is_verified:
            flash("Bitte best\u00e4tige zuerst deine E-Mail-Adresse.", "warning")
            return render_template("auth/login.html")

        login_user(user, remember=remember)
        next_page = request.args.get("next")
        return redirect(next_page or url_for("main.index"))

    return render_template("auth/login.html")


# LOGOUT

@auth_bp.route("/logout")
@login_required
def logout():
    logout_user()
    flash("Du wurdest ausgeloggt.", "info")
    return redirect(url_for("main.index"))


# FORGOT PASSWORD

@auth_bp.route("/forgot-password", methods=["GET", "POST"])
def forgot_password():
    if request.method == "POST":
        email = request.form.get("email", "").strip().lower()
        user  = User.query.filter_by(email=email, is_verified=True).first()

        flash("Falls diese E-Mail registriert ist, wurde ein Reset-Link gesendet.", "info")

        if user:
            # Deduplication: skip if a fresh reset token (issued in the last 5 min)
            # already exists. Prevents multiple mails from browser retries.
            dedup_threshold = datetime.now(timezone.utc) + timedelta(minutes=55)
            existing = PasswordResetToken.query.filter(
                PasswordResetToken.user_id == user.id,
                PasswordResetToken.used == False,  # noqa: E712
                PasswordResetToken.expires_at >= dedup_threshold,
            ).first()

            if not existing:
                PasswordResetToken.query.filter_by(user_id=user.id, used=False).update({"used": True})

                token_str = secrets.token_urlsafe(48)
                token = PasswordResetToken(
                    token=token_str,
                    user_id=user.id,
                    expires_at=datetime.now(timezone.utc) + timedelta(hours=1),
                )
                db.session.add(token)
                db.session.commit()

                reset_url = url_for("auth.reset_password", token=token_str, _external=True)
                send_password_reset_email(user, reset_url)

        return redirect(url_for("auth.login"))

    return render_template("auth/forgot_password.html")


# RESET PASSWORD

@auth_bp.route("/reset-password/<token>", methods=["GET", "POST"])
def reset_password(token):
    record = PasswordResetToken.query.filter_by(token=token, used=False).first()

    if not record:
        flash("Ung\u00fcltiger oder bereits verwendeter Reset-Link.", "danger")
        return redirect(url_for("auth.forgot_password"))

    if datetime.now(timezone.utc) > record.expires_at:
        flash("Der Reset-Link ist abgelaufen. Bitte fordere einen neuen an.", "danger")
        return redirect(url_for("auth.forgot_password"))

    if request.method == "POST":
        password = request.form.get("password", "")
        confirm  = request.form.get("confirm_password", "")

        if len(password) < 8:
            flash("Das Passwort muss mindestens 8 Zeichen lang sein.", "danger")
            return render_template("auth/reset_password.html", token=token)

        if password != confirm:
            flash("Die Passw\u00f6rter stimmen nicht \u00fcberein.", "danger")
            return render_template("auth/reset_password.html", token=token)

        record.used = True
        record.user.set_password(password)
        db.session.commit()

        logger.info("Password reset completed for user %s", record.user.email)
        flash("Passwort erfolgreich ge\u00e4ndert. Du kannst dich jetzt anmelden.", "success")
        return redirect(url_for("auth.login"))

    return render_template("auth/reset_password.html", token=token)


# UNSUBSCRIBE

@auth_bp.route("/unsubscribe/<token>")
def unsubscribe(token):
    user = User.query.filter_by(unsubscribe_token=token).first()
    if not user:
        flash("Ung\u00fcltiger Abmeldelink.", "danger")
        return redirect(url_for("main.index"))

    if not user.newsletter:
        flash("Du bist bereits vom Newsletter abgemeldet.", "info")
        return redirect(url_for("main.index"))

    user.newsletter = False
    db.session.commit()
    logger.info("User %s unsubscribed from newsletter via token", user.email)
    return render_template("auth/unsubscribe.html", user=user)


# ACCOUNT

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
    # Must match the string in the template exactly. \u00f6 = Ö (Python macht komische Sachen wenn man auf Ö überprüft daher die UTF-16 schreibweise um den Compiler/Interpreter nicht zu verwüren lol)
    if confirm != "L\u00d6SCHEN":
        flash("Bitte gib L\u00d6SCHEN ein, um deinen Account zu l\u00f6schen.", "danger")
        return redirect(url_for("auth.account"))

    user = current_user._get_current_object()
    logout_user()
    db.session.delete(user)
    db.session.commit()
    flash("Dein Account wurde gel\u00f6scht.", "info")
    return redirect(url_for("main.index"))