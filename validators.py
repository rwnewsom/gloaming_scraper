"""Data validation utilities."""
import re
import logging
from urllib.parse import urlparse

logger = logging.getLogger(__name__)


class URLValidator:
    """Validate URL format and structure"""

    URL_PATTERN = re.compile(
        r'^https?://'  # http:// or https://
        r'(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+[A-Z]{2,6}\.?|'  # domain
        r'localhost|'  # localhost
        r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})'  # IP
        r'(?::\d+)?'  # optional port
        r'(?:/?|[/?]\S+)$', re.IGNORECASE
    )

    @staticmethod
    def validate(url: str) -> bool:
        """
        Validate URL format.
        Returns True if valid, False otherwise.
        """
        if not url or not isinstance(url, str):
            return False

        if len(url) > 2048:
            return False

        try:
            result = urlparse(url)
            return all([result.scheme, result.netloc])
        except Exception:
            return False

    @staticmethod
    def is_valid_listing_url(url: str, base_url: str) -> bool:
        """
        Check if URL is a valid listing URL.
        Should start with base domain.
        """
        if not URLValidator.validate(url):
            return False

        try:
            base_domain = urlparse(base_url).netloc
            url_domain = urlparse(url).netloc
            return url_domain == base_domain
        except Exception:
            return False


class EmailValidator:
    """Validate email format"""

    EMAIL_PATTERN = re.compile(
        r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    )

    @staticmethod
    def validate(email: str) -> bool:
        """
        Validate email format.
        Returns True if valid, False otherwise.
        """
        if not email or not isinstance(email, str):
            return False

        email = email.strip()

        if len(email) > 254:
            return False

        if not EmailValidator.EMAIL_PATTERN.match(email):
            return False

        # Check for obvious obfuscation/issues
        if email.count('@') != 1:
            return False

        local, domain = email.rsplit('@', 1)

        if len(local) == 0 or len(domain) == 0:
            return False

        # Check for consecutive dots
        if '..' in email:
            return False

        # Check domain has at least one dot
        if '.' not in domain:
            return False

        return True

    @staticmethod
    def is_potentially_malformed(email: str) -> bool:
        """
        Check if email appears malformed or suspicious.
        Used for logging malformed emails.
        """
        if not email or not isinstance(email, str):
            return True

        # Empty or mostly spaces
        if not email.strip():
            return True

        # Contains common obfuscation patterns
        if any(pattern in email.lower() for pattern in ['[at]', '(at)', '[dot]', '(dot)']):
            return True

        # Multiple @ symbols (obfuscation attempt)
        if email.count('@') > 1:
            return True

        # Very short email
        if len(email) < 5:
            return True

        return not EmailValidator.validate(email)
