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
                logger.warning(f"Post {post_id}: Could not find body tag")
                return result

            expected_classes = self.target_config.get('selector_detail_body_class', 'mob version').split()
            body_classes = body.get('class', [])

            for expected_class in expected_classes:
                if expected_class not in body_classes:
                    logger.warning(f"Post {post_id}: Body class '{expected_class}' not found")

            # Find form
            form = soup.find('form', {
                'name': self.target_config.get('selector_detail_form_name')
            })

            if not form:
                logger.warning(f"Post {post_id}: Could not find form")
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
                        logger.warning(f"Post {post_id}: Malformed email: {email}")
                        self.malformed_emails.append(email)
                        self.malformed_email_count += 1

                        if self.malformed_email_count > self.config['validation'].get('malformed_email_threshold', 5):
                            raise RuntimeError(
                                f"Malformed email threshold exceeded: {self.malformed_email_count}"
                            )
                else:
                    result[email_key] = email

            # Extract description from detail page
            description = self._extract_description(soup, post_id)
            if description:
                result['description'] = description

        except RuntimeError:
            raise

        except Exception as e:
            logger.error(f"Post {post_id}: Error parsing detail page: {e}")

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
                logger.debug(f"Post {post_id}: Input field '{input_name}' not found")
                return None

            value = input_field.get('value', '').strip()
            return value if value else None

        except Exception as e:
            logger.debug(f"Post {post_id}: Error extracting input '{input_name}': {e}")
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
            required_classes = self.target_config.get('selector_description_container_class', '').split()
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

        except Exception as e:
            logger.debug(f"Post {post_id}: Error extracting description: {e}")
            return None
