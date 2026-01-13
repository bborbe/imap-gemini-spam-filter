"""Factory module for creating application components (composition root)."""

from imap_spam_filter.config import Config, IMAPConfig
from imap_spam_filter.email_client import EmailClient
from imap_spam_filter.imap_config_parser import parse_imap_config
from imap_spam_filter.spam_classifier import SpamClassifier


def create_email_client(config: IMAPConfig) -> EmailClient:
    """Create and return an EmailClient instance.

    Args:
        config: IMAP configuration

    Returns:
        Configured EmailClient instance
    """
    return EmailClient(config)


def create_spam_classifier(api_key: str) -> SpamClassifier:
    """Create and return a SpamClassifier instance.

    Args:
        api_key: Gemini API key

    Returns:
        Configured SpamClassifier instance
    """
    return SpamClassifier(api_key)


def create_config(argv: list[str], require_gemini_key: bool = True) -> tuple[Config, int, bool]:
    """Parse command-line arguments and create configuration.

    Args:
        argv: Command-line arguments
        require_gemini_key: Whether Gemini API key is required

    Returns:
        Tuple of (Config, limit, list_folders_only)
    """
    return parse_imap_config(argv, require_gemini_key)
