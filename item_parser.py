"""Parse items from API responses."""
import logging
import re
from typing import Dict, List, Any, Optional
from datetime import datetime
from bs4 import BeautifulSoup
from bson import ObjectId

from validators import URLValidator

logger = logging.getLogger(__name__)


class PaginationExtractor:
    """Extract pagination information from pagination HTML"""

    def __init__(self, config: Dict[str, str]):
        self.config = config

    def extract_next_page(self, pagination_html: str) -> Optional[int]:
        """
        Extract next page number from pagination HTML.

        Args:
            pagination_html: HTML string of pagination container

        Returns:
            Next page number or None if no more pages
        """
        try:
            if not pagination_html or not pagination_html.strip():
                logger.debug("Pagination HTML is empty")
                return None

            soup = BeautifulSoup(pagination_html, 'html.parser')

            # Find pagination ul
            pagination_ul = soup.find('ul', {
                'class': self.config.get('selector_pagination_ul_class', 'pagination')
            })

            if not pagination_ul:
                logger.debug("Pagination ul not found")
                return None

            # Find all li items
            all_li = pagination_ul.find_all('li')
            if not all_li:
                logger.debug("No pagination items found")
                return None

            # Find active page li
            active_li = pagination_ul.find('li', {'class': 'active'})
            if not active_li:
                logger.debug("No active page found")
                return None

            # Find next li after active (skip disabled items)
            found_active = False
            for li in all_li:
                if found_active:
                    # Check if this li is disabled
                    classes = li.get('class', [])
                    if 'disabled' in classes:
                        continue

                    # Get the link from this li
                    link = li.find('a')
                    if not link:
                        continue

                    # Extract page number from onclick
                    onclick = link.get('onclick', '')
                    if not onclick:
                        continue

                    # Extract page number from onclick handler
                    match = re.search(r'\w+\((\d+),', onclick)
                    if match:
                        page_num = int(match.group(1))
                        logger.debug(f"Extracted next page number: {page_num}")
                        return page_num

                    logger.debug(f"Could not extract page number from onclick: {onclick[:100]}")
                    return None

                if li == active_li:
                    found_active = True

            logger.debug("No next page found after active page")
            return None

        except Exception as e:
            logger.error(f"Error extracting next page: {e}")
            return None


class ItemParser:
    """Parse items from API response"""

    def __init__(self, base_url: str, config: Dict[str, Any]):
        """
        Initialize item parser.

        Args:
            base_url: Base URL for constructing item URLs
            config: Configuration with selectors and settings
        """
        self.base_url = base_url
        self.config = config
        self.target_config = config.get('target_extraction', {})
        self.malformed_urls = []
        self.malformed_url_count = 0

    def parse_items(self, product_html: str) -> List[Dict[str, Any]]:
        """
        Parse items from API response HTML.

        Args:
            product_html: HTML string containing items

        Returns:
            List of item dicts
        """
        items = []

        try:
            soup = BeautifulSoup(product_html, 'html.parser')

            # Find items container
            items_ul = soup.find('ul', {
                'id': self.target_config.get('selector_listings_ul_id'),
                'class': self.target_config.get('selector_listings_ul_class')
            })

            # If no container found, try parsing <li> elements directly (API may return bare list items)
            if items_ul:
                item_list = items_ul.find_all('li')
            else:
                logger.debug("No ul container found, parsing <li> elements directly")
                item_list = soup.find_all('li')

            if not item_list:
                logger.warning("Could not find items container or list items")
                return items

            # Parse each item
            for item in item_list:
                try:
                    item_data = self._parse_item(item)
                    if item_data:
                        items.append(item_data)
                except Exception as e:
                    logger.warning(f"Error parsing item: {e}")
                    continue

        except Exception as e:
            logger.error(f"Error parsing items HTML: {e}")

        logger.info(f"Parsed {len(items)} items")
        return items

    def _parse_item(self, item) -> Optional[Dict[str, Any]]:
        """
        Parse a single item.

        Args:
            item: BeautifulSoup element representing an item

        Returns:
            Dict with item data or None
        """
        # Extract heading
        heading = item.find('h3', {
            'id': self.target_config.get('selector_heading_id')
        })

        if not heading:
            return None

        # Extract link and href
        link = heading.find('a', {
            'class': self.target_config.get('selector_link_class')
        })

        if not link:
            return None

        href = link.get('href', '').strip()
        if not href:
            return None

        # Construct full URL
        post_url = f"{self.base_url}/{href}"

        # Validate URL
        if not URLValidator.validate(post_url):
            self.malformed_urls.append(post_url)
            self.malformed_url_count += 1
            logger.warning(f"Malformed URL: {post_url}")

            if self.malformed_url_count >= self.config['scraping'].get('malformed_url_threshold', 10):
                raise RuntimeError(
                    f"Malformed URL threshold exceeded: {self.malformed_url_count}"
                )
            return None

        # Extract post owner
        posting_div = item.find('div', {
            'class': self.target_config.get('selector_posting_div_class')
        })

        post_owner = None
        if posting_div:
            post_by_div = posting_div.find('div', {
                'class': self.target_config.get('selector_post_by_div_class')
            })

            if post_by_div:
                owner_span = post_by_div.find('span')
                if owner_span:
                    post_owner = owner_span.get_text(strip=True)

        # Extract last active date
        last_active = None
        last_active_div = item.find('div', {
            'class': self.target_config.get('selector_last_active_div_class')
        })
        if last_active_div:
            date_span = last_active_div.find(self.target_config.get('selector_date_span_tag'))
            if date_span:
                date_text = date_span.get_text(strip=True)
                last_active = self._parse_date(date_text)

        # Create item data with field names from config (required, no defaults)
        fields = self.config['output_fields']

        return {
            fields['field_post_id']: self._extract_post_id(post_url),
            fields['field_post_owner']: post_owner or 'Unknown',
            fields['field_post_url']: post_url,
            fields['field_last_active']: last_active,
            fields['field_user_id']: None,
            fields['field_email']: None,
            fields['field_description']: None
        }

    def _extract_post_id(self, post_url: str) -> Any:
        """
        Extract post ID from URL. Tries to extract HRid first, falls back to ObjectId.

        Args:
            post_url: Full URL of the post

        Returns:
            Integer ID from URL, or ObjectId if extraction fails
        """
        try:
            match = re.search(r'HRid-(\d+)', post_url)
            if match:
                return int(match.group(1))
        except (AttributeError, ValueError):
            pass

        return ObjectId()

    def _parse_date(self, date_text: str) -> Optional[str]:
        """
        Parse date from DD/MM/YYYY format to ISO 8601 (YYYY-MM-DD).

        Args:
            date_text: Date string in DD/MM/YYYY format

        Returns:
            ISO 8601 date string or None if parsing fails
        """
        if not date_text or not date_text.strip():
            return None

        try:
            parsed_date = datetime.strptime(date_text.strip(), '%d/%m/%Y')
            return parsed_date.strftime('%Y-%m-%d')
        except ValueError:
            logger.debug(f"Failed to parse date: {date_text}")
            return None

    def get_malformed_urls(self) -> List[str]:
        """Get list of malformed URLs"""
        return self.malformed_urls

    def get_malformed_url_count(self) -> int:
        """Get count of malformed URLs"""
        return self.malformed_url_count
