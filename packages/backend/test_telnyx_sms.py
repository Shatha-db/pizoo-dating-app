"""
Telnyx SMS Test Script
Tests the Telnyx integration by sending a test SMS
"""
import os
import sys
from dotenv import load_dotenv
import requests
from datetime import datetime

# Load environment variables
load_dotenv()

# Telnyx Configuration
TELNYX_API_KEY = os.getenv('TELNYX_API_KEY')
TELNYX_PUBLIC_KEY = os.getenv('TELNYX_PUBLIC_KEY')
TELNYX_MESSAGING_PROFILE_ID = os.getenv('TELNYX_MESSAGING_PROFILE_ID')
TELNYX_PHONE_NUMBER = os.getenv('TELNYX_PHONE_NUMBER')
TELNYX_API_VERSION = os.getenv('TELNYX_API_VERSION', 'v2')

def test_telnyx_connection():
    """Test Telnyx API connection"""
    print("=" * 60)
    print("🔐 TELNYX SMS INTEGRATION TEST")
    print("=" * 60)
    print(f"\n📅 Test Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
    
    # Verify environment variables
    print("1️⃣ Checking Environment Variables...")
    missing = []
    
    if not TELNYX_API_KEY or TELNYX_API_KEY.startswith('<'):
        missing.append('TELNYX_API_KEY')
    else:
        print(f"   ✅ TELNYX_API_KEY: {TELNYX_API_KEY[:20]}...")
    
    if not TELNYX_PUBLIC_KEY or TELNYX_PUBLIC_KEY.startswith('<'):
        missing.append('TELNYX_PUBLIC_KEY')
    else:
        print(f"   ✅ TELNYX_PUBLIC_KEY: {TELNYX_PUBLIC_KEY[:20]}...")
    
    if not TELNYX_MESSAGING_PROFILE_ID or TELNYX_MESSAGING_PROFILE_ID.startswith('<'):
        missing.append('TELNYX_MESSAGING_PROFILE_ID')
    else:
        print(f"   ✅ TELNYX_MESSAGING_PROFILE_ID: {TELNYX_MESSAGING_PROFILE_ID}")
    
    if not TELNYX_PHONE_NUMBER or TELNYX_PHONE_NUMBER.startswith('<'):
        missing.append('TELNYX_PHONE_NUMBER')
    else:
        print(f"   ✅ TELNYX_PHONE_NUMBER: {TELNYX_PHONE_NUMBER}")
    
    print(f"   ✅ TELNYX_API_VERSION: {TELNYX_API_VERSION}")
    
    if missing:
        print(f"\n   ❌ Missing environment variables: {', '.join(missing)}")
        return False
    
    print("\n2️⃣ Testing Telnyx API Connection...")
    
    # Test API with a GET request to messaging profiles
    try:
        url = f"https://api.telnyx.com/{TELNYX_API_VERSION}/messaging_profiles/{TELNYX_MESSAGING_PROFILE_ID}"
        headers = {
            'Authorization': f'Bearer {TELNYX_API_KEY}',
            'Content-Type': 'application/json'
        }
        
        print(f"   🔗 GET {url}")
        response = requests.get(url, headers=headers, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            profile = data.get('data', {})
            print(f"   ✅ API Connection Successful!")
            print(f"   📋 Messaging Profile: {profile.get('name', 'N/A')}")
            print(f"   🆔 ID: {profile.get('id', 'N/A')}")
            print(f"   ✅ Enabled: {profile.get('enabled', False)}")
            return True
        else:
            print(f"   ❌ API Error: {response.status_code}")
            print(f"   Response: {response.text[:200]}")
            return False
            
    except requests.exceptions.RequestException as e:
        print(f"   ❌ Connection Error: {str(e)}")
        return False
    except Exception as e:
        print(f"   ❌ Unexpected Error: {str(e)}")
        return False


def send_test_sms(to_number=None, test_message=None):
    """Send a test SMS using Telnyx"""
    
    if not to_number:
        to_number = TELNYX_PHONE_NUMBER  # Send to registered number
    
    if not test_message:
        test_message = f"🎉 Pizoo Test SMS - {datetime.now().strftime('%H:%M:%S')} - Telnyx integration is working!"
    
    print("\n3️⃣ Sending Test SMS...")
    print(f"   📱 From: {TELNYX_PHONE_NUMBER}")
    print(f"   📱 To: {to_number}")
    print(f"   💬 Message: {test_message[:50]}...")
    
    try:
        url = f"https://api.telnyx.com/{TELNYX_API_VERSION}/messages"
        headers = {
            'Authorization': f'Bearer {TELNYX_API_KEY}',
            'Content-Type': 'application/json'
        }
        
        payload = {
            'from': TELNYX_PHONE_NUMBER,
            'to': to_number,
            'text': test_message,
            'messaging_profile_id': TELNYX_MESSAGING_PROFILE_ID
        }
        
        print(f"\n   🔗 POST {url}")
        response = requests.post(url, json=payload, headers=headers, timeout=15)
        
        if response.status_code in [200, 201, 202]:
            data = response.json()
            message_data = data.get('data', {})
            
            print(f"\n   ✅ SMS Sent Successfully!")
            print(f"   📨 Message ID: {message_data.get('id', 'N/A')}")
            print(f"   📊 Status: {message_data.get('status', 'N/A')}")
            print(f"   🕐 Created: {message_data.get('created_at', 'N/A')}")
            print(f"   💰 Cost: {message_data.get('cost', {}).get('amount', 0)} {message_data.get('cost', {}).get('currency', 'USD')}")
            
            print(f"\n   🎯 Next Steps:")
            print(f"      1. Check your phone ({to_number}) for the SMS")
            print(f"      2. Verify delivery in Telnyx dashboard")
            print(f"      3. Check webhook for delivery receipt")
            
            return True
        else:
            print(f"\n   ❌ SMS Failed: {response.status_code}")
            print(f"   Response: {response.text[:500]}")
            
            # Parse error details
            try:
                error_data = response.json()
                errors = error_data.get('errors', [])
                for error in errors:
                    print(f"   ⚠️  Error: {error.get('title', 'Unknown')} - {error.get('detail', 'No details')}")
            except:
                pass
            
            return False
            
    except requests.exceptions.RequestException as e:
        print(f"\n   ❌ Request Error: {str(e)}")
        return False
    except Exception as e:
        print(f"\n   ❌ Unexpected Error: {str(e)}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """Main test function"""
    
    # Test 1: Check connection
    if not test_telnyx_connection():
        print("\n❌ Telnyx connection test failed. Please check your credentials.")
        sys.exit(1)
    
    # Test 2: Send SMS
    success = send_test_sms()
    
    print("\n" + "=" * 60)
    if success:
        print("✅ TELNYX INTEGRATION TEST PASSED")
    else:
        print("❌ TELNYX INTEGRATION TEST FAILED")
    print("=" * 60)
    
    return 0 if success else 1


if __name__ == '__main__':
    sys.exit(main())
