import os
from dotenv import load_dotenv
from google import genai

# Load API key from .env
load_dotenv()

api_key = os.getenv("GEMINI_API_KEY")

# Check API key
if not api_key:
    print("❌ Gemini API key not found.")
    print("Make sure your .env file contains:")
    print("GEMINI_API_KEY=your_api_key")
    exit()

# Connect to Gemini
client = genai.Client(api_key=api_key)

# Send a test request
response = client.models.generate_content(
    model="gemini-3.6-flash",
    contents="Explain in one simple sentence what a business anomaly is."
)

# Display response
print("\n🤖 Gemini Response:")
print(response.text)