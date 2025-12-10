"""Email sending service for SMTP and SendGrid."""
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from typing import Optional
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail

from app.models.email_provider import EmailProviderSettings, ProviderType
from app.services.crypto_service import decrypt_value


def send_smtp_email(
    settings: EmailProviderSettings,
    to_email: str,
    subject: str,
    body: str
) -> None:
    """
    Send email via SMTP.
    
    Args:
        settings: Email provider settings
        to_email: Recipient email
        subject: Email subject
        body: Email body (plain text)
        
    Raises:
        Exception: If email sending fails
    """
    # Decrypt password
    password = decrypt_value(settings.smtp_password_encrypted)
    
    # Create message
    msg = MIMEMultipart('alternative')
    msg['Subject'] = subject
    msg['From'] = f"{settings.from_name} <{settings.from_email}>"
    msg['To'] = to_email
    
    # Attach body
    part = MIMEText(body, 'plain')
    msg.attach(part)
    
    # Send email
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


def send_sendgrid_email(
    settings: EmailProviderSettings,
    to_email: str,
    subject: str,
    body: str
) -> None:
    """
    Send email via SendGrid.
    
    Args:
        settings: Email provider settings
        to_email: Recipient email
        subject: Email subject
        body: Email body (plain text)
        
    Raises:
        Exception: If email sending fails
    """
    # Decrypt API key
    api_key = decrypt_value(settings.sendgrid_api_key_encrypted)
    
    try:
        message = Mail(
            from_email=(settings.from_email, settings.from_name),
            to_emails=to_email,
            subject=subject,
            plain_text_content=body
        )
        
        sg = SendGridAPIClient(api_key)
        response = sg.send(message)
        
        if response.status_code not in [200, 201, 202]:
            raise Exception(f"SendGrid returned status {response.status_code}")
            
    except Exception as e:
        raise Exception(f"SendGrid send failed: {str(e)}")


def send_email(
    provider_settings: EmailProviderSettings,
    to_email: str,
    subject: str,
    body: str
) -> None:
    """
    Send email using configured provider.
    
    Args:
        provider_settings: Email provider configuration
        to_email: Recipient email
        subject: Email subject
        body: Email body
        
    Raises:
        Exception: If sending fails
    """
    if provider_settings.provider_type == ProviderType.SMTP:
        send_smtp_email(provider_settings, to_email, subject, body)
    elif provider_settings.provider_type == ProviderType.SENDGRID:
        send_sendgrid_email(provider_settings, to_email, subject, body)
    else:
        raise ValueError(f"Unsupported provider type: {provider_settings.provider_type}")
