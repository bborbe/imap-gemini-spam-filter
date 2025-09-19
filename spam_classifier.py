from google import genai
from email_client import EmailMessage

class SpamClassifier:
    def __init__(self, api_key: str):
        self.client = genai.Client(api_key=api_key)

    def classify_email(self, email: EmailMessage) -> str:
        """Classify an email as spam or not spam"""

        # Create the prompt with email content
        prompt = f"""
        Analyze the following email and determine if it's spam or legitimate.

        Subject: {email.subject}
        From: {email.from_addr}
        Body: {email.body[:1000]}...  # Limit body to first 1000 chars

        Consider these spam indicators:
        - Suspicious sender addresses
        - Urgent/aggressive language
        - Requests for personal information
        - Unusual offers or promotions
        - Poor grammar/spelling
        - Suspicious links or attachments

        Respond with only one word: "SPAM" or "LEGITIMATE"
        """

        try:
            response = self.client.models.generate_content(
                model="gemini-2.0-flash-exp",
                contents=prompt
            )

            result = response.text.strip().upper()
            return "SPAM" if "SPAM" in result else "LEGITIMATE"

        except Exception as e:
            print(f"Error classifying email: {e}")
            return "ERROR"