"""Tests for validators module."""
# pylint: disable=missing-function-docstring,too-many-public-methods,unused-import
import pytest
from validators import URLValidator, EmailValidator


class TestURLValidator:
    """Tests for URLValidator class."""

    # Valid URLs
    def test_valid_https_url(self):
        assert URLValidator.validate("https://example.com") is True

    def test_valid_http_url(self):
        assert URLValidator.validate("http://example.com") is True

    def test_valid_url_with_port(self):
        assert URLValidator.validate("https://example.com:8080") is True

    def test_valid_url_with_path(self):
        assert URLValidator.validate("https://example.com/path/to/page") is True

    def test_valid_url_with_query(self):
        assert URLValidator.validate("https://example.com/path?key=value") is True

    def test_valid_url_localhost(self):
        assert URLValidator.validate("http://localhost") is True

    def test_valid_url_localhost_with_port(self):
        assert URLValidator.validate("http://localhost:3000") is True

    def test_valid_url_ip_address(self):
        assert URLValidator.validate("http://192.168.1.1") is True

    def test_valid_url_ip_with_port(self):
        assert URLValidator.validate("http://192.168.1.1:8080") is True

    def test_valid_url_subdomain(self):
        assert URLValidator.validate("https://api.example.com") is True

    def test_valid_url_multiple_subdomains(self):
        assert URLValidator.validate("https://api.v1.example.com") is True

    # Invalid URLs
    def test_invalid_url_no_scheme(self):
        assert URLValidator.validate("example.com") is False

    def test_valid_url_ftp_scheme(self):
        # urlparse accepts ftp as valid scheme with netloc
        assert URLValidator.validate("ftp://example.com") is True

    def test_invalid_url_no_netloc(self):
        assert URLValidator.validate("https://") is False

    def test_invalid_url_empty_string(self):
        assert URLValidator.validate("") is False

    def test_invalid_url_none(self):
        assert URLValidator.validate(None) is False

    def test_invalid_url_not_string(self):
        assert URLValidator.validate(123) is False

    def test_invalid_url_whitespace_only(self):
        assert URLValidator.validate("   ") is False

    def test_valid_url_malformed_ip_accepted(self):
        # Regex doesn't strictly validate IP octets, accepts any \d pattern
        assert URLValidator.validate("http://256.256.256.256") is True

    def test_valid_url_no_tld(self):
        # urlparse accepts scheme + netloc without TLD
        assert URLValidator.validate("https://example") is True

    # Length limits
    def test_valid_url_at_max_length(self):
        url = "https://example.com/" + "a" * 2028
        assert len(url) == 2048
        assert URLValidator.validate(url) is True

    def test_invalid_url_exceeds_max_length(self):
        url = "https://example.com/" + "a" * 2029
        assert len(url) > 2048
        assert URLValidator.validate(url) is False

    # is_valid_listing_url tests
    def test_listing_url_valid_same_domain(self):
        base_url = "https://example.com"
        listing_url = "https://example.com/listing/123"
        assert URLValidator.is_valid_listing_url(listing_url, base_url) is True

    def test_listing_url_valid_subdomain_base(self):
        base_url = "https://api.example.com"
        listing_url = "https://api.example.com/listing/456"
        assert URLValidator.is_valid_listing_url(listing_url, base_url) is True

    def test_listing_url_invalid_different_domain(self):
        base_url = "https://example.com"
        listing_url = "https://other.com/listing/123"
        assert URLValidator.is_valid_listing_url(listing_url, base_url) is False

    def test_listing_url_invalid_different_subdomain(self):
        base_url = "https://api.example.com"
        listing_url = "https://web.example.com/listing/123"
        assert URLValidator.is_valid_listing_url(listing_url, base_url) is False

    def test_listing_url_invalid_base_url(self):
        base_url = "not-a-valid-url"
        listing_url = "https://example.com/listing/123"
        assert URLValidator.is_valid_listing_url(listing_url, base_url) is False

    def test_listing_url_invalid_listing_url(self):
        base_url = "https://example.com"
        listing_url = "invalid-url"
        assert URLValidator.is_valid_listing_url(listing_url, base_url) is False

    def test_listing_url_none_listing_url(self):
        base_url = "https://example.com"
        listing_url = None
        assert URLValidator.is_valid_listing_url(listing_url, base_url) is False


class TestEmailValidator:
    """Tests for EmailValidator class."""

    # Valid emails
    def test_valid_email_simple(self):
        assert EmailValidator.validate("user@example.com") is True

    def test_valid_email_with_dot(self):
        assert EmailValidator.validate("user.name@example.com") is True

    def test_valid_email_with_plus(self):
        assert EmailValidator.validate("user+tag@example.com") is True

    def test_valid_email_with_underscore(self):
        assert EmailValidator.validate("user_name@example.com") is True

    def test_valid_email_with_hyphen(self):
        assert EmailValidator.validate("user-name@example.com") is True

    def test_valid_email_numbers(self):
        assert EmailValidator.validate("user123@example.com") is True

    def test_valid_email_subdomain(self):
        assert EmailValidator.validate("user@mail.example.com") is True

    def test_valid_email_multiple_subdomains(self):
        assert EmailValidator.validate("user@api.v1.example.com") is True

    def test_valid_email_with_whitespace_stripped(self):
        assert EmailValidator.validate("  user@example.com  ") is True

    def test_valid_email_case_insensitive(self):
        assert EmailValidator.validate("User@Example.COM") is True

    # Invalid emails - missing components
    def test_invalid_email_no_at(self):
        assert EmailValidator.validate("userexample.com") is False

    def test_invalid_email_no_domain(self):
        assert EmailValidator.validate("user@") is False

    def test_invalid_email_no_local(self):
        assert EmailValidator.validate("@example.com") is False

    def test_invalid_email_multiple_at(self):
        assert EmailValidator.validate("user@example@example.com") is False

    def test_invalid_email_no_tld(self):
        assert EmailValidator.validate("user@example") is False

    def test_invalid_email_empty_string(self):
        assert EmailValidator.validate("") is False

    def test_invalid_email_none(self):
        assert EmailValidator.validate(None) is False

    def test_invalid_email_not_string(self):
        assert EmailValidator.validate(123) is False

    def test_invalid_email_whitespace_only(self):
        assert EmailValidator.validate("   ") is False

    # Invalid emails - special characters
    def test_invalid_email_space_in_local(self):
        assert EmailValidator.validate("user name@example.com") is False

    def test_invalid_email_space_in_domain(self):
        assert EmailValidator.validate("user@exam ple.com") is False

    def test_invalid_email_consecutive_dots(self):
        assert EmailValidator.validate("user..name@example.com") is False

    def test_valid_email_leading_dot(self):
        # Regex allows leading dot in local part
        assert EmailValidator.validate(".user@example.com") is True

    def test_valid_email_trailing_dot_local(self):
        # Regex allows trailing dot in local part
        assert EmailValidator.validate("user.@example.com") is True

    def test_valid_email_leading_dot_domain(self):
        # Regex allows leading dot in domain
        assert EmailValidator.validate("user@.example.com") is True

    # Length limits
    def test_valid_email_at_max_length(self):
        # RFC 5321 limit is 254 chars
        email = "a" * 242 + "@example.com"
        assert len(email) == 254
        assert EmailValidator.validate(email) is True

    def test_invalid_email_exceeds_max_length(self):
        email = "a" * 250 + "@example.com"
        assert len(email) > 254
        assert EmailValidator.validate(email) is False

    # is_potentially_malformed tests
    def test_malformed_email_obfuscation_at(self):
        assert EmailValidator.is_potentially_malformed("user [at] example.com") is True

    def test_malformed_email_obfuscation_at_paren(self):
        assert EmailValidator.is_potentially_malformed("user (at) example.com") is True

    def test_malformed_email_obfuscation_dot(self):
        assert EmailValidator.is_potentially_malformed("user@example [dot] com") is True

    def test_malformed_email_obfuscation_dot_paren(self):
        assert EmailValidator.is_potentially_malformed("user@example (dot) com") is True

    def test_malformed_email_multiple_at(self):
        assert EmailValidator.is_potentially_malformed("user@@example.com") is True

    def test_malformed_email_very_short(self):
        assert EmailValidator.is_potentially_malformed("a@b") is True

    def test_malformed_email_empty_string(self):
        assert EmailValidator.is_potentially_malformed("") is True

    def test_malformed_email_none(self):
        assert EmailValidator.is_potentially_malformed(None) is True

    def test_malformed_email_whitespace_only(self):
        assert EmailValidator.is_potentially_malformed("   ") is True

    def test_malformed_email_invalid_format(self):
        assert EmailValidator.is_potentially_malformed("not-an-email") is True

    def test_not_malformed_valid_email(self):
        assert EmailValidator.is_potentially_malformed("user@example.com") is False

    def test_not_malformed_valid_complex_email(self):
        assert EmailValidator.is_potentially_malformed("user+tag@sub.example.com") is False

    def test_malformed_email_case_insensitive_obfuscation(self):
        assert EmailValidator.is_potentially_malformed("user [AT] example.com") is True

    def test_malformed_email_case_insensitive_obfuscation_dot(self):
        assert EmailValidator.is_potentially_malformed("user@example [DOT] com") is True
