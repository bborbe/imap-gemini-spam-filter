#!/usr/bin/env python3

import getopt
import os
import sys
from config import IMAPConfig, Config

def parse_imap_config(argv, require_gemini_key=True):
    """Parse IMAP configuration from command line arguments and environment variables"""

    opts, args = getopt.getopt(argv, 'h', [
        'debug=',
        'imap-server=',
        'imap-port=',
        'imap-username=',
        'imap-password=',
        'imap-mailbox=',
        'imap-ssl=',
        'spam-folder=',
        'gemini-api-key=',
        'limit=',
        'list-folders',
    ])

    # Check if running in Docker (environment variables)
    # Otherwise use default values and require command line arguments
    in_docker = os.getenv('DOCKER_ENV') == 'true'

    if in_docker:
        # Load configuration from environment variables (Docker)
        imap_server: str = os.getenv('IMAP_SERVER', 'imap.gmail.com')
        imap_port: int = int(os.getenv('IMAP_PORT', '993'))
        imap_username: str = os.getenv('IMAP_USERNAME', '')
        imap_password: str = os.getenv('IMAP_PASSWORD', '')
        imap_mailbox: str = os.getenv('IMAP_MAILBOX', 'INBOX')
        imap_ssl: bool = os.getenv('IMAP_SSL', 'true').lower() == 'true'
        spam_folder: str = os.getenv('SPAM_FOLDER', 'Junk')
        gemini_api_key: str = os.getenv('GEMINI_API_KEY', '')
        limit: int = int(os.getenv('LIMIT', '10'))
    else:
        # Set default values (Makefile/CLI)
        imap_server: str = 'imap.gmail.com'
        imap_port: int = 993
        imap_username: str = ''
        imap_password: str = ''
        imap_mailbox: str = 'INBOX'
        imap_ssl: bool = True
        spam_folder: str = 'Junk'
        gemini_api_key: str = ''
        limit: int = 10

    list_folders_only: bool = False

    # Parse command line arguments
    for opt, arg in opts:
        if opt == '-h':
            print('Usage: --imap-server=server --imap-username=user --imap-password=pass --gemini-api-key=key')
            sys.exit()
        elif opt in ('--debug',):
            import logging
            logger = logging.getLogger()
            logger.setLevel(level=logging.DEBUG)
        elif opt in ('--imap-server',):
            imap_server = arg
        elif opt in ('--imap-port',):
            imap_port = int(arg)
        elif opt in ('--imap-username',):
            imap_username = arg
        elif opt in ('--imap-password',):
            imap_password = arg
        elif opt in ('--imap-mailbox',):
            imap_mailbox = arg
        elif opt in ('--imap-ssl',):
            imap_ssl = arg.lower() == 'true'
        elif opt in ('--spam-folder',):
            spam_folder = arg
        elif opt in ('--gemini-api-key',):
            gemini_api_key = arg
        elif opt in ('--limit',):
            limit = int(arg)
        elif opt in ('--list-folders',):
            list_folders_only = True

    # Validate required configuration
    if require_gemini_key and not list_folders_only and not gemini_api_key:
        print("Error: GEMINI_API_KEY is required")
        sys.exit(1)

    if not imap_username or not imap_password:
        print("Error: IMAP_USERNAME and IMAP_PASSWORD are required")
        sys.exit(1)

    # Create config from parsed arguments
    config = Config(
        imap=IMAPConfig(
            server=imap_server,
            port=imap_port,
            username=imap_username,
            password=imap_password,
            mailbox=imap_mailbox,
            use_ssl=imap_ssl,
            spam_folder=spam_folder
        ),
        gemini_api_key=gemini_api_key
    )

    return config, limit, list_folders_only