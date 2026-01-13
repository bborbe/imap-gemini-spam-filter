import email
import logging
from collections.abc import Generator
from email.header import decode_header

from imapclient import IMAPClient

from imap_spam_filter.config import IMAPConfig


class EmailMessage:
    def __init__(self, uid: int, subject: str, from_addr: str, body: str):
        self.uid = uid
        self.subject = subject
        self.from_addr = from_addr
        self.body = body


class EmailClient:
    def __init__(self, config: IMAPConfig):
        self.config = config
        self.client: IMAPClient | None = None

    def connect(self) -> None:
        """Connect to IMAP server"""
        self.client = IMAPClient(self.config.server, port=self.config.port, ssl=self.config.use_ssl)
        self.client.login(self.config.username, self.config.password)
        self.client.select_folder(self.config.mailbox)

    def disconnect(self) -> None:
        """Disconnect from IMAP server"""
        if self.client:
            self.client.logout()

    def fetch_emails(self, limit: int = 10) -> Generator[EmailMessage, None, None]:
        """Fetch recent emails from the mailbox"""
        if not self.client:
            raise RuntimeError("Not connected to IMAP server")

        # Search for all emails (or recent ones)
        messages = self.client.search(["ALL"])

        # Get the most recent messages
        recent_messages = messages[-limit:] if len(messages) > limit else messages

        for uid in recent_messages:
            # Fetch the email data
            raw_message = self.client.fetch([uid], ["RFC822"])
            email_data = raw_message[uid][b"RFC822"]

            # Parse the email
            msg = email.message_from_bytes(email_data)

            # Extract subject and from address
            subject = self._decode_header(msg.get("Subject", "No Subject"))
            from_addr = self._decode_header(msg.get("From", "Unknown Sender"))

            # Extract body text
            body = self._extract_body(msg)

            yield EmailMessage(uid, subject, from_addr, body)

    def _decode_header(self, header_value: str) -> str:
        """Decode email header that might be encoded"""
        if not header_value:
            return ""

        decoded_parts = []
        for part, encoding in decode_header(header_value):
            if isinstance(part, bytes):
                if encoding:
                    decoded_parts.append(part.decode(encoding, errors="ignore"))
                else:
                    decoded_parts.append(part.decode("utf-8", errors="ignore"))
            else:
                decoded_parts.append(part)

        return "".join(decoded_parts)

    def _extract_body(self, msg: email.message.Message) -> str:
        """Extract text body from email message"""
        body = ""

        if msg.is_multipart():
            for part in msg.walk():
                if part.get_content_type() == "text/plain":
                    payload = part.get_payload(decode=True)
                    if isinstance(payload, bytes):
                        body += payload.decode("utf-8", errors="ignore")
        else:
            if msg.get_content_type() == "text/plain":
                payload = msg.get_payload(decode=True)
                if isinstance(payload, bytes):
                    body = payload.decode("utf-8", errors="ignore")

        return body.strip()

    def __enter__(self) -> "EmailClient":
        self.connect()
        return self

    def list_folders(self) -> list[str]:
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
            logging.warning(f"[EmailClient] MOVE command failed: {e}, attempting COPY+DELETE fallback")
            try:
                self.client.copy([uid], spam_folder)
                self.client.add_flags([uid], [r"\Deleted"])
                self.client.expunge()
                return True
            except Exception as copy_e:
                logging.error(f"[EmailClient] Both MOVE and COPY+DELETE failed. MOVE error: {e}, COPY error: {copy_e}")
                raise RuntimeError(
                    f"Failed to move email to spam folder: {e}, Copy fallback also failed: {copy_e}"
                ) from copy_e

    def __exit__(self, exc_type, exc_val, exc_tb) -> None:  # type: ignore[no-untyped-def]
        self.disconnect()
