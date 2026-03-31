"""Input validation and normalization helpers."""
import re
from typing import Optional


_WHITESPACE_RE = re.compile(r"\s+")


def normalize_email(email: Optional[str]) -> Optional[str]:
    if email is None:
        return None
    return email.strip().lower()


def sanitize_text(value: Optional[str], max_len: int = 1000) -> Optional[str]:
    if value is None:
        return None

    cleaned = _WHITESPACE_RE.sub(" ", value).strip()
    if not cleaned:
        return None
    return cleaned[:max_len]
