#!/usr/bin/env python3

import logging
import sys

from imap_spam_filter.email_client import EmailClient
from imap_spam_filter.imap_config_parser import parse_imap_config


def main(argv: list[str]) -> None:
    """List folders in IMAP mailbox"""

    logging.basicConfig(
        format="%(asctime)s %(levelname)-8s [%(filename)s:%(lineno)d] %(message)s",
        level=logging.INFO,
        datefmt="%Y-%m-%d %H:%M:%S",
    )

    # Parse configuration (don't require Gemini key for folder listing)
    config, limit, list_folders_only = parse_imap_config(argv, require_gemini_key=False)

    logging.info(f"imap_server = {config.imap.server}")
    logging.info(f"imap_port = {config.imap.port}")
    logging.info(f"imap_username = {config.imap.username}")
    logging.info(f"imap_password.length = {len(config.imap.password)}")
    logging.info(f"imap_ssl = {config.imap.use_ssl}")

    logging.info(f"Connecting to {config.imap.server}:{config.imap.port}")
    logging.info(f"Username: {config.imap.username}")
    logging.info("-" * 50)

    try:
        # Connect to email server and list folders
        with EmailClient(config.imap) as email_client:
            logging.info("Connected to IMAP server successfully!")

            folders = email_client.list_folders()
            logging.info("Available folders:")
            for folder in folders:
                logging.info(f"  - {folder}")

    except Exception as e:
        logging.error(f"Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main(sys.argv[1:])
