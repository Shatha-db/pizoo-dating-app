import os
import requests

# Direct env values
TELNYX_API_KEY = '<REDACTED_TELNYX_KEY>'
TELNYX_API_VERSION = 'v2'

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
