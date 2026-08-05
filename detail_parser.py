"""Parse detail pages to extract user information."""
import logging
from typing import Dict, List, Any, Optional
from bs4 import BeautifulSoup

from validators import EmailValidator

logger = logging.getLogger(__name__)


class DetailParser:
    """Parse detail pages to extract user information"""

    def __init__(self, config: Dict[str, Any]):
        """
        Initialize detail parser.

        Args:
            config: Configuration with selectors and settings
        """
        self.config = config
        self.target_config = config.get('target_extraction', {})
        self.malformed_emails = []
        self.malformed_email_count = 0

    def parse_detail_page(self, html: str, post_id: str) -> Dict[str, Any]:
        """
        Parse detail page to extract user information.

        Args:
            html: HTML content of detail page
            post_id: Post ID for reference in logging

        Returns:
            Dict with extracted fields from config
        """
        fields = self.config['detail_parser_fields']

        user_id_key = fields['field_user_id']
        email_key = fields['field_email']

        result = {
            user_id_key: None,
            email_key: None
        }

        try:
            soup = BeautifulSoup(html, 'html.parser')

            # Verify body class
            body = soup.find('body')
            if not body:
                logger.warning("Post %s: Could not find body tag", post_id)
                return result

            expected_classes = self.target_config.get(
                'selector_detail_body_class', 'mob version').split()
            body_classes = body.get('class', [])

            for expected_class in expected_classes:
                if expected_class not in body_classes:
                    logger.warning("Post %s: Body class '%s' not found", post_id,
                                   expected_class)

            # Find form
            form = soup.find('form', {
                'name': self.target_config.get('selector_detail_form_name')
            })

            if not form:
                logger.warning("Post %s: Could not find form", post_id)
                return result

            # Extract input values
            result[user_id_key] = self._extract_input_value(
                form,
                self.target_config.get('selector_input_userid_attr'),
                post_id
            )

            email = self._extract_input_value(
                form,
                self.target_config.get('selector_input_email_attr'),
                post_id
            )

            if email:
                validate_email = self.config['validation'].get('validate_email', False)

                if validate_email:
                    if EmailValidator.validate(email):
                        result[email_key] = email
                    else:
                        logger.warning("Post %s: Malformed email: %s", post_id, email)
                        self.malformed_emails.append(email)
                        self.malformed_email_count += 1

                        threshold = self.config['validation'].get(
                            'malformed_email_threshold', 5)
                        if self.malformed_email_count > threshold:
                            raise RuntimeError(
                                "Malformed email threshold exceeded: %d" %
                                self.malformed_email_count
                            )
                else:
                    result[email_key] = email

            # Extract description from detail page
            description = self._extract_description(soup, post_id)
            if description:
                result['description'] = description

        except RuntimeError:
            raise

        except (AttributeError, ValueError) as e:
            logger.error("Post %s: Error parsing detail page: %s", post_id, e)

        return result

    def _extract_input_value(self, form, input_name: str, post_id: str) -> Optional[str]:
        """
        Extract value from hidden input field.

        Args:
            form: BeautifulSoup form element
            input_name: Input field name attribute
            post_id: Post ID for logging

        Returns:
            Input value or None
        """
        try:
            if not input_name:
                return None

            input_field = form.find('input', {
                'name': input_name
            })

            if not input_field:
                logger.debug("Post %s: Input field '%s' not found", post_id, input_name)
                return None

            value = input_field.get('value', '').strip()
            return value if value else None

        except (AttributeError, ValueError) as e:
            logger.debug("Post %s: Error extracting input '%s': %s", post_id,
                         input_name, e)
            return None

    def get_malformed_emails(self) -> List[str]:
        """Get list of malformed emails"""
        return self.malformed_emails

    def get_malformed_email_count(self) -> int:
        """Get count of malformed emails"""
        return self.malformed_email_count

    def _extract_description(self, soup, post_id: str) -> Optional[str]:
        """
        Extract description from detail page.

        Args:
            soup: BeautifulSoup parsed HTML
            post_id: Post ID for logging

        Returns:
            Description text truncated to max length, or None
        """
        try:
            required_classes = self.target_config.get(
                'selector_description_container_class', '').split()
            if not required_classes:
                return None

            description_div = soup.find('div', {
                'class': lambda x: x and all(c in x for c in required_classes)
            })

            if not description_div:
                return None

            description_span = description_div.find('span')
            if not description_span:
                return None

            description_text = description_span.get_text(strip=True)
            if not description_text:
                return None

            max_length = int(self.target_config.get('selector_description_max_length', 2000))
            return description_text[:max_length]

        except (AttributeError, ValueError) as e:
            logger.debug("Post %s: Error extracting description: %s", post_id, e)
            return None
