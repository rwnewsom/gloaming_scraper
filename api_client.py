"""HTTP client with TOR proxy support and exponential backoff retry logic."""
import logging
import time
import json
import random
from typing import Dict, Any, Optional

import requests

logger = logging.getLogger(__name__)


class APIClient:
    """Handle API requests via TOR proxy with exponential backoff"""

    def __init__(self, session: requests.Session, base_url: str, config: Dict[str, Any]):
        """
        Initialize API client.

        Args:
            session: requests.Session configured with TOR proxy
            base_url: Base URL for the target website
            config: Configuration dict with retry and target settings
        """
        self.session = session
        self.base_url = base_url
        self.retry_config = config.get('retry', {})
        self.target_config = config.get('target_extraction', {})
        self.request_count = 0

    def post_json(self, endpoint_path: str, payload: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        Make POST request with JSON payload and exponential backoff.

        Args:
            endpoint_path: API endpoint path (from config)
            payload: JSON payload dict

        Returns:
            Parsed JSON response or None if failed after retries
        """
        url = self.base_url + endpoint_path
        self.request_count += 1

        max_retries = self.retry_config.get('max_retries', 5)
        max_delay = self.retry_config.get('max_delay', 180)

        for attempt in range(max_retries + 1):
            try:
                logger.debug(
                    "API POST to %s (attempt %d/%d)", endpoint_path,
                    attempt + 1, max_retries + 1)

                response = self.session.post(
                    url,
                    json=payload,
                    timeout=30,
                    headers={'Content-Type': 'application/json'}
                )

                response.raise_for_status()

                try:
                    return response.json()
                except json.JSONDecodeError as e:
                    logger.error("JSON decode error: %s", e)
                    return None

            except requests.exceptions.Timeout:
                logger.warning("Timeout on attempt %d", attempt + 1)
                if attempt < max_retries:
                    delay = self._calculate_backoff(attempt, max_delay)
                    logger.info("Retrying in %.1fs...", delay)
                    time.sleep(delay)
                continue

            except requests.exceptions.ConnectionError as e:
                logger.warning("Connection error: %s", e)
                if attempt < max_retries:
                    delay = self._calculate_backoff(attempt, max_delay)
                    logger.info("Retrying in %.1fs...", delay)
                    time.sleep(delay)
                continue

            except requests.exceptions.RequestException as e:
                logger.error("Request failed: %s", e)
                if attempt < max_retries:
                    delay = self._calculate_backoff(attempt, max_delay)
                    logger.info("Retrying in %.1fs...", delay)
                    time.sleep(delay)
                continue

        logger.error("Failed to POST to %s after %d attempts", endpoint_path,
                     max_retries + 1)
        return None

    def get_page(self, url: str) -> Optional[str]:
        """
        Make GET request for a page and return HTML content.

        Args:
            url: Full URL to fetch

        Returns:
            HTML content or None if failed after retries
        """
        max_retries = self.retry_config.get('max_retries', 5)
        max_delay = self.retry_config.get('max_delay', 180)

        for attempt in range(max_retries + 1):
            try:
                logger.debug("GET %s (attempt %d/%d)", url, attempt + 1,
                             max_retries + 1)

                response = self.session.get(
                    url,
                    timeout=30
                )

                response.raise_for_status()
                return response.text

            except requests.exceptions.Timeout:
                logger.warning("Timeout on attempt %d", attempt + 1)
                if attempt < max_retries:
                    delay = self._calculate_backoff(attempt, max_delay)
                    time.sleep(delay)
                continue

            except requests.exceptions.ConnectionError as e:
                logger.warning("Connection error: %s", e)
                if attempt < max_retries:
                    delay = self._calculate_backoff(attempt, max_delay)
                    time.sleep(delay)
                continue

            except requests.exceptions.RequestException as e:
                logger.error("Request failed: %s", e)
                if attempt < max_retries:
                    delay = self._calculate_backoff(attempt, max_delay)
                    time.sleep(delay)
                continue

        logger.error("Failed to GET %s after %d attempts", url, max_retries + 1)
        return None

    @staticmethod
    def _calculate_backoff(attempt: int, max_delay: int) -> float:
        """
        Calculate exponential backoff with jitter.

        Args:
            attempt: Current attempt number (0-indexed)
            max_delay: Maximum delay in seconds

        Returns:
            Delay in seconds
        """
        # Exponential backoff: 2^attempt + random jitter
        base_delay = 2 ** attempt
        jitter = random.uniform(0, base_delay * 0.1)
        delay = base_delay + jitter

        # Cap at max_delay
        return min(delay, max_delay)

    def get_request_count(self) -> int:
        """Get total number of requests made"""
        return self.request_count
