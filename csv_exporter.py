"""CSV export functionality for scraped data."""
import csv
import logging
from pathlib import Path
from typing import List, Dict, Any


logger = logging.getLogger(__name__)


class CSVExporter:
    """Export scraped data to CSV format"""

    def __init__(self, output_file: str = 'output/scrape_results.csv',
                 config: Dict[str, Any] = None):
        """
        Initialize CSV exporter.

        Args:
            output_file: Path to output CSV file
            config: Configuration dict with output_fields section
        """
        self.output_file = Path(output_file)
        self.config = config or {}
        self.output_fields = self.config['output_fields']
        self.fieldnames = list(self.output_fields.values())

    def export(self, posts: List[Dict[str, Any]]) -> bool:
        """
        Export posts to CSV file.

        Args:
            posts: List of post dicts

        Returns:
            True if successful, False otherwise
        """
        try:
            with open(self.output_file, 'w', newline='', encoding='utf-8') as csvfile:
                writer = csv.DictWriter(csvfile, fieldnames=self.fieldnames)
                writer.writeheader()

                for post in posts:
                    row = {}
                    for field_key, field_name in self.output_fields.items():
                        # Handle ObjectId conversion for post_id
                        if field_key == 'field_post_id':
                            row[field_name] = str(post.get(field_name, ''))
                        else:
                            row[field_name] = post.get(field_name) or ''
                    writer.writerow(row)

            logger.info("Exported %d posts to %s", len(posts), self.output_file)
            return True

        except OSError as e:
            logger.error("Failed to export CSV: %s", e)
            return False

    def get_output_path(self) -> Path:
        """Get output file path"""
        return self.output_file
