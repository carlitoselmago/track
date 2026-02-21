from __future__ import annotations

from email.message import EmailMessage
import logging
import smtplib

from app.core.config import settings

logger = logging.getLogger("track.email")


def send_email(*, to_email: str, subject: str, body: str) -> bool:
    if not settings.smtp_host:
        logger.info(
            "SMTP not configured. Skipping email send to %s (subject: %s).",
            to_email,
            subject,
        )
        return False

    message = EmailMessage()
    message["From"] = settings.email_from
    message["To"] = to_email
    message["Subject"] = subject
    message.set_content(body)

    try:
        with smtplib.SMTP(settings.smtp_host, settings.smtp_port, timeout=10) as smtp:
            if settings.smtp_use_tls:
                smtp.starttls()
            if settings.smtp_username:
                smtp.login(settings.smtp_username, settings.smtp_password)
            smtp.send_message(message)
        return True
    except Exception:
        logger.exception(
            "Failed to send email to %s (subject: %s).",
            to_email,
            subject,
        )
        return False
