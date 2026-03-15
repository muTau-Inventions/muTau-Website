import logging
import smtplib
import threading
from email.mime.text import MIMEText
from email.utils import parseaddr

from flask import render_template, url_for

from .config import get_mail_cfg

logger = logging.getLogger(__name__)

_smtp_lock = threading.Semaphore(1)


def _smtp_cfg() -> dict:
    mc = get_mail_cfg()
    return {
        "host":     mc.get("smtp_host", ""),
        "port":     int(mc.get("smtp_port", 587)),
        "use_tls":  bool(mc.get("smtp_use_tls", True)),
        "user":     mc.get("smtp_user", ""),
        "password": mc.get("smtp_password", ""),
        "sender":   mc.get("from_address") or mc.get("smtp_user", ""),
    }


def _envelope_from(sender: str) -> str:
    _, addr = parseaddr(sender)
    return addr or sender


def _subject(key: str, **fmt) -> str:
    mc = get_mail_cfg()
    defaults = {
        "newsletter":     "Neue Forschungspublikation: {title}",
        "verification":   "Bitte bestätige deine E-Mail-Adresse — muTau-Inventions",
        "password_reset": "Passwort zurücksetzen — muTau-Inventions",
    }
    tpl = mc.get("subjects", {}).get(key, defaults.get(key, key))
    return tpl.format(**fmt) if fmt else tpl


def _send_now(to_addresses: list, subject: str, body_html: str) -> None:
    cfg = _smtp_cfg()
    if not cfg["host"]:
        raise RuntimeError("mail.smtp_host is not configured in config.yml")

    msg = MIMEText(body_html, "html", "utf-8")
    msg["Subject"] = subject
    msg["From"]    = cfg["sender"]
    msg["To"]      = ", ".join(to_addresses)

    envelope_from = _envelope_from(cfg["sender"])

    with smtplib.SMTP(cfg["host"], cfg["port"], timeout=30) as smtp:
        smtp.ehlo()
        if cfg["use_tls"]:
            smtp.starttls()
            smtp.ehlo()
        if cfg["user"] and cfg["password"]:
            smtp.login(cfg["user"], cfg["password"])
        smtp.sendmail(envelope_from, to_addresses, msg.as_string())

    logger.info("Mail sent  to=%s  subject=%r", to_addresses, subject)


def _send_async(to_addresses: list, subject: str, body_html: str) -> None:
    def _worker():
        acquired = _smtp_lock.acquire(timeout=60)
        if not acquired:
            logger.error("Mail queue timeout — could not acquire SMTP lock for %s", to_addresses)
            return
        try:
            _send_now(to_addresses, subject, body_html)
        except Exception:
            logger.exception("Async mail failed  to=%s  subject=%r", to_addresses, subject)
        finally:
            _smtp_lock.release()

    t = threading.Thread(target=_worker, daemon=True, name=f"mail-{to_addresses[0]}")
    t.start()

def send_verification_email(user, verify_url: str) -> None:
    try:
        body = render_template("email/verification.html", user=user, verify_url=verify_url)
        _send_async([user.email], _subject("verification"), body)
    except Exception:
        logger.exception("Failed to queue verification e-mail for %s", user.email)


def send_password_reset_email(user, reset_url: str) -> None:
    try:
        body = render_template("email/password_reset.html", user=user, reset_url=reset_url)
        _send_async([user.email], _subject("password_reset"), body)
    except Exception:
        logger.exception("Failed to queue password-reset e-mail for %s", user.email)


def send_newsletter(users, paper, pdf_url: str, research_url: str) -> None:
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
            _send_async([user.email], subject, body)
        except Exception:
            logger.exception("Newsletter: failed to queue mail for %s", user.email)
            failed += 1

    queued = len([u for u in users if u.email]) - failed
    logger.info("Newsletter '%s': %d queued, %d failed", paper.title, queued, failed)