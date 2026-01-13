"""Pytest configuration and shared fixtures."""

import pytest


@pytest.fixture
def sample_imap_config():
    """Sample IMAP configuration for testing."""
    from imap_spam_filter.config import IMAPConfig

    return IMAPConfig(
        server="imap.example.com",
        port=993,
        username="test@example.com",
        password="test-password",
        mailbox="INBOX",
        use_ssl=True,
        spam_folder="Junk",
    )


@pytest.fixture
def sample_config(sample_imap_config):
    """Sample full configuration for testing."""
    from imap_spam_filter.config import Config

    return Config(imap=sample_imap_config, gemini_api_key="test-api-key")


@pytest.fixture
def sample_email_message():
    """Sample email message for testing."""
    from imap_spam_filter.email_client import EmailMessage

    return EmailMessage(
        uid=1, subject="Test Subject", from_addr="sender@example.com", body="This is a test email body."
    )
