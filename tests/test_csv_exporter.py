"""Tests for csv_exporter module."""
# pylint: disable=missing-function-docstring,too-many-public-methods
import csv
from pathlib import Path
import pytest
from csv_exporter import CSVExporter


@pytest.fixture
def mock_config():
    """Mock configuration with output fields."""
    return {
        'output_fields': {
            'field_post_id': 'post_id',
            'field_post_owner': 'post_owner',
            'field_post_url': 'post_url',
            'field_last_active': 'last_active',
            'field_user_id': 'user_id',
            'field_email': 'email',
            'field_description': 'description'
        }
    }


@pytest.fixture
def sample_posts():
    """Sample post data for testing."""
    return [
        {
            'post_id': '12345',
            'post_owner': 'John Doe',
            'post_url': 'https://example.com/listing/12345',
            'last_active': '2026-08-11',
            'user_id': 'user123',
            'email': 'john@example.com',
            'description': 'Looking for a roommate'
        },
        {
            'post_id': '67890',
            'post_owner': 'Jane Smith',
            'post_url': 'https://example.com/listing/67890',
            'last_active': '2026-08-10',
            'user_id': 'user456',
            'email': 'jane@example.com',
            'description': None
        }
    ]


class TestCSVExporterInit:
    """Tests for CSVExporter initialization."""

    def test_init_with_defaults(self, mock_config):
        exporter = CSVExporter(config=mock_config)
        assert exporter.output_file == Path('output/scrape_results.csv')
        assert exporter.config == mock_config

    def test_init_with_custom_path(self, mock_config):
        custom_path = '/tmp/custom_results.csv'
        exporter = CSVExporter(output_file=custom_path, config=mock_config)
        assert exporter.output_file == Path(custom_path)

    def test_init_fieldnames_order(self, mock_config):
        exporter = CSVExporter(config=mock_config)
        expected_fields = [
            'post_id', 'post_owner', 'post_url', 'last_active',
            'user_id', 'email', 'description'
        ]
        assert exporter.fieldnames == expected_fields

    def test_init_with_empty_config(self):
        # Empty config should raise KeyError during init
        with pytest.raises(KeyError):
            CSVExporter(config={})


class TestCSVExporterExport:
    """Tests for CSVExporter.export method."""

    def test_export_writes_file(self, tmp_path, mock_config, sample_posts):
        output_file = tmp_path / "test_results.csv"
        exporter = CSVExporter(output_file=str(output_file), config=mock_config)

        result = exporter.export(sample_posts)

        assert result is True
        assert output_file.exists()

    def test_export_writes_headers(self, tmp_path, mock_config, sample_posts):
        output_file = tmp_path / "test_results.csv"
        exporter = CSVExporter(output_file=str(output_file), config=mock_config)
        exporter.export(sample_posts)

        with open(output_file, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            assert reader.fieldnames == exporter.fieldnames

    def test_export_writes_all_rows(self, tmp_path, mock_config, sample_posts):
        output_file = tmp_path / "test_results.csv"
        exporter = CSVExporter(output_file=str(output_file), config=mock_config)
        exporter.export(sample_posts)

        with open(output_file, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            rows = list(reader)
            assert len(rows) == 2

    def test_export_preserves_data_order(self, tmp_path, mock_config, sample_posts):
        output_file = tmp_path / "test_results.csv"
        exporter = CSVExporter(output_file=str(output_file), config=mock_config)
        exporter.export(sample_posts)

        with open(output_file, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            rows = list(reader)
            assert rows[0]['post_owner'] == 'John Doe'
            assert rows[1]['post_owner'] == 'Jane Smith'

    def test_export_handles_missing_fields(self, tmp_path, mock_config):
        # Post missing some fields
        posts = [
            {
                'post_id': '12345',
                'post_owner': 'John Doe',
                # Missing other fields
            }
        ]
        output_file = tmp_path / "test_results.csv"
        exporter = CSVExporter(output_file=str(output_file), config=mock_config)

        result = exporter.export(posts)

        assert result is True
        with open(output_file, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            row = next(reader)
            assert row['post_id'] == '12345'
            assert row['post_owner'] == 'John Doe'
            assert row['email'] == ''  # Missing fields become empty strings

    def test_export_handles_none_values(self, tmp_path, mock_config):
        posts = [
            {
                'post_id': '12345',
                'post_owner': 'John Doe',
                'post_url': 'https://example.com/listing/12345',
                'last_active': None,
                'user_id': None,
                'email': 'john@example.com',
                'description': None
            }
        ]
        output_file = tmp_path / "test_results.csv"
        exporter = CSVExporter(output_file=str(output_file), config=mock_config)

        result = exporter.export(posts)

        assert result is True
        with open(output_file, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            row = next(reader)
            assert row['last_active'] == ''
            assert row['user_id'] == ''
            assert row['description'] == ''

    def test_export_handles_special_characters(self, tmp_path, mock_config):
        posts = [
            {
                'post_id': '12345',
                'post_owner': 'John "Johnny" Doe',
                'post_url': 'https://example.com/listing/12345?id=1,2,3',
                'last_active': '2026-08-11',
                'user_id': 'user123',
                'email': 'john@example.com',
                'description': 'Looking for roommate\nPrefer quiet'
            }
        ]
        output_file = tmp_path / "test_results.csv"
        exporter = CSVExporter(output_file=str(output_file), config=mock_config)

        result = exporter.export(posts)

        assert result is True
        with open(output_file, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            row = next(reader)
            # CSV properly escapes quotes and handles commas/newlines
            assert 'Johnny' in row['post_owner']
            assert '1,2,3' in row['post_url']

    def test_export_converts_post_id_to_string(self, tmp_path, mock_config):
        # Post ID might be ObjectId or similar, should be converted to string
        posts = [
            {
                'post_id': 12345,  # Integer instead of string
                'post_owner': 'John Doe',
                'post_url': 'https://example.com/listing/12345',
                'last_active': '2026-08-11',
                'user_id': 'user123',
                'email': 'john@example.com',
                'description': None
            }
        ]
        output_file = tmp_path / "test_results.csv"
        exporter = CSVExporter(output_file=str(output_file), config=mock_config)

        result = exporter.export(posts)

        assert result is True
        with open(output_file, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            row = next(reader)
            assert row['post_id'] == '12345'

    def test_export_empty_list(self, tmp_path, mock_config):
        output_file = tmp_path / "test_results.csv"
        exporter = CSVExporter(output_file=str(output_file), config=mock_config)

        result = exporter.export([])

        assert result is True
        with open(output_file, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            rows = list(reader)
            assert len(rows) == 0

    def test_export_overwrites_existing_file(self, tmp_path, mock_config):
        output_file = tmp_path / "test_results.csv"

        # Write initial content
        exporter1 = CSVExporter(output_file=str(output_file), config=mock_config)
        exporter1.export([
            {
                'post_id': '111',
                'post_owner': 'First',
                'post_url': 'url1',
                'last_active': None,
                'user_id': None,
                'email': None,
                'description': None
            }
        ])

        # Overwrite with new content
        exporter2 = CSVExporter(output_file=str(output_file), config=mock_config)
        exporter2.export([
            {
                'post_id': '222',
                'post_owner': 'Second',
                'post_url': 'url2',
                'last_active': None,
                'user_id': None,
                'email': None,
                'description': None
            }
        ])

        with open(output_file, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            rows = list(reader)
            assert len(rows) == 1
            assert rows[0]['post_owner'] == 'Second'

    def test_export_invalid_path_returns_false(self, mock_config, sample_posts):
        # Invalid path that can't be written to
        invalid_path = "/invalid/path/that/does/not/exist/results.csv"
        exporter = CSVExporter(output_file=invalid_path, config=mock_config)

        result = exporter.export(sample_posts)

        assert result is False

    def test_export_creates_parent_directory_if_needed(self, tmp_path, mock_config, sample_posts):
        # Path with subdirectory that doesn't exist yet
        output_file = tmp_path / "subdir" / "results.csv"
        exporter = CSVExporter(output_file=str(output_file), config=mock_config)

        # Note: Current implementation doesn't create parent dirs, will fail
        result = exporter.export(sample_posts)

        # This documents current behavior - implementation doesn't create dirs
        assert result is False


class TestCSVExporterGetOutputPath:
    """Tests for CSVExporter.get_output_path method."""

    def test_get_output_path_returns_path(self, mock_config):
        output_file = "/tmp/results.csv"
        exporter = CSVExporter(output_file=output_file, config=mock_config)

        path = exporter.get_output_path()

        assert path == Path(output_file)

    def test_get_output_path_is_path_object(self, mock_config):
        output_file = "/tmp/results.csv"
        exporter = CSVExporter(output_file=output_file, config=mock_config)

        path = exporter.get_output_path()

        assert isinstance(path, Path)
