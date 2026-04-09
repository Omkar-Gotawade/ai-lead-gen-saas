"""Abstract API email validation service."""
import logging
from typing import Dict

import requests

logger = logging.getLogger(__name__)


class AbstractEmailValidator:
    """Validate email addresses using Abstract API."""

    BASE_URL = "https://emailvalidation.abstractapi.com/v1/"

    def __init__(self, api_key: str):
        self.api_key = api_key

    def validate(self, email: str) -> Dict[str, object]:
        """Validate a single email and return normalized verdict."""
        try:
            response = requests.get(
                self.BASE_URL,
                params={"api_key": self.api_key, "email": email},
                timeout=15,
            )
            response.raise_for_status()
            data = response.json() or {}

            is_valid_format = bool(data.get("is_valid_format", {}).get("value"))
            is_mx_found = bool(data.get("is_mx_found", {}).get("value"))
            is_smtp_valid = bool(data.get("is_smtp_valid", {}).get("value"))
            is_disposable = bool(data.get("is_disposable_email", {}).get("value"))
            quality_score = float(data.get("quality_score") or 0)

            is_deliverable = (
                is_valid_format
                and is_mx_found
                and (is_smtp_valid or quality_score >= 0.7)
                and not is_disposable
            )

            return {
                "email": email,
                "is_deliverable": is_deliverable,
                "quality_score": quality_score,
                "is_mx_found": is_mx_found,
                "is_smtp_valid": is_smtp_valid,
                "is_disposable": is_disposable,
            }
        except Exception as exc:
            logger.warning("Abstract validation failed for %s: %s", email, exc)
            return {
                "email": email,
                "is_deliverable": False,
                "quality_score": 0.0,
                "is_mx_found": False,
                "is_smtp_valid": False,
                "is_disposable": False,
            }
