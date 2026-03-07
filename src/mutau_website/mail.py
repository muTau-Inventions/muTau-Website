"""
Mail stubs — all functions are no-ops until SMTP is configured.

When implementing:
1. Add MAIL_SERVER, MAIL_PORT, MAIL_USERNAME, MAIL_PASSWORD to config / env
2. Install Flask-Mail (add to requirements.txt)
3. Replace the pass statements with real send logic
"""


def send_verification_email(user):
    """Send email verification link after registration."""
    pass


def send_password_reset_email(user, token):
    """Send password reset link."""
    pass


def send_newsletter(users, paper):
    """Notify subscribed users about a new research paper."""
    pass
