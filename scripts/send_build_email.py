#!/usr/bin/env python3
"""Send build-ready notification emails from local builds or GitHub Actions.

The script is intentionally no-op by default when SMTP settings are missing so
builds do not fail just because notifications have not been configured yet.
Set MAIL_REQUIRE=true to make missing configuration a hard error.
"""

from __future__ import annotations

import os
import smtplib
import ssl
import sys
from email.message import EmailMessage


REQUIRED_ENV = ("SMTP_HOST", "SMTP_USERNAME", "SMTP_PASSWORD", "MAIL_TO")


def env_bool(name: str, default: bool = False) -> bool:
    value = os.environ.get(name)
    if value is None or value == "":
        return default
    return value.strip().lower() in {"1", "true", "yes", "on"}


def missing_required() -> list[str]:
    return [name for name in REQUIRED_ENV if not os.environ.get(name)]


def build_message() -> EmailMessage:
    subject = os.environ.get("MAIL_SUBJECT", "Sam And Em Android build ready")
    body = os.environ.get("MAIL_BODY", "A new Sam And Em Android build is ready.")
    sender = os.environ.get("MAIL_FROM") or os.environ["SMTP_USERNAME"]
    recipients = [item.strip() for item in os.environ["MAIL_TO"].replace(";", ",").split(",") if item.strip()]

    if not recipients:
        raise RuntimeError("MAIL_TO did not contain any recipient addresses.")

    message = EmailMessage()
    message["Subject"] = subject
    message["From"] = sender
    message["To"] = ", ".join(recipients)
    message.set_content(body)
    return message


def send(message: EmailMessage) -> None:
    host = os.environ["SMTP_HOST"]
    port = int(os.environ.get("SMTP_PORT") or ("465" if env_bool("SMTP_SSL") else "587"))
    username = os.environ["SMTP_USERNAME"]
    password = os.environ["SMTP_PASSWORD"]

    if env_bool("SMTP_SSL"):
        context = ssl.create_default_context()
        with smtplib.SMTP_SSL(host, port, context=context, timeout=60) as smtp:
            smtp.login(username, password)
            smtp.send_message(message)
        return

    with smtplib.SMTP(host, port, timeout=60) as smtp:
        smtp.ehlo()
        if env_bool("SMTP_STARTTLS", default=True):
            smtp.starttls(context=ssl.create_default_context())
            smtp.ehlo()
        smtp.login(username, password)
        smtp.send_message(message)


def main() -> int:
    missing = missing_required()
    if missing:
        text = "Email notification skipped; missing environment variables: " + ", ".join(missing)
        if env_bool("MAIL_REQUIRE"):
            print(text, file=sys.stderr)
            return 1
        print(text)
        return 0

    try:
        message = build_message()
        send(message)
    except Exception as exc:  # noqa: BLE001 - print actionable build-log errors.
        if env_bool("MAIL_REQUIRE"):
            print(f"Email notification failed: {exc}", file=sys.stderr)
            return 1
        print(f"Email notification failed but build will continue: {exc}")
        return 0

    print("Email notification sent.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
