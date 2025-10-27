"""
SMS Service for Pizoo
Supports Twilio, Telnyx, and Mock modes
"""

import os
import random
import time
import hashlib
import hmac
import json
import urllib.request

# Configuration
PROVIDER = os.getenv("SMS_PROVIDER", "mock")  # mock | twilio | telnyx
TWILIO_SID = os.getenv("TWILIO_ACCOUNT_SID")
TWILIO_TOKEN = os.getenv("TWILIO_AUTH_TOKEN")
TWILIO_FROM = os.getenv("TWILIO_FROM", "+10000000000")

TELNYX_API_KEY = os.getenv("TELNYX_API_KEY")
TELNYX_FROM = os.getenv("TELNYX_FROM")

OTP_TTL = int(os.getenv("OTP_TTL_SECONDS", "300"))  # 5 minutes
OTP_MAX = int(os.getenv("OTP_MAX_ATTEMPTS", "5"))


def _otp(n=6):
    """Generate n-digit OTP code"""
    return f"{random.randint(0, 10**n - 1):0{n}d}"


def _hash(code, phone):
    """Create secure hash of code + phone"""
    secret = (os.getenv("JWT_SECRET", "pizoo-secret") or "pizoo-secret").encode()
    return hmac.new(secret, f"{phone}-{code}".encode(), hashlib.sha256).hexdigest()


def _send_twilio(phone, message):
    """Send SMS via Twilio"""
    try:
        from twilio.rest import Client
        client = Client(TWILIO_SID, TWILIO_TOKEN)
        client.messages.create(
            from_=TWILIO_FROM,
            to=phone,
            body=message
        )
        print(f"✅ Twilio SMS sent to {phone}")
        return True
    except Exception as e:
        print(f"❌ Twilio error: {e}")
        return False


def _send_telnyx(phone, message):
    """Send SMS via Telnyx"""
    try:
        url = "https://api.telnyx.com/v2/messages"
        req = urllib.request.Request(url, method="POST")
        req.add_header("Authorization", f"Bearer {TELNYX_API_KEY}")
        req.add_header("Content-Type", "application/json")
        
        body = json.dumps({
            "from": TELNYX_FROM,
            "to": phone,
            "text": message
        }).encode()
        
        with urllib.request.urlopen(req, body) as resp:
            success = 200 <= resp.getcode() < 300
            if success:
                print(f"✅ Telnyx SMS sent to {phone}")
            return success
    except Exception as e:
        print(f"❌ Telnyx error: {e}")
        return False


def _send(phone, msg):
    """Send SMS via configured provider"""
    if PROVIDER == "twilio":
        return _send_twilio(phone, msg)
    elif PROVIDER == "telnyx":
        return _send_telnyx(phone, msg)
    else:
        # Mock mode
        print(f"[MOCK SMS] to={phone} msg={msg}")
        return True


def generate_and_send(phone):
    """
    Generate OTP and send via SMS
    Returns dict with hash, expiry, and attempts left
    """
    if not phone or not phone.startswith("+") or len(phone) < 8:
        return None
    
    code = _otp(6)
    ok = _send(phone, f"Pizoo verification code: {code}")
    
    if not ok:
        return None
    
    return {
        "hash": _hash(code, phone),
        "expires_at": int(time.time()) + OTP_TTL,
        "attempts_left": OTP_MAX
    }


def verify(phone, code, h):
    """Verify OTP code against hash"""
    return _hash(code, phone) == h


def send_sms(phone: str, message: str) -> bool:
    """
    Public function to send SMS
    Can be used by other modules
    """
    return _send(phone, message)
