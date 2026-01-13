#!/usr/bin/env python3

import logging
import os
import sys

# Suppress Google API logs before importing anything
os.environ["GRPC_VERBOSITY"] = "ERROR"
os.environ["GLOG_minloglevel"] = "2"

# Configure base logging first to catch all loggers
logging.basicConfig(level=logging.CRITICAL)
for name in ["models", "_client", "google", "google.generativeai", "google.ai.generativelanguage"]:
    logger = logging.getLogger(name)
    logger.setLevel(logging.CRITICAL)
    logger.disabled = True

from imap_spam_filter.email_client import EmailClient
from imap_spam_filter.imap_config_parser import parse_imap_config
from imap_spam_filter.spam_classifier import SpamClassifier


class GoogleAPIFilter(logging.Filter):
    def filter(self, record) -> bool:  # type: ignore[no-untyped-def]
        # Block specific Google API messages
        blocked_messages = [
            "AFC is enabled",
            "AFC remote call",
            "HTTP Request: POST https://generativelanguage.googleapis.com",
        ]
        return not any(msg in record.getMessage() for msg in blocked_messages)


def main(argv: list[str]) -> None:
    """Main spam filter application"""

    # Reconfigure logging for our application
    for handler in logging.root.handlers[:]:
        logging.root.removeHandler(handler)

    logging.basicConfig(
        format="%(asctime)s %(levelname)-8s [%(filename)s:%(lineno)d] %(message)s",
        level=logging.INFO,
        datefmt="%Y-%m-%d %H:%M:%S",
    )

    # Add the filter to all handlers
    api_filter = GoogleAPIFilter()
    for handler in logging.root.handlers:
        handler.addFilter(api_filter)

    # Suppress noisy third-party loggers
    for logger_name in [
        "google",
        "google.generativeai",
        "google.ai.generativelanguage",
        "models",
        "_client",
        "urllib3",
        "httpcore",
        "httpx",
    ]:
        logging.getLogger(logger_name).setLevel(logging.CRITICAL)
        logging.getLogger(logger_name).propagate = False

    # Parse configuration
    config, limit, list_folders_only = parse_imap_config(argv)

    logging.info(f"imap_server = {config.imap.server}")
    logging.info(f"imap_port = {config.imap.port}")
    logging.info(f"imap_username = {config.imap.username}")
    logging.info(f"imap_password.length = {len(config.imap.password)}")
    logging.info(f"imap_mailbox = {config.imap.mailbox}")
    logging.info(f"imap_ssl = {config.imap.use_ssl}")
    logging.info(f"gemini_api_key.length = {len(config.gemini_api_key)}")
    logging.info(f"limit = {limit}")

    logging.info(f"Connecting to {config.imap.server}:{config.imap.port}")
    logging.info(f"Username: {config.imap.username}")
    logging.info(f"Mailbox: {config.imap.mailbox}")
    logging.info("-" * 50)

    try:
        # Connect to email server
        with EmailClient(config.imap) as email_client:
            logging.info("Connected to IMAP server successfully!")

            if list_folders_only:
                # List folders and exit
                folders = email_client.list_folders()
                logging.info("Available folders:")
                for folder in folders:
                    logging.info(f"  - {folder}")
                return

            # Initialize spam classifier for normal operation
            classifier = SpamClassifier(config.gemini_api_key)

            # Fetch and process emails
            email_count = 0
            for email in email_client.fetch_emails(limit=limit):
                email_count += 1

                # Display email in human-readable format
                print(f"\n{'=' * 60}")
                print(f"Subject: {email.subject}")
                print(f"From: {email.from_addr}")
                print(f"{'=' * 60}")

                # Show email body preview (first 500 characters, preserve formatting)
                body_preview = email.body.strip()
                if len(body_preview) > 500:
                    body_preview = body_preview[:500] + "..."
                print(body_preview)
                print()

                # Classify the email
                classification, probability, reasoning = classifier.classify_email(email)

                # Display classification result with confidence
                if classification == "SPAM":
                    print(f"🚨 Classification: {classification} ({probability}%)")
                    print(f"Reasoning: {reasoning}")
                elif classification == "LEGITIMATE":
                    print(f"✅ Classification: {classification} ({probability}%)")
                    print(f"Reasoning: {reasoning}")
                elif classification == "UNCERTAIN":
                    print(f"⚠️ Classification: {classification} ({probability}%)")
                    print(f"Reasoning: {reasoning}")
                else:  # ERROR
                    print(f"❌ Classification: {classification}")
                    print(f"Error: {reasoning}")

                # Handle different classification types
                if classification == "SPAM":
                    while True:
                        response = (
                            input(f"\nMove this spam email to {config.imap.spam_folder} folder? (y/n): ")
                            .strip()
                            .lower()
                        )
                        if response in ["y", "yes"]:
                            try:
                                success = email_client.move_to_spam(email.uid, config.imap.spam_folder)
                                if success:
                                    print(f"✅ Email moved to {config.imap.spam_folder} folder")
                                else:
                                    print("❌ Failed to move email to spam folder")
                            except Exception as e:
                                print(f"❌ Error moving email to spam: {e}")
                            break
                        elif response in ["n", "no"]:
                            print("📥 Email left in inbox")
                            break
                        else:
                            print("Please enter 'y' for yes or 'n' for no.")

                elif classification == "UNCERTAIN":
                    while True:
                        response = (
                            input(f"\nThis email is uncertain ({probability}%). Is it spam? (y/n): ").strip().lower()
                        )
                        if response in ["y", "yes"]:
                            # User says it's spam, ask if they want to move it
                            while True:
                                move_response = (
                                    input(f"Move to {config.imap.spam_folder} folder? (y/n): ").strip().lower()
                                )
                                if move_response in ["y", "yes"]:
                                    try:
                                        success = email_client.move_to_spam(email.uid, config.imap.spam_folder)
                                        if success:
                                            print(f"✅ Email moved to {config.imap.spam_folder} folder")
                                        else:
                                            print("❌ Failed to move email to spam folder")
                                    except Exception as e:
                                        print(f"❌ Error moving email to spam: {e}")
                                    break
                                elif move_response in ["n", "no"]:
                                    print("📥 Email marked as spam but left in inbox")
                                    break
                                else:
                                    print("Please enter 'y' for yes or 'n' for no.")
                            break
                        elif response in ["n", "no"]:
                            print("✅ Email marked as legitimate and left in inbox")
                            break
                        else:
                            print("Please enter 'y' for yes or 'n' for no.")

                elif classification == "LEGITIMATE":
                    print("📥 Email left in inbox")

                elif classification == "ERROR":
                    print("⚠️ Could not classify email due to error")

            if email_count == 0:
                logging.info("No emails found in mailbox.")
            else:
                logging.info(f"\nProcessed {email_count} emails.")

    except Exception as e:
        logging.error(f"Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main(sys.argv[1:])
