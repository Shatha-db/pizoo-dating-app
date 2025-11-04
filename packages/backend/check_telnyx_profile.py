import os
import requests
import json
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Get from environment variables (NEVER hardcode API keys!)
TELNYX_API_KEY = os.getenv('TELNYX_API_KEY')
TELNYX_MESSAGING_PROFILE_ID = os.getenv('TELNYX_MESSAGING_PROFILE_ID')
TELNYX_API_VERSION = os.getenv('TELNYX_API_VERSION', 'v2')

if not TELNYX_API_KEY:
    print("❌ Error: TELNYX_API_KEY not found in environment variables")
    print("Please set TELNYX_API_KEY in your .env file")
    exit(1)

if not TELNYX_MESSAGING_PROFILE_ID:
    print("❌ Error: TELNYX_MESSAGING_PROFILE_ID not found in environment variables")
    print("Please set TELNYX_MESSAGING_PROFILE_ID in your .env file")
    exit(1)

url = f"https://api.telnyx.com/{TELNYX_API_VERSION}/messaging_profiles/{TELNYX_MESSAGING_PROFILE_ID}/phone_numbers"
headers = {
    'Authorization': f'Bearer {TELNYX_API_KEY}',
    'Content-Type': 'application/json'
}

print("📋 Fetching Phone Numbers for Messaging Profile...")
response = requests.get(url, headers=headers, timeout=10)

print(f"Status: {response.status_code}")
if response.status_code == 200:
    data = response.json()
    print(json.dumps(data, indent=2))
else:
    print(response.text[:500])
