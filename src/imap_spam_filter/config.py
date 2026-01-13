import logging
import os
from dataclasses import dataclass


@dataclass
class IMAPConfig:
    server: str
    port: int
    username: str
    password: str
    mailbox: str = "INBOX"
    use_ssl: bool = True
    spam_folder: str = "Junk"


@dataclass
class Config:
    imap: IMAPConfig
    gemini_api_key: str


def load_config() -> Config:
    """Load configuration from environment variables"""
    try:
        port = int(os.getenv("IMAP_PORT", "993"))
    except ValueError as e:
        logging.error(f"Invalid IMAP_PORT value: {e}, using default 993")
        port = 993

    return Config(
        imap=IMAPConfig(
            server=os.getenv("IMAP_SERVER", "imap.gmail.com"),
            port=port,
            username=os.getenv("IMAP_USERNAME", ""),
            password=os.getenv("IMAP_PASSWORD", ""),
            mailbox=os.getenv("IMAP_MAILBOX", "INBOX"),
            use_ssl=os.getenv("IMAP_SSL", "true").lower() == "true",
            spam_folder=os.getenv("SPAM_FOLDER", "Junk"),
        ),
        gemini_api_key=os.getenv("GEMINI_API_KEY", ""),
    )
