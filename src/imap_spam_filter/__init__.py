"""IMAP Spam Filter using Google Gemini AI."""

__version__ = "0.1.0"

__all__ = [
    "Config",
    "IMAPConfig",
    "EmailClient",
    "EmailMessage",
    "SpamClassifier",
]

from imap_spam_filter.config import Config, IMAPConfig
from imap_spam_filter.email_client import EmailClient, EmailMessage
from imap_spam_filter.spam_classifier import SpamClassifier
