#!/usr/bin/env python3

import logging
import sys
from imap_config_parser import parse_imap_config
from email_client import EmailClient
from spam_classifier import SpamClassifier

def main(argv):
    """Main spam filter application"""

    logging.basicConfig(
        format='%(asctime)s %(levelname)-8s [%(filename)s:%(lineno)d] %(message)s',
        level=logging.INFO,
        datefmt='%Y-%m-%d %H:%M:%S'
    )

    # Parse configuration
    config, limit, list_folders_only = parse_imap_config(argv)

    logging.info(f'imap_server = {config.imap.server}')
    logging.info(f'imap_port = {config.imap.port}')
    logging.info(f'imap_username = {config.imap.username}')
    logging.info(f'imap_password.length = {len(config.imap.password)}')
    logging.info(f'imap_mailbox = {config.imap.mailbox}')
    logging.info(f'imap_ssl = {config.imap.use_ssl}')
    logging.info(f'gemini_api_key.length = {len(config.gemini_api_key)}')
    logging.info(f'limit = {limit}')

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

                logging.info(f"\nEmail #{email_count}:")
                logging.info(f"Subject: {email.subject}")
                logging.info(f"From: {email.from_addr}")

                # Classify the email
                logging.info("Analyzing...")
                classification = classifier.classify_email(email)

                logging.info(f"Classification: {classification}")

                # If classified as spam, ask user if they want to move it
                if "spam" in classification.lower():
                    while True:
                        response = input(f"Move this spam email to {config.imap.spam_folder} folder? (y/n): ").strip().lower()
                        if response in ['y', 'yes']:
                            try:
                                success = email_client.move_to_spam(email.uid, config.imap.spam_folder)
                                if success:
                                    logging.info(f"Email moved to {config.imap.spam_folder} folder")
                                else:
                                    logging.error("Failed to move email to spam folder")
                            except Exception as e:
                                logging.error(f"Error moving email to spam: {e}")
                            break
                        elif response in ['n', 'no']:
                            logging.info("Email left in inbox")
                            break
                        else:
                            print("Please enter 'y' for yes or 'n' for no.")

                logging.info("-" * 30)

            if email_count == 0:
                logging.info("No emails found in mailbox.")
            else:
                logging.info(f"\nProcessed {email_count} emails.")

    except Exception as e:
        logging.error(f"Error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main(sys.argv[1:])