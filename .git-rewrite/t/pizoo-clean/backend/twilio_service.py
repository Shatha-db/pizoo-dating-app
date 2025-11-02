import os
from typing import Optional
from twilio.jwt.access_token import AccessToken
from twilio.jwt.access_token.grants import VoiceGrant, VideoGrant
from twilio.rest import Client

TWILIO_ACCOUNT_SID = os.getenv("TWILIO_ACCOUNT_SID")
TWILIO_API_KEY_SID = os.getenv("TWILIO_API_KEY_SID")
TWILIO_API_KEY_SECRET = os.getenv("TWILIO_API_KEY_SECRET")
TWILIO_AUTH_TOKEN = os.getenv("TWILIO_AUTH_TOKEN")
TWILIO_VOICE_APP_SID = os.getenv("TWILIO_VOICE_APPLICATION_SID")
TWILIO_FROM = os.getenv("TWILIO_FROM")
VERIFY_SERVICE_SID = os.getenv("TWILIO_VERIFY_SERVICE_SID")

def create_voice_token(identity: str) -> str:
    """Generate Twilio Voice access token for WebRTC calls"""
    token = AccessToken(
        TWILIO_ACCOUNT_SID,
        TWILIO_API_KEY_SID,
        TWILIO_API_KEY_SECRET,
        identity=identity,
        ttl=3600
    )
    grant = VoiceGrant(
        outgoing_application_sid=TWILIO_VOICE_APP_SID,
        incoming_allow=True
    )
    token.add_grant(grant)
    return token.to_jwt().decode()

def create_video_token(identity: str, room_name: str) -> str:
    """Generate Twilio Video access token for video calls"""
    token = AccessToken(
        TWILIO_ACCOUNT_SID,
        TWILIO_API_KEY_SID,
        TWILIO_API_KEY_SECRET,
        identity=identity,
        ttl=3600
    )
    grant = VideoGrant(room=room_name)
    token.add_grant(grant)
    return token.to_jwt().decode()

def send_sms(to: str, body: str) -> bool:
    """Send SMS via Twilio (or mock if credentials not configured)"""
    if not (TWILIO_ACCOUNT_SID and TWILIO_AUTH_TOKEN and TWILIO_FROM):
        print(f"[MOCK SMS] To: {to}, Message: {body}")
        return True
    
    try:
        client = Client(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)
        message = client.messages.create(
            to=to,
            from_=TWILIO_FROM,
            body=body
        )
        print(f"✅ SMS sent successfully: {message.sid}")
        return True
    except Exception as e:
        print(f"❌ Twilio SMS error: {e}")
        return False

def verify_start(phone: str, channel: str = "sms"):
    """Start Twilio Verify OTP verification"""
    if not VERIFY_SERVICE_SID:
        # Fallback to normal SMS OTP (already implemented)
        print("[MOCK VERIFY] Twilio Verify not configured, using fallback")
        return {"mock": True}
    
    try:
        client = Client(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)
        verification = client.verify.v2.services(VERIFY_SERVICE_SID).verifications.create(
            to=phone,
            channel=channel
        )
        print(f"✅ Twilio Verify started: {verification.status}")
        return {"status": verification.status}
    except Exception as e:
        print(f"❌ Twilio Verify start error: {e}")
        return {"mock": True, "error": str(e)}

def verify_check(phone: str, code: str):
    """Check Twilio Verify OTP code"""
    if not VERIFY_SERVICE_SID:
        print("[MOCK VERIFY] Twilio Verify not configured")
        return {"valid": False, "reason": "Verify not configured"}
    
    try:
        client = Client(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)
        verification_check = client.verify.v2.services(VERIFY_SERVICE_SID).verification_checks.create(
            to=phone,
            code=code
        )
        is_valid = verification_check.status == "approved"
        print(f"✅ Twilio Verify check: {verification_check.status}")
        return {"valid": is_valid, "status": verification_check.status}
    except Exception as e:
        print(f"❌ Twilio Verify check error: {e}")
        return {"valid": False, "reason": str(e)}
