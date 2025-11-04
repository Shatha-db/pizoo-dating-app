import os
import requests
import json

TELNYX_API_KEY = '<REDACTED_TELNYX_KEY>'
TELNYX_MESSAGING_PROFILE_ID = '<REDACTED_PROFILE_ID>'
TELNYX_API_VERSION = 'v2'

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
