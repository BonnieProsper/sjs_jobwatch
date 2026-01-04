import os
import smtplib
from email.message import EmailMessage


def require_env(name: str) -> str:
    value = os.getenv(name)
    if not value:
        raise RuntimeError(f"Missing environment variable: {name}")
    return value


def send_email(subject: str, body: str) -> None:
    msg = EmailMessage()
    msg["Subject"] = subject
    msg["From"] = require_env("EMAIL_FROM")
    msg["To"] = require_env("EMAIL_TO")
    msg.set_content(body)

    host = require_env("SMTP_HOST")
    port = int(require_env("SMTP_PORT"))
    user = require_env("SMTP_USER")
    password = require_env("SMTP_PASS")

    with smtplib.SMTP(host, port) as server:
        server.starttls()
        server.login(user, password)
        server.send_message(msg)
