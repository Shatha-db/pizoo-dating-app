import os
import requests
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Get from environment variables (NEVER hardcode API keys!)
TELNYX_API_KEY = os.getenv('TELNYX_API_KEY')
TELNYX_API_VERSION = os.getenv('TELNYX_API_VERSION', 'v2')

if not TELNYX_API_KEY:
    print("❌ Error: TELNYX_API_KEY not found in environment variables")
    print("Please set TELNYX_API_KEY in your .env file")
    exit(1)

# Get phone numbers
url = f"https://api.telnyx.com/{TELNYX_API_VERSION}/phone_numbers"
headers = {
    'Authorization': f'Bearer {TELNYX_API_KEY}',
    'Content-Type': 'application/json'
}

print("📱 Fetching Telnyx Phone Numbers...")
response = requests.get(url, headers=headers, timeout=10)

if response.status_code == 200:
    data = response.json()
    numbers = data.get('data', [])
    print(f"\n✅ Found {len(numbers)} phone number(s):\n")
    for num in numbers:
        print(f"   Phone: {num.get('phone_number')}")
        print(f"   Status: {num.get('status')}")
        print(f"   Messaging Profile: {num.get('messaging_profile_id')}")
        print(f"   Type: {num.get('record_type')}")
        print("")
else:
    print(f"❌ Error: {response.status_code}")
    print(response.text[:500])
