"""TOR proxy management and connection handling."""
import logging
import socket
from typing import Optional

import requests

logger = logging.getLogger(__name__)


class TORManager:
    """Manage TOR SOCKS5 proxy connection and identity rotation"""

    def __init__(self, tor_host: str, tor_port: int, socks_version: int = 5):
        """Initialize TOR connection parameters"""
        self.tor_host = tor_host
        self.tor_port = tor_port
        self.socks_version = socks_version
        self.proxy_url = self._build_proxy_url()
        self.current_exit_ip = None
        self._verify_connection()

    def _build_proxy_url(self) -> str:
        """Build SOCKS proxy URL with remote DNS resolution"""
        # Use socks5h (h = hostname resolution through proxy) to prevent DNS leaks
        # socks5h prevents the application from doing local DNS resolution
        socks_type = f"socks{self.socks_version}h"
        return f"{socks_type}://{self.tor_host}:{self.tor_port}"

    def _verify_connection(self):
        """Verify TOR connection is accessible"""
        try:
            test_session = requests.Session()
            test_session.proxies = {
                'http': self.proxy_url,
                'https': self.proxy_url
            }

            # Test connection by fetching IP info
            response = test_session.get(
                'https://api.ipify.org?format=json',
                timeout=10
            )
            response.raise_for_status()
            self.current_exit_ip = response.json().get('ip')

            logger.info("TOR connected to %s:%d (SOCKS%d)", self.tor_host,
                        self.tor_port, self.socks_version)
            logger.info("TOR exit IP: %s", self.current_exit_ip)

        except socket.timeout as e:
            raise ConnectionError(
                "TOR SOCKS proxy timeout at %s:%d" % (self.tor_host, self.tor_port)
            ) from e
        except ConnectionRefusedError as e:
            raise ConnectionError(
                "TOR SOCKS proxy connection refused at %s:%d" %
                (self.tor_host, self.tor_port)
            ) from e
        except (OSError, requests.RequestException) as e:
            raise ConnectionError("Failed to verify TOR connection: %s" % e) from e

    def get_session(self) -> requests.Session:
        """Get a requests session configured with TOR proxy"""
        session = requests.Session()
        session.proxies = {
            'http': self.proxy_url,
            'https': self.proxy_url
        }
        session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })
        return session

    def get_current_exit_ip(self) -> Optional[str]:
        """Get current TOR exit IP"""
        return self.current_exit_ip

    def rotate_identity(self) -> bool:
        """
        Attempt to rotate TOR identity (requires control port access).
        Returns True if successful, False otherwise.
        """
        try:
            import stem.process
            from stem.connection import authenticate
            from stem.controller import Controller

            logger.debug("Attempting to rotate TOR identity...")

            # This is a placeholder for stem library integration
            # Actual implementation would require TOR control port setup
            logger.warning("TOR identity rotation not yet fully implemented")
            return False

        except ImportError:
            logger.debug("stem library not available for identity rotation")
            return False
        except Exception as e:
            logger.error(f"Failed to rotate TOR identity: {e}")
            return False
