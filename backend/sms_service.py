"""
SMS Service for Pizoo
Supports Twilio (production) and Mock (development)
"""

import os
import random
import time
import hashlib
import hmac

# Configuration
PROVIDER = os.getenv("SMS_PROVIDER", "mock")
SID = os.getenv("TWILIO_ACCOUNT_SID")
TOKEN = os.getenv("TWILIO_AUTH_TOKEN")
SFROM = os.getenv("TWILIO_FROM", "+10000000000")
OTP_TTL = int(os.getenv("OTP_TTL_SECONDS", "300"))  # 5 minutes
OTP_MAX = int(os.getenv("OTP_MAX_ATTEMPTS", "5"))


def _otp(n=6):
    """Generate n-digit OTP code"""
    return f"{random.randint(0, 10**n - 1):0{n}d}"


def _hash(code, phone):
    """Create secure hash of code + phone"""
    secret = (os.getenv("JWT_SECRET", "pizoo-secret") or "pizoo-secret").encode()
    return hmac.new(secret, f"{phone}-{code}".encode(), hashlib.sha256).hexdigest()


def _send(phone, msg):
    """Send SMS via configured provider"""
    if PROVIDER != "twilio":
        print(f"[MOCK SMS] to={phone} msg={msg}")
        return True
    
    try:
        from twilio.rest import Client
        client = Client(SID, TOKEN)
        client.messages.create(
            from_=SFROM,
            to=phone,
            body=msg
        )
        return True
    except Exception as e:
        print(f"Twilio error: {e}")
        return False


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
