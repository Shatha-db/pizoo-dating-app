"""
SMS Service for Pizoo
Supports Telnyx with Alphanumeric Sender ID, Twilio, and Mock modes
"""

import os
import random
import time
import hashlib
import hmac
import json
import urllib.request
import re

# Configuration
PROVIDER = os.getenv("SMS_PROVIDER", "mock")  # mock | twilio | telnyx
TWILIO_SID = os.getenv("TWILIO_ACCOUNT_SID")
TWILIO_TOKEN = os.getenv("TWILIO_AUTH_TOKEN")
TWILIO_FROM = os.getenv("TWILIO_FROM", "+10000000000")

TELNYX_API_KEY = os.getenv("TELNYX_API_KEY")
TELNYX_FROM = os.getenv("TELNYX_FROM")
ALPHA_SENDER = os.getenv("ALPHA_SENDER_ID", "PIZOO")[:11]  # Max 11 chars
ALPHA_ALLOWED = set([
    c.strip().upper() 
    for c in (os.getenv("ALPHA_ALLOWED_COUNTRIES", "").split(",") 
    if os.getenv("ALPHA_ALLOWED_COUNTRIES") else [])
])

OTP_TTL = int(os.getenv("OTP_TTL_SECONDS", "300"))  # 5 minutes
OTP_MAX = int(os.getenv("OTP_MAX_ATTEMPTS", "5"))

# E.164 phone format regex
E164 = re.compile(r"^\+([1-9]\d{1,14})$")


def _otp(n=6):
    """Generate n-digit OTP code"""
    return f"{random.randint(0, 10**n - 1):0{n}d}"


def _hash(code, phone):
    """Create secure hash of code + phone"""
    secret = (os.getenv("JWT_SECRET", "pizoo-secret") or "pizoo-secret").encode()
    return hmac.new(secret, f"{phone}-{code}".encode(), hashlib.sha256).hexdigest()


def _country_from_e164(phone: str) -> str:
    """
    Extract country code from E.164 phone number
    Returns ISO country code (e.g., 'AE', 'SA', 'US')
    """
    # Country code mapping (major countries)
    mapping = {
        # Middle East
        "971": "AE",  # UAE
        "966": "SA",  # Saudi Arabia
        "20": "EG",   # Egypt
        "974": "QA",  # Qatar
        "973": "BH",  # Bahrain
        "965": "KW",  # Kuwait
        "968": "OM",  # Oman
        "962": "JO",  # Jordan
        "961": "LB",  # Lebanon
        # Europe
        "44": "GB",   # UK
        "49": "DE",   # Germany
        "33": "FR",   # France
        "34": "ES",   # Spain
        "39": "IT",   # Italy
        "90": "TR",   # Turkey
        "351": "PT",  # Portugal
        "31": "NL",   # Netherlands
        "46": "SE",   # Sweden
        "47": "NO",   # Norway
        "45": "DK",   # Denmark
        "41": "CH",   # Switzerland
        # North America
        "1": "US",    # US/Canada (both use +1)
    }
    
    m = E164.match(phone)
    if not m:
        return ""
    
    digits = m.group(1)
    
    # Check for exact matches first (longest prefix first)
    for code, country in sorted(mapping.items(), key=lambda x: -len(x[0])):
        if digits.startswith(code):
            return country
    
    return ""


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


def _send_telnyx(phone, message, use_alpha=False):
    """
    Send SMS via Telnyx
    Args:
        phone: E.164 format phone number
        message: SMS text content
        use_alpha: Use alphanumeric sender ID instead of numeric
    """
    try:
        url = "https://api.telnyx.com/v2/messages"
        req = urllib.request.Request(url, method="POST")
        req.add_header("Authorization", f"Bearer {TELNYX_API_KEY}")
        req.add_header("Content-Type", "application/json")
        
        # Choose sender: alphanumeric or numeric
        sender = ALPHA_SENDER if use_alpha else TELNYX_FROM
        
        body = json.dumps({
            "from": sender,
            "to": phone,
            "text": message
        }).encode()
        
        with urllib.request.urlopen(req, body) as resp:
            success = 200 <= resp.getcode() < 300
            if success:
                sender_type = "alphanumeric" if use_alpha else "numeric"
                print(f"✅ Telnyx SMS sent to {phone} from {sender} ({sender_type})")
            return success
    except Exception as e:
        print(f"❌ Telnyx error: {e}")
        return False


def send_sms(phone: str, message: str) -> bool:
    """
    Send SMS via configured provider with intelligent sender selection
    
    For Telnyx:
    - Automatically uses alphanumeric sender ID in supported countries
    - Falls back to numeric sender if alphanumeric fails or not allowed
    - US/CA always use numeric sender (alphanumeric not supported)
    """
    if PROVIDER == "twilio":
        return _send_twilio(phone, message)
    
    elif PROVIDER == "telnyx":
        # Detect country from phone number
        country = _country_from_e164(phone)
        
        # Check if alphanumeric sender is allowed
        # US and CA don't support alphanumeric senders
        can_alpha = (
            country in ALPHA_ALLOWED 
            and country not in {"US", "CA"} 
            and ALPHA_SENDER 
            and len(ALPHA_SENDER) > 0
        )
        
        if can_alpha:
            # Try alphanumeric first
            ok = _send_telnyx(phone, message, use_alpha=True)
            
            if not ok:
                # Automatic fallback to numeric sender
                print(f"⚠️  Alphanumeric failed, falling back to numeric sender for {phone}")
                ok = _send_telnyx(phone, message, use_alpha=False)
            
            return ok
        else:
            # Use numeric sender directly
            return _send_telnyx(phone, message, use_alpha=False)
    
    else:
        # Mock mode
        print(f"[MOCK SMS] to={phone} msg={message}")
        return True


def generate_and_send(phone, lang="en"):
    """
    Generate OTP and send via SMS with language-aware message
    
    Args:
        phone: E.164 format phone number
        lang: Language code (en, ar, fr, es, etc.)
    
    Returns:
        dict with hash, expiry, and attempts left, or None if failed
    """
    if not phone or not phone.startswith("+") or len(phone) < 8:
        return None
    
    # Language-aware message templates
    templates = {
        "en": "Pizoo verification code: {}",
        "ar": "رمز التحقق من Pizoo: {}",
        "fr": "Code de vérification Pizoo: {}",
        "es": "Código de verificación Pizoo: {}",
        "de": "Pizoo Verifizierungscode: {}",
        "tr": "Pizoo doğrulama kodu: {}",
        "it": "Codice di verifica Pizoo: {}",
        "pt": "Código de verificação Pizoo: {}",
        "ru": "Код подтверждения Pizoo: {}"
    }
    
    # Get template for language, fallback to English
    template = templates.get(lang, templates["en"])
    
    code = _otp(6)
    message = template.format(code)
    
    ok = send_sms(phone, message)
    
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
