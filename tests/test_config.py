"""Tests for config module."""

from imap_spam_filter.config import IMAPConfig


def test_imap_config_creation(sample_imap_config):
    """Test IMAP config creation."""
    assert sample_imap_config.server == "imap.example.com"
    assert sample_imap_config.port == 993
    assert sample_imap_config.username == "test@example.com"
    assert sample_imap_config.use_ssl is True


def test_config_creation(sample_config):
    """Test full config creation."""
    assert sample_config.imap.server == "imap.example.com"
    assert sample_config.gemini_api_key == "test-api-key"


def test_imap_config_defaults():
    """Test IMAP config default values."""
    config = IMAPConfig(server="test.server", port=993, username="user", password="pass")
    assert config.mailbox == "INBOX"
    assert config.use_ssl is True
    assert config.spam_folder == "Junk"
