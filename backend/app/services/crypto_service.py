"""Encryption service for sensitive data."""
from cryptography.fernet import Fernet
from app.config import settings
import base64
import hashlib


def _get_fernet() -> Fernet:
    """
    Get Fernet cipher instance.
    
    Note: In production, use a proper KMS (Key Management Service)
    like AWS KMS, Google Cloud KMS, or HashiCorp Vault.
    """
    # Derive a 32-byte key from the encryption key in settings
    key = hashlib.sha256(settings.ENCRYPTION_KEY.encode()).digest()
    key_base64 = base64.urlsafe_b64encode(key)
    return Fernet(key_base64)


def encrypt_value(plain_text: str) -> str:
    """
    Encrypt a plain text value.
    
    Args:
        plain_text: Text to encrypt
        
    Returns:
        Encrypted text as string
    """
    if not plain_text:
        return ""
    
    f = _get_fernet()
    encrypted_bytes = f.encrypt(plain_text.encode())
    return encrypted_bytes.decode()


def decrypt_value(encrypted_text: str) -> str:
    """
    Decrypt an encrypted value.
    
    Args:
        encrypted_text: Encrypted text
        
    Returns:
        Decrypted plain text
    """
    if not encrypted_text:
        return ""
    
    f = _get_fernet()
    decrypted_bytes = f.decrypt(encrypted_text.encode())
    return decrypted_bytes.decode()
