"""Main orchestrator for web scraping pipeline."""
# pylint: disable=invalid-name
import logging
import re
import sys
import time
from pathlib import Path
from bs4 import BeautifulSoup  # pylint: disable=import-error

from redacted.config_manager import ConfigManager  # pylint: disable=import-error
from tor_manager import TORManager
from api_client import APIClient
from item_parser import ItemParser, PaginationExtractor
from detail_parser import DetailParser
from csv_exporter import CSVExporter


class WebScraper:
    """Main orchestrator for web scraping operations"""

    def __init__(self, config_file: str = 'config.ini'):
        """
        Initialize web scraper.

        Args:
            config_file: Path to configuration file
        """
        self.output_dir = Path('output')
        self.output_dir.mkdir(exist_ok=True)

        self.config = ConfigManager(config_file)
        self.logger = None

        self.tor_manager = None
        self.api_client = None
        self.item_parser = None
        self.detail_parser = None
        self.csv_exporter = None

        self.all_posts = []
        self.start_time = None
        self.dynamic_cityid = None
        self.city_name = None

    def setup_logging(self, city_name: str = None, cityid: int = None):
        """Set up logging configuration"""
        date_str = time.strftime("%Y%m%d")
        if city_name and cityid:
            log_file = self.output_dir / f'scraper_{city_name}_{cityid}_{date_str}.log'
        else:
            log_file = self.output_dir / 'scraper.log'

        log_format = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'

        # Remove existing handlers to avoid duplicates
        root_logger = logging.getLogger()
        for handler in root_logger.handlers[:]:
            root_logger.removeHandler(handler)

        # File handler
        file_handler = logging.FileHandler(log_file, mode='a')
        file_handler.setLevel(logging.DEBUG)
        file_handler.setFormatter(logging.Formatter(log_format))

        # Console handler
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(logging.INFO)
        console_handler.setFormatter(logging.Formatter(log_format))

        # Root logger
        root_logger.setLevel(logging.DEBUG)
        root_logger.addHandler(file_handler)
        root_logger.addHandler(console_handler)

        self.logger = logging.getLogger(__name__)

    def run(self) -> bool:
        """
        Execute the full scraping pipeline.

        Returns:
            True if successful, False otherwise
        """
        self.start_time = time.time()

        try:
            # Phase 0: Setup (initializes logging)
            if not self._phase_0_setup():
                return False

            self.logger.info("=" * 60)
            self.logger.info("Web Scraper Started")
            self.logger.info("=" * 60)

            # Phase 1: List Scraping
            if not self._phase_1_list_scraping():
                return False

            # Phase 2: Detail Scraping
            if not self._phase_2_detail_scraping():
                return False

            # Phase 3: Export
            if not self._phase_3_export():
                return False

            self._print_summary()
            return True

        except (OSError, RuntimeError) as exc_error:
            if self.logger:
                self.logger.error("Scraper failed: %s", exc_error, exc_info=True)
            else:
                print("Scraper failed during initialization: %s" % e)
            return False

    def _extract_city_name_from_url(self) -> str:
        """Extract city name from initial URL using regex (no API or logging needed)"""
        try:
            initial_url = self.config.get('urls', 'initial_url')
            # Extract city name from URL (e.g., "city-columbus" -> "columbus")
            city_match = re.search(r'city-([a-z]+)', initial_url, re.IGNORECASE)
            return city_match.group(1) if city_match else "unknown"
        except (AttributeError, ValueError):
            return "unknown"

    def _extract_cityid_from_initial_url_silent(self) -> int:
        """Fetch initial URL and extract cityid (no logging, called before logger setup)"""
        try:
            initial_url = self.config.get('urls', 'initial_url')
            response = self.api_client.get_page(initial_url)
            if not response:
                return int(self.config.get('target_extraction', 'variable_cityid'))

            soup = BeautifulSoup(response, 'html.parser')
            cityid_input = soup.find('input', {
                'id': self.config.get('target_extraction', 'selector_cityid_input_id')
            })

            if cityid_input and cityid_input.get('value'):
                return int(cityid_input['value'])
            return int(self.config.get('target_extraction', 'variable_cityid'))

        except (AttributeError, ValueError):
            return int(self.config.get('target_extraction', 'variable_cityid'))

    def _extract_cityid_from_initial_url(self) -> int:
        """Fetch initial URL and extract cityid (requires logger, called after logging setup)"""
        try:
            initial_url = self.config.get('urls', 'initial_url')
            self.logger.debug("Fetching cityid from %s", initial_url)

            response = self.api_client.get_page(initial_url)
            if not response:
                self.logger.warning("Failed to fetch initial URL, using configured cityid")
                return int(self.config.get('target_extraction', 'variable_cityid'))

            soup = BeautifulSoup(response, 'html.parser')
            cityid_input = soup.find('input', {
                'id': self.config.get('target_extraction', 'selector_cityid_input_id')
            })

            if cityid_input and cityid_input.get('value'):
                cityid = int(cityid_input['value'])
                self.logger.info("Extracted cityid: %s", cityid)
                return cityid
            self.logger.warning("Could not find cityid in initial URL, using configured value")
            return int(self.config.get('target_extraction', 'variable_cityid'))

        except (AttributeError, ValueError) as exc_error:
            self.logger.error("Error extracting cityid: %s", exc_error)
            return int(self.config.get('target_extraction', 'variable_cityid'))

    def _phase_0_setup(self) -> bool:
        """Phase 0: Setup & Configuration"""
        try:
            # Extract city name from URL (no dependencies)
            self.city_name = self._extract_city_name_from_url()

            # Initialize TOR (before logging setup)
            if self.config.get('tor', 'use_tor'):
                self.tor_manager = TORManager(
                    tor_host=self.config.get('tor', 'tor_host'),
                    tor_port=self.config.get('tor', 'tor_port'),
                    socks_version=self.config.get('tor', 'tor_socks_version')
                )
                session = self.tor_manager.get_session()
            else:
                import requests  # pylint: disable=import-outside-toplevel
                session = requests.Session()
                session.headers.update({
                    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
                })

            # Initialize API client (before logging setup)
            self.api_client = APIClient(
                session=session,
                base_url=self.config.get('urls', 'base_url'),
                config=self.config.validated_config
            )

            # Extract cityid using API client (before logging setup)
            self.dynamic_cityid = self._extract_cityid_from_initial_url_silent()

            # Now setup logging with complete city info (single log file)
            self.setup_logging(self.city_name, self.dynamic_cityid)

            self.logger.info("\n[PHASE 0] Setup & Configuration")
            self.logger.info("-" * 60)

            self.config.log_config_status()

            # Log TOR status
            if self.config.get('tor', 'use_tor'):
                self.logger.info("TOR connection initialized")
            else:
                self.logger.warning("TOR is disabled - traffic NOT anonymized")

            # Fetch and log robots.txt for compliance documentation
            self._log_robots_txt()

            # Initialize parsers
            self.item_parser = ItemParser(
                base_url=self.config.get('urls', 'base_url'),
                config=self.config.validated_config
            )

            self.detail_parser = DetailParser(
                config=self.config.validated_config
            )

            # Initialize exporter with dynamic filename and output directory
            date_str = time.strftime("%Y%m%d")
            output_file = (
                self.output_dir /
                f'scrape_results_{self.city_name}_{self.dynamic_cityid}_{date_str}.csv'
            )
            self.csv_exporter = CSVExporter(
                output_file=str(output_file),
                config=self.config.validated_config
            )

            self.logger.info("Phase 0 complete: All components initialized")
            return True

        except (OSError, RuntimeError, AttributeError, ValueError) as exc_error:
            if self.logger:
                self.logger.error("Phase 0 failed: %s", exc_error)
            else:
                print("Phase 0 failed: %s" % e)
            return False

    def _log_robots_txt(self):
        """Fetch and log robots.txt content for compliance documentation"""
        try:
            base_url = self.config.get('urls', 'base_url')
            robots_url = f"{base_url}/robots.txt"
            robots_content = self.api_client.get_page(robots_url)

            if robots_content:
                self.logger.info("%s", "\n" + "=" * 60)
                self.logger.info("ROBOTS.TXT COMPLIANCE")
                self.logger.info("%s", "=" * 60)
                for line in robots_content.split('\n'):
                    self.logger.info(line)
                self.logger.info("=" * 60)
            else:
                self.logger.warning("Could not fetch robots.txt")

        except (OSError, AttributeError, ValueError) as exc_error:
            self.logger.debug("Error fetching robots.txt: %s", exc_error)

    def _phase_1_list_scraping(self) -> bool:
        """Phase 1: List Scraping (Pagination Loop)"""
        try:
            self.logger.info("\n[PHASE 1] List Scraping")
            self.logger.info("-" * 60)

            page_num = 0
            page_count = 0

            while True:
                page_count += 1

                # Check dev mode limit
                if self.config.get('development', 'dev_mode'):
                    max_pages = self.config.get('development', 'dev_mode_max_pages')
                    if page_count > max_pages:
                        self.logger.info(
                            "Dev mode limit reached. Stopping after page %d",
                            page_count - 1)
                        break

                # Build API request (convert numeric strings to integers)
                pagesize = int(
                    self.config.get('target_extraction', 'variable_pagesize')
                )
                # Use dynamically extracted cityid from initial URL, fallback to config if not available
                cityid = self.dynamic_cityid if self.dynamic_cityid else int(
                    self.config.get('target_extraction', 'variable_cityid')
                )
                # API uses 1-indexed pages (1, 2, 3...) not 0-indexed
                api_page = page_num + 1

                payload = {
                    self.config.get('target_extraction', 'variable_page_key'):
                        api_page,
                    self.config.get('target_extraction', 'variable_pagesize_key'):
                        pagesize,
                    self.config.get('target_extraction', 'variable_cityid_key'):
                        cityid,
                    self.config.get('target_extraction', 'variable_usercityid_key'):
                        0,
                    'userType': self.config.get(
                        'target_extraction', 'variable_usertype_value'),
                    'RoomtypeID': self.config.get(
                        'target_extraction', 'variable_roomtype_value'),
                    'Gender': self.config.get(
                        'target_extraction', 'variable_gender_value'),
                    'Furnishingtype': self.config.get(
                        'target_extraction', 'variable_furnishingtype_value'),
                }

                self.logger.debug("API payload: %s", payload)

                # Make API request
                response = self.api_client.post_json(
                    endpoint_path=self.config.get('target_extraction', 'api_endpoint_path'),
                    payload=payload
                )

                if not response:
                    self.logger.error("Failed to fetch page %s", page_num)
                    break

                # Extract response data
                response_data = response.get('d', [{}])[0] if response.get('d') else {}
                product_html = response_data.get(self.config.get(
                    'target_extraction', 'response_field_listings_html'), '')
                pagination_html = response_data.get(self.config.get(
                    'target_extraction', 'response_field_pagination_html'), '')

                if not product_html:
                    self.logger.info("No listings in page %s", page_num)
                    break

                # Parse listings
                items = self.item_parser.parse_items(product_html)
                self.all_posts.extend(items)

                self.logger.info("Page %d: %d items found", page_num, len(items))

                # Check for next page
                pagination_extractor = PaginationExtractor(
                    self.config.validated_config['target_extraction'])
                next_page_num = pagination_extractor.extract_next_page(pagination_html)

                if next_page_num is None:
                    self.logger.info("No more pages available")
                    break

                page_num = next_page_num

                # Rate limiting
                delay = self.config.get('scraping', 'request_delay')
                if delay > 0:
                    time.sleep(delay)

            self.logger.info("Phase 1 complete: %d total items found",
                             len(self.all_posts))
            return True

        except (OSError, RuntimeError, AttributeError, ValueError) as exc_error:
            self.logger.error("Phase 1 failed: %s", exc_error)
            return False

    def _phase_2_detail_scraping(self) -> bool:
        """Phase 2: Detail Scraping (Individual Pages)"""
        try:
            self.logger.info("\n[PHASE 2] Detail Scraping")
            self.logger.info("-" * 60)

            enriched_count = 0

            for idx, post in enumerate(self.all_posts, 1):
                try:
                    # Fetch detail page
                    html = self.api_client.get_page(post['post_url'])

                    if not html:
                        self.logger.warning("Post %d: Failed to fetch detail page",
                                           idx)
                        continue

                    # Parse detail page
                    detail_data = self.detail_parser.parse_detail_page(html, post['post_id'])

                    # Update post with extracted data
                    post['user_id'] = detail_data.get('user_id')
                    post['email'] = detail_data.get('email')
                    if 'description' in detail_data:
                        post['description'] = detail_data.get('description')

                    enriched_count += 1

                    if idx % 10 == 0:
                        self.logger.info("Processed %d/%d detail pages",
                                        idx, len(self.all_posts))

                    # Rate limiting
                    delay = self.config.get('scraping', 'request_delay')
                    if delay > 0:
                        time.sleep(delay)

                except (OSError, AttributeError, ValueError) as exc_error:
                    self.logger.error("Post %d: Error processing detail: %s",
                                     idx, exc_error)
                    continue

            self.logger.info("Phase 2 complete: %d posts enriched with user data",
                            enriched_count)
            return True

        except (OSError, RuntimeError, AttributeError, ValueError) as exc_error:
            self.logger.error("Phase 2 failed: %s", exc_error)
            return False

    def _phase_3_export(self) -> bool:
        """Phase 3: Export & Cleanup"""
        try:
            self.logger.info("\n[PHASE 3] Export & Cleanup")
            self.logger.info("-" * 60)

            # Export to CSV
            if not self.csv_exporter.export(self.all_posts):
                return False

            # Write malformed URLs
            malformed_urls = self.item_parser.get_malformed_urls()
            if malformed_urls:
                with open('malformed_urls.txt', 'w', encoding='utf-8') as f:
                    for url in malformed_urls:
                        f.write(url + '\n')
                self.logger.info(
                    "Wrote %d malformed URLs to malformed_urls.txt",
                    len(malformed_urls))

            # Write malformed emails
            malformed_emails = self.detail_parser.get_malformed_emails()
            if malformed_emails:
                with open('malformed_emails.txt', 'w', encoding='utf-8') as f:
                    for email in malformed_emails:
                        f.write(email + '\n')
                self.logger.info(
                    "Wrote %d malformed emails to malformed_emails.txt",
                    len(malformed_emails))

            self.logger.info("Phase 3 complete: All data exported")
            return True

        except (OSError, RuntimeError, AttributeError, ValueError) as exc_error:
            self.logger.error("Phase 3 failed: %s", exc_error)
            return False

    def _print_summary(self):
        """Print final summary"""
        elapsed_time = time.time() - self.start_time

        complete_count = sum(1 for p in self.all_posts if p.get('email') and p.get('user_id'))
        partial_count = len(self.all_posts) - complete_count

        self.logger.info("%s", "\n" + "=" * 60)
        self.logger.info("SCRAPING SUMMARY")
        self.logger.info("%s", "=" * 60)

        if self.config.get('development', 'dev_mode'):
            max_pages = self.config.get('development', 'dev_mode_max_pages')
            self.logger.info(
                "DEV MODE - Limited to %d pages", max_pages)

        self.logger.info("Total posts found: %s", len(self.all_posts))
        self.logger.info("Posts with complete data: %s", complete_count)
        self.logger.info("Posts with partial data: %s", partial_count)
        self.logger.info("Malformed URLs: %s", self.item_parser.get_malformed_url_count())
        self.logger.info("Malformed emails: %s", self.detail_parser.get_malformed_email_count())
        self.logger.info("Execution time: %.1fs", elapsed_time)
        self.logger.info("%s", "=" * 60)


if __name__ == '__main__':
    scraper = WebScraper(config_file='redacted/config.ini')
    completed = scraper.run()
    sys.exit(0 if completed else 1)
