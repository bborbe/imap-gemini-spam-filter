import logging

from google import genai

from imap_spam_filter.email_client import EmailMessage


class SpamClassifier:
    def __init__(self, api_key: str):
        self.client = genai.Client(api_key=api_key)

    def classify_email(self, email: EmailMessage) -> tuple[str, int, str]:
        """Classify an email and return classification, confidence percentage, and reasoning"""

        # Create the prompt with email content
        prompt = f"""
        Analyze the following email and determine the probability it's spam (0-100%).

        Subject: {email.subject}
        From: {email.from_addr}
        Body: {email.body[:1000]}...

        Consider these spam indicators:
        - Suspicious sender addresses (unknown domains, typos in well-known brands)
        - Urgent/aggressive language ("Act now!", "Limited time!")
        - Requests for personal information or money
        - Unusual offers or promotions (too good to be true)
        - Poor grammar/spelling
        - Suspicious links or attachments
        - Unsolicited marketing

        However, also consider legitimate business emails may contain:
        - Professional financial/trading content
        - Marketing from established companies
        - Educational content with promotional elements
        - Newsletters from known services

        Respond in this exact format:
        PROBABILITY: [0-100]%
        REASONING: [Brief explanation of your decision]

        Examples:
        - FTMO trading emails: Usually legitimate educational content (20-30%)
        - Unknown senders with urgent language: High spam probability (80-90%)
        - Established companies with opt-in marketing: Low spam probability (10-20%)
        """

        try:
            response = self.client.models.generate_content(model="gemini-2.0-flash-exp", contents=prompt)

            if not response.text:
                return "ERROR", 0, "Empty response from Gemini API"

            result = response.text.strip()

            # Parse the response
            probability = 0
            reasoning = "No reasoning provided"

            for line in result.split("\n"):
                if line.startswith("PROBABILITY:"):
                    prob_str = line.replace("PROBABILITY:", "").strip().replace("%", "")
                    try:
                        probability = int(prob_str)
                    except ValueError:
                        probability = 50  # Default to uncertain
                elif line.startswith("REASONING:"):
                    reasoning = line.replace("REASONING:", "").strip()

            # Determine classification based on probability
            if probability <= 30:
                classification = "LEGITIMATE"
            elif probability >= 71:
                classification = "SPAM"
            else:
                classification = "UNCERTAIN"

            return classification, probability, reasoning

        except Exception as e:
            logging.error(f"[SpamClassifier] Error classifying email: {e}")
            return "ERROR", 0, str(e)
