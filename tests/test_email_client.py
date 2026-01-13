"""Tests for email_client module."""

from imap_spam_filter.email_client import EmailClient


def test_email_message_creation(sample_email_message):
    """Test EmailMessage creation."""
    assert sample_email_message.uid == 1
    assert sample_email_message.subject == "Test Subject"
    assert sample_email_message.from_addr == "sender@example.com"
    assert sample_email_message.body == "This is a test email body."


def test_email_client_initialization(sample_imap_config):
    """Test EmailClient initialization."""
    client = EmailClient(sample_imap_config)
    assert client.config == sample_imap_config
    assert client.client is None


# TODO: Add tests for:
# - connect() method
# - disconnect() method
# - fetch_emails() method
# - _decode_header() method
# - _extract_body() method
# - list_folders() method
# - move_to_spam() method
# - context manager (__enter__/__exit__)
