"""Tests for spam_classifier module."""

from imap_spam_filter.spam_classifier import SpamClassifier


def test_spam_classifier_initialization():
    """Test SpamClassifier initialization."""
    classifier = SpamClassifier("test-api-key")
    assert classifier.client is not None


# TODO: Add tests for:
# - classify_email() method with mocked Gemini API
# - Response parsing for different probability levels
# - Error handling when API fails
# - Classification thresholds (<=30% LEGITIMATE, >=71% SPAM, else UNCERTAIN)
