#!/usr/bin/env python3
"""
Test SMS sending functionality
"""
import os
import sys
from dotenv import load_dotenv

# Load environment variables
load_dotenv('/app/backend/.env')

# Try to import sms_service
sys.path.insert(0, '/app/backend')
try:
    from sms_service import send_sms, generate_and_send
except ImportError as e:
    print(f"❌ Import error: {e}")
    print("Trying alternative import...")
    try:
        from backend.sms_service import send_sms, generate_and_send
    except ImportError as e2:
        print(f"❌ Alternative import failed: {e2}")
        sys.exit(1)

def test_sms():
    """Test SMS sending"""
    test_phone = "+14648007410"
    
    print("=" * 60)
    print("📱 SMS Test - Pizoo Dating App")
    print("=" * 60)
    
    # Check environment variables
    print("\n🔍 Checking environment variables:")
    
    sms_provider = os.getenv("SMS_PROVIDER", "mock")
    print(f"   SMS_PROVIDER: {sms_provider}")
    
    twilio_sid = os.getenv("TWILIO_ACCOUNT_SID", "Not set")
    twilio_token = os.getenv("TWILIO_AUTH_TOKEN", "Not set")
    twilio_from = os.getenv("TWILIO_PHONE_FROM", "Not set")
    
    print(f"   TWILIO_ACCOUNT_SID: {twilio_sid[:10]}..." if len(twilio_sid) > 10 else f"   TWILIO_ACCOUNT_SID: {twilio_sid}")
    print(f"   TWILIO_AUTH_TOKEN: {'✅ Set' if twilio_token != 'Not set' and twilio_token != 'your_twilio_auth_token_here' else '❌ Not set'}")
    print(f"   TWILIO_PHONE_FROM: {twilio_from}")
    
    telnyx_key = os.getenv("TELNYX_API_KEY", "Not set")
    telnyx_from = os.getenv("TELNYX_FROM", "Not set")
    
    print(f"   TELNYX_API_KEY: {'✅ Set' if telnyx_key != 'Not set' else '❌ Not set'}")
    print(f"   TELNYX_FROM: {telnyx_from}")
    
    print("\n" + "=" * 60)
    
    # Test SMS sending
    if sms_provider == "mock":
        print("⚠️  SMS_PROVIDER is set to 'mock'")
        print("   SMS will be simulated, not actually sent")
        print("\n🧪 Testing mock SMS...")
        
        result = send_sms(test_phone, "Test message from Pizoo - This is a test!")
        
        if result:
            print("✅ Mock SMS 'sent' successfully!")
        else:
            print("❌ Mock SMS failed")
    else:
        print(f"📤 Attempting to send real SMS via {sms_provider}...")
        print(f"   To: {test_phone}")
        print(f"   Message: 'Your Pizoo verification code is: 123456 (TEST)'")
        
        result = send_sms(test_phone, "Your Pizoo verification code is: 123456 (TEST)")
        
        if result:
            print("\n✅ SMS sent successfully!")
            print(f"   Check phone {test_phone} for the message")
        else:
            print("\n❌ SMS sending failed")
            print("   Check the logs above for error details")
    
    print("=" * 60)
    
    # Test OTP generation
    print("\n🔐 Testing OTP generation with generate_and_send:")
    try:
        pack = generate_and_send(test_phone, "en")
        
        if pack:
            print("✅ OTP generation successful!")
            print(f"   Code expires in: {pack.get('expires_at', 0) - int(__import__('time').time())} seconds")
            print(f"   Attempts left: {pack.get('attempts_left', 0)}")
        else:
            print("❌ OTP generation failed (SMS provider might not be configured)")
    except Exception as e:
        print(f"❌ Error: {e}")
    
    print("=" * 60)

if __name__ == "__main__":
    try:
        test_sms()
    except Exception as e:
        print(f"\n❌ Test failed with error: {e}")
        import traceback
        traceback.print_exc()
