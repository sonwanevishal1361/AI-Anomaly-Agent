import os
import resend
from dotenv import load_dotenv

load_dotenv()

api_key = os.getenv("RESEND_API_KEY")
receiver_email = os.getenv("ALERT_EMAIL")

if not api_key:
    print("❌ RESEND_API_KEY not found in .env")
    exit()

if not receiver_email:
    print("❌ ALERT_EMAIL not found in .env")
    exit()

resend.api_key = api_key

try:
    response = resend.Emails.send(
        {
            "from": "onboarding@resend.dev",
            "to": [receiver_email],
            "subject": "🤖 AI Anomaly Agent - Test Email",
            "html": """
                <h2>🤖 AI Business Anomaly Agent</h2>

                <p>This is a test email from your
                AI Business Anomaly Agent.</p>

                <p>✅ Email system is working!</p>

                <p>You can now use this system to send
                anomaly alerts.</p>
            """
        }
    )

    print("✅ Email sent successfully!")
    print(response)

except Exception as e:

    print("❌ Email sending failed!")
    print(e)