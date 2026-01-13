#!/usr/bin/env python3
"""CLI entry point for IMAP Spam Filter."""

import sys

from imap_spam_filter.spam_filter import main

if __name__ == "__main__":
    main(sys.argv[1:])
