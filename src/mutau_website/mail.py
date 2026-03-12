"""
Mail helpers.
URLs are passed in as parameters so this module stays free of Flask request context.
SMTP settings come from config.yml.
"""
import logging
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

from flask import render_template, url_for

from .config import get_mail_cfg

logger = logging.getLogger(__name__)


# ── Internal helpers ───────────────────────────────────────────────────────

def _smtp_cfg() -> dict:
    mc = get_mail_cfg()
    return {
        "host":     mc.get("smtp_host", ""),
        "port":     int(mc.get("smtp_port", 587)),
        "use_tls":  bool(mc.get("smtp_use_tls", True)),
        "user":     mc.get("smtp_user", ""),
        "password": mc.get("smtp_password", ""),
        # from_address must match the authenticated SMTP user on most servers.
        # Leave it blank in config.yml to fall back to smtp_user automatically.
        "sender":   mc.get("from_address") or mc.get("smtp_user", ""),
    }


def _subject(key: str, **fmt) -> str:
    mc       = get_mail_cfg()
    defaults = {
        "newsletter":     "Neue Forschungspublikation: {title}",
        "verification":   "Bitte bestätige deine E-Mail-Adresse — muTau-Inventions",
        "password_reset": "Passwort zurücksetzen — muTau-Inventions",
    }
    tpl = mc.get("subjects", {}).get(key, defaults.get(key, key))
    return tpl.format(**fmt) if fmt else tpl


def _send(to_addresses: list, subject: str, body_html: str) -> None:
    """Send one e-mail. Raises on SMTP failure."""
    cfg = _smtp_cfg()

    if not cfg["host"]:
        raise RuntimeError("mail.smtp_host is not configured in config.yml")

    msg = MIMEMultipart("alternative")
    msg["Subject"] = subject
    msg["From"]    = cfg["sender"]
    msg["To"]      = ", ".join(to_addresses)
    msg.attach(MIMEText(body_html, "html", "utf-8"))

    with smtplib.SMTP(cfg["host"], cfg["port"], timeout=10) as smtp:
        if cfg["use_tls"]:
            smtp.starttls()
        if cfg["user"] and cfg["password"]:
            smtp.login(cfg["user"], cfg["password"])
        smtp.sendmail(cfg["sender"], to_addresses, msg.as_string())

    logger.info("Mail sent  to=%s  subject=%r", to_addresses, subject)


# ── Public API ─────────────────────────────────────────────────────────────

def send_verification_email(user, verify_url: str) -> None:
    """
    Send account e-mail verification after registration.
    verify_url: absolute URL to the /verify-email/<token> route.
    """
    try:
        body = render_template("email/verification.html", user=user, verify_url=verify_url)
        _send([user.email], _subject("verification"), body)
    except Exception:
        logger.exception("Failed to send verification e-mail to %s", user.email)


def send_password_reset_email(user, reset_url: str) -> None:
    """
    Send a password-reset link.
    reset_url: absolute URL to the /reset-password/<token> route.
    """
    try:
        body = render_template("email/password_reset.html", user=user, reset_url=reset_url)
        _send([user.email], _subject("password_reset"), body)
    except Exception:
        logger.exception("Failed to send password-reset e-mail to %s", user.email)


def send_newsletter(users, paper, pdf_url: str, research_url: str) -> None:
    """
    Notify newsletter subscribers about a new research paper.
    Each recipient gets a personalised unsubscribe link via their token.
    """
    subject = _subject("newsletter", title=paper.title)
    failed  = 0

    for user in users:
        if not user.email:
            continue
        try:
            unsubscribe_url = url_for(
                "auth.unsubscribe", token=user.unsubscribe_token, _external=True
            )
            body = render_template(
                "email/newsletter.html",
                paper=paper,
                pdf_url=pdf_url,
                research_url=research_url,
                unsubscribe_url=unsubscribe_url,
            )
            _send([user.email], subject, body)
        except Exception:
            logger.exception("Newsletter: failed to send to %s", user.email)
            failed += 1

    sent = len([u for u in users if u.email]) - failed
    logger.info("Newsletter '%s': %d sent, %d failed", paper.title, sent, failed)