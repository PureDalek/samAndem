# Build Email Notifications

Android build workflows call `scripts/send_build_email.py` after successful builds.

The mailer never attaches APKs. It only sends a short "build ready" email with the GitHub workflow, release, or S3 update link.

## GitHub Secrets

Set these repository secrets:

```text
SMTP_HOST
SMTP_PORT
SMTP_USERNAME
SMTP_PASSWORD
MAIL_TO
MAIL_FROM
```

Notes:

- `MAIL_TO` can be one address or a comma-separated list.
- `MAIL_FROM` is optional; when missing, the script uses `SMTP_USERNAME`.
- For Gmail, use `SMTP_HOST=smtp.gmail.com`, `SMTP_PORT=587`, and an app password as `SMTP_PASSWORD`.
- The script skips email if required values are missing so builds still pass before email is configured.

## Local Use

After a local APK build:

```powershell
$env:SMTP_HOST = "smtp.gmail.com"
$env:SMTP_PORT = "587"
$env:SMTP_USERNAME = "you@example.com"
$env:SMTP_PASSWORD = "app-password"
$env:MAIL_TO = "you@example.com"
$env:MAIL_SUBJECT = "Sam And Em build ready on git"
$env:MAIL_BODY = "A new Sam And Em build is ready on git."
python scripts\send_build_email.py
```

Or build and notify in one command:

```powershell
powershell -ExecutionPolicy Bypass -File scripts\build_android_local.ps1
```
