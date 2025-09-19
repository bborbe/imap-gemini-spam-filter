import email
from typing import List, Generator
from imapclient import IMAPClient
from config import IMAPConfig

class EmailMessage:
    def __init__(self, uid: int, subject: str, from_addr: str, body: str):
        self.uid = uid
        self.subject = subject
        self.from_addr = from_addr
        self.body = body

class EmailClient:
    def __init__(self, config: IMAPConfig):
        self.config = config
        self.client = None

    def connect(self):
        """Connect to IMAP server"""
        self.client = IMAPClient(self.config.server, port=self.config.port, ssl=self.config.use_ssl)
        self.client.login(self.config.username, self.config.password)
        self.client.select_folder(self.config.mailbox)

    def disconnect(self):
        """Disconnect from IMAP server"""
        if self.client:
            self.client.logout()

    def fetch_emails(self, limit: int = 10) -> Generator[EmailMessage, None, None]:
        """Fetch recent emails from the mailbox"""
        if not self.client:
            raise RuntimeError("Not connected to IMAP server")

        # Search for all emails (or recent ones)
        messages = self.client.search(['ALL'])

        # Get the most recent messages
        recent_messages = messages[-limit:] if len(messages) > limit else messages

        for uid in recent_messages:
            # Fetch the email data
            raw_message = self.client.fetch([uid], ['RFC822'])
            email_data = raw_message[uid][b'RFC822']

            # Parse the email
            msg = email.message_from_bytes(email_data)

            # Extract subject and from address
            subject = msg.get('Subject', 'No Subject')
            from_addr = msg.get('From', 'Unknown Sender')

            # Extract body text
            body = self._extract_body(msg)

            yield EmailMessage(uid, subject, from_addr, body)

    def _extract_body(self, msg) -> str:
        """Extract text body from email message"""
        body = ""

        if msg.is_multipart():
            for part in msg.walk():
                if part.get_content_type() == "text/plain":
                    body += part.get_payload(decode=True).decode('utf-8', errors='ignore')
        else:
            if msg.get_content_type() == "text/plain":
                body = msg.get_payload(decode=True).decode('utf-8', errors='ignore')

        return body.strip()

    def __enter__(self):
        self.connect()
        return self

    def list_folders(self) -> List[str]:
        """List all available folders on the IMAP server"""
        if not self.client:
            raise RuntimeError("Not connected to IMAP server")

        folders = self.client.list_folders()
        return [folder[-1] for folder in folders]

    def move_to_spam(self, uid: int, spam_folder: str) -> bool:
        """Move an email to the spam folder"""
        if not self.client:
            raise RuntimeError("Not connected to IMAP server")

        try:
            # Try to move the email to spam folder
            self.client.move([uid], spam_folder)
            return True
        except Exception as e:
            # If move fails, try copy and mark as deleted
            try:
                self.client.copy([uid], spam_folder)
                self.client.add_flags([uid], [r'\Deleted'])
                self.client.expunge()
                return True
            except Exception as copy_e:
                raise RuntimeError(f"Failed to move email to spam folder: {e}, Copy fallback also failed: {copy_e}")

        return False

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.disconnect()