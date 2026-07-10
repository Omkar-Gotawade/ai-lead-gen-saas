"""Email sending service for SMTP and SendGrid.

Threading support: pass in_reply_to and references to attach follow-up emails
to the correct conversation thread in Gmail / Outlook.  When both are None
the email is sent as a fresh message (existing behaviour, fully backward-compat).
"""
import smtplib
from email import utils as email_utils
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from typing import Optional, Tuple

from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail, Header

from app.models.email_provider import EmailProviderSettings, ProviderType
from app.services.crypto_service import decrypt_value


def _make_message_id(from_email: str) -> str:
    """Generate an RFC-compliant Message-ID using the sender's domain."""
    domain = from_email.split("@")[-1] if "@" in from_email else "mail.local"
    return email_utils.make_msgid(domain=domain)


def _thread_subject(subject: str, is_reply: bool) -> str:
    """Prefix subject with 'Re: ' when this is a threaded follow-up."""
    if not is_reply:
        return subject
    if subject.lower().startswith("re:"):
        return subject  # already prefixed
    return f"Re: {subject}"


def send_smtp_email(
    settings: EmailProviderSettings,
    to_email: str,
    subject: str,
    body: str,
    in_reply_to: Optional[str] = None,
    references: Optional[str] = None,
) -> str:
    """
    Send email via SMTP and return the outgoing Message-ID.

    Args:
        settings:     Email provider settings
        to_email:     Recipient email
        subject:      Email subject
        body:         Email body (plain text)
        in_reply_to:  Message-ID of the original email (threading)
        references:   References header value — same as in_reply_to for single-anchor threading

    Returns:
        The Message-ID string of the email that was sent (e.g. "<abc@domain.com>")

    Raises:
        Exception: If email sending fails
    """
    password = decrypt_value(settings.smtp_password_encrypted)
    is_reply = bool(in_reply_to)

    msg = MIMEMultipart("alternative")
    msg["Subject"] = _thread_subject(subject, is_reply)
    msg["From"] = f"{settings.from_name} <{settings.from_email}>"
    msg["To"] = to_email

    # Generate a fresh Message-ID for this outgoing email
    outgoing_message_id = _make_message_id(settings.from_email)
    msg["Message-ID"] = outgoing_message_id

    # Attach threading headers when this is a follow-up
    if in_reply_to:
        msg["In-Reply-To"] = in_reply_to
        msg["References"] = references or in_reply_to

    part = MIMEText(body, "plain")
    msg.attach(part)

    try:
        if settings.use_ssl:
            server = smtplib.SMTP_SSL(settings.smtp_host, settings.smtp_port)
        else:
            server = smtplib.SMTP(settings.smtp_host, settings.smtp_port)
            if settings.use_tls:
                server.starttls()

        server.login(settings.smtp_username, password)
        server.sendmail(settings.from_email, [to_email], msg.as_string())
        server.quit()
    except Exception as e:
        raise Exception(f"SMTP send failed: {str(e)}")

    return outgoing_message_id


def send_sendgrid_email(
    settings: EmailProviderSettings,
    to_email: str,
    subject: str,
    body: str,
    in_reply_to: Optional[str] = None,
    references: Optional[str] = None,
) -> str:
    """
    Send email via SendGrid and return a generated Message-ID.

    Threading is applied via SendGrid custom headers (In-Reply-To / References).
    SendGrid does not expose the actual SMTP Message-ID it assigns, so we return
    the same outgoing_message_id we inject as a custom header — email clients
    that honour it will thread correctly.

    Args:
        settings:     Email provider settings
        to_email:     Recipient email
        subject:      Email subject
        body:         Email body (plain text)
        in_reply_to:  Message-ID of the original email (threading)
        references:   References header value

    Returns:
        The Message-ID string injected into the outgoing email headers

    Raises:
        Exception: If email sending fails
    """
    api_key = decrypt_value(settings.sendgrid_api_key_encrypted)
    is_reply = bool(in_reply_to)

    message = Mail(
        from_email=(settings.from_email, settings.from_name),
        to_emails=to_email,
        subject=_thread_subject(subject, is_reply),
        plain_text_content=body,
    )

    # Inject a Message-ID so we have a stable identifier to store
    outgoing_message_id = _make_message_id(settings.from_email)
    message.header = Header("Message-ID", outgoing_message_id)

    if in_reply_to:
        message.header = Header("In-Reply-To", in_reply_to)
        message.header = Header("References", references or in_reply_to)

    try:
        sg = SendGridAPIClient(api_key)
        response = sg.send(message)

        if response.status_code not in [200, 201, 202]:
            raise Exception(f"SendGrid returned status {response.status_code}")

    except Exception as e:
        raise Exception(f"SendGrid send failed: {str(e)}")

    return outgoing_message_id


def send_email(
    provider_settings: EmailProviderSettings,
    to_email: str,
    subject: str,
    body: str,
    in_reply_to: Optional[str] = None,
    references: Optional[str] = None,
) -> str:
    """
    Send email using the configured provider and return the outgoing Message-ID.

    Args:
        provider_settings: Email provider configuration
        to_email:          Recipient email
        subject:           Email subject
        body:              Email body
        in_reply_to:       Original Message-ID for threading (optional)
        references:        References header for threading (optional)

    Returns:
        Outgoing Message-ID string

    Raises:
        Exception: If sending fails
    """
    if provider_settings.provider_type == ProviderType.SMTP:
        return send_smtp_email(
            provider_settings, to_email, subject, body,
            in_reply_to=in_reply_to, references=references,
        )
    elif provider_settings.provider_type == ProviderType.SENDGRID:
        return send_sendgrid_email(
            provider_settings, to_email, subject, body,
            in_reply_to=in_reply_to, references=references,
        )
    else:
        raise ValueError(f"Unsupported provider type: {provider_settings.provider_type}")
