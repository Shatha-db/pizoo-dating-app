from fastapi import FastAPI, APIRouter, HTTPException, Depends, status, WebSocket, WebSocketDisconnect, File, UploadFile, Request, Form, BackgroundTasks
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi.responses import PlainTextResponse, JSONResponse
from dotenv import load_dotenv
from starlette.middleware.cors import CORSMiddleware
from motor.motor_asyncio import AsyncIOMotorClient
import os
import logging
import re
import time
from pathlib import Path
from pydantic import BaseModel, Field, ConfigDict, EmailStr, field_validator
from typing import List, Optional, Dict
import uuid
import json
from datetime import datetime, timezone, timedelta
from passlib.context import CryptContext
from jose import JWTError, jwt
from image_service import ImageUploadService
from auth_service import AuthService
from sms_service import generate_and_send, verify as verify_otp
from twilio_service import create_voice_token, create_video_token, send_sms, verify_start, verify_check
from twilio.twiml.voice_response import VoiceResponse, Dial
from bson import ObjectId
import sys

# Configure logging at the very start
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Startup logging
logger.info("=" * 70)
logger.info("🚀 PIZOO DATING APP - STARTING")
logger.info("=" * 70)
logger.info(f"Python version: {sys.version}")
logger.info(f"Working directory: {os.getcwd()}")
logger.info(f"MONGO_URL present: {'MONGO_URL' in os.environ or 'MONGODB_URI' in os.environ}")
logger.info(f"DB_NAME present: {'DB_NAME' in os.environ or 'MONGODB_DB_NAME' in os.environ}")
logger.info("=" * 70)

# Helper function to convert MongoDB documents to JSON-safe format
def serialize_mongo_doc(doc):
    """Convert MongoDB document to JSON-safe format"""
    if doc is None:
        return None
    if isinstance(doc, list):
        return [serialize_mongo_doc(item) for item in doc]
    if isinstance(doc, dict):
        return {key: serialize_mongo_doc(value) for key, value in doc.items()}
    if isinstance(doc, ObjectId):
        return str(doc)
    if isinstance(doc, datetime):
        return doc.isoformat()
    return doc

import httpx

ROOT_DIR = Path(__file__).parent
load_dotenv(ROOT_DIR / '.env')

# Import LiveKitService AFTER loading .env
from livekit_service import LiveKitService, LIVEKIT_URL as LK_URL
logging.info(f"✅ LiveKit URL loaded: {LK_URL}")

# Initialize Sentry for error tracking
try:
    import sentry_sdk
    from sentry_sdk.integrations.fastapi import FastApiIntegration
    
    sentry_dsn = os.getenv("SENTRY_DSN_BACKEND") or os.getenv("SENTRY_DSN")
    if sentry_dsn:
        sentry_sdk.init(
            dsn=sentry_dsn,
            traces_sample_rate=float(os.getenv("SENTRY_TRACES_SAMPLE", "0.2")),
            environment=os.getenv("ENVIRONMENT", "production"),
            integrations=[FastApiIntegration()],
            send_default_pii=True,  # Include request headers, IP, user data
        )
        logging.info("✅ Sentry initialized for backend")
        logging.info(f"   DSN: {sentry_dsn[:50]}...")
        logging.info(f"   Environment: {os.getenv('ENVIRONMENT', 'production')}")
        logging.info(f"   PII Tracking: Enabled")
    else:
        logging.warning("⚠️ Sentry DSN not configured")
except ImportError:
    logging.warning("⚠️ Sentry SDK not installed. Run: pip install sentry-sdk[fastapi]")
except Exception as e:
    logging.error(f"❌ Failed to initialize Sentry: {e}")

# MongoDB connection with error handling
try:
    mongo_url = os.environ.get('MONGO_URL') or os.environ.get('MONGODB_URI')
    if not mongo_url:
        raise ValueError("MONGO_URL or MONGODB_URI environment variable is required")
    
    client = AsyncIOMotorClient(
        mongo_url,
        serverSelectionTimeoutMS=5000,  # 5 second timeout
        connectTimeoutMS=10000,  # 10 second connection timeout
        socketTimeoutMS=10000,   # 10 second socket timeout
    )
    
    db_name = os.environ.get('DB_NAME') or os.environ.get('MONGODB_DB_NAME', 'pizoo_database')
    db = client[db_name]
    
    logging.info(f"✅ MongoDB client initialized with database: {db_name}")
except Exception as e:
    logging.error(f"❌ Failed to initialize MongoDB client: {e}")
    # Create a dummy client so the app can still start
    # Health checks will report the database as unavailable
    client = None
    db = None

# WebSocket Connection Manager
class ConnectionManager:
    def __init__(self):
        self.active_connections: Dict[str, WebSocket] = {}
        self.user_status: Dict[str, dict] = {}
    
    async def connect(self, user_id: str, websocket: WebSocket):
        await websocket.accept()
        self.active_connections[user_id] = websocket
        self.user_status[user_id] = {
            'online': True,
            'last_seen': datetime.now(timezone.utc).isoformat()
        }
        # Broadcast user online status
        await self.broadcast_status(user_id, True)
    
    def disconnect(self, user_id: str):
        if user_id in self.active_connections:
            del self.active_connections[user_id]
        self.user_status[user_id] = {
            'online': False,
            'last_seen': datetime.now(timezone.utc).isoformat()
        }
    
    async def send_personal_message(self, message: dict, user_id: str):
        if user_id in self.active_connections:
            try:
                await self.active_connections[user_id].send_json(message)
            except Exception:
                self.disconnect(user_id)
    
    async def broadcast_status(self, user_id: str, online: bool):
        status_message = {
            'type': 'user_status',
            'user_id': user_id,
            'online': online,
            'timestamp': datetime.now(timezone.utc).isoformat()
        }
        for connection_user_id, connection in self.active_connections.items():
            if connection_user_id != user_id:
                try:
                    await connection.send_json(status_message)
                except Exception:
                    pass
    
    def is_user_online(self, user_id: str) -> bool:
        return user_id in self.active_connections
    
    def get_user_status(self, user_id: str) -> dict:
        return self.user_status.get(user_id, {'online': False, 'last_seen': None})

manager = ConnectionManager()

# Password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# JWT settings
SECRET_KEY = os.environ.get('SECRET_KEY')
if not SECRET_KEY:
    # For development only - in production this will be set by deployment system
    SECRET_KEY = 'dev-secret-key-do-not-use-in-production'
    print("WARNING: Using development SECRET_KEY. Ensure SECRET_KEY is set in production!")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60 * 24 * 7  # 7 days

# Security
security = HTTPBearer()


# ===== Utility Functions =====

def calculate_distance(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """
    Calculate distance between two points using Haversine formula
    Returns distance in kilometers
    """
    from math import radians, sin, cos, asin, sqrt
    
    # Convert to radians
    lat1, lon1, lat2, lon2 = map(radians, [lat1, lon1, lat2, lon2])
    
    # Haversine formula
    dlat = lat2 - lat1
    dlon = lon2 - lon1
    a = sin(dlat / 2)**2 + cos(lat1) * cos(lat2) * sin(dlon / 2)**2
    c = 2 * asin(sqrt(a))
    
    # Earth radius in kilometers
    r = 6371
    
    return c * r


# Create the main app without a prefix
app = FastAPI()

# Create a router with the /api prefix
api_router = APIRouter(prefix="/api")

# Simple root endpoint for basic connectivity check
@app.get("/")
async def root():
    """
    Simple root endpoint that returns immediately
    Used for basic connectivity testing
    """
    return {"status": "running", "app": "Pizoo Dating App", "version": "1.0.0"}

# Health Check Endpoint
@app.get("/health")
async def health_check():
    """
    Health check endpoint for monitoring service status
    Returns: Status of database, OTP service, and AI matching
    """
    checks = {"db": "unknown", "otp": "unknown", "ai": "unknown", "status": "unknown"}
    
    # Check MongoDB connection
    try:
        if db is None:
            checks["db"] = "not_initialized"
        else:
            await db.command("ping")
            checks["db"] = "ok"
    except Exception as e:
        checks["db"] = f"fail: {str(e)[:50]}"
        logging.error(f"Health check - DB failed: {e}")
    
    # Check OTP service (Telnyx/Twilio)
    try:
        telnyx_key = os.getenv("TELNYX_API_KEY")
        twilio_sid = os.getenv("TWILIO_ACCOUNT_SID")
        
        if telnyx_key:
            # Quick check for Telnyx
            checks["otp"] = "ok"  # Assume OK if key exists
        elif twilio_sid:
            # Quick check for Twilio
            checks["otp"] = "ok"  # Assume OK if credentials exist
        else:
            checks["otp"] = "not_configured"
    except Exception as e:
        checks["otp"] = f"fail: {str(e)[:50]}"
        logging.error(f"Health check - OTP failed: {e}")
    
    # Check AI matching service
    try:
        if db is None:
            checks["ai"] = "not_initialized"
        else:
            # Test if we can access users collection for matching
            user_count = await db.users.count_documents({"profileSetupComplete": True})
            checks["ai"] = "ok" if user_count >= 0 else "fail"
    except Exception as e:
        checks["ai"] = f"fail: {str(e)[:50]}"
        logging.error(f"Health check - AI failed: {e}")
    
    # Overall status
    all_ok = all(v in ("ok", "not_configured", "not_initialized") for v in [checks["db"], checks["otp"], checks["ai"]])
    checks["status"] = "healthy" if all_ok else "degraded"
    
    # Return 200 even if services are degraded, so container becomes ready
    # This allows debugging and gradual service recovery
    return JSONResponse(content=checks, status_code=200)


# Debug endpoint for testing Sentry (REMOVE IN PRODUCTION)
@app.get("/debug-sentry")
async def debug_sentry():
    """
    Test endpoint to verify Sentry is working
    WARNING: Remove this in production!
    """
    try:
        # Intentional error for testing
        result = 1 / 0
    except Exception as e:
        # Capture exception in Sentry
        sentry_sdk.capture_exception(e)
        logging.error(f"Debug Sentry test error: {e}")
        return JSONResponse(
            content={
                "message": "Error captured and sent to Sentry",
                "error": str(e),
                "sentry_enabled": bool(os.getenv("SENTRY_DSN_BACKEND"))
            },
            status_code=200
        )
    return {"message": "This should not happen"}

# Country-based default radius mapping (in km)
COUNTRY_DEFAULT_RADIUS = {
    "BH": 10,  # Bahrain (small)
    "QA": 15,  # Qatar (small)
    "KW": 20,  # Kuwait (small)
    "AE": 25,  # UAE (medium)
    "OM": 30,  # Oman (medium)
    "LB": 20,  # Lebanon (medium)
    "JO": 25,  # Jordan (medium)
    "SA": 50,  # Saudi Arabia (large)
    "EG": 50,  # Egypt (large)
    "IQ": 50,  # Iraq (large)
    "MA": 50,  # Morocco (large)
    "DZ": 75,  # Algeria (very large)
    "FR": 50,  # France
    "DE": 40,  # Germany
    "ES": 50,  # Spain
    "IT": 40,  # Italy
    "GB": 40,  # United Kingdom
    "TR": 50,  # Turkey
    "US": 100, # United States (very large)
    "CA": 100, # Canada (very large)
    "BR": 100, # Brazil (very large)
    "MX": 75,  # Mexico (large)
    "RU": 100, # Russia (very large)
    "CH": 25,  # Switzerland (for Basel testing)
}
GLOBAL_DEFAULT_RADIUS = 25  # Default fallback


def radius_for_country(country: Optional[str], fallback: float = GLOBAL_DEFAULT_RADIUS) -> float:
    """Get default radius for a country code"""
    if country:
        r = COUNTRY_DEFAULT_RADIUS.get(country.upper())
        if r:
            return float(r)
    return float(fallback)


# ===== Models =====

class User(BaseModel):
    model_config = ConfigDict(extra="ignore")
    
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    name: str
    email: EmailStr
    phone_number: str
    password_hash: str
    email_verified: bool = False
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    trial_end_date: datetime
    subscription_status: str = "trial"  # trial, active, cancelled, expired
    terms_accepted: bool = False
    terms_accepted_at: Optional[datetime] = None
    profile_completed: bool = False
    
    # One-time account verification
    verified: bool = False  # Account verification status
    verified_method: Optional[str] = None  # "google_oauth", "facebook_oauth", "email_link", "phone_otp"
    verified_at: Optional[datetime] = None  # When verification completed
    
    # i18n & Geo
    language: Optional[str] = "en"  # BCP-47: ar, en, fr, es, de, tr, it, pt-BR, ru
    country: Optional[str] = None  # ISO 3166-1 alpha-2: SA, US, FR, etc.
    
    # Premium tier (free, gold, platinum)
    premium_tier: str = "free"
    
    # Weekly usage tracking for free users
    likes_sent_this_week: int = 0
    messages_sent_this_week: int = 0
    week_start_date: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class Profile(BaseModel):
    model_config = ConfigDict(extra="ignore")
    
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    user_id: str
    display_name: str  # اسم العرض أو الاسم المستعار
    bio: Optional[str] = None  # نبذة عن النفس
    date_of_birth: Optional[str] = None
    age: Optional[int] = None  # العمر المحسوب من تاريخ الميلاد
    gender: Optional[str] = None  # male, female, other
    height: Optional[int] = None  # بالسم
    looking_for: Optional[str] = None  # ماذا يبحث عنه
    interests: List[str] = []  # الهوايات
    photos: List[str] = []  # قائمة روابط الصور
    location: Optional[str] = None  # Location string (e.g., "New York, USA")
    latitude: Optional[float] = None  # GPS latitude coordinate
    longitude: Optional[float] = None  # GPS longitude coordinate
    occupation: Optional[str] = None
    education: Optional[str] = None
    relationship_goals: Optional[str] = None  # serious, casual, friendship
    smoking: Optional[str] = None  # yes, no, sometimes
    drinking: Optional[str] = None  # yes, no, sometimes
    has_children: Optional[bool] = None
    wants_children: Optional[bool] = None
    languages: List[str] = []
    current_mood: Optional[str] = None  # serious, casual, fun, romantic - كيف تشعر اليوم
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class Subscription(BaseModel):
    model_config = ConfigDict(extra="ignore")
    
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    user_id: str
    status: str  # trial, active, cancelled, expired
    start_date: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    trial_end_date: datetime
    next_payment_date: datetime
    annual_amount: float = 396.0  # CHF
    currency: str = "CHF"
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class PaymentMethod(BaseModel):
    model_config = ConfigDict(extra="ignore")
    
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    user_id: str
    payment_type: str  # card, paypal, bank_transfer
    card_last_four: Optional[str] = None
    card_brand: Optional[str] = None  # visa, mastercard, etc
    paypal_email: Optional[EmailStr] = None
    bank_account_country: Optional[str] = None
    is_active: bool = True
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))



# Session Management Models
class UserSession(BaseModel):
    model_config = ConfigDict(extra="ignore")
    
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    user_id: str  # References User.id
    session_token: str  # The persistent token (7 days)
    refresh_token: Optional[str] = None  # Optional refresh token for JWT
    device_info: Optional[str] = None  # Device/browser info
    ip_address: Optional[str] = None
    expires_at: datetime  # Session expiry (7 days from creation)
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    last_used_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class EmailVerificationToken(BaseModel):
    model_config = ConfigDict(extra="ignore")
    
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    user_id: str
    token: str  # Random verification token
    email: str
    expires_at: datetime  # 15 minutes TTL
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    used: bool = False


class PhoneVerificationOTP(BaseModel):
    model_config = ConfigDict(extra="ignore")
    
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    user_id: str
    phone_number: str
    otp_code: str  # 6-digit OTP
    expires_at: datetime  # 10 minutes TTL
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    verified: bool = False
    attempts: int = 0  # Track verification attempts


# Rate Limiting Model
class RateLimit(BaseModel):
    model_config = ConfigDict(extra="ignore")
    
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    user_id: str
    endpoint: str  # e.g., "/livekit/token"
    count: int = 0  # Number of requests
    window_start: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    last_request: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))



class Notification(BaseModel):
    model_config = ConfigDict(extra="ignore")
    
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    user_id: str  # المستخدم الذي سيستقبل الإشعار
    type: str  # new_match, new_message, new_like, super_like, profile_view
    title: str
    message: str
    link: Optional[str] = None  # رابط للانتقال إليه عند الضغط
    related_user_id: Optional[str] = None  # المستخدم المرتبط بالإشعار
    related_user_name: Optional[str] = None
    related_user_photo: Optional[str] = None
    is_read: bool = False
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))



class Story(BaseModel):
    model_config = ConfigDict(extra="ignore")
    
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    user_id: str
    media_url: str
    media_type: str  # image, video
    caption: Optional[str] = None
    views: List[str] = []  # List of user_ids who viewed
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    expires_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc) + timedelta(hours=24))


class Swipe(BaseModel):
    model_config = ConfigDict(extra="ignore")
    
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    user_id: str
    swiped_user_id: str
    action: str  # like, pass, super_like
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class Match(BaseModel):
    model_config = ConfigDict(extra="ignore")
    
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    match_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    user1_id: str
    user2_id: str
    matched_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    unmatched: bool = False
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class Report(BaseModel):
    model_config = ConfigDict(extra="ignore")
    
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    reporter_id: str  # User who is reporting
    reported_user_id: str  # User being reported
    reason: str  # harassment, inappropriate_content, fake_profile, scam, other
    details: Optional[str] = None
    status: str = "pending"  # pending, reviewed, resolved
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class Block(BaseModel):
    model_config = ConfigDict(extra="ignore")
    
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    blocker_id: str  # User who is blocking
    blocked_user_id: str  # User being blocked
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class Boost(BaseModel):
    model_config = ConfigDict(extra="ignore")
    
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    user_id: str
    started_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    ends_at: datetime  # 30 minutes from start
    is_active: bool = True


class PremiumSubscription(BaseModel):
    model_config = ConfigDict(extra="ignore")
    
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    user_id: str
    tier: str  # free, gold, platinum
    status: str  # active, expired, cancelled
    start_date: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    end_date: Optional[datetime] = None
    features: dict = Field(default_factory=lambda: {
        "unlimited_likes": False,
        "see_who_liked": False,
        "unlimited_rewinds": False,
        "super_likes_per_day": 1,
        "boosts_per_month": 0,
        "top_picks": False,
        "read_receipts": False,
        "profile_controls": False
    })
    auto_renew: bool = False
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class Message(BaseModel):
    model_config = ConfigDict(extra="ignore")
    
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    match_id: str
    sender_id: str
    receiver_id: str
    content: str
    message_type: str = "text"  # text, gif, sticker, audio
    status: str = "sent"  # sent, delivered, read
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    read_at: Optional[datetime] = None


class Conversation(BaseModel):
    model_config = ConfigDict(extra="ignore")
    
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    match_id: str
    user1_id: str
    user2_id: str
    last_message: Optional[str] = None
    last_message_at: Optional[datetime] = None
    unread_count_user1: int = 0
    unread_count_user2: int = 0
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class UserSettings(BaseModel):
    model_config = ConfigDict(extra="ignore")
    
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    user_id: str
    visibility_mode: str = "standard"  # standard, incognito
    incognito_enabled: bool = False
    verified_only_chat: bool = False
    send_read_receipts: bool = True
    allow_contacts_sync: bool = False
    auto_play_videos: bool = True
    show_activity_status: bool = True
    theme: str = "system"  # system, light, dark
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class DiscoverySettings(BaseModel):
    model_config = ConfigDict(extra="ignore")
    
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    user_id: str
    location: str = ""
    max_distance: int = 50  # in kilometers
    interested_in: str = "all"  # male, female, all
    min_age: int = 18
    max_age: int = 100
    show_new_profiles_only: bool = False
    show_verified_only: bool = False
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class DoubleDatingFriend(BaseModel):
    model_config = ConfigDict(extra="ignore")
    
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    user_id: str  # User who owns this friend list
    friend_user_id: str  # Friend's user ID
    status: str = "pending"  # pending, accepted, rejected
    invited_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    accepted_at: Optional[datetime] = None


# ===== Request/Response Models =====

class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: dict


class UserProfile(BaseModel):
    id: str
    name: str
    email: str
    subscription_status: str
    trial_end_date: datetime
    created_at: datetime


class SubscriptionStatus(BaseModel):
    status: str
    trial_end_date: datetime
    next_payment_date: Optional[datetime]
    days_remaining: int
    annual_amount: float
    currency: str


class ProfileCreateRequest(BaseModel):
    display_name: str
    bio: Optional[str] = None
    date_of_birth: Optional[str] = None
    age: Optional[int] = None
    gender: Optional[str] = None
    height: Optional[int] = None
    looking_for: Optional[str] = None
    interests: List[str] = []
    location: Optional[str] = None
    latitude: Optional[float] = None  # GPS latitude coordinate
    longitude: Optional[float] = None  # GPS longitude coordinate
    occupation: Optional[str] = None
    education: Optional[str] = None
    relationship_goals: Optional[str] = None
    smoking: Optional[str] = None
    drinking: Optional[str] = None
    has_children: Optional[bool] = None
    wants_children: Optional[bool] = None
    languages: List[str] = []


class ProfileUpdateRequest(BaseModel):
    display_name: Optional[str] = None
    bio: Optional[str] = None
    date_of_birth: Optional[str] = None
    age: Optional[int] = None
    gender: Optional[str] = None
    height: Optional[int] = None
    looking_for: Optional[str] = None
    interests: Optional[List[str]] = None
    location: Optional[str] = None
    latitude: Optional[float] = None  # GPS latitude coordinate
    longitude: Optional[float] = None  # GPS longitude coordinate
    occupation: Optional[str] = None
    education: Optional[str] = None
    relationship_goals: Optional[str] = None
    smoking: Optional[str] = None
    drinking: Optional[str] = None
    has_children: Optional[bool] = None
    wants_children: Optional[bool] = None
    languages: Optional[List[str]] = None
    photos: Optional[List[str]] = None  # Add photos field
    primary_photo_index: Optional[int] = None
    # Additional fields
    school: Optional[str] = None
    company: Optional[str] = None
    job_title: Optional[str] = None
    living_in: Optional[str] = None
    hometown: Optional[str] = None
    gender_identity: Optional[str] = None
    show_gender: Optional[bool] = None
    sexual_orientation: Optional[str] = None
    show_orientation: Optional[bool] = None
    sleeping_habits: Optional[str] = None
    social_media: Optional[str] = None
    vaccinated: Optional[str] = None
    religion: Optional[str] = None
    political_views: Optional[str] = None
    zodiac_sign: Optional[str] = None
    personality_type: Optional[str] = None
    communication_style: Optional[str] = None
    love_style: Optional[str] = None
    pets: Optional[str] = None
    exercise: Optional[str] = None
    dietary_preference: Optional[str] = None
    family_plans: Optional[str] = None


class PhotoUploadRequest(BaseModel):
    photo_data: str  # base64 encoded image

# ===== Helper Functions =====

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


# ===== Helper Functions for Usage Limits =====

async def check_and_reset_weekly_limits(user: dict):
    """Check if a week has passed and reset weekly limits"""
    if 'week_start_date' not in user:
        # Initialize if not exists
        await db.users.update_one(
            {"id": user['id']},
            {"$set": {
                "week_start_date": datetime.now(timezone.utc).isoformat(),
                "likes_sent_this_week": 0,
                "messages_sent_this_week": 0,
                "premium_tier": user.get('premium_tier', 'free')
            }}
        )
        user['likes_sent_this_week'] = 0
        user['messages_sent_this_week'] = 0
        user['premium_tier'] = user.get('premium_tier', 'free')
        return user
    
    if isinstance(user['week_start_date'], str):
        week_start = datetime.fromisoformat(user['week_start_date'])
        # Ensure timezone awareness
        if week_start.tzinfo is None:
            week_start = week_start.replace(tzinfo=timezone.utc)
    else:
        week_start = user['week_start_date']
        if week_start.tzinfo is None:
            week_start = week_start.replace(tzinfo=timezone.utc)
    
    now = datetime.now(timezone.utc)
    days_passed = (now - week_start).days
    
    # If 7 days have passed, reset the counters
    if days_passed >= 7:
        await db.users.update_one(
            {"id": user['id']},
            {"$set": {
                "week_start_date": now.isoformat(),
                "likes_sent_this_week": 0,
                "messages_sent_this_week": 0
            }}
        )
        user['likes_sent_this_week'] = 0
        user['messages_sent_this_week'] = 0
        user['week_start_date'] = now.isoformat()
    
    return user


async def can_send_like(user: dict) -> tuple[bool, str]:
    """Check if user can send a like"""
    # Premium users have unlimited likes
    if user.get('premium_tier') in ['gold', 'platinum']:
        return True, "unlimited"
    
    # Free users have 12 likes per week
    user = await check_and_reset_weekly_limits(user)
    likes_sent = user.get('likes_sent_this_week', 0)
    
    if likes_sent >= 12:
        return False, f"Weekly like limit reached. You've sent {likes_sent}/12 likes this week."
    
    return True, f"{12 - likes_sent} likes remaining"


async def can_send_message(user: dict) -> tuple[bool, str]:
    """Check if user can send a message"""
    # Premium users have unlimited messages
    if user.get('premium_tier') in ['gold', 'platinum']:
        return True, "unlimited"
    
    # Free users have 10 messages per week
    user = await check_and_reset_weekly_limits(user)
    messages_sent = user.get('messages_sent_this_week', 0)
    
    if messages_sent >= 10:
        return False, f"Weekly message limit reached. You've sent {messages_sent}/10 messages this week."
    
    return True, f"{10 - messages_sent} messages remaining"


async def increment_likes_count(user_id: str):
    """Increment the weekly likes counter"""
    await db.users.update_one(
        {"id": user_id},
        {"$inc": {"likes_sent_this_week": 1}}
    )


async def increment_messages_count(user_id: str):
    """Increment the weekly messages counter"""
    await db.users.update_one(
        {"id": user_id},
        {"$inc": {"messages_sent_this_week": 1}}
    )


# ===== Authentication =====

async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        token = credentials.credentials
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id: str = payload.get("sub")
        if user_id is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception
    
    user = await db.users.find_one({"id": user_id}, {"_id": 0})
    if user is None:
        raise credentials_exception
    return user


async def optional_auth(credentials: Optional[HTTPAuthorizationCredentials] = Depends(HTTPBearer(auto_error=False))):
    """
    Optional authentication - returns user if authenticated, None otherwise
    Used for endpoints that work both with and without authentication
    """
    if not credentials:
        return None
    
    try:
        token = credentials.credentials
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id: str = payload.get("sub")
        if user_id is None:
            return None
        
        user = await db.users.find_one({"id": user_id}, {"_id": 0})
        return user
    except (JWTError, Exception):
        return None



# ===== Request Models =====

class RegisterRequest(BaseModel):
    name: str
    email: EmailStr
    phone_number: str
    password: str
    terms_accepted: bool


class LoginRequest(BaseModel):
    email: Optional[EmailStr] = None
    phone: Optional[str] = None
    password: str
    
    @field_validator('phone')
    @classmethod
    def check_at_least_one_identifier(cls, v, info):
        # Check if at least one of email or phone is provided
        email = info.data.get('email')
        if not v and not email:
            raise ValueError('Either email or phone must be provided')
        return v


class SwipeRequest(BaseModel):
    swiped_user_id: str
    action: str  # like, pass, super_like


class ReportRequest(BaseModel):
    reported_user_id: str
    reason: str  # harassment, inappropriate_content, fake_profile, scam, other
    details: Optional[str] = None


class BlockRequest(BaseModel):
    blocked_user_id: str


# ===== API Endpoints =====

@api_router.get("/")
async def root():
    return {"message": "Welcome to Subscription API"}


@api_router.get("/health")
async def health_check():
    """
    Health check endpoint for CI/CD and monitoring
    """
    try:
        # Check MongoDB connection
        if db is None:
            return {
                "status": "unhealthy",
                "database": "disconnected",
                "message": "MongoDB client not initialized"
            }
        
        # Try to ping the database
        await db.command("ping")
        
        return {
            "status": "healthy",
            "database": "connected",
            "timestamp": datetime.now(timezone.utc).isoformat()
        }
    except Exception as e:
        logging.error(f"Health check failed: {e}")
        return {
            "status": "unhealthy",
            "database": "error",
            "error": str(e)
        }


@api_router.post("/auth/register", response_model=TokenResponse)
async def register(request: RegisterRequest):
    # Validate terms accepted
    if not request.terms_accepted:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="يجب الموافقة على الشروط والأحكام"
        )
    
    # Check if user already exists
    existing_user = await db.users.find_one({"email": request.email}, {"_id": 0})
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="البريد الإلكتروني مسجل مسبقاً"
        )
    
    # Create user
    trial_end_date = datetime.now(timezone.utc) + timedelta(days=14)
    user = User(
        name=request.name,
        email=request.email,
        phone_number=request.phone_number,
        password_hash=get_password_hash(request.password),
        trial_end_date=trial_end_date,
        subscription_status="trial",
        terms_accepted=True,
        terms_accepted_at=datetime.now(timezone.utc)
    )
    
    user_dict = user.model_dump()
    user_dict['created_at'] = user_dict['created_at'].isoformat()
    user_dict['trial_end_date'] = user_dict['trial_end_date'].isoformat()
    user_dict['terms_accepted_at'] = user_dict['terms_accepted_at'].isoformat()
    
    await db.users.insert_one(user_dict)
    
    # Create subscription
    next_payment_date = trial_end_date
    subscription = Subscription(
        user_id=user.id,
        status="trial",
        trial_end_date=trial_end_date,
        next_payment_date=next_payment_date
    )
    
    subscription_dict = subscription.model_dump()
    subscription_dict['created_at'] = subscription_dict['created_at'].isoformat()
    subscription_dict['start_date'] = subscription_dict['start_date'].isoformat()
    subscription_dict['trial_end_date'] = subscription_dict['trial_end_date'].isoformat()
    subscription_dict['next_payment_date'] = subscription_dict['next_payment_date'].isoformat()
    
    await db.subscriptions.insert_one(subscription_dict)
    
    # Create empty profile for the user
    from datetime import date
    age = None
    try:
        # Try to calculate age if date of birth exists
        if hasattr(user, 'date_of_birth') and user.date_of_birth:
            today = date.today()
            dob = datetime.fromisoformat(user.date_of_birth).date()
            age = today.year - dob.year - ((today.month, today.day) < (dob.month, dob.day))
    except Exception:
        pass
    
    profile = Profile(
        user_id=user.id,
        display_name=user.name,
        photos=[],
        interests=[],
        languages=[],
        age=age
    )
    
    profile_dict = profile.model_dump()
    profile_dict['created_at'] = profile_dict['created_at'].isoformat()
    profile_dict['updated_at'] = profile_dict['updated_at'].isoformat()
    
    await db.profiles.insert_one(profile_dict)
    
    # Create access token
    access_token = create_access_token(data={"sub": user.id})
    
    return TokenResponse(
        access_token=access_token,
        user={
            "id": user.id,
            "name": user.name,
            "email": user.email,
            "subscription_status": user.subscription_status,
            "trial_end_date": user.trial_end_date.isoformat()
        }
    )


@api_router.post("/auth/login", response_model=TokenResponse)
async def login(request: LoginRequest):
    # Build query based on provided identifier (email or phone)
    query = {}
    if request.email:
        query["email"] = request.email
    elif request.phone:
        query["phone"] = request.phone
    else:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email or phone number is required"
        )
    
    user = await db.users.find_one(query, {"_id": 0})
    
    if not user or not verify_password(request.password, user['password_hash']):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="البريد الإلكتروني أو كلمة المرور غير صحيحة"
        )
    
    access_token = create_access_token(data={"sub": user['id']})
    
    # Convert trial_end_date to ISO string to prevent JSON serialization issues
    trial_end_date = user['trial_end_date']
    if isinstance(trial_end_date, datetime):
        trial_end_date_str = trial_end_date.isoformat()
    elif isinstance(trial_end_date, str):
        trial_end_date_str = trial_end_date
    else:
        trial_end_date_str = datetime.now(timezone.utc).isoformat()
    
    return TokenResponse(
        access_token=access_token,
        user={
            "id": user['id'],
            "name": user['name'],
            "email": user['email'],
            "subscription_status": user['subscription_status'],
            "trial_end_date": trial_end_date_str,
            "verified": user.get('verified', False),
            "verified_method": user.get('verified_method'),
            "premium_tier": user.get('premium_tier', 'free')
        }
    )


# ==================================================================================
# NEW ONE-TIME VERIFICATION AUTH ENDPOINTS
# ==================================================================================

# ===== Google OAuth (Emergent) =====

class EmergentOAuthRequest(BaseModel):
    session_id: str  # Temporary token from URL fragment


@api_router.post("/auth/oauth/google")
async def google_oauth_login(request: EmergentOAuthRequest):
    """
    Google OAuth login via Emergent
    User redirects to: https://auth.emergentagent.com/?redirect={your_app_url}
    After auth, user lands at: {your_app_url}#session_id={session_id}
    Frontend extracts session_id and calls this endpoint
    
    Returns: Access token, Refresh token, User data
    """
    try:
        # Get session data from Emergent
        session_data = await AuthService.get_emergent_oauth_session_data(request.session_id)
        
        if not session_data:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid or expired session"
            )
        
        # Extract user data
        oauth_id = session_data.get("id")
        email = session_data.get("email")
        name = session_data.get("name")
        picture = session_data.get("picture")
        emergent_session_token = session_data.get("session_token")
        
        # Check if user exists
        user = await db.users.find_one({"email": email}, {"_id": 0})
        
        if user:
            # Existing user - update if not verified
            if not user.get("verified"):
                await db.users.update_one(
                    {"id": user["id"]},
                    {"$set": {
                        "verified": True,
                        "verified_method": "google_oauth",
                        "verified_at": datetime.now(timezone.utc).isoformat()
                    }}
                )
                user["verified"] = True
                user["verified_method"] = "google_oauth"
        else:
            # New user - create account with verified=True
            trial_end_date = datetime.now(timezone.utc) + timedelta(days=14)
            user = User(
                name=name,
                email=email,
                phone_number="",  # No phone for OAuth
                password_hash="",  # No password for OAuth
                trial_end_date=trial_end_date,
                subscription_status="trial",
                terms_accepted=True,
                terms_accepted_at=datetime.now(timezone.utc),
                verified=True,
                verified_method="google_oauth",
                verified_at=datetime.now(timezone.utc)
            )
            
            user_dict = user.model_dump()
            user_dict['created_at'] = user_dict['created_at'].isoformat()
            user_dict['trial_end_date'] = user_dict['trial_end_date'].isoformat()
            user_dict['terms_accepted_at'] = user_dict['terms_accepted_at'].isoformat()
            user_dict['verified_at'] = user_dict['verified_at'].isoformat()
            
            await db.users.insert_one(user_dict)
            
            # Create subscription
            subscription = Subscription(
                user_id=user.id,
                status="trial",
                trial_end_date=trial_end_date,
                next_payment_date=trial_end_date
            )
            
            subscription_dict = subscription.model_dump()
            subscription_dict['created_at'] = subscription_dict['created_at'].isoformat()
            subscription_dict['start_date'] = subscription_dict['start_date'].isoformat()
            subscription_dict['trial_end_date'] = subscription_dict['trial_end_date'].isoformat()
            subscription_dict['next_payment_date'] = subscription_dict['next_payment_date'].isoformat()
            
            await db.subscriptions.insert_one(subscription_dict)
            
            # Create profile
            profile = Profile(
                user_id=user.id,
                display_name=name,
                photos=[picture] if picture else [],
                interests=[],
                languages=[]
            )
            
            profile_dict = profile.model_dump()
            profile_dict['created_at'] = profile_dict['created_at'].isoformat()
            profile_dict['updated_at'] = profile_dict['updated_at'].isoformat()
            
            await db.profiles.insert_one(profile_dict)
            
            user = user_dict
        
        # Create JWT tokens
        user_id = user.get("id") if isinstance(user, dict) else user.id
        access_token = AuthService.create_access_token(data={"sub": user_id})
        refresh_token = AuthService.create_refresh_token(data={"sub": user_id})
        
        # Create session in database
        session_expiry = AuthService.calculate_session_expiry()
        user_session = UserSession(
            user_id=user_id,
            session_token=emergent_session_token,
            refresh_token=refresh_token,
            expires_at=session_expiry
        )
        
        session_dict = user_session.model_dump()
        session_dict['expires_at'] = session_dict['expires_at'].isoformat()
        session_dict['created_at'] = session_dict['created_at'].isoformat()
        session_dict['last_used_at'] = session_dict['last_used_at'].isoformat()
        
        await db.user_sessions.insert_one(session_dict)
        
        logging.info(f"✅ Google OAuth login successful for {email}")
        
        return {
            "success": True,
            "access_token": access_token,
            "refresh_token": refresh_token,
            "token_type": "bearer",
            "expires_in": 3600,  # 1 hour
            "user": {
                "id": user_id,
                "name": user.get("name") if isinstance(user, dict) else user.name,
                "email": user.get("email") if isinstance(user, dict) else user.email,
                "verified": True,
                "verified_method": "google_oauth"
            }
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logging.error(f"❌ Google OAuth error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Authentication failed"
        )


# ===== Email Magic Link =====

class EmailVerificationSendRequest(BaseModel):
    email: EmailStr
    name: str


class EmailVerificationVerifyRequest(BaseModel):
    token: str


@api_router.post("/auth/email/send-link")
async def send_email_verification_link(request: EmailVerificationSendRequest):
    """
    Send magic link to email for one-time account verification
    Link expires in 15 minutes
    """
    try:
        # Check if user already exists and is verified
        existing_user = await db.users.find_one({"email": request.email}, {"_id": 0})
        
        if existing_user and existing_user.get("verified"):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already verified. Please login."
            )
        
        # Generate verification token
        token = AuthService.generate_verification_token()
        expires_at = datetime.now(timezone.utc) + timedelta(minutes=15)
        
        # If user doesn't exist, create a pending user
        if not existing_user:
            trial_end_date = datetime.now(timezone.utc) + timedelta(days=14)
            user = User(
                name=request.name,
                email=request.email,
                phone_number="",
                password_hash="",  # No password for email link
                trial_end_date=trial_end_date,
                subscription_status="trial",
                terms_accepted=True,
                terms_accepted_at=datetime.now(timezone.utc),
                verified=False,  # Not verified yet
                verified_method=None
            )
            
            user_dict = user.model_dump()
            user_dict['created_at'] = user_dict['created_at'].isoformat()
            user_dict['trial_end_date'] = user_dict['trial_end_date'].isoformat()
            user_dict['terms_accepted_at'] = user_dict['terms_accepted_at'].isoformat()
            
            await db.users.insert_one(user_dict)
            user_id = user.id
        else:
            user_id = existing_user["id"]
        
        # Store verification token
        verification_token = EmailVerificationToken(
            user_id=user_id,
            token=token,
            email=request.email,
            expires_at=expires_at
        )
        
        token_dict = verification_token.model_dump()
        token_dict['created_at'] = token_dict['created_at'].isoformat()
        token_dict['expires_at'] = token_dict['expires_at'].isoformat()
        
        await db.email_verification_tokens.insert_one(token_dict)
        
        # Send verification email
        email_sent = await AuthService.send_verification_email(request.email, token, request.name)
        
        if not email_sent:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to send verification email"
            )
        
        logging.info(f"✅ Verification email sent to {request.email}")
        
        return {
            "success": True,
            "message": "Verification email sent. Please check your inbox.",
            "expires_in": 900  # 15 minutes in seconds
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logging.error(f"❌ Email verification send error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to send verification email"
        )


@api_router.post("/auth/email/verify")
async def verify_email_link(request: EmailVerificationVerifyRequest):
    """
    Verify email using magic link token
    Sets user.verified = true and issues JWT tokens
    """
    try:
        # Find verification token
        token_data = await db.email_verification_tokens.find_one(
            {"token": request.token, "used": False},
            {"_id": 0}
        )
        
        if not token_data:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid or expired verification link"
            )
        
        # Check if expired
        expires_at = datetime.fromisoformat(token_data["expires_at"]) if isinstance(token_data["expires_at"], str) else token_data["expires_at"]
        if expires_at.tzinfo is None:
            expires_at = expires_at.replace(tzinfo=timezone.utc)
        
        if datetime.now(timezone.utc) > expires_at:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Verification link has expired"
            )
        
        # Mark token as used
        await db.email_verification_tokens.update_one(
            {"token": request.token},
            {"$set": {"used": True}}
        )
        
        # Update user verification status
        user_id = token_data["user_id"]
        await db.users.update_one(
            {"id": user_id},
            {"$set": {
                "verified": True,
                "verified_method": "email_link",
                "verified_at": datetime.now(timezone.utc).isoformat(),
                "email_verified": True
            }}
        )
        
        # Get updated user
        user = await db.users.find_one({"id": user_id}, {"_id": 0})
        
        # Create JWT tokens
        access_token = AuthService.create_access_token(data={"sub": user_id})
        refresh_token = AuthService.create_refresh_token(data={"sub": user_id})
        
        # Create session
        session_expiry = AuthService.calculate_session_expiry()
        session_token = AuthService.generate_verification_token()
        user_session = UserSession(
            user_id=user_id,
            session_token=session_token,
            refresh_token=refresh_token,
            expires_at=session_expiry
        )
        
        session_dict = user_session.model_dump()
        session_dict['expires_at'] = session_dict['expires_at'].isoformat()
        session_dict['created_at'] = session_dict['created_at'].isoformat()
        session_dict['last_used_at'] = session_dict['last_used_at'].isoformat()
        
        await db.user_sessions.insert_one(session_dict)
        
        # Create subscription and profile if they don't exist
        subscription = await db.subscriptions.find_one({"user_id": user_id})
        if not subscription:
            trial_end_date = datetime.now(timezone.utc) + timedelta(days=14)
            subscription = Subscription(
                user_id=user_id,
                status="trial",
                trial_end_date=trial_end_date,
                next_payment_date=trial_end_date
            )
            
            subscription_dict = subscription.model_dump()
            subscription_dict['created_at'] = subscription_dict['created_at'].isoformat()
            subscription_dict['start_date'] = subscription_dict['start_date'].isoformat()
            subscription_dict['trial_end_date'] = subscription_dict['trial_end_date'].isoformat()
            subscription_dict['next_payment_date'] = subscription_dict['next_payment_date'].isoformat()
            
            await db.subscriptions.insert_one(subscription_dict)
        
        profile = await db.profiles.find_one({"user_id": user_id})
        if not profile:
            profile = Profile(
                user_id=user_id,
                display_name=user["name"],
                photos=[],
                interests=[],
                languages=[]
            )
            
            profile_dict = profile.model_dump()
            profile_dict['created_at'] = profile_dict['created_at'].isoformat()
            profile_dict['updated_at'] = profile_dict['updated_at'].isoformat()
            
            await db.profiles.insert_one(profile_dict)
        
        logging.info(f"✅ Email verification successful for {user['email']}")
        
        return {
            "success": True,
            "access_token": access_token,
            "refresh_token": refresh_token,
            "token_type": "bearer",
            "expires_in": 3600,
            "user": {
                "id": user["id"],
                "name": user["name"],
                "email": user["email"],
                "verified": True,
                "verified_method": "email_link"
            }
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logging.error(f"❌ Email verification error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Email verification failed"
        )


# ===== JWT Refresh Token =====

class RefreshTokenRequest(BaseModel):
    refresh_token: str


@api_router.post("/auth/refresh")
async def refresh_access_token(request: RefreshTokenRequest):
    """
    Refresh access token using refresh token
    Refresh tokens are valid for 7 days
    """
    try:
        # Verify refresh token
        payload = AuthService.verify_token(request.refresh_token, token_type="refresh")
        
        if not payload:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid or expired refresh token"
            )
        
        user_id = payload.get("sub")
        
        # Verify session exists and is valid
        session = await db.user_sessions.find_one(
            {"user_id": user_id, "refresh_token": request.refresh_token},
            {"_id": 0}
        )
        
        if not session:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Session not found"
            )
        
        # Check if session expired
        expires_at = datetime.fromisoformat(session["expires_at"]) if isinstance(session["expires_at"], str) else session["expires_at"]
        if expires_at.tzinfo is None:
            expires_at = expires_at.replace(tzinfo=timezone.utc)
        
        if datetime.now(timezone.utc) > expires_at:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Session has expired. Please login again."
            )
        
        # Generate new access token
        access_token = AuthService.create_access_token(data={"sub": user_id})
        
        # Update session last_used_at
        await db.user_sessions.update_one(
            {"user_id": user_id, "refresh_token": request.refresh_token},
            {"$set": {"last_used_at": datetime.now(timezone.utc).isoformat()}}
        )
        
        logging.info(f"✅ Token refreshed for user {user_id}")
        
        return {
            "success": True,
            "access_token": access_token,
            "token_type": "bearer",
            "expires_in": 3600
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logging.error(f"❌ Token refresh error: {e}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token refresh failed"
        )


# ===== Logout =====

@api_router.post("/auth/logout")
async def logout(current_user: dict = Depends(get_current_user)):
    """
    Logout user by deleting session
    """
    try:
        user_id = current_user["id"]
        
        # Delete all sessions for this user
        await db.user_sessions.delete_many({"user_id": user_id})
        
        logging.info(f"✅ User {user_id} logged out")
        
        return {
            "success": True,
            "message": "Logged out successfully"
        }
        
    except Exception as e:
        logging.error(f"❌ Logout error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Logout failed"
        )


# ===== Get Current User Info =====

@api_router.get("/auth/me")
async def get_current_user_profile(current_user: dict = Depends(get_current_user)):
    """
    Get current authenticated user profile
    """
    return {
        "success": True,
        "user": {
            "id": current_user["id"],
            "name": current_user["name"],
            "email": current_user["email"],
            "verified": current_user.get("verified", False),
            "verified_method": current_user.get("verified_method"),
            "subscription_status": current_user.get("subscription_status"),
            "premium_tier": current_user.get("premium_tier", "free")
        }
    }




@api_router.get("/user/profile")
async def get_profile(current_user: dict = Depends(get_current_user)):
    """Get user profile - returns JSON-serializable data"""
    # Convert datetime fields to ISO strings
    trial_end_date = current_user.get('trial_end_date')
    if isinstance(trial_end_date, datetime):
        trial_end_date_str = trial_end_date.isoformat()
    elif isinstance(trial_end_date, str):
        trial_end_date_str = trial_end_date
    else:
        trial_end_date_str = None
    
    created_at = current_user.get('created_at')
    if isinstance(created_at, datetime):
        created_at_str = created_at.isoformat()
    elif isinstance(created_at, str):
        created_at_str = created_at
    else:
        created_at_str = datetime.now(timezone.utc).isoformat()
    
    return {
        "id": current_user['id'],
        "name": current_user['name'],
        "email": current_user['email'],
        "subscription_status": current_user.get('subscription_status', 'trial'),
        "trial_end_date": trial_end_date_str,
        "created_at": created_at_str,
        "verified": current_user.get('verified', False),
        "verified_method": current_user.get('verified_method'),
        "premium_tier": current_user.get('premium_tier', 'free')
    }


class AddPaymentRequest(BaseModel):
    payment_type: str  # card, paypal
    card_number: Optional[str] = None
    card_holder_name: Optional[str] = None
    card_expiry: Optional[str] = None
    card_cvv: Optional[str] = None
    paypal_email: Optional[EmailStr] = None


# ============================================================================
# PHONE OTP AUTHENTICATION
# ============================================================================

PHONE_RE = re.compile(r"^\+[1-9]\d{7,14}$")

class PhonePayload(BaseModel):
    phone: str = Field(..., description="+41791234567")

class VerifyPayload(BaseModel):
    phone: str
    code: str
    otpId: str

@api_router.post("/auth/phone/send-otp")
async def send_phone_otp(payload: PhonePayload, request: Request, current_user: dict = Depends(optional_auth)):
    """Send OTP code to phone number with language-aware message"""
    phone = payload.phone.strip()
    
    # Validate phone format
    if not PHONE_RE.match(phone):
        raise HTTPException(status_code=400, detail="INVALID_PHONE")
    
    # Rate limiting: prevent spam (30 seconds between requests)
    now = int(time.time())
    last = await db.user_otp.find_one({"phone": phone}, sort=[("_id", -1)])
    if last and (now - last.get("created_at", 0) < 30):
        raise HTTPException(status_code=429, detail="TOO_MANY_REQUESTS")
    
    # Detect user language (if authenticated) or default to 'en'
    user_lang = 'en'
    if current_user:
        user = await db.users.find_one({"id": current_user.get("id")}, {"language": 1})
        if user and user.get("language"):
            user_lang = user["language"]
    
    # Check if phone exists in users and get their language preference
    if not current_user:
        existing_user = await db.users.find_one({"phone": phone}, {"language": 1})
        if existing_user and existing_user.get("language"):
            user_lang = existing_user["language"]
    
    # Generate and send OTP with language-aware message
    pack = generate_and_send(phone, user_lang)
    if not pack:
        raise HTTPException(status_code=500, detail="SMS_FAILED")
    
    # Store OTP in database
    doc = {
        "phone": phone,
        "hash": pack["hash"],
        "expires_at": pack["expires_at"],
        "attempts_left": pack["attempts_left"],
        "verified": False,
        "created_at": now,
        "language": user_lang  # Store language for reference
    }
    ins = await db.user_otp.insert_one(doc)
    
    return {
        "ok": True,
        "otpId": str(ins.inserted_id),
        "ttl": pack["expires_at"] - now
    }

@api_router.post("/auth/phone/verify-otp")
async def verify_phone_otp(payload: VerifyPayload):
    """Verify OTP code and login/register user"""
    # Find OTP document
    try:
        otp_doc = await db.user_otp.find_one({"_id": ObjectId(payload.otpId)})
    except:
        otp_doc = None
    
    if not otp_doc or otp_doc.get("phone") != payload.phone:
        raise HTTPException(status_code=400, detail="OTP_NOT_FOUND")
    
    # Check if already verified
    if otp_doc.get("verified"):
        return {"ok": True, "verified": True}
    
    # Check expiration
    now = int(time.time())
    if now > int(otp_doc.get("expires_at", 0)):
        raise HTTPException(status_code=410, detail="OTP_EXPIRED")
    
    # Check attempts left
    left = int(otp_doc.get("attempts_left", 0))
    if left <= 0:
        raise HTTPException(status_code=429, detail="OTP_LOCKED")
    
    # Verify code
    if not verify_otp(payload.phone, payload.code.strip(), otp_doc["hash"]):
        await db.user_otp.update_one(
            {"_id": otp_doc["_id"]},
            {"$inc": {"attempts_left": -1}}
        )
        raise HTTPException(status_code=400, detail="OTP_INVALID")
    
    # Mark as verified
    await db.user_otp.update_one(
        {"_id": otp_doc["_id"]},
        {"$set": {"verified": True}}
    )
    
    # Find or create user
    user = await db.users.find_one({"phone": payload.phone})
    if not user:
        # Create new user with phone
        user_id = str(uuid.uuid4())
        new_user = {
            "id": user_id,
            "phone": payload.phone,
            "language": "en",
            "email_verified": False,
            "created_at": datetime.now(timezone.utc).isoformat()
        }
        await db.users.insert_one(new_user)
        user = new_user
    
    # Generate JWT token
    token_data = {
        "sub": user.get("id") or user.get("_id"),
        "phone": payload.phone,
        "exp": datetime.now(timezone.utc) + timedelta(days=30)
    }
    token = jwt.encode(token_data, SECRET_KEY, algorithm=ALGORITHM)
    
    return {
        "ok": True,
        "verified": True,
        "token": token,
        "user_id": user.get("id") or user.get("_id")
    }



# ========================================
# Twilio Voice & Video Integration
# ========================================

class VoiceTokenPayload(BaseModel):
    identity: str

@api_router.post("/twilio/voice/token")
async def twilio_voice_token(payload: VoiceTokenPayload, current_user: dict = Depends(get_current_user)):
    """Generate Twilio Voice token for WebRTC calls"""
    try:
        # Use user ID as identity
        identity = payload.identity or current_user.get('id')
        token = create_voice_token(identity)
        return {"ok": True, "token": token, "identity": identity}
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to generate voice token: {str(e)}"
        )

class VideoTokenPayload(BaseModel):
    identity: str
    room: str

@api_router.post("/twilio/video/token")
async def twilio_video_token(payload: VideoTokenPayload, current_user: dict = Depends(get_current_user)):
    """Generate Twilio Video token for video calls"""
    try:
        identity = payload.identity or current_user.get('id')
        token = create_video_token(identity, payload.room)
        return {"ok": True, "token": token, "identity": identity, "room": payload.room}
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to generate video token: {str(e)}"
        )

# Webhook for incoming PSTN calls -> route to app client
@api_router.post("/twilio/voice/incoming", response_class=PlainTextResponse)
async def twilio_voice_incoming(request: Request, To: str = Form(None), From: str = Form(None)):
    """Handle incoming PSTN calls and route to app client"""
    # TODO: Implement logic to determine which app client should receive the call
    # For now, route to a default "support" identity
    client_identity = "support"
    
    r = VoiceResponse()
    dial = Dial(callerId=To or os.getenv("TWILIO_FROM"))
    dial.client(client_identity)
    r.append(dial)
    
    print(f"📞 Incoming call from {From} to {To} -> routing to {client_identity}")
    return str(r)

# Optional: Webhook for call status tracking
@api_router.post("/twilio/voice/status", response_class=PlainTextResponse)
async def twilio_voice_status(request: Request):
    """Track call status updates"""
    data = await request.form()
    print(f"📊 Twilio call status: {dict(data)}")
    return "OK"



# ========================================
# LiveKit Real-Time Communication (RTC)
# ========================================

class LiveKitTokenRequest(BaseModel):
    """Request model for LiveKit token generation"""
    match_id: str = Field(..., description="Match/Chat ID for the call")
    call_type: str = Field(default="video", description="Type of call: 'video' or 'audio'")
    participant_name: Optional[str] = Field(default=None, description="Display name for participant")

@api_router.post("/livekit/token")
async def generate_livekit_token(
    payload: LiveKitTokenRequest,
    current_user: dict = Depends(get_current_user)
):
    """
    Generate LiveKit access token for video/voice calls
    
    Requirements:
    - User must be verified (verified=True)
    - Rate limited to 30 requests per hour per user
    
    Features:
    - 1-to-1 video calls
    - Voice-only calls (audio)
    - Secure room-based communication
    - Automatic participant naming
    - Short-lived tokens (10 minutes TTL)
    
    Returns:
        token: JWT token for LiveKit
        url: LiveKit server WebSocket URL
        room_name: Room name to join
        participant_info: User identity and name
    """
    try:
        # Check if user is verified
        if not current_user.get("verified"):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Account not verified. Please complete verification to use calls."
            )
        
        # Rate limiting: 30 calls per hour
        user_id = current_user.get('id')
        now = datetime.now(timezone.utc)
        rate_limit_window = timedelta(hours=1)
        window_start = now - rate_limit_window
        
        # Check existing rate limit
        rate_limit = await db.rate_limits.find_one(
            {"user_id": user_id, "endpoint": "/livekit/token"},
            {"_id": 0}
        )
        
        if rate_limit:
            window_start_dt = datetime.fromisoformat(rate_limit["window_start"]) if isinstance(rate_limit["window_start"], str) else rate_limit["window_start"]
            if window_start_dt.tzinfo is None:
                window_start_dt = window_start_dt.replace(tzinfo=timezone.utc)
            
            # Reset if window expired
            if now - window_start_dt >= rate_limit_window:
                await db.rate_limits.update_one(
                    {"user_id": user_id, "endpoint": "/livekit/token"},
                    {"$set": {
                        "count": 1,
                        "window_start": now.isoformat(),
                        "last_request": now.isoformat()
                    }}
                )
            else:
                # Check if limit exceeded
                if rate_limit["count"] >= 30:
                    raise HTTPException(
                        status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                        detail=f"Rate limit exceeded. Maximum 30 calls per hour. Try again in {int((rate_limit_window - (now - window_start_dt)).total_seconds() / 60)} minutes."
                    )
                
                # Increment count
                await db.rate_limits.update_one(
                    {"user_id": user_id, "endpoint": "/livekit/token"},
                    {"$inc": {"count": 1}, "$set": {"last_request": now.isoformat()}}
                )
        else:
            # Create new rate limit entry
            rate_limit_entry = RateLimit(
                user_id=user_id,
                endpoint="/livekit/token",
                count=1,
                window_start=now,
                last_request=now
            )
            
            rate_limit_dict = rate_limit_entry.model_dump()
            rate_limit_dict['window_start'] = rate_limit_dict['window_start'].isoformat()
            rate_limit_dict['last_request'] = rate_limit_dict['last_request'].isoformat()
            
            await db.rate_limits.insert_one(rate_limit_dict)
        
        # Check if LiveKit is configured
        if not LiveKitService.is_configured():
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="خدمة المكالمات غير متاحة حالياً. يرجى المحاولة لاحقاً."
            )
        
        # Get user info
        user_name = payload.participant_name or current_user.get('display_name') or f"User-{user_id[:8]}"
        
        # Generate token with 10 minutes TTL
        result = LiveKitService.create_room_token(
            match_id=payload.match_id,
            user_id=user_id,
            user_name=user_name,
            call_type=payload.call_type
        )
        
        if not result.get("success"):
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=result.get("error", "فشل إنشاء جلسة المكالمة")
            )
        
        logging.info(f"✅ LiveKit token generated for verified user {user_id} in match {payload.match_id}")
        
        return {
            "success": True,
            "token": result["token"],
            "url": result["url"],
            "room_name": result["room_name"],
            "participant": {
                "identity": result["participant_identity"],
                "name": result["participant_name"]
            },
            "call_type": payload.call_type,
            "video_enabled": result["video_enabled"],
            "audio_enabled": result["audio_enabled"]
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logging.error(f"❌ LiveKit token error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="حدث خطأ أثناء إنشاء جلسة المكالمة"
        )

@api_router.get("/livekit/status")
async def livekit_status():
    """
    Check LiveKit service status
    
    Returns:
        configured: Whether LiveKit is properly configured
        url: LiveKit server URL (if configured)
    """
    from livekit_service import LIVEKIT_URL
    is_configured = LiveKitService.is_configured()
    
    return {
        "configured": is_configured,
        "url": LIVEKIT_URL if is_configured else None,
        "message": "LiveKit is ready" if is_configured else "LiveKit credentials not configured"
    }

# ========================================
# Twilio Verify (Alternative OTP System)
# ========================================

class StartVerifyPayload(BaseModel):
    phone: str
    channel: Optional[str] = "sms"

@api_router.post("/auth/verify/start")
async def start_verify(payload: StartVerifyPayload):
    """Start Twilio Verify OTP verification"""
    # Validate phone format
    phone_re = re.compile(r'^\+[1-9]\d{7,14}$')
    if not phone_re.match(payload.phone):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="INVALID_PHONE"
        )
    
    res = verify_start(payload.phone, payload.channel or "sms")
    
    if res.get("mock"):
        return {"ok": True, "mock": True, "message": "Twilio Verify not configured, using fallback"}
    
    return {"ok": True, "status": res.get("status"), "phone": payload.phone}

class CheckVerifyPayload(BaseModel):
    phone: str
    code: str

@api_router.post("/auth/verify/check")
async def check_verify(payload: CheckVerifyPayload):
    """Verify OTP code using Twilio Verify"""
    res = verify_check(payload.phone, payload.code)
    
    if not res.get("valid"):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="OTP_INVALID"
        )
    
    return {"ok": True, "verified": True, "phone": payload.phone}


@api_router.post("/payment/add")
async def add_payment_method(request: AddPaymentRequest, current_user: dict = Depends(get_current_user)):
    # Check if payment method already exists
    existing_payment = await db.payment_methods.find_one({"user_id": current_user['id']}, {"_id": 0})
    
    if existing_payment:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="طريقة دفع موجودة بالفعل"
        )
    
    # Create payment method
    payment_method_data = {
        "user_id": current_user['id'],
        "payment_type": request.payment_type,
        "is_active": True
    }
    
    if request.payment_type == "card" and request.card_number:
        payment_method_data["card_last_four"] = request.card_number[-4:]
        payment_method_data["card_brand"] = "visa"
    elif request.payment_type == "paypal" and request.paypal_email:
        payment_method_data["paypal_email"] = request.paypal_email
    
    payment_method = PaymentMethod(**payment_method_data)
    payment_dict = payment_method.model_dump()
    payment_dict['created_at'] = payment_dict['created_at'].isoformat()
    
    await db.payment_methods.insert_one(payment_dict)
    
    return {"message": "تم إضافة طريقة الدفع بنجاح"}


@api_router.get("/payment/status")
async def get_payment_status(current_user: dict = Depends(get_current_user)):
    payment = await db.payment_methods.find_one({"user_id": current_user['id']}, {"_id": 0})
    
    if not payment:
        return {"has_payment": False}
    
    return {
        "has_payment": True,
        "payment_type": payment.get('payment_type'),
        "card_last_four": payment.get('card_last_four'),
        "paypal_email": payment.get('paypal_email')
    }


@api_router.get("/subscription/status", response_model=SubscriptionStatus)
async def get_subscription_status(current_user: dict = Depends(get_current_user)):
    subscription = await db.subscriptions.find_one({"user_id": current_user['id']}, {"_id": 0})
    
    if not subscription:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="الاشتراك غير موجود"
        )
    
    trial_end = datetime.fromisoformat(subscription['trial_end_date']) if isinstance(subscription['trial_end_date'], str) else subscription['trial_end_date']
    days_remaining = max(0, (trial_end - datetime.now(timezone.utc)).days)
    
    next_payment = None
    if subscription['next_payment_date']:
        next_payment = datetime.fromisoformat(subscription['next_payment_date']) if isinstance(subscription['next_payment_date'], str) else subscription['next_payment_date']
    
    return SubscriptionStatus(
        status=subscription['status'],
        trial_end_date=trial_end,
        next_payment_date=next_payment,
        days_remaining=days_remaining,
        annual_amount=subscription['annual_amount'],
        currency=subscription['currency']
    )


@api_router.post("/profile/create")
async def create_profile(request: ProfileCreateRequest, current_user: dict = Depends(get_current_user)):
    # Check if profile already exists
    existing_profile = await db.profiles.find_one({"user_id": current_user['id']}, {"_id": 0})
    if existing_profile:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="الملف الشخصي موجود بالفعل"
        )
    
    # Create profile
    profile = Profile(
        user_id=current_user['id'],
        display_name=request.display_name,
        bio=request.bio,
        date_of_birth=request.date_of_birth,
        age=request.age,
        gender=request.gender,
        height=request.height,
        looking_for=request.looking_for,
        interests=request.interests,
        location=request.location,
        latitude=request.latitude,
        longitude=request.longitude,
        occupation=request.occupation,
        education=request.education,
        relationship_goals=request.relationship_goals,
        smoking=request.smoking,
        drinking=request.drinking,
        has_children=request.has_children,
        wants_children=request.wants_children,
        languages=request.languages
    )
    
    profile_dict = profile.model_dump()
    profile_dict['created_at'] = profile_dict['created_at'].isoformat()
    profile_dict['updated_at'] = profile_dict['updated_at'].isoformat()
    
    await db.profiles.insert_one(profile_dict)
    
    # Update user profile_completed status
    await db.users.update_one(
        {"id": current_user['id']},
        {"$set": {"profile_completed": True}}
    )
    
    # Remove non-serializable fields from response
    response_profile = {k: v for k, v in profile_dict.items() if k != '_id'}
    return {"message": "تم إنشاء الملف الشخصي بنجاح", "profile": response_profile}


@api_router.get("/profile/me")
async def get_my_profile(current_user: dict = Depends(get_current_user)):
    profile = await db.profiles.find_one({"user_id": current_user['id']}, {"_id": 0})
    
    if not profile:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="الملف الشخصي غير موجود"
        )
    
    # Use serialize_mongo_doc to convert datetime objects to ISO strings
    return serialize_mongo_doc(profile)



@api_router.get("/me")
async def get_current_user_info(current_user: dict = Depends(get_current_user)):
    """Get current user information including language preference"""
    user = await db.users.find_one({"id": current_user['id']}, {"_id": 0})
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    # Return essential user info including language
    return {
        "id": user.get('id'),
        "email": user.get('email'),
        "phone": user.get('phone'),
        "name": user.get('name'),
        "language": user.get('language', 'en'),  # Default to 'en'
        "premium_tier": user.get('premium_tier', 'free')
    }


@api_router.get("/usage-stats")
async def get_usage_stats(current_user: dict = Depends(get_current_user)):
    """Get current usage statistics for free users"""
    # Check and reset if needed
    user = await check_and_reset_weekly_limits(current_user)
    
    # Refresh user data
    user = await db.users.find_one({"id": current_user['id']}, {"_id": 0})
    
    premium_tier = user.get('premium_tier', 'free')
    
    if premium_tier in ['gold', 'platinum']:
        return {
            "premium_tier": premium_tier,
            "is_premium": True,
            "likes": {
                "unlimited": True,
                "sent": user.get('likes_sent_this_week', 0),
                "remaining": None
            },
            "messages": {
                "unlimited": True,
                "sent": user.get('messages_sent_this_week', 0),
                "remaining": None
            }
        }
    
    # Free user
    likes_sent = user.get('likes_sent_this_week', 0)
    messages_sent = user.get('messages_sent_this_week', 0)
    
    return {
        "premium_tier": "free",
        "is_premium": False,
        "likes": {
            "unlimited": False,
            "limit": 12,
            "sent": likes_sent,
            "remaining": max(0, 12 - likes_sent)
        },
        "messages": {
            "unlimited": False,
            "limit": 10,
            "sent": messages_sent,
            "remaining": max(0, 10 - messages_sent)
        },
        "week_start_date": user.get('week_start_date')
    }


@api_router.put("/profile/update")
async def update_profile(request: ProfileUpdateRequest, current_user: dict = Depends(get_current_user)):
    profile = await db.profiles.find_one({"user_id": current_user['id']}, {"_id": 0})
    
    # If profile doesn't exist, create it
    if not profile:
        from datetime import date
        age = None
        
        new_profile = Profile(
            user_id=current_user['id'],
            display_name=current_user.get('name', ''),
            photos=[],
            interests=[],
            languages=[],
            age=age
        )
        
        profile_dict = new_profile.model_dump()
        profile_dict['created_at'] = profile_dict['created_at'].isoformat()
        profile_dict['updated_at'] = profile_dict['updated_at'].isoformat()
        
        await db.profiles.insert_one(profile_dict)
        profile = profile_dict
    
    # Update only provided fields (but allow empty lists/arrays)
    update_data = {}
    for key, value in request.model_dump().items():
        if value is not None:
            update_data[key] = value
        # Special handling for photos - allow empty list
        elif key == 'photos' and value is not None:
            update_data[key] = value
    
    update_data['updated_at'] = datetime.now(timezone.utc).isoformat()
    
    # If photos are being updated, ensure primary_photo_index is valid
    if 'photos' in update_data and update_data['photos']:
        if 'primary_photo_index' not in update_data:
            update_data['primary_photo_index'] = 0
        elif update_data['primary_photo_index'] >= len(update_data['photos']):
            update_data['primary_photo_index'] = 0
    
    await db.profiles.update_one(
        {"user_id": current_user['id']},
        {"$set": update_data}
    )
    
    # Return updated profile
    updated_profile = await db.profiles.find_one({"user_id": current_user['id']}, {"_id": 0})
    
    return {
        "message": "تم تحديث الملف الشخصي بنجاح",
        "profile": updated_profile
    }


@api_router.post("/profile/photo/upload")
async def upload_profile_photo(
    file: UploadFile = File(...),
    is_primary: bool = False,
    current_user: dict = Depends(get_current_user)
):
    """
    Upload photo with Cloudinary integration
    - Automatic compression and optimization
    - Organized folder structure: pizoo/users/profiles/{user_id}
    - Support for primary/avatar photo
    - Maximum 9 photos per profile
    """
    try:
        # Get current profile
        profile = await db.profiles.find_one({"user_id": current_user['id']}, {"_id": 0})
        
        if not profile:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="الملف الشخصي غير موجود"
            )
        
        # Read file content
        file_content = await file.read()
        
        # Upload to Cloudinary using ImageUploadService
        upload_result = ImageUploadService.upload_image(
            file_bytes=file_content,
            user_id=current_user['id'],
            upload_type="profile",
            filename=file.filename,
            is_primary=is_primary,
            mime_type=file.content_type
        )
        
        # Check if upload was successful
        if not upload_result.get("success"):
            error_code = upload_result.get("error_code", "UNKNOWN")
            error_message = upload_result.get("error", "فشل رفع الصورة")
            
            # Return appropriate HTTP status codes
            if error_code == "FILE_TOO_LARGE":
                raise HTTPException(
                    status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
                    detail=error_message
                )
            elif error_code == "UNSUPPORTED_TYPE":
                raise HTTPException(
                    status_code=status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
                    detail=error_message
                )
            elif error_code == "SERVICE_UNAVAILABLE":
                raise HTTPException(
                    status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                    detail=error_message
                )
            else:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=error_message
                )
        
        # Get current photos
        photos = profile.get('photos', [])
        
        # If this is the first photo or marked as primary, insert at beginning
        if is_primary or len(photos) == 0:
            photos.insert(0, upload_result['url'])
        else:
            photos.append(upload_result['url'])
        
        # Limit to 9 photos (Tinder/Bumble standard)
        if len(photos) > 9:
            photos = photos[:9]
        
        # Update profile with new photo
        await db.profiles.update_one(
            {"user_id": current_user['id']},
            {"$set": {
                "photos": photos,
                "updated_at": datetime.now(timezone.utc).isoformat()
            }}
        )
        
        return {
            "success": True,
            "message": "تم رفع الصورة بنجاح",
            "photo": {
                "url": upload_result['url'],
                "webp_url": upload_result.get('webp_url'),
                "public_id": upload_result.get('public_id'),
                "width": upload_result.get('width'),
                "height": upload_result.get('height'),
                "is_primary": is_primary or len(photos) == 1
            },
            "total_photos": len(photos)
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logging.error(f"Photo upload error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="حدث خطأ أثناء رفع الصورة"
        )



@api_router.post("/media/upload")
async def upload_media(
    file: UploadFile = File(...),
    upload_type: str = Form("profile"),  # profile, story, verification, avatar
    is_primary: bool = Form(False),
    current_user: dict = Depends(get_current_user)
):
    """
    General media upload endpoint
    - Auto-orient and strip EXIF metadata
    - Resize to max 1600px on longest side
    - Generate WebP preview
    - Store in users/<userId>/ folder
    - Return secure HTTPS URLs
    
    Supported types: profile, story, verification, avatar
    Max size: 5MB (configurable via MAX_IMAGE_MB)
    Allowed formats: JPEG, PNG, WebP (configurable via ALLOWED_MIME)
    """
    try:
        # Read file content
        file_content = await file.read()
        
        # Upload to Cloudinary using ImageUploadService
        upload_result = ImageUploadService.upload_image(
            file_bytes=file_content,
            user_id=current_user['id'],
            upload_type=upload_type,
            filename=file.filename,
            is_primary=is_primary,
            mime_type=file.content_type
        )
        
        # Check if upload was successful
        if not upload_result.get("success"):
            error_code = upload_result.get("error_code", "UNKNOWN")
            error_message = upload_result.get("error", "فشل رفع الصورة")
            
            # Return appropriate HTTP status codes
            if error_code == "FILE_TOO_LARGE":
                raise HTTPException(
                    status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
                    detail=error_message
                )
            elif error_code == "UNSUPPORTED_TYPE":
                raise HTTPException(
                    status_code=status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
                    detail=error_message
                )
            elif error_code == "SERVICE_UNAVAILABLE":
                raise HTTPException(
                    status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                    detail=error_message
                )
            else:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=error_message
                )
        
        return {
            "success": True,
            "message": "تم رفع الملف بنجاح",
            "media": {
                "url": upload_result['url'],
                "webp_url": upload_result.get('webp_url'),
                "public_id": upload_result.get('public_id'),
                "width": upload_result.get('width'),
                "height": upload_result.get('height'),
                "format": upload_result.get('format'),
                "size": upload_result.get('size'),
                "type": upload_type
            }
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logging.error(f"Media upload error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="حدث خطأ أثناء رفع الملف"
        )


@api_router.delete("/profile/photo/{index}")
async def delete_photo(index: int, current_user: dict = Depends(get_current_user)):
    profile = await db.profiles.find_one({"user_id": current_user['id']}, {"_id": 0})
    
    if not profile:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="الملف الشخصي غير موجود"
        )
    
    photos = profile.get('photos', [])
    if index < 0 or index >= len(photos):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="رقم الصورة غير صحيح"
        )
    
    photos.pop(index)
    
    await db.profiles.update_one(
        {"user_id": current_user['id']},
        {"$set": {"photos": photos, "updated_at": datetime.now(timezone.utc).isoformat()}}
    )
    
    return {"message": "تم حذف الصورة بنجاح"}


# Soft Delete Account - GDPR Compliance
async def purge_user_assets_background(user_id: str):
    """
    Background task to delete user-related data
    This includes: messages, matches, swipes, photos, etc.
    """
    try:
        # Delete user messages
        await db.messages.delete_many({"$or": [{"sender_id": user_id}, {"receiver_id": user_id}]})
        
        # Delete user swipes
        await db.swipes.delete_many({"$or": [{"user_id": user_id}, {"swiped_user_id": user_id}]})
        
        # Delete user matches
        await db.matches.delete_many({"$or": [{"user1_id": user_id}, {"user2_id": user_id}]})
        
        # Delete user likes
        await db.likes.delete_many({"$or": [{"from_user_id": user_id}, {"to_user_id": user_id}]})
        
        # Delete user notifications
        await db.notifications.delete_many({"user_id": user_id})
        
        # Delete user sessions
        await db.sessions.delete_many({"user_id": user_id})
        
        # Delete user profile
        await db.profiles.delete_one({"user_id": user_id})
        
        # TODO: Delete photos from Cloudinary/S3
        # image_service.delete_user_photos(user_id)
        
        logging.info(f"✅ Successfully purged all data for user: {user_id}")
    except Exception as e:
        logging.error(f"❌ Failed to purge user assets for {user_id}: {e}")


@api_router.delete("/users/me", status_code=204)
async def delete_my_account(
    background_tasks: BackgroundTasks,
    current_user: dict = Depends(get_current_user)
):
    """
    Delete user account (GDPR compliant soft delete)
    - Marks account as deleted immediately
    - Schedules background task to purge all related data
    """
    user_id = current_user.get('id')
    
    # Check if user exists
    user = await db.users.find_one({"id": user_id})
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Check if already deleted
    if user.get('is_deleted'):
        raise HTTPException(status_code=400, detail="Account already deleted")
    
    # Soft delete - mark as deleted
    await db.users.update_one(
        {"id": user_id},
        {
            "$set": {
                "is_deleted": True,
                "deleted_at": datetime.now(timezone.utc),
                "email": f"deleted_{user_id}@deleted.com",  # Anonymize email
                "phone_number": "",  # Clear phone
                "name": "Deleted User"  # Anonymize name
            }
        }
    )
    
    # Schedule background purge
    background_tasks.add_task(purge_user_assets_background, user_id)
    
    logging.info(f"🗑️ User account marked for deletion: {user_id}")
    return


@api_router.get("/profiles/discover")
async def discover_profiles(
    current_user: dict = Depends(get_current_user), 
    limit: int = 20,
    category: Optional[str] = None,
    min_age: Optional[int] = None,
    max_age: Optional[int] = None,
    max_distance: Optional[int] = None,
    gender: Optional[str] = None
):
    """
    Discover profiles with advanced filtering and smart matching
    """
    # Get current user's profile
    my_profile = await db.profiles.find_one({"user_id": current_user['id']}, {"_id": 0})
    
    if not my_profile:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="يجب إكمال ملفك الشخصي أولاً"
        )
    
    # Get users already swiped
    swiped = await db.swipes.find({"user_id": current_user['id']}, {"_id": 0, "swiped_user_id": 1}).to_list(length=1000)
    swiped_ids = [s['swiped_user_id'] for s in swiped]
    
    # Get blocked users (both ways - users I blocked and users who blocked me)
    my_blocks = await db.blocks.find({"blocker_id": current_user['id']}, {"_id": 0, "blocked_user_id": 1}).to_list(length=1000)
    blocked_me = await db.blocks.find({"blocked_user_id": current_user['id']}, {"_id": 0, "blocker_id": 1}).to_list(length=1000)
    
    blocked_ids = [b['blocked_user_id'] for b in my_blocks] + [b['blocker_id'] for b in blocked_me]
    
    # Combine all excluded IDs
    excluded_ids = list(set(swiped_ids + blocked_ids))
    
    # Build filter query
    query = {
        "user_id": {"$ne": current_user['id'], "$nin": excluded_ids}
    }
    
    # Apply filters
    if category:
        # Filter by interests/category
        query["interests"] = {"$in": [category]}
    
    if gender:
        query["gender"] = gender
    
    # Age filter
    if min_age or max_age:
        age_filter = {}
        if min_age:
            age_filter["$gte"] = min_age
        if max_age:
            age_filter["$lte"] = max_age
        if age_filter:
            query["age"] = age_filter
    
    # Get filtered profiles
    profiles = await db.profiles.find(query, {"_id": 0}).limit(limit * 2).to_list(length=limit * 2)
    
    # Filter by distance if user has location coordinates
    if max_distance and my_profile.get('latitude') and my_profile.get('longitude'):
        filtered_by_distance = []
        for profile in profiles:
            if profile.get('latitude') and profile.get('longitude'):
                distance = calculate_distance(
                    my_profile['latitude'], my_profile['longitude'],
                    profile['latitude'], profile['longitude']
                )
                if distance <= max_distance:
                    profile['distance'] = round(distance, 1)  # Add distance to profile
                    filtered_by_distance.append(profile)
            else:
                # Include profiles without location data
                profile['distance'] = None
                filtered_by_distance.append(profile)
        profiles = filtered_by_distance
    else:
        # Add distance to all profiles if coordinates available
        for profile in profiles:
            if (my_profile.get('latitude') and my_profile.get('longitude') and 
                profile.get('latitude') and profile.get('longitude')):
                distance = calculate_distance(
                    my_profile['latitude'], my_profile['longitude'],
                    profile['latitude'], profile['longitude']
                )
                profile['distance'] = round(distance, 1)
            else:
                profile['distance'] = None
    
    # Score and sort profiles by compatibility
    scored_profiles = []
    for profile in profiles:
        score = 0
        
        # Interest matching (highest weight - 40 points)
        if my_profile.get('interests') and profile.get('interests'):
            common_interests = set(my_profile['interests']) & set(profile['interests'])
            score += len(common_interests) * 8
        
        # Relationship goals matching (30 points)
        if my_profile.get('relationship_goals') == profile.get('relationship_goals'):
            score += 30
        elif my_profile.get('relationship_goals') and profile.get('relationship_goals'):
            # Partial match for similar goals
            my_goals = my_profile.get('relationship_goals', '')
            their_goals = profile.get('relationship_goals', '')
            if 'long-term' in my_goals and 'long-term' in their_goals:
                score += 15
            elif 'short-term' in my_goals and 'short-term' in their_goals:
                score += 15
        
        # Age compatibility (15 points)
        if my_profile.get('age') and profile.get('age'):
            age_diff = abs(my_profile['age'] - profile['age'])
            if age_diff <= 3:
                score += 15
            elif age_diff <= 5:
                score += 10
            elif age_diff <= 10:
                score += 5
        
        # Language matching (10 points)
        if my_profile.get('languages') and profile.get('languages'):
            common_languages = set(my_profile['languages']) & set(profile['languages'])
            score += min(len(common_languages) * 5, 10)
        
        # Lifestyle compatibility (5 points total)
        lifestyle_factors = ['pets', 'drinking', 'smoking', 'exercise', 'dietary_preference']
        matching_lifestyle = 0
        for factor in lifestyle_factors:
            if my_profile.get(factor) and profile.get(factor):
                if my_profile.get(factor) == profile.get(factor):
                    matching_lifestyle += 1
        score += matching_lifestyle
        
        # Proximity bonus (20 points) - closer users get higher scores
        if profile.get('distance') is not None:
            distance = profile['distance']
            if distance <= 5:  # Within 5 km
                score += 20
            elif distance <= 15:  # Within 15 km
                score += 15
            elif distance <= 30:  # Within 30 km
                score += 10
            elif distance <= 50:  # Within 50 km
                score += 5
        
        # Profile completeness bonus (photos, bio, interests) - encourage complete profiles
        if profile.get('photos') and len(profile.get('photos', [])) >= 3:
            score += 5
        if profile.get('bio') and len(profile.get('bio', '')) > 50:
            score += 3
        if profile.get('interests') and len(profile.get('interests', [])) >= 3:
            score += 2
        
        scored_profiles.append((profile, score))
    
    # Sort by score descending and return top results
    scored_profiles.sort(key=lambda x: x[1], reverse=True)
    final_profiles = [profile for profile, score in scored_profiles[:limit]]
    
    return {"profiles": final_profiles}



# Duplicate swipe endpoint removed - using the one at line 1535


@api_router.get("/profiles/{user_id}")
async def get_profile_by_id(
    user_id: str,
    current_user: dict = Depends(get_current_user)
):
    """
    Get a specific user profile by user_id
    """
    # Fetch the profile
    profile = await db.profiles.find_one({"user_id": user_id}, {"_id": 0})
    
    if not profile:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Profile not found"
        )
    
    # Calculate distance if both users have GPS coordinates
    my_profile = await db.profiles.find_one({"user_id": current_user['id']}, {"_id": 0})
    if my_profile and profile.get('latitude') and profile.get('longitude') and my_profile.get('latitude') and my_profile.get('longitude'):
        profile['distance'] = calculate_distance(
            my_profile['latitude'],
            my_profile['longitude'],
            profile['latitude'],
            profile['longitude']
        )
    
    return profile


@api_router.get("/profiles/top-picks")
async def get_top_picks(current_user: dict = Depends(get_current_user)):
    """
    Get daily top picks based on user preferences and compatibility
    """
    # Get current user's profile
    my_profile = await db.profiles.find_one({"user_id": current_user['id']}, {"_id": 0})
    
    if not my_profile:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="يجب إكمال ملفك الشخصي أولاً"
        )
    
    # Get users already swiped
    swiped = await db.swipes.find({"user_id": current_user['id']}, {"_id": 0, "swiped_user_id": 1}).to_list(length=1000)
    swiped_ids = [s['swiped_user_id'] for s in swiped]
    
    # Get all profiles
    all_profiles = await db.profiles.find(
        {
            "user_id": {"$ne": current_user['id'], "$nin": swiped_ids}
        },
        {"_id": 0}
    ).to_list(length=100)
    
    # Score profiles based on compatibility
    scored_profiles = []
    for profile in all_profiles:
        score = 0
        
        # Interest matching (30 points)
        if my_profile.get('interests') and profile.get('interests'):
            common_interests = set(my_profile['interests']) & set(profile['interests'])
            score += len(common_interests) * 10
        
        # Relationship goals matching (25 points)
        if my_profile.get('relationship_goals') == profile.get('relationship_goals'):
            score += 25
        
        # Age compatibility (20 points)
        if my_profile.get('age') and profile.get('age'):
            age_diff = abs(my_profile['age'] - profile['age'])
            if age_diff <= 5:
                score += 20
            elif age_diff <= 10:
                score += 10
        
        # Language matching (15 points)
        if my_profile.get('languages') and profile.get('languages'):
            common_languages = set(my_profile['languages']) & set(profile['languages'])
            score += len(common_languages) * 5
        
        # Lifestyle compatibility (10 points)
        lifestyle_factors = ['pets', 'drinking', 'smoking', 'exercise']
        for factor in lifestyle_factors:
            if my_profile.get(factor) == profile.get(factor):
                score += 2.5
        
        scored_profiles.append((profile, score))
    
    # Sort by score and get top 10
    scored_profiles.sort(key=lambda x: x[1], reverse=True)
    top_picks = [profile for profile, score in scored_profiles[:10]]
    
    return {"profiles": top_picks}


@api_router.post("/swipe")
async def swipe_action(request: SwipeRequest, current_user: dict = Depends(get_current_user)):
    # Check if action is a like and enforce limits
    if request.action in ['like', 'super_like']:
        can_like, message = await can_send_like(current_user)
        if not can_like:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=message
            )
    
    # Save swipe
    swipe = Swipe(
        user_id=current_user['id'],
        swiped_user_id=request.swiped_user_id,
        action=request.action
    )
    
    swipe_dict = swipe.model_dump()
    swipe_dict['created_at'] = swipe_dict['created_at'].isoformat()
    
    await db.swipes.insert_one(swipe_dict)
    
    # Increment like counter if it's a like action
    if request.action in ['like', 'super_like']:
        await increment_likes_count(current_user['id'])
    
    # Check for match if action is like or super_like
    is_match = False
    if request.action in ['like', 'super_like']:
        # Check if the other user also liked
        other_swipe = await db.swipes.find_one({
            "user_id": request.swiped_user_id,
            "swiped_user_id": current_user['id'],
            "action": {"$in": ['like', 'super_like']}
        })
        
        if other_swipe:
            # It's a match!
            is_match = True
            
            # Check if match already exists
            existing_match = await db.matches.find_one({
                "$or": [
                    {"user1_id": current_user['id'], "user2_id": request.swiped_user_id},
                    {"user1_id": request.swiped_user_id, "user2_id": current_user['id']}
                ]
            })
            
            if not existing_match:
                match = Match(
                    user1_id=current_user['id'],
                    user2_id=request.swiped_user_id
                )
                
                match_dict = match.model_dump()
                match_dict['matched_at'] = match_dict['matched_at'].isoformat()
                
                await db.matches.insert_one(match_dict)
                
                # Create notifications for both users
                current_user_profile = await db.profiles.find_one(
                    {"user_id": current_user['id']},
                    {"_id": 0, "display_name": 1, "photos": 1}
                )
                swiped_user_profile = await db.profiles.find_one(
                    {"user_id": request.swiped_user_id},
                    {"_id": 0, "display_name": 1, "photos": 1}
                )
                
                # Notification for current user
                if swiped_user_profile:
                    await create_notification(
                        user_id=current_user['id'],
                        notification_type="new_match",
                        title="🎉 تطابق جديد!",
                        message=f"لديك تطابق جديد مع {swiped_user_profile.get('display_name', 'مستخدم')}",
                        link=f"/chat/{match.id}",
                        related_user_id=request.swiped_user_id,
                        related_user_name=swiped_user_profile.get('display_name'),
                        related_user_photo=swiped_user_profile.get('photos', [None])[0] if swiped_user_profile.get('photos') else None
                    )
                
                # Notification for swiped user
                if current_user_profile:
                    await create_notification(
                        user_id=request.swiped_user_id,
                        notification_type="new_match",
                        title="🎉 تطابق جديد!",
                        message=f"لديك تطابق جديد مع {current_user_profile.get('display_name', 'مستخدم')}",
                        link=f"/chat/{match.id}",
                        related_user_id=current_user['id'],
                        related_user_name=current_user_profile.get('display_name'),
                        related_user_photo=current_user_profile.get('photos', [None])[0] if current_user_profile.get('photos') else None
                    )
        else:
            # No match yet, but send notification for like received
            if request.action == 'super_like':
                current_user_profile = await db.profiles.find_one(
                    {"user_id": current_user['id']},
                    {"_id": 0, "display_name": 1, "photos": 1}
                )
                if current_user_profile:
                    await create_notification(
                        user_id=request.swiped_user_id,
                        notification_type="super_like",
                        title="⭐ Super Like!",
                        message=f"{current_user_profile.get('display_name', 'شخص ما')} أرسل لك Super Like!",
                        link=f"/profile/{current_user['id']}",
                        related_user_id=current_user['id'],
                        related_user_name=current_user_profile.get('display_name'),
                        related_user_photo=current_user_profile.get('photos', [None])[0] if current_user_profile.get('photos') else None
                    )
    
    # Get remaining limits for response
    remaining_likes = None
    if current_user.get('premium_tier') not in ['gold', 'platinum']:
        updated_user = await db.users.find_one({"id": current_user['id']}, {"_id": 0})
        likes_sent = updated_user.get('likes_sent_this_week', 0)
        remaining_likes = max(0, 12 - likes_sent)
    
    return {
        "success": True,
        "is_match": is_match,
        "action": request.action,
        "remaining_likes": remaining_likes
    }


@api_router.get("/matches")
async def get_matches(current_user: dict = Depends(get_current_user)):
    # Get all matches
    matches = await db.matches.find({
        "$or": [
            {"user1_id": current_user['id']},
            {"user2_id": current_user['id']}
        ],
        "unmatched": False
    }, {"_id": 0}).to_list(length=100)
    
    # Get profiles for matches
    match_profiles = []
    for match in matches:
        other_user_id = match['user2_id'] if match['user1_id'] == current_user['id'] else match['user1_id']
        profile = await db.profiles.find_one({"user_id": other_user_id}, {"_id": 0})
        if profile:
            match_profiles.append({
                "match_id": match['id'],
                "matched_at": match['matched_at'],
                "profile": profile
            })
    
    return {"matches": match_profiles}


@api_router.get("/matches/{match_id}")
async def get_match(match_id: str, current_user: dict = Depends(get_current_user)):
    """Get a specific match by ID"""
    match = await db.matches.find_one({
        "id": match_id,
        "$or": [
            {"user1_id": current_user['id']},
            {"user2_id": current_user['id']}
        ]
    }, {"_id": 0})
    
    if not match:
        raise HTTPException(status_code=404, detail="Match not found")
    
    return match


@api_router.get("/likes/sent")
async def get_sent_likes(current_user: dict = Depends(get_current_user)):
    # Get users I liked
    likes = await db.swipes.find({
        "user_id": current_user['id'],
        "action": {"$in": ['like', 'super_like']}
    }, {"_id": 0}).to_list(length=100)
    
    # Get profiles
    profiles = []
    for like in likes:
        profile = await db.profiles.find_one({"user_id": like['swiped_user_id']}, {"_id": 0})
        if profile:
            profiles.append(profile)
    
    return {"profiles": profiles}


@api_router.get("/likes/received")
async def get_received_likes(current_user: dict = Depends(get_current_user)):
    # Get users who liked me
    likes = await db.swipes.find({
        "swiped_user_id": current_user['id'],
        "action": {"$in": ['like', 'super_like']}
    }, {"_id": 0}).to_list(length=100)
    
    # Get profiles
    profiles = []
    for like in likes:
        profile = await db.profiles.find_one({"user_id": like['user_id']}, {"_id": 0})
        if profile:
            profiles.append(profile)
    
    return {"profiles": profiles}


@api_router.post("/seed/dummy-profiles")
async def create_dummy_profiles():
    """Create 50 diverse dummy profiles for testing"""
    
    photos_list = [
        ["https://images.unsplash.com/photo-1560250097-0b93528c311a"],
        ["https://images.unsplash.com/photo-1629425733761-caae3b5f2e50"],
        ["https://images.unsplash.com/photo-1657128344786-360c3f8e57e5"],
        ["https://images.unsplash.com/photo-1652471943570-f3590a4e52ed"],
        ["https://images.unsplash.com/photo-1563170446-9c3c0622d8a9"],
        ["https://images.unsplash.com/photo-1606143412458-acc5f86de897"],
        ["https://images.unsplash.com/photo-1557053910-d9eadeed1c58"],
        ["https://images.unsplash.com/photo-1580489944761-15a19d654956"],
        ["https://images.unsplash.com/photo-1557053908-4793c484d06f"],
        ["https://images.unsplash.com/photo-1592621385612-4d7129426394"],
        ["https://images.unsplash.com/photo-1573496359142-b8d87734a5a2"],
        ["https://images.unsplash.com/photo-1519085360753-af0119f7cbe7"],
        ["https://images.unsplash.com/photo-1573497019940-1c28c88b4f3e"],
        ["https://images.unsplash.com/photo-1633037543479-a70452ea1e12"],
        ["https://images.pexels.com/photos/9504516/pexels-photo-9504516.jpeg"],
        ["https://images.pexels.com/photos/6925361/pexels-photo-6925361.jpeg"],
        ["https://images.pexels.com/photos/774909/pexels-photo-774909.jpeg"],
        ["https://images.pexels.com/photos/1181686/pexels-photo-1181686.jpeg"],
        ["https://images.pexels.com/photos/2182970/pexels-photo-2182970.jpeg"],
        ["https://images.pexels.com/photos/2381069/pexels-photo-2381069.jpeg"]
    ]
    
    dummy_data = [
        {"name": "Sarah", "name_ar": "سارة", "bio": "Love traveling and photography 📸✈️", "bio_ar": "أحب السفر والتصوير 📸✈️", "gender": "female", "age": 28, "height": 165, "location": "New York, USA", "interests": ["السفر", "التصوير", "القراءة"], "occupation": "Graphic Designer", "photo_idx": 0},
        {"name": "Ahmed", "name_ar": "أحمد", "bio": "Engineer & fitness enthusiast 💪", "bio_ar": "مهندس ومهتم باللياقة 💪", "gender": "male", "age": 32, "height": 180, "location": "Dubai, UAE", "interests": ["الرياضة", "التكنولوجيا", "السفر"], "occupation": "Software Engineer", "photo_idx": 1},
        {"name": "Emily", "name_ar": "إيميلي", "bio": "Artist & coffee lover ☕🎨", "bio_ar": "فنانة ومحبة للقهوة ☕🎨", "gender": "female", "age": 26, "height": 168, "location": "Paris, France", "interests": ["الفن", "القهوة", "الموسيقى"], "occupation": "Artist", "photo_idx": 2},
        {"name": "Omar", "name_ar": "عمر", "bio": "Doctor passionate about helping people 🩺", "bio_ar": "طبيب شغوف بمساعدة الناس 🩺", "gender": "male", "age": 35, "height": 178, "location": "Cairo, Egypt", "interests": ["الطب", "القراءة", "الرياضة"], "occupation": "Doctor", "photo_idx": 3},
        {"name": "Sofia", "name_ar": "صوفيا", "bio": "Marketing specialist & foodie 🍕", "bio_ar": "متخصصة تسويق وعاشقة للطعام 🍕", "gender": "female", "age": 29, "height": 163, "location": "Barcelona, Spain", "interests": ["التسويق", "الطعام", "السفر"], "occupation": "Marketing Specialist", "photo_idx": 4},
        {"name": "Karim", "name_ar": "كريم", "bio": "Pilot exploring the world ✈️", "bio_ar": "طيار يستكشف العالم ✈️", "gender": "male", "age": 33, "height": 183, "location": "Riyadh, Saudi Arabia", "interests": ["الطيران", "السفر", "المغامرات"], "occupation": "Pilot", "photo_idx": 5},
        {"name": "Layla", "name_ar": "ليلى", "bio": "Writer & bookworm 📚✍️", "bio_ar": "كاتبة ومحبة للكتب 📚✍️", "gender": "female", "age": 27, "height": 160, "location": "Beirut, Lebanon", "interests": ["الكتابة", "القراءة", "الأدب"], "occupation": "Writer", "photo_idx": 6},
        {"name": "Marco", "name_ar": "ماركو", "bio": "Chef & food enthusiast 🍝👨‍🍳", "bio_ar": "طاهٍ ومحب للطعام 🍝👨‍🍳", "gender": "male", "age": 30, "height": 175, "location": "Rome, Italy", "interests": ["الطبخ", "الطعام", "السفر"], "occupation": "Chef", "photo_idx": 7},
        {"name": "Noor", "name_ar": "نور", "bio": "Teacher & nature lover 🌿", "bio_ar": "معلمة ومحبة للطبيعة 🌿", "gender": "female", "age": 25, "height": 162, "location": "Doha, Qatar", "interests": ["التعليم", "الطبيعة", "اليوغا"], "occupation": "Teacher", "photo_idx": 8},
        {"name": "Lucas", "name_ar": "لوكاس", "bio": "Entrepreneur & tech lover 💻", "bio_ar": "رائد أعمال ومحب للتقنية 💻", "gender": "male", "age": 31, "height": 179, "location": "London, UK", "interests": ["ريادة الأعمال", "التكنولوجيا", "الابتكار"], "occupation": "Entrepreneur", "photo_idx": 9},
        {"name": "Aisha", "name_ar": "عائشة", "bio": "Pharmacist & fitness lover 💊🏃‍♀️", "bio_ar": "صيدلانية ومحبة للرياضة 💊🏃‍♀️", "gender": "female", "age": 28, "height": 164, "location": "Manama, Bahrain", "interests": ["الصحة", "الرياضة", "التغذية"], "occupation": "Pharmacist", "photo_idx": 10},
        {"name": "David", "name_ar": "ديفيد", "bio": "Architect & design enthusiast 🏗️", "bio_ar": "مهندس معماري ومحب للتصميم 🏗️", "gender": "male", "age": 34, "height": 181, "location": "Sydney, Australia", "interests": ["الهندسة", "التصميم", "الفن"], "occupation": "Architect", "photo_idx": 11},
        {"name": "Mariam", "name_ar": "مريم", "bio": "Lawyer & justice seeker ⚖️", "bio_ar": "محامية وباحثة عن العدالة ⚖️", "gender": "female", "age": 30, "height": 167, "location": "Amman, Jordan", "interests": ["القانون", "القراءة", "العدالة"], "occupation": "Lawyer", "photo_idx": 12},
        {"name": "Alex", "name_ar": "أليكس", "bio": "Photographer capturing moments 📷", "bio_ar": "مصور يوثق اللحظات 📷", "gender": "male", "age": 29, "height": 176, "location": "Berlin, Germany", "interests": ["التصوير", "السفر", "الفن"], "occupation": "Photographer", "photo_idx": 13},
        {"name": "Yasmin", "name_ar": "ياسمين", "bio": "Journalist & storyteller 📰", "bio_ar": "صحفية وراوية قصص 📰", "gender": "female", "age": 27, "height": 161, "location": "Casablanca, Morocco", "interests": ["الصحافة", "الكتابة", "السفر"], "occupation": "Journalist", "photo_idx": 14},
        {"name": "Ryan", "name_ar": "رايان", "bio": "Personal trainer & health coach 🏋️", "bio_ar": "مدرب شخصي ومدرب صحة 🏋️", "gender": "male", "age": 28, "height": 182, "location": "Los Angeles, USA", "interests": ["اللياقة", "الصحة", "التغذية"], "occupation": "Personal Trainer", "photo_idx": 15},
        {"name": "Lara", "name_ar": "لارا", "bio": "Fashion designer & trendsetter 👗", "bio_ar": "مصممة أزياء ورائدة موضة 👗", "gender": "female", "age": 26, "height": 169, "location": "Milan, Italy", "interests": ["الموضة", "التصميم", "الفن"], "occupation": "Fashion Designer", "photo_idx": 16},
        {"name": "Hassan", "name_ar": "حسن", "bio": "Financial analyst & investor 📈", "bio_ar": "محلل مالي ومستثمر 📈", "gender": "male", "age": 33, "height": 177, "location": "Abu Dhabi, UAE", "interests": ["المال", "الاستثمار", "القراءة"], "occupation": "Financial Analyst", "photo_idx": 17},
        {"name": "Maya", "name_ar": "مايا", "bio": "Dentist with a bright smile 😁🦷", "bio_ar": "طبيبة أسنان بابتسامة مشرقة 😁🦷", "gender": "female", "age": 29, "height": 165, "location": "Toronto, Canada", "interests": ["طب الأسنان", "الصحة", "السفر"], "occupation": "Dentist", "photo_idx": 18},
        {"name": "Zaid", "name_ar": "زيد", "bio": "Data scientist & AI enthusiast 🤖", "bio_ar": "عالم بيانات ومحب للذكاء الاصطناعي 🤖", "gender": "male", "age": 30, "height": 174, "location": "Jeddah, Saudi Arabia", "interests": ["البيانات", "الذكاء الاصطناعي", "التكنولوجيا"], "occupation": "Data Scientist", "photo_idx": 19}
    ]
    
    dummy_users_data = []
    dummy_profiles_data = []
    
    for i, data in enumerate(dummy_data):
        user_id = f"dummy-user-{i}"
        
        # User
        dummy_users_data.append({
            "id": user_id,
            "name": data['name'],
            "email": f"dummy{i}@pizoo.com",
            "phone_number": f"+123456789{i:02d}",
            "password_hash": pwd_context.hash("dummy123"),
            "created_at": datetime.now(timezone.utc).isoformat(),
            "trial_end_date": (datetime.now(timezone.utc) + timedelta(days=14)).isoformat(),
            "subscription_status": "trial",
            "terms_accepted": True,
            "terms_accepted_at": datetime.now(timezone.utc).isoformat(),
            "profile_completed": True
        })
        
        # Profile
        photo_url = photos_list[data['photo_idx']][0] if data['photo_idx'] < len(photos_list) else ""
        
        dummy_profiles_data.append({
            "id": f"profile-{i}",
            "user_id": user_id,
            "display_name": data['name_ar'],
            "bio": data['bio_ar'],
            "date_of_birth": f"{1997 - data['age']}-06-15",
            "gender": data['gender'],
            "height": data['height'],
            "looking_for": "serious" if i % 2 == 0 else "casual",
            "interests": data['interests'],
            "photos": [photo_url] if photo_url else [],
            "location": data['location'],
            "occupation": data['occupation'],
            "education": "Bachelor's Degree" if i % 3 == 0 else "Master's Degree",
            "relationship_goals": "serious" if i % 2 == 0 else "casual",
            "smoking": "no",
            "drinking": "sometimes" if i % 3 == 0 else "no",
            "has_children": False,
            "wants_children": True if i % 2 == 0 else False,
            "languages": ["العربية", "English"] if i % 2 == 0 else ["English"],
            "created_at": datetime.now(timezone.utc).isoformat(),
            "updated_at": datetime.now(timezone.utc).isoformat()
        })
    
    dummy_users = dummy_users_data
    
    dummy_profiles = [
        {
            "id": f"profile-{i}",
            "user_id": f"dummy-user-{i}",
            "display_name": profile['name'],
            "bio": profile['bio'],
            "date_of_birth": profile['dob'],
            "gender": profile['gender'],
            "height": profile['height'],
            "looking_for": profile['looking_for'],
            "interests": profile['interests'],
            "location": profile['location'],
            "occupation": profile['occupation'],
            "education": profile['education'],
            "relationship_goals": profile['goals'],
            "smoking": "no",
            "drinking": "no",
            "has_children": False,
            "wants_children": True,
            "languages": ["العربية", "الإنجليزية"],
            "photos": [],
            "created_at": datetime.now(timezone.utc).isoformat(),
            "updated_at": datetime.now(timezone.utc).isoformat()
        }
        for i, profile in enumerate([
            {"name": "سارة", "bio": "أحب السفر والقراءة والمغامرات الجديدة ☕📚✈️", "dob": "1995-05-15", "gender": "female", "height": 165, "looking_for": "علاقة جدية", "interests": ["السفر", "القراءة", "التصوير", "الطبخ"], "location": "جدة، السعودية", "occupation": "مصممة جرافيك", "education": "بكالوريوس", "goals": "serious"},
            {"name": "محمد", "bio": "رياضي ومهتم بالتكنولوجيا. أبحث عن شريكة حياة 💪🏋️", "dob": "1992-08-20", "gender": "male", "height": 180, "looking_for": "علاقة جدية", "interests": ["الرياضة", "التكنولوجيا", "السفر", "البرمجة"], "location": "الرياض، السعودية", "occupation": "مهندس برمجيات", "education": "ماجستير", "goals": "serious"},
            {"name": "لينا", "bio": "طبيبة وأحب مساعدة الناس. أحب الهدوء والطبيعة 🌸🌿", "dob": "1994-03-10", "gender": "female", "height": 168, "looking_for": "صداقة أولاً", "interests": ["الطب", "الطبيعة", "اليوغا", "القراءة"], "location": "دبي، الإمارات", "occupation": "طبيبة", "education": "دكتوراه", "goals": "serious"},
            {"name": "أحمد", "bio": "رائد أعمال ومحب للحياة والمغامرات 🚀💼", "dob": "1990-11-25", "gender": "male", "height": 178, "looking_for": "علاقة جدية", "interests": ["ريادة الأعمال", "السفر", "القراءة", "الرياضة"], "location": "أبوظبي، الإمارات", "occupation": "رائد أعمال", "education": "ماجستير", "goals": "serious"},
            {"name": "نور", "bio": "معلمة ومهتمة بالفن والثقافة. أحب التعرف على أشخاص جدد 🎨📖", "dob": "1996-07-12", "gender": "female", "height": 162, "looking_for": "صداقة", "interests": ["الفن", "الثقافة", "الموسيقى", "التعليم"], "location": "الدوحة، قطر", "occupation": "معلمة", "education": "بكالوريوس", "goals": "friendship"},
            {"name": "يوسف", "bio": "مصور فوتوغرافي أحب توثيق اللحظات الجميلة 📷✨", "dob": "1993-04-18", "gender": "male", "height": 175, "looking_for": "علاقة عابرة", "interests": ["التصوير", "السفر", "الفن", "الطبيعة"], "location": "الكويت، الكويت", "occupation": "مصور", "education": "بكالوريوس", "goals": "casual"},
            {"name": "ريم", "bio": "كاتبة ومدونة. أحب القصص والمغامرات ✍️💭", "dob": "1997-09-30", "gender": "female", "height": 160, "looking_for": "صداقة أولاً", "interests": ["الكتابة", "القراءة", "السفر", "الثقافة"], "location": "بيروت، لبنان", "occupation": "كاتبة", "education": "بكالوريوس", "goals": "friendship"},
            {"name": "عمر", "bio": "محامي ومهتم بالعدالة والقانون. أحب النقاشات العميقة ⚖️", "dob": "1991-12-05", "gender": "male", "height": 182, "looking_for": "علاقة جدية", "interests": ["القانون", "القراءة", "الشطرنج", "التاريخ"], "location": "القاهرة، مصر", "occupation": "محامي", "education": "ماجستير", "goals": "serious"},
            {"name": "مريم", "bio": "مهندسة معمارية أحب التصميم والإبداع 🏗️🎨", "dob": "1995-06-22", "gender": "female", "height": 167, "looking_for": "علاقة جدية", "interests": ["الهندسة", "التصميم", "الفن", "السفر"], "location": "عمّان، الأردن", "occupation": "مهندسة معمارية", "education": "بكالوريوس", "goals": "serious"},
            {"name": "خالد", "bio": "طيار ومحب للسماء والطيران ✈️☁️", "dob": "1989-02-14", "gender": "male", "height": 183, "looking_for": "علاقة جدية", "interests": ["الطيران", "السفر", "المغامرات", "الرياضة"], "location": "الرياض، السعودية", "occupation": "طيار", "education": "بكالوريوس", "goals": "serious"},
            {"name": "دانة", "bio": "صيدلانية ومهتمة بالصحة والرياضة 💊🏃‍♀️", "dob": "1996-10-08", "gender": "female", "height": 164, "looking_for": "صداقة أولاً", "interests": ["الصحة", "الرياضة", "التغذية", "القراءة"], "location": "المنامة، البحرين", "occupation": "صيدلانية", "education": "بكالوريوس", "goals": "friendship"},
            {"name": "فهد", "bio": "مدير تسويق ومحب للإبداع والابتكار 📊💡", "dob": "1992-03-28", "gender": "male", "height": 177, "looking_for": "علاقة عابرة", "interests": ["التسويق", "الإبداع", "التكنولوجيا", "السفر"], "location": "جدة، السعودية", "occupation": "مدير تسويق", "education": "ماجستير", "goals": "casual"},
            {"name": "ليلى", "bio": "مترجمة وأحب اللغات والثقافات المختلفة 🌍📚", "dob": "1994-08-15", "gender": "female", "height": 163, "looking_for": "صداقة", "interests": ["اللغات", "الترجمة", "السفر", "الثقافة"], "location": "الدار البيضاء، المغرب", "occupation": "مترجمة", "education": "ماجستير", "goals": "friendship"},
            {"name": "سلطان", "bio": "محلل مالي ومهتم بالاستثمار والأعمال 💰📈", "dob": "1990-05-20", "gender": "male", "height": 179, "looking_for": "علاقة جدية", "interests": ["المال", "الاستثمار", "القراءة", "الرياضة"], "location": "دبي، الإمارات", "occupation": "محلل مالي", "education": "ماجستير", "goals": "serious"},
            {"name": "جود", "bio": "طالبة طب أحلم بمساعدة الناس وتغيير العالم 🩺💗", "dob": "1998-11-11", "gender": "female", "height": 161, "looking_for": "صداقة أولاً", "interests": ["الطب", "التطوع", "القراءة", "الموسيقى"], "location": "الرياض، السعودية", "occupation": "طالبة طب", "education": "بكالوريوس", "goals": "friendship"},
            {"name": "ماجد", "bio": "مدرب رياضي ومحب للحياة الصحية 💪🏋️‍♂️", "dob": "1991-07-07", "gender": "male", "height": 181, "looking_for": "علاقة جدية", "interests": ["الرياضة", "اللياقة", "التغذية", "التحفيز"], "location": "أبوظبي، الإمارات", "occupation": "مدرب رياضي", "education": "بكالوريوس", "goals": "serious"}
        ])
    ]
    
    # Insert users and profiles
    try:
        await db.users.insert_many(dummy_users)
        await db.profiles.insert_many(dummy_profiles)
        return {
            "message": "تم إنشاء البروفايلات الوهمية بنجاح",
            "count": len(dummy_profiles)
        }
    except Exception as e:
        # Profiles might already exist
        return {
            "message": "البروفايلات موجودة بالفعل أو حدث خطأ",
            "error": str(e)
        }


# ===== Premium Subscription APIs =====

@api_router.get("/premium/subscription")
async def get_premium_subscription(current_user: dict = Depends(get_current_user)):
    """Get user's current premium subscription status"""
    subscription = await db.premium_subscriptions.find_one(
        {"user_id": current_user['id']},
        {"_id": 0}
    )
    
    if not subscription:
        # Return free tier
        return {
            "tier": "free",
            "status": "active",
            "features": {
                "unlimited_likes": False,
                "see_who_liked": False,
                "unlimited_rewinds": False,
                "super_likes_per_day": 1,
                "boosts_per_month": 0,
                "top_picks": False,
                "read_receipts": False,
                "profile_controls": False
            }
        }
    
    return subscription


@api_router.post("/premium/subscribe")
async def subscribe_premium(
    tier: str,  # gold or platinum
    duration: str,  # 1week, 1month, 3months, 6months, 1year
    current_user: dict = Depends(get_current_user)
):
    """Subscribe to premium tier (Mock - no real payment)"""
    
    # Define features based on tier
    if tier == "gold":
        features = {
            "unlimited_likes": True,
            "see_who_liked": True,
            "unlimited_rewinds": True,
            "super_likes_per_day": 5,
            "boosts_per_month": 1,
            "top_picks": True,
            "read_receipts": False,
            "profile_controls": False
        }
    elif tier == "platinum":
        features = {
            "unlimited_likes": True,
            "see_who_liked": True,
            "unlimited_rewinds": True,
            "super_likes_per_day": 10,
            "boosts_per_month": 2,
            "top_picks": True,
            "read_receipts": True,
            "profile_controls": True
        }
    else:
        raise HTTPException(status_code=400, detail="Invalid tier")
    
    # Calculate end date based on duration
    duration_map = {
        "1week": 7,
        "1month": 30,
        "3months": 90,
        "6months": 180,
        "1year": 365
    }
    
    days = duration_map.get(duration, 30)
    end_date = datetime.now(timezone.utc) + timedelta(days=days)
    
    # Check if subscription exists
    existing = await db.premium_subscriptions.find_one({"user_id": current_user['id']})
    
    subscription_data = {
        "user_id": current_user['id'],
        "tier": tier,
        "status": "active",
        "start_date": datetime.now(timezone.utc).isoformat(),
        "end_date": end_date.isoformat(),
        "features": features,
        "auto_renew": False,
        "updated_at": datetime.now(timezone.utc).isoformat()
    }
    
    if existing:
        await db.premium_subscriptions.update_one(
            {"user_id": current_user['id']},
            {"$set": subscription_data}
        )
    else:
        subscription_data["id"] = str(uuid.uuid4())
        subscription_data["created_at"] = datetime.now(timezone.utc).isoformat()
        await db.premium_subscriptions.insert_one(subscription_data)
    
    return {
        "message": f"تم الاشتراك في {tier.capitalize()} بنجاح!",
        "subscription": subscription_data
    }


@api_router.get("/premium/plans")
async def get_premium_plans():
    """Get available premium plans and pricing (Mock prices)"""
    return {
        "plans": [
            {
                "tier": "gold",
                "name": "Pizoo Gold",
                "description": "افتح جميع المميزات الأساسية",
                "features": [
                    "إعجابات غير محدودة",
                    "شاهد من أبدى إعجابه بك",
                    "تراجعات غير محدودة",
                    "5 Super Likes يومياً",
                    "1 Boost شهرياً",
                    "أفضل الاختيارات اليومية"
                ],
                "pricing": [
                    {"duration": "1week", "price": 49.99, "currency": "SAR"},
                    {"duration": "1month", "price": 149.99, "currency": "SAR"},
                    {"duration": "3months", "price": 399.99, "currency": "SAR"},
                    {"duration": "6months", "price": 699.99, "currency": "SAR"}
                ]
            },
            {
                "tier": "platinum",
                "name": "Pizoo Platinum",
                "description": "أفضل تجربة مواعدة",
                "features": [
                    "جميع مميزات Gold",
                    "رسالة قبل المطابقة",
                    "10 Super Likes يومياً",
                    "2 Boost شهرياً",
                    "إشعارات القراءة",
                    "التحكم في الملف الشخصي"
                ],
                "pricing": [
                    {"duration": "1week", "price": 79.99, "currency": "SAR"},
                    {"duration": "1month", "price": 249.99, "currency": "SAR"},
                    {"duration": "3months", "price": 649.99, "currency": "SAR"},
                    {"duration": "6months", "price": 1199.99, "currency": "SAR"}
                ]
            }
        ]
    }


# ===== Chat & Messaging APIs =====

@api_router.get("/conversations")
async def get_conversations(current_user: dict = Depends(get_current_user)):
    """Get all conversations for current user"""
    matches = await db.matches.find(
        {
            "$or": [
                {"user1_id": current_user['id']},
                {"user2_id": current_user['id']}
            ],
            "unmatched": False
        },
        {"_id": 0}
    ).to_list(length=None)
    
    conversations = []
    for match in matches:
        other_user_id = match['user2_id'] if match['user1_id'] == current_user['id'] else match['user1_id']
        
        # Get other user's profile
        other_profile = await db.profiles.find_one({"user_id": other_user_id}, {"_id": 0})
        other_user = await db.users.find_one({"id": other_user_id}, {"_id": 0})
        
        # Get last message
        last_message = await db.messages.find_one(
            {"match_id": match['id']},
            {"_id": 0},
            sort=[("created_at", -1)]
        )
        
        # Count unread messages
        unread_count = await db.messages.count_documents({
            "match_id": match['id'],
            "receiver_id": current_user['id'],
            "status": {"$ne": "read"}
        })
        
        conversations.append({
            "match_id": match['id'],
            "user": {
                "id": other_user_id,
                "name": other_user.get('name') if other_user else "Unknown",
                "display_name": other_profile.get('display_name') if other_profile else "Unknown",
                "photo": other_profile.get('photos', [None])[0] if other_profile else None,
                "is_online": False  # TODO: implement online status
            },
            "last_message": {
                "content": last_message.get('content') if last_message else None,
                "created_at": last_message.get('created_at') if last_message else match['matched_at'],
                "sender_id": last_message.get('sender_id') if last_message else None
            },
            "unread_count": unread_count,
            "matched_at": match['matched_at']
        })
    
    # Sort by last message time
    conversations.sort(key=lambda x: x['last_message']['created_at'], reverse=True)
    
    return {"conversations": conversations}


@api_router.get("/conversations/{match_id}/messages")
async def get_messages(match_id: str, current_user: dict = Depends(get_current_user)):
    """Get all messages for a conversation"""
    # Verify match exists and user is part of it
    match = await db.matches.find_one(
        {
            "id": match_id,
            "$or": [
                {"user1_id": current_user['id']},
                {"user2_id": current_user['id']}
            ]
        },
        {"_id": 0}
    )
    
    if not match:
        raise HTTPException(status_code=404, detail="Match not found")
    
    # Get messages
    messages = await db.messages.find(
        {"match_id": match_id},
        {"_id": 0}
    ).sort("created_at", 1).to_list(length=None)
    
    # Mark messages as read
    await db.messages.update_many(
        {
            "match_id": match_id,
            "receiver_id": current_user['id'],
            "status": {"$ne": "read"}
        },
        {
            "$set": {
                "status": "read",
                "read_at": datetime.now(timezone.utc).isoformat()
            }
        }
    )
    
    return {"messages": messages}


class SendMessageRequest(BaseModel):
    content: str
    message_type: str = "text"

@api_router.post("/conversations/{match_id}/messages")
async def send_message(
    match_id: str,
    request: SendMessageRequest,
    current_user: dict = Depends(get_current_user)
):
    """Send a message in a conversation"""
    # Check message limits for free users
    can_message, message_limit_info = await can_send_message(current_user)
    if not can_message:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=message_limit_info
        )
    
    # Verify match exists
    match = await db.matches.find_one(
        {
            "id": match_id,
            "$or": [
                {"user1_id": current_user['id']},
                {"user2_id": current_user['id']}
            ]
        },
        {"_id": 0}
    )
    
    if not match:
        raise HTTPException(status_code=404, detail="Match not found")
    
    # Determine receiver
    receiver_id = match['user2_id'] if match['user1_id'] == current_user['id'] else match['user1_id']
    
    # Create message
    message_data = {
        "id": str(uuid.uuid4()),
        "match_id": match_id,
        "sender_id": current_user['id'],
        "receiver_id": receiver_id,
        "content": request.content,
        "message_type": request.message_type,
        "status": "sent",
        "created_at": datetime.now(timezone.utc).isoformat(),
        "read_at": None
    }
    
    await db.messages.insert_one(message_data)
    
    # Increment message counter for free users
    if current_user.get('premium_tier') not in ['gold', 'platinum']:
        await increment_messages_count(current_user['id'])
    
    # Send notification to receiver
    sender_profile = await db.profiles.find_one(
        {"user_id": current_user['id']},
        {"_id": 0, "display_name": 1, "photos": 1}
    )
    
    if sender_profile:
        preview = request.content[:50] + "..." if len(request.content) > 50 else request.content
        await create_notification(
            user_id=receiver_id,
            notification_type="new_message",
            title=f"💬 رسالة جديدة من {sender_profile.get('display_name', 'مستخدم')}",
            message=preview,
            link=f"/chat/{match_id}",
            related_user_id=current_user['id'],
            related_user_name=sender_profile.get('display_name'),
            related_user_photo=sender_profile.get('photos', [None])[0] if sender_profile.get('photos') else None
        )
    
    # Get remaining messages for response
    remaining_messages = None
    if current_user.get('premium_tier') not in ['gold', 'platinum']:
        updated_user = await db.users.find_one({"id": current_user['id']}, {"_id": 0})
        messages_sent = updated_user.get('messages_sent_this_week', 0)
        remaining_messages = max(0, 10 - messages_sent)
    
    return {
        "message": "Message sent successfully",
        "data": message_data,
        "remaining_messages": remaining_messages
    }


@api_router.post("/conversations/{match_id}/read-receipts")
async def mark_as_read(match_id: str, current_user: dict = Depends(get_current_user)):
    """Mark all messages in conversation as read"""
    result = await db.messages.update_many(
        {
            "match_id": match_id,
            "receiver_id": current_user['id'],
            "status": {"$ne": "read"}
        },
        {
            "$set": {
                "status": "read",
                "read_at": datetime.now(timezone.utc).isoformat()
            }
        }
    )
    
    return {
        "message": f"Marked {result.modified_count} messages as read"
    }


@api_router.post("/voice-message/upload")
async def upload_voice_message(
    file: UploadFile = File(...),
    current_user: dict = Depends(get_current_user)
):
    """Upload voice message to Cloudinary and return URL"""
    try:
        # Validate file type
        if not file.content_type or not file.content_type.startswith('audio/'):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid file type. Must be audio file."
            )
        
        # Read file content
        contents = await file.read()
        
        # Upload to Cloudinary as video (audio files work with video upload)
        import cloudinary.uploader
        result = cloudinary.uploader.upload(
            contents,
            resource_type="video",  # Cloudinary handles audio as video resource
            folder=f"pizoo/voice_messages/{current_user['id']}",
            format="webm",
            transformation=[
                {'audio_codec': 'opus', 'bit_rate': '32k'}
            ]
        )
        
        return {
            "success": True,
            "url": result['secure_url'],
            "duration": result.get('duration', 0),
            "public_id": result['public_id']
        }
        
    except Exception as e:
        logger.error(f"Voice message upload error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to upload voice message: {str(e)}"
        )


def calculate_compatibility_score(user1_profile: dict, user2_profile: dict) -> dict:
    """
    Calculate compatibility score between two users
    Returns score (0-100) and breakdown by category
    """
    scores = {
        'interests': 0,
        'lifestyle': 0,
        'communication': 0,
        'values': 0
    }
    
    # 1. Interests Match (based on common interests)
    interests1 = set(user1_profile.get('interests', []))
    interests2 = set(user2_profile.get('interests', []))
    if interests1 and interests2:
        common = len(interests1.intersection(interests2))
        total = len(interests1.union(interests2))
        scores['interests'] = int((common / total) * 100) if total > 0 else 50
    else:
        scores['interests'] = 50
    
    # 2. Lifestyle Match (based on age proximity, location, occupation)
    lifestyle_score = 0
    
    # Age proximity (closer age = higher score)
    age1 = user1_profile.get('age', 25)
    age2 = user2_profile.get('age', 25)
    age_diff = abs(age1 - age2)
    age_score = max(0, 100 - (age_diff * 10))  # -10 points per year difference
    lifestyle_score += age_score * 0.4
    
    # Location proximity (if available)
    if user1_profile.get('latitude') and user2_profile.get('latitude'):
        distance = calculate_distance(
            user1_profile['latitude'], user1_profile['longitude'],
            user2_profile['latitude'], user2_profile['longitude']
        )
        if distance < 10:
            lifestyle_score += 100 * 0.3
        elif distance < 50:
            lifestyle_score += 70 * 0.3
        else:
            lifestyle_score += 40 * 0.3
    else:
        lifestyle_score += 50 * 0.3
    
    # Occupation/education level
    if user1_profile.get('occupation') and user2_profile.get('occupation'):
        lifestyle_score += 80 * 0.3
    else:
        lifestyle_score += 50 * 0.3
    
    scores['lifestyle'] = int(lifestyle_score)
    
    # 3. Communication Match (based on languages)
    languages1 = set(user1_profile.get('languages', []))
    languages2 = set(user2_profile.get('languages', []))
    if languages1 and languages2:
        common_langs = len(languages1.intersection(languages2))
        scores['communication'] = min(100, common_langs * 50)
    else:
        scores['communication'] = 60
    
    # 4. Values Match (based on relationship goals, current_mood)
    values_score = 0
    
    # Relationship goals/mood alignment
    mood1 = user1_profile.get('current_mood', '')
    mood2 = user2_profile.get('current_mood', '')
    if mood1 and mood2:
        if mood1 == mood2:
            values_score = 100
        elif (mood1 in ['serious', 'romantic'] and mood2 in ['serious', 'romantic']) or \
             (mood1 in ['casual', 'fun'] and mood2 in ['casual', 'fun']):
            values_score = 75
        else:
            values_score = 50
    else:
        values_score = 60
    
    scores['values'] = values_score
    
    # Calculate overall score (weighted average)
    overall_score = int(
        scores['interests'] * 0.30 +
        scores['lifestyle'] * 0.25 +
        scores['communication'] * 0.20 +
        scores['values'] * 0.25
    )
    
    return {
        'score': overall_score,
        'breakdown': scores
    }


@api_router.get("/compatibility/{user_id}")
async def get_compatibility(
    user_id: str,
    current_user: dict = Depends(get_current_user)
):
    """Calculate compatibility score with another user"""
    # Get both profiles
    user1_profile = await db.profiles.find_one(
        {"user_id": current_user['id']},
        {"_id": 0}
    )
    user2_profile = await db.profiles.find_one(
        {"user_id": user_id},
        {"_id": 0}
    )
    
    if not user1_profile or not user2_profile:
        raise HTTPException(status_code=404, detail="Profile not found")
    
    # Calculate compatibility
    compatibility = calculate_compatibility_score(user1_profile, user2_profile)
    
    return {
        "success": True,
        "compatibility": compatibility
    }


# ===== Settings APIs =====

@api_router.get("/settings")
async def get_settings(current_user: dict = Depends(get_current_user)):
    """Get user settings"""
    settings = await db.user_settings.find_one({"user_id": current_user['id']}, {"_id": 0})
    
    if not settings:
        # Create default settings
        settings_data = {
            "id": str(uuid.uuid4()),
            "user_id": current_user['id'],
            "visibility_mode": "standard",
            "incognito_enabled": False,
            "verified_only_chat": False,
            "send_read_receipts": True,
            "allow_contacts_sync": False,
            "auto_play_videos": True,
            "show_activity_status": True,
            "theme": "system",
            "created_at": datetime.now(timezone.utc).isoformat(),
            "updated_at": datetime.now(timezone.utc).isoformat()
        }
        await db.user_settings.insert_one(settings_data)
        return settings_data
    
    return settings


@api_router.put("/settings")
async def update_settings(
    settings_update: dict,
    current_user: dict = Depends(get_current_user)
):
    """Update user settings"""
    settings_update["updated_at"] = datetime.now(timezone.utc).isoformat()
    
    result = await db.user_settings.update_one(
        {"user_id": current_user['id']},
        {"$set": settings_update}
    )
    
    if result.matched_count == 0:
        # Create if doesn't exist
        settings_data = {
            "id": str(uuid.uuid4()),
            "user_id": current_user['id'],
            **settings_update,
            "created_at": datetime.now(timezone.utc).isoformat()
        }
        await db.user_settings.insert_one(settings_data)
        return {"message": "Settings created", "settings": settings_data}
    
    return {"message": "Settings updated successfully"}


# ===== Discovery Settings APIs =====

@api_router.get("/discovery-settings")
async def get_discovery_settings(current_user: dict = Depends(get_current_user)):
    """Get user discovery settings"""
    settings = await db.discovery_settings.find_one({"user_id": current_user['id']}, {"_id": 0})
    
    if not settings:
        # Create default settings
        settings_data = {
            "id": str(uuid.uuid4()),
            "user_id": current_user['id'],
            "location": "",
            "max_distance": 50,
            "interested_in": "all",
            "min_age": 18,
            "max_age": 100,
            "show_new_profiles_only": False,
            "show_verified_only": False,
            "created_at": datetime.now(timezone.utc).isoformat(),
            "updated_at": datetime.now(timezone.utc).isoformat()
        }
        await db.discovery_settings.insert_one(settings_data)
        # Remove _id if it was added by MongoDB
        settings_data.pop('_id', None)
        return settings_data
    
    return settings


@api_router.put("/discovery-settings")
async def update_discovery_settings(
    settings_update: dict,
    current_user: dict = Depends(get_current_user)
):
    """Update user discovery settings"""
    settings_update["updated_at"] = datetime.now(timezone.utc).isoformat()
    
    result = await db.discovery_settings.update_one(
        {"user_id": current_user['id']},
        {"$set": settings_update}
    )
    
    if result.matched_count == 0:
        # Create if doesn't exist
        settings_data = {
            "id": str(uuid.uuid4()),
            "user_id": current_user['id'],
            **settings_update,
            "created_at": datetime.now(timezone.utc).isoformat()
        }
        await db.discovery_settings.insert_one(settings_data)
        # Remove _id if it was added by MongoDB
        settings_data.pop('_id', None)
        return {"message": "Discovery settings created", "settings": settings_data}
    
    return {"message": "Discovery settings updated successfully"}


# ===== Double Dating System =====

@api_router.get("/double-dating/friends")
async def get_double_dating_friends(current_user: dict = Depends(get_current_user)):
    """Get user's double dating friends"""
    friends_data = await db.double_dating_friends.find({
        "user_id": current_user['id'],
        "status": "accepted"
    }).to_list(length=None)
    
    # Get friend profiles
    friends = []
    for friend_data in friends_data:
        friend_profile = await db.profiles.find_one(
            {"user_id": friend_data['friend_user_id']},
            {"_id": 0}
        )
        if friend_profile:
            friends.append({
                "id": friend_data['id'],
                "user_id": friend_data['friend_user_id'],
                "name": friend_profile.get('name', 'Unknown'),
                "photo": friend_profile.get('primary_photo', friend_profile.get('photos', [None])[0]),
                "age": friend_profile.get('age'),
                "accepted_at": friend_data.get('accepted_at')
            })
    
    return {"friends": friends}


@api_router.post("/double-dating/invite/{friend_user_id}")
async def invite_double_dating_friend(
    friend_user_id: str,
    current_user: dict = Depends(get_current_user)
):
    """Invite a friend to double dating"""
    # Check if already invited
    existing = await db.double_dating_friends.find_one({
        "user_id": current_user['id'],
        "friend_user_id": friend_user_id
    })
    
    if existing:
        return {"message": "Friend already invited", "status": existing['status']}
    
    # Check limit (max 3 friends)
    count = await db.double_dating_friends.count_documents({
        "user_id": current_user['id'],
        "status": "accepted"
    })
    
    if count >= 3:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="You can only have up to 3 double dating friends"
        )
    
    # Create invitation
    friend_data = {
        "id": str(uuid.uuid4()),
        "user_id": current_user['id'],
        "friend_user_id": friend_user_id,
        "status": "pending",
        "invited_at": datetime.now(timezone.utc).isoformat()
    }
    
    await db.double_dating_friends.insert_one(friend_data)
    
    return {"message": "Friend invited successfully", "invitation": friend_data}


@api_router.post("/double-dating/accept/{invitation_id}")
async def accept_double_dating_invitation(
    invitation_id: str,
    current_user: dict = Depends(get_current_user)
):
    """Accept double dating invitation"""
    invitation = await db.double_dating_friends.find_one({
        "id": invitation_id,
        "friend_user_id": current_user['id'],
        "status": "pending"
    })
    
    if not invitation:
        raise HTTPException(status_code=404, detail="Invitation not found")
    
    # Update status
    await db.double_dating_friends.update_one(
        {"id": invitation_id},
        {
            "$set": {
                "status": "accepted",
                "accepted_at": datetime.now(timezone.utc).isoformat()
            }
        }
    )
    
    return {"message": "Invitation accepted successfully"}


@api_router.delete("/double-dating/friends/{friend_id}")
async def remove_double_dating_friend(
    friend_id: str,
    current_user: dict = Depends(get_current_user)
):
    """Remove a double dating friend"""
    result = await db.double_dating_friends.delete_one({
        "id": friend_id,
        "user_id": current_user['id']
    })
    
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Friend not found")
    
    return {"message": "Friend removed successfully"}


# ===== Report & Block System =====

@api_router.post("/report")
async def report_user(
    request: ReportRequest,
    current_user: dict = Depends(get_current_user)
):
    """Report a user for inappropriate behavior"""
    # Check if already reported
    existing_report = await db.reports.find_one({
        "reporter_id": current_user['id'],
        "reported_user_id": request.reported_user_id
    })
    
    if existing_report:
        return {"message": "لقد قمت بالإبلاغ عن هذا المستخدم مسبقاً"}
    
    # Create report
    report = Report(
        reporter_id=current_user['id'],
        reported_user_id=request.reported_user_id,
        reason=request.reason,
        details=request.details
    )
    
    report_dict = report.model_dump()
    report_dict['created_at'] = report_dict['created_at'].isoformat()
    
    await db.reports.insert_one(report_dict)
    
    return {
        "message": "تم الإبلاغ بنجاح. سنراجع الأمر في أقرب وقت",
        "report_id": report.id
    }


@api_router.post("/block")
async def block_user(
    request: BlockRequest,
    current_user: dict = Depends(get_current_user)
):
    """Block a user"""
    # Check if already blocked
    existing_block = await db.blocks.find_one({
        "blocker_id": current_user['id'],
        "blocked_user_id": request.blocked_user_id
    })
    
    if existing_block:
        return {"message": "هذا المستخدم محظور بالفعل"}
    
    # Create block
    block = Block(
        blocker_id=current_user['id'],
        blocked_user_id=request.blocked_user_id
    )
    
    block_dict = block.model_dump()
    block_dict['created_at'] = block_dict['created_at'].isoformat()
    
    await db.blocks.insert_one(block_dict)
    
    # Remove any existing matches
    await db.matches.delete_many({
        "$or": [
            {"user1_id": current_user['id'], "user2_id": request.blocked_user_id},
            {"user1_id": request.blocked_user_id, "user2_id": current_user['id']}
        ]
    })
    
    return {
        "message": "تم حظر المستخدم بنجاح",
        "block_id": block.id
    }


@api_router.delete("/block/{blocked_user_id}")
async def unblock_user(
    blocked_user_id: str,
    current_user: dict = Depends(get_current_user)
):
    """Unblock a user"""
    result = await db.blocks.delete_one({
        "blocker_id": current_user['id'],
        "blocked_user_id": blocked_user_id
    })
    
    if result.deleted_count == 0:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="لم يتم العثور على حظر لهذا المستخدم"
        )
    
    return {"message": "تم إلغاء الحظر بنجاح"}


@api_router.get("/blocked-users")
async def get_blocked_users(current_user: dict = Depends(get_current_user)):
    """Get list of blocked users"""
    blocks = await db.blocks.find(
        {"blocker_id": current_user['id']},
        {"_id": 0}
    ).to_list(length=1000)
    
    blocked_user_ids = [block['blocked_user_id'] for block in blocks]
    
    # Get profiles of blocked users
    profiles = []
    if blocked_user_ids:
        profiles = await db.profiles.find(
            {"user_id": {"$in": blocked_user_ids}},
            {"_id": 0, "user_id": 1, "display_name": 1, "photos": 1}
        ).to_list(length=1000)
    
    return {"blocked_users": profiles}



# ===== Notification System =====

@api_router.get("/notifications")
async def get_notifications(
    skip: int = 0,
    limit: int = 50,
    unread_only: bool = False,
    current_user: dict = Depends(get_current_user)
):
    """Get user notifications"""
    query = {"user_id": current_user['id']}
    
    if unread_only:
        query["is_read"] = False
    
    notifications = await db.notifications.find(
        query,
        {"_id": 0}
    ).sort("created_at", -1).skip(skip).limit(limit).to_list(length=limit)
    
    # Convert datetime to string for JSON serialization
    for notif in notifications:
        if isinstance(notif.get('created_at'), datetime):
            notif['created_at'] = notif['created_at'].isoformat()
    
    return {"notifications": notifications, "count": len(notifications)}


@api_router.get("/notifications/unread-count")
async def get_unread_notifications_count(current_user: dict = Depends(get_current_user)):
    """Get count of unread notifications"""
    count = await db.notifications.count_documents({
        "user_id": current_user['id'],
        "is_read": False
    })
    
    return {"unread_count": count}


@api_router.put("/notifications/{notification_id}/read")
async def mark_notification_as_read(
    notification_id: str,
    current_user: dict = Depends(get_current_user)
):
    """Mark a notification as read"""
    result = await db.notifications.update_one(
        {
            "id": notification_id,
            "user_id": current_user['id']
        },
        {"$set": {"is_read": True}}
    )
    
    if result.modified_count == 0:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Notification not found"
        )
    
    return {"message": "Notification marked as read"}


@api_router.put("/notifications/mark-all-read")
async def mark_all_notifications_as_read(current_user: dict = Depends(get_current_user)):
    """Mark all notifications as read"""
    result = await db.notifications.update_many(
        {
            "user_id": current_user['id'],
            "is_read": False
        },
        {"$set": {"is_read": True}}
    )
    
    return {"message": f"Marked {result.modified_count} notifications as read"}


@api_router.delete("/notifications/{notification_id}")
async def delete_notification(
    notification_id: str,
    current_user: dict = Depends(get_current_user)
):
    """Delete a notification"""
    result = await db.notifications.delete_one({
        "id": notification_id,
        "user_id": current_user['id']
    })
    
    if result.deleted_count == 0:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Notification not found"
        )
    
    return {"message": "Notification deleted"}


async def create_notification(
    user_id: str,
    notification_type: str,
    title: str,
    message: str,
    link: Optional[str] = None,
    related_user_id: Optional[str] = None,
    related_user_name: Optional[str] = None,
    related_user_photo: Optional[str] = None
):
    """Helper function to create a notification"""
    notification = Notification(
        user_id=user_id,
        type=notification_type,
        title=title,
        message=message,
        link=link,
        related_user_id=related_user_id,
        related_user_name=related_user_name,
        related_user_photo=related_user_photo
    )
    
    notification_dict = notification.model_dump()
    notification_dict['created_at'] = notification_dict['created_at'].isoformat()
    
    await db.notifications.insert_one(notification_dict)
    return notification



# ===== Boost System =====



# ===== Stories System =====

@api_router.post("/stories")
async def create_story(
    media_url: str,
    media_type: str,
    caption: Optional[str] = None,
    current_user: dict = Depends(get_current_user)
):
    """Create a new story"""
    story = Story(
        user_id=current_user['id'],
        media_url=media_url,
        media_type=media_type,
        caption=caption
    )
    
    story_dict = story.model_dump()
    story_dict['created_at'] = story_dict['created_at'].isoformat()
    story_dict['expires_at'] = story_dict['expires_at'].isoformat()
    
    await db.stories.insert_one(story_dict)
    
    return {"message": "Story created successfully", "story": story_dict}


@api_router.get("/stories/feed")
async def get_stories_feed(current_user: dict = Depends(get_current_user)):
    """Get all active stories from matches and connections"""
    # Get user's matches
    matches = await db.matches.find({
        "$or": [
            {"user1_id": current_user['id']},
            {"user2_id": current_user['id']}
        ]
    }).to_list(length=1000)
    
    # Extract match user IDs
    match_user_ids = set()
    for match in matches:
        if match['user1_id'] != current_user['id']:
            match_user_ids.add(match['user1_id'])
        if match['user2_id'] != current_user['id']:
            match_user_ids.add(match['user2_id'])
    
    # Add current user to see their own stories
    match_user_ids.add(current_user['id'])
    
    # Get active stories (not expired)
    now = datetime.now(timezone.utc)
    stories = await db.stories.find({
        "user_id": {"$in": list(match_user_ids)},
        "expires_at": {"$gt": now.isoformat()}
    }, {"_id": 0}).sort("created_at", -1).to_list(length=1000)
    
    # Group stories by user
    stories_by_user = {}
    for story in stories:
        user_id = story['user_id']
        if user_id not in stories_by_user:
            stories_by_user[user_id] = []
        
        # Check if current user has viewed this story
        story['viewed_by_me'] = current_user['id'] in story.get('views', [])
        stories_by_user[user_id].append(story)
    
    # Get profile info for each user with stories
    user_profiles = {}
    for user_id in stories_by_user.keys():
        profile = await db.profiles.find_one(
            {"user_id": user_id},
            {"_id": 0, "user_id": 1, "display_name": 1, "photos": 1}
        )
        if profile:
            user_profiles[user_id] = profile
    
    # Format response
    feed = []
    for user_id, user_stories in stories_by_user.items():
        if user_id in user_profiles:
            feed.append({
                "user": user_profiles[user_id],
                "stories": user_stories,
                "has_unseen": any(not s['viewed_by_me'] for s in user_stories)
            })
    
    return {"feed": feed}


@api_router.post("/stories/{story_id}/view")
async def view_story(
    story_id: str,
    current_user: dict = Depends(get_current_user)
):
    """Mark story as viewed"""
    story = await db.stories.find_one({"id": story_id}, {"_id": 0})
    
    if not story:
        raise HTTPException(status_code=404, detail="Story not found")
    
    # Add user to views if not already viewed
    if current_user['id'] not in story.get('views', []):
        await db.stories.update_one(
            {"id": story_id},
            {"$push": {"views": current_user['id']}}
        )
    
    return {"message": "Story viewed"}


@api_router.get("/stories/user/{user_id}")
async def get_user_stories(
    user_id: str,
    current_user: dict = Depends(get_current_user)
):
    """Get stories for a specific user"""
    now = datetime.now(timezone.utc)
    stories = await db.stories.find({
        "user_id": user_id,
        "expires_at": {"$gt": now.isoformat()}
    }, {"_id": 0}).sort("created_at", 1).to_list(length=100)
    
    for story in stories:
        story['viewed_by_me'] = current_user['id'] in story.get('views', [])
    
    return {"stories": stories}


@api_router.delete("/stories/{story_id}")
async def delete_story(
    story_id: str,
    current_user: dict = Depends(get_current_user)
):
    """Delete a story"""
    story = await db.stories.find_one({"id": story_id}, {"_id": 0})
    
    if not story:
        raise HTTPException(status_code=404, detail="Story not found")
    
    if story['user_id'] != current_user['id']:
        raise HTTPException(status_code=403, detail="Not authorized to delete this story")
    
    await db.stories.delete_one({"id": story_id})
    
    return {"message": "Story deleted successfully"}


@api_router.get("/stories/my-stories")
async def get_my_stories(current_user: dict = Depends(get_current_user)):
    """Get current user's active stories with view counts"""
    now = datetime.now(timezone.utc)
    stories = await db.stories.find({
        "user_id": current_user['id'],
        "expires_at": {"$gt": now.isoformat()}
    }, {"_id": 0}).sort("created_at", -1).to_list(length=100)
    
    for story in stories:
        story['view_count'] = len(story.get('views', []))
    
    return {"stories": stories}


@api_router.post("/boost/activate")
async def activate_boost(current_user: dict = Depends(get_current_user)):
    """Activate boost for 30 minutes (increases profile visibility)"""
    # Check if user already has an active boost
    active_boost = await db.boosts.find_one({
        "user_id": current_user['id'],
        "is_active": True
    })
    
    if active_boost:
        # Check if still valid
        ends_at = datetime.fromisoformat(active_boost['ends_at'])
        if ends_at > datetime.now(timezone.utc):
            return {
                "message": "لديك boost نشط بالفعل",
                "ends_at": active_boost['ends_at']
            }
    
    # Create new boost (30 minutes duration)
    ends_at = datetime.now(timezone.utc) + timedelta(minutes=30)
    
    boost = Boost(
        user_id=current_user['id'],
        ends_at=ends_at
    )
    
    boost_dict = boost.model_dump()
    boost_dict['started_at'] = boost_dict['started_at'].isoformat()
    boost_dict['ends_at'] = boost_dict['ends_at'].isoformat()
    
    await db.boosts.insert_one(boost_dict)
    
    return {
        "message": "تم تفعيل Boost لمدة 30 دقيقة! 🚀",
        "boost_id": boost.id,
        "ends_at": boost_dict['ends_at']
    }


@api_router.get("/boost/status")
async def get_boost_status(current_user: dict = Depends(get_current_user)):
    """Get current boost status"""
    active_boost = await db.boosts.find_one({
        "user_id": current_user['id'],
        "is_active": True
    })
    
    if not active_boost:
        return {
            "is_active": False,
            "message": "لا يوجد boost نشط"
        }
    
    ends_at = datetime.fromisoformat(active_boost['ends_at'])
    now = datetime.now(timezone.utc)
    
    if ends_at <= now:
        # Boost expired, deactivate it
        await db.boosts.update_one(
            {"id": active_boost['id']},
            {"$set": {"is_active": False}}
        )
        return {
            "is_active": False,
            "message": "انتهى Boost"
        }
    
    time_remaining = (ends_at - now).total_seconds()
    
    return {
        "is_active": True,
        "ends_at": active_boost['ends_at'],
        "time_remaining_seconds": int(time_remaining)
    }


@api_router.get("/terms")
async def get_terms():
    terms_content = """
# شروط وأحكام استخدام التطبيق

آخر تحديث: {date}

مرحباً بك في تطبيقنا. بتسجيلك في هذه الخدمة، فإنك توافق على الالتزام بالشروط والأحكام التالية. يرجى قراءتها بعناية.

---

## 1. القبول والموافقة

1.1 باستخدامك لهذا التطبيق، فإنك تقر بأنك قد قرأت وفهمت ووافقت على جميع الشروط والأحكام الواردة في هذه الوثيقة.

1.2 إذا كنت لا توافق على أي من هذه الشروط، يرجى عدم استخدام التطبيق.

---

## 2. الاشتراك والفترة التجريبية

### 2.1 الفترة التجريبية المجانية
- يحصل جميع المستخدمين الجدد على **فترة تجريبية مجانية مدتها 14 يوماً** من تاريخ التسجيل
- خلال هذه الفترة، لن يتم خصم أي مبلغ من حسابك
- يمكنك إلغاء الاشتراك في أي وقت خلال الفترة التجريبية دون أي رسوم

### 2.2 الاشتراك السنوي
- **قيمة الاشتراك**: 396 فرنك سويسري (CHF) سنوياً
- **المعادل الشهري**: 33 فرنك سويسري شهرياً (وفر 20% مقارنة بالاشتراك الشهري)
- **الدفع التلقائي**: بعد انتهاء الفترة التجريبية البالغة 14 يوماً، سيتم خصم مبلغ 396 CHF تلقائياً من طريقة الدفع المسجلة لديك
- **التجديد التلقائي**: يتجدد الاشتراك تلقائياً كل عام ما لم يتم إلغاؤه قبل تاريخ التجديد بـ 7 أيام على الأقل

---

## 3. طرق الدفع

### 3.1 الطرق المقبولة
نقبل الدفع عبر:
- البطاقات البنكية (Visa, Mastercard, American Express)
- PayPal
- طرق دفع أخرى حسب البلد

### 3.2 إلزامية معلومات الدفع
- إضافة طريقة دفع صالحة **إلزامية** عند التسجيل، حتى خلال الفترة التجريبية
- يجب أن تكون معلومات الدفع صحيحة ومحدثة دائماً
- أنت مسؤول عن تحديث معلومات الدفع في حالة انتهاء صلاحية البطاقة

### 3.3 أمن المعلومات المالية
- جميع معلومات الدفع مشفرة ومحمية بأعلى معايير الأمان (PCI-DSS)
- لا نقوم بتخزين معلومات البطاقة الكاملة على خوادمنا
- نحتفظ فقط بالأربعة أرقام الأخيرة للتعريف

### 3.4 فشل الدفع
- في حالة فشل عملية الدفع التلقائي، سيتم إرسال إشعار لك عبر البريد الإلكتروني
- لديك 7 أيام لتحديث معلومات الدفع
- بعد 7 أيام، سيتم إيقاف الخدمة مؤقتاً حتى يتم تحديث معلومات الدفع

---

## 4. سياسة الإلغاء والاسترجاع

### 4.1 الإلغاء خلال الفترة التجريبية
- يمكنك إلغاء اشتراكك في **أي وقت خلال فترة الـ 14 يوماً** التجريبية
- لن يتم خصم أي مبلغ إذا تم الإلغاء قبل انتهاء الفترة التجريبية
- سيتوقف وصولك للخدمة فوراً عند الإلغاء

### 4.2 استرجاع كامل المبلغ
- بعد خصم المبلغ السنوي، يمكنك طلب استرجاع **كامل المبلغ خلال 7 أيام** من تاريخ الدفع
- سيتم معالجة طلب الاسترجاع خلال 7-10 أيام عمل
- سيعاد المبلغ إلى نفس طريقة الدفع المستخدمة

### 4.3 استرجاع جزئي
- بعد مرور 7 أيام من الدفع، يمكن طلب استرجاع جزئي
- يُحسب المبلغ المسترجع على أساس الفترة المتبقية من الاشتراك السنوي
- يُخصم رسوم إدارية 10% من المبلغ المسترجع

### 4.4 طريقة الإلغاء
- يمكن إلغاء الاشتراك من خلال **لوحة التحكم** الخاصة بك
- أو بالتواصل مع **فريق الدعم** عبر البريد الإلكتروني

### 4.5 استمرار الخدمة بعد الإلغاء
- عند إلغاء الاشتراك، ستستمر إمكانية الوصول للخدمة حتى **نهاية الفترة المدفوعة**
- لن يتم تجديد الاشتراك تلقائياً بعد انتهاء الفترة

---

## 5. التحقق من الهوية ومكافحة الاحتيال

### 5.1 المعلومات المطلوبة
للتسجيل في الخدمة، يجب تقديم:
- الاسم الكامل
- عنوان بريد إلكتروني صالح
- رقم هاتف للتواصل
- معلومات طريقة الدفع (بطاقة بنكية أو PayPal)

### 5.2 التحقق من الهوية
- قد نطلب منك تقديم وثائق إضافية للتحقق من هويتك في حالات معينة
- هذا يساعدنا في حماية حسابك ومنع الاحتيال
- المعلومات المقدمة تُستخدم فقط لأغراض التحقق ولن تُشارك مع أطراف ثالثة

### 5.3 حماية الحساب
- أنت مسؤول عن الحفاظ على سرية معلومات حسابك وكلمة المرور
- يجب إبلاغنا فوراً في حالة الاشتباه في استخدام غير مصرح به لحسابك

---

## 6. سياسة الخصوصية وحماية البيانات

### 6.1 جمع البيانات
نقوم بجمع المعلومات التالية:
- **معلومات شخصية**: الاسم، البريد الإلكتروني، رقم الهاتف
- **معلومات الدفع**: نوع طريقة الدفع، آخر 4 أرقام من البطاقة
- **بيانات الاستخدام**: تواريخ الدخول، نشاطات الحساب

### 6.2 استخدام البيانات
نستخدم بياناتك الشخصية لـ:
- تقديم وتحسين خدماتنا
- معالجة المدفوعات والاشتراكات
- التواصل معك بخصوص حسابك
- تحسين تجربة المستخدم
- الامتثال للمتطلبات القانونية

### 6.3 مشاركة البيانات
- **لن نبيع** معلوماتك الشخصية لأطراف ثالثة أبداً
- قد نشارك البيانات مع:
  - معالجي الدفع (لمعالجة المدفوعات فقط)
  - مقدمي الخدمات السحابية (لتخزين البيانات بشكل آمن)
  - السلطات القانونية (عند الطلب القانوني فقط)

### 6.4 أمن البيانات
- نستخدم تشفير SSL/TLS لجميع الاتصالات
- البيانات المالية مشفرة وفق معايير PCI-DSS
- الوصول للبيانات مقيد بالموظفين المصرح لهم فقط
- نجري فحوصات أمنية دورية

### 6.5 حقوقك
لديك الحق في:
- **الوصول**: الاطلاع على بياناتك الشخصية
- **التعديل**: تحديث أو تصحيح معلوماتك
- **الحذف**: طلب حذف حسابك وبياناتك
- **النقل**: الحصول على نسخة من بياناتك
- **الاعتراض**: الاعتراض على معالجة بياناتك في حالات معينة

### 6.6 الاحتفاظ بالبيانات
- نحتفظ ببياناتك طالما كان حسابك نشطاً
- بعد حذف الحساب، نحتفظ ببعض البيانات لمدة 90 يوماً للأغراض القانونية
- بعد ذلك، يتم حذف جميع البيانات بشكل دائم

### 6.7 ملفات تعريف الارتباط (Cookies)
- نستخدم cookies لتحسين تجربتك
- يمكنك تعطيل cookies من إعدادات المتصفح
- بعض الوظائف قد لا تعمل بدون cookies

---

## 7. شروط استخدام الخدمة

### 7.1 الأهلية
- يجب أن يكون عمرك **18 عاماً على الأقل** لاستخدام هذه الخدمة
- إذا كنت تمثل شركة، يجب أن يكون لديك السلطة لإلزام الشركة بهذه الشروط

### 7.2 الاستخدام المسموح
- يحق لك استخدام الخدمة للأغراض الشخصية أو التجارية المشروعة فقط
- يمكنك استخدام حساب واحد فقط لكل شخص
- جميع المحتويات والبيانات يجب أن تتوافق مع القوانين المحلية والدولية

### 7.3 الاستخدام المحظور
يُحظر استخدام الخدمة لـ:
- أي أنشطة غير قانونية أو احتيالية
- نشر محتوى مسيء، عنصري، أو يحرض على الكراهية
- إرسال رسائل غير مرغوب فيها (spam)
- محاولة اختراق الخدمة أو الوصول غير المصرح به
- انتهاك حقوق الملكية الفكرية للآخرين
- إساءة استخدام الخدمة بطريقة تؤثر على المستخدمين الآخرين

### 7.4 إنهاء الحساب
- يحق لنا إنهاء أو تعليق حسابك فوراً في حالة انتهاك هذه الشروط
- ستتلقى إشعاراً قبل 7 أيام من الإنهاء (ما لم يكن الانتهاك جسيماً)
- يمكنك حذف حسابك في أي وقت من لوحة التحكم

---

## 8. التغييرات على الشروط والأحكام

### 8.1 حقنا في التعديل
- نحتفظ بالحق في تعديل هذه الشروط في أي وقت
- سيتم إشعارك بأي تغييرات جوهرية قبل 30 يوماً من سريانها
- الإشعار سيكون عبر البريد الإلكتروني أو داخل التطبيق

### 8.2 قبول التعديلات
- استمرارك في استخدام الخدمة بعد التعديلات يعني موافقتك عليها
- إذا لم توافق على التعديلات، يمكنك إلغاء اشتراكك

---

## 9. إخلاء المسؤولية والضمانات

### 9.1 توفر الخدمة
- نبذل قصارى جهدنا لضمان توفر الخدمة 24/7
- قد تحدث انقطاعات مؤقتة للصيانة أو التحديثات
- نحن غير مسؤولين عن انقطاعات الخدمة خارج سيطرتنا

### 9.2 الضمانات
- الخدمة متاحة "كما هي" دون أي ضمانات صريحة أو ضمنية
- لا نضمن أن الخدمة ستكون خالية من الأخطاء أو الفيروسات
- لا نضمن أن الخدمة ستلبي احتياجاتك المحددة

### 9.3 حدود المسؤولية
- لا نتحمل المسؤولية عن:
  - أي أضرار مباشرة أو غير مباشرة ناتجة عن استخدام الخدمة
  - خسارة البيانات أو الأرباح
  - أي أضرار ناتجة عن انقطاع الخدمة
- المسؤولية القصوى تقتصر على المبلغ المدفوع خلال آخر 12 شهر

---

## 10. القانون الساري وحل النزاعات

### 10.1 القانون الساري
- تخضع هذه الشروط للقوانين السويسرية
- يتم تفسير أي بنود غامضة وفقاً للقانون السويسري

### 10.2 حل النزاعات
- في حالة نشوء أي نزاع، نشجعك على التواصل معنا أولاً لحله ودياً
- إذا لم يتم التوصل لحل، يُحال النزاع إلى **المحاكم السويسرية المختصة**
- مكان الاختصاص القضائي: زيورخ، سويسرا

---

## 11. الاتصال بنا

إذا كان لديك أي أسئلة أو استفسارات حول هذه الشروط والأحكام، يمكنك التواصل معنا:

📧 **البريد الإلكتروني**: support@example.com  
📞 **الهاتف**: +41 XX XXX XX XX  
🕐 **ساعات العمل**: الاثنين - الجمعة، 9:00 - 18:00 (توقيت زيورخ)

---

## 12. الإقرار النهائي

**بالتسجيل في خدمتنا، فإنك تقر وتوافق على ما يلي:**

✅ قرأت وفهمت جميع بنود هذه الشروط والأحكام  
✅ توافق على الالتزام بجميع الشروط المذكورة أعلاه  
✅ توافق على دفع رسوم الاشتراك السنوي (396 CHF) بعد انتهاء الفترة التجريبية  
✅ تفهم أنه سيتم خصم المبلغ تلقائياً من طريقة الدفع المسجلة  
✅ تفهم حقك في الإلغاء خلال الفترة التجريبية أو طلب استرجاع المبلغ  

---

*آخر تحديث: {date}*  
*رقم الإصدار: 1.0*
""".format(date=datetime.now().strftime("%d/%m/%Y"))
    
    return {"terms": terms_content}


# Include the router in the main app
app.include_router(api_router)


# Import and include admin router
try:
    from admin_tools import admin_router
    app.include_router(admin_router)
    print("✅ Admin router loaded")
except ImportError as e:
    print(f"⚠️  Admin router not loaded: {e}")


app.add_middleware(
    CORSMiddleware,
    allow_credentials=True,
    allow_origins=os.environ.get('CORS_ORIGINS', '*').split(','),
    allow_methods=["*"],
    allow_headers=["*"],
)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# WebSocket Endpoint for Real-Time Chat
@app.websocket("/ws/{user_id}")
async def websocket_endpoint(websocket: WebSocket, user_id: str):
    await manager.connect(user_id, websocket)
    try:
        while True:
            # Receive message from client
            data = await websocket.receive_json()
            
            message_type = data.get('type')
            
            if message_type == 'message':
                # Send message to receiver
                receiver_id = data.get('receiver_id')
                message_data = {
                    'type': 'new_message',
                    'sender_id': user_id,
                    'message': data.get('message'),
                    'match_id': data.get('match_id'),
                    'timestamp': datetime.now(timezone.utc).isoformat()
                }
                
                # Save to database
                await db.messages.insert_one({
                    'id': str(uuid.uuid4()),
                    'match_id': data.get('match_id'),
                    'sender_id': user_id,
                    'receiver_id': receiver_id,
                    'content': data.get('message'),
                    'message_type': 'text',
                    'status': 'sent',
                    'created_at': datetime.now(timezone.utc).isoformat()
                })
                
                # Send to receiver if online
                await manager.send_personal_message(message_data, receiver_id)
                
                # Send confirmation to sender
                await manager.send_personal_message({
                    'type': 'message_sent',
                    'success': True
                }, user_id)
            
            elif message_type == 'typing':
                # Broadcast typing indicator
                receiver_id = data.get('receiver_id')
                await manager.send_personal_message({
                    'type': 'typing',
                    'user_id': user_id,
                    'is_typing': data.get('is_typing', True)
                }, receiver_id)
            
            elif message_type == 'read_receipt':
                # Mark messages as read
                match_id = data.get('match_id')
                await db.messages.update_many(
                    {
                        'match_id': match_id,
                        'receiver_id': user_id,
                        'status': {'$ne': 'read'}
                    },
                    {
                        '$set': {
                            'status': 'read',
                            'read_at': datetime.now(timezone.utc).isoformat()
                        }
                    }
                )
                
                # Notify sender
                sender_id = data.get('sender_id')
                await manager.send_personal_message({
                    'type': 'read_receipt',
                    'match_id': match_id,
                    'read_by': user_id
                }, sender_id)
    
    except WebSocketDisconnect:
        manager.disconnect(user_id)
        await manager.broadcast_status(user_id, False)
    except Exception as e:
        logger.error(f"WebSocket error for user {user_id}: {str(e)}")
        manager.disconnect(user_id)

@app.on_event("shutdown")
async def shutdown_db_client():
    client.close()


# ===== Email Verification System =====

from email_service import email_service

class EmailVerificationRequest(BaseModel):
    email: EmailStr

class VerifyOTPRequest(BaseModel):
    email: EmailStr
    code: str

@api_router.post("/auth/send-verification-otp")
async def send_verification_otp(request: EmailVerificationRequest):
    """Send OTP to email for verification"""
    try:
        success = email_service.send_verification_otp(request.email)
        
        if success:
            return {
                "message": "تم إرسال رمز التحقق إلى بريدك الإلكتروني",
                "email": request.email
            }
        else:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="فشل إرسال رمز التحقق"
            )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"خطأ في إرسال البريد: {str(e)}"
        )

@api_router.post("/auth/verify-otp")
async def verify_email_otp(request: VerifyOTPRequest):
    """Verify OTP code"""
    is_valid = email_service.verify_otp(request.email, request.code)


# ========================================
# Email Service Diagnostics & Testing
# ========================================

class EmailTestRequest(BaseModel):
    to_email: EmailStr
    test_type: str = "verification"  # verification | welcome | notification

@api_router.post("/admin/test-email")
async def test_email_service(request: EmailTestRequest):
    """
    Test email service configuration
    
    Test types:
    - verification: Send test verification email
    - welcome: Send welcome email
    - notification: Send test notification
    """
    try:
        if request.test_type == "verification":
            html_content = f"""
            <html>
                <body style="font-family: Arial, sans-serif; padding: 20px; background-color: #f5f5f5;">
                    <div style="max-width: 600px; margin: 0 auto; background: white; padding: 30px; border-radius: 10px;">
                        <h1 style="color: #e91e63; text-align: center;">Pizoo Email Test</h1>
                        <p>This is a test email from Pizoo's SendGrid integration.</p>
                        <p>If you received this email, your SendGrid configuration is working correctly! ✅</p>
                        <hr style="margin: 20px 0;">
                        <p style="color: #666; font-size: 12px;">
                            Provider: SendGrid<br>
                            From: {email_service.sender_email}<br>
                            Time: {datetime.now(timezone.utc).isoformat()}
                        </p>
                    </div>
                </body>
            </html>
            """
            
            plain_text = "This is a test email from Pizoo's SendGrid integration. If you received this, your configuration is working!"
            
            success = email_service.send_email(
                to_email=request.to_email,
                subject="[Pizoo] Email Service Test",
                html_content=html_content,
                plain_text_content=plain_text
            )
        
        elif request.test_type == "welcome":
            html_content = f"""
            <html>
                <body style="font-family: Arial, sans-serif; padding: 20px; background-color: #f5f5f5;">
                    <div style="max-width: 600px; margin: 0 auto; background: white; padding: 30px; border-radius: 10px;">
                        <h1 style="color: #e91e63; text-align: center;">Welcome to Pizoo! 💕</h1>
                        <p>Thank you for joining Pizoo, the dating app that helps you find meaningful connections.</p>
                        <p>Get started by completing your profile and start swiping!</p>
                        <div style="text-align: center; margin: 30px 0;">
                            <a href="https://pizoo.app" style="background: linear-gradient(to right, #e91e63, #f06292); color: white; padding: 15px 30px; text-decoration: none; border-radius: 25px;">Complete Your Profile</a>
                        </div>
                    </div>
                </body>
            </html>
            """
            
            success = email_service.send_email(
                to_email=request.to_email,
                subject="Welcome to Pizoo! 💕",
                html_content=html_content
            )
        
        else:
            html_content = "<html><body><h1>Test Notification</h1><p>This is a test notification from Pizoo.</p></body></html>"
            success = email_service.send_email(
                to_email=request.to_email,
                subject="[Pizoo] Test Notification",
                html_content=html_content
            )
        
        if success:
            return {
                "ok": True,
                "message": "Test email sent successfully",
                "provider": email_service.provider,
                "to": request.to_email
            }
        else:
            raise HTTPException(
                status_code=500,
                detail="Failed to send test email"
            )
    
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Email service error: {str(e)}"
        )

@api_router.get("/admin/email-status")
async def get_email_service_status():
    """Get current email service configuration status"""
    return {
        "provider": email_service.provider,
        "configured": email_service.sg is not None if email_service.provider == 'sendgrid' else True,
        "from_email": email_service.sender_email,
        "from_name": email_service.sender_name,
        "api_key_set": bool(email_service.api_key),
        "api_key_prefix": email_service.api_key[:8] + "..." if email_service.api_key else None
    }

    
    if is_valid:
        # Update user's email verification status
        await db.users.update_one(
            {"email": request.email},
            {"$set": {"email_verified": True}}
        )
        
        return {
            "message": "تم تأكيد بريدك الإلكتروني بنجاح",
            "verified": True
        }
    else:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="رمز التحقق غير صحيح أو منتهي الصلاحية"
        )

@api_router.post("/notifications/email/test")
async def test_email_notification(
    notification_type: str,
    current_user: dict = Depends(get_current_user)
):
    """Test email notifications (for development)"""
    profile = await db.profiles.find_one({"user_id": current_user['id']}, {"_id": 0})
    user_email = current_user.get('email')
    
    if not user_email:
        raise HTTPException(status_code=400, detail="No email found")
    
    if notification_type == "match":
        success = email_service.send_new_match_notification(
            user_email,
            "أحمد محمد",
            "https://randomuser.me/api/portraits/men/1.jpg"
        )
    elif notification_type == "message":
        success = email_service.send_new_message_notification(
            user_email,
            "سارة أحمد",
            "مرحباً! كيف حالك؟ 😊"
        )
    elif notification_type == "like":
        success = email_service.send_new_like_notification(
            user_email,
            "فاطمة علي"
        )
    elif notification_type == "reengagement":
        success = email_service.send_reengagement_email(
            user_email,
            profile.get('display_name', 'المستخدم') if profile else "المستخدم"
        )
    else:
        raise HTTPException(status_code=400, detail="Invalid notification type")
    
    return {"success": success, "type": notification_type}


# ============================================================================
# i18n & Geo Endpoints
# ============================================================================

SUPPORTED_LANGUAGES = ["ar", "en", "fr", "es", "de", "tr", "it", "pt-BR", "ru"]

@api_router.put("/user/language")
async def update_user_language(
    request: dict,
    current_user: dict = Depends(get_current_user)
):
    """Update user's preferred language (BCP-47)"""
    lang = request.get("language")
    
    if not lang or lang not in SUPPORTED_LANGUAGES:
        raise HTTPException(
            status_code=400,
            detail=f"Unsupported language. Must be one of: {', '.join(SUPPORTED_LANGUAGES)}"
        )
    
    # Update user language
    await db.users.update_one(
        {"id": current_user["id"]},
        {"$set": {"language": lang}}
    )
    
    return {"success": True, "language": lang}


@api_router.get("/me")
async def get_current_user_info(
    current_user: dict = Depends(get_current_user)
):
    """Get current user info including language preference"""
    user = await db.users.find_one({"id": current_user["id"]})
    
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Get profile for location data
    profile = await db.profiles.find_one({"user_id": current_user["id"]})
    
    return {
        "id": user["id"],
        "name": user["name"],
        "email": user["email"],
        "language": user.get("language", "en"),
        "country": user.get("country"),
        "premium_tier": user.get("premium_tier", "free"),
        "profile_completed": user.get("profile_completed", False),
        "latitude": profile.get("latitude") if profile else None,
        "longitude": profile.get("longitude") if profile else None,
        "radiusKm": profile.get("radiusKm", 25) if profile else 25
    }


@api_router.get("/geoip")
async def get_geoip_info(request: Request):
    """
    Get country from IP address (GeoIP fallback)
    For testing: returns default country (CH for Basel)
    In production: integrate with ipapi.co or similar service
    """
    try:
        client_ip = request.client.host if request.client else "0.0.0.0"
        
        # TODO: In production, call external GeoIP service
        # Example: requests.get(f"https://ipapi.co/{client_ip}/json/")
        # For now, return default for testing
        default_country = "CH"  # Basel, Switzerland for testing
        
        return {
            "ip": client_ip,
            "country": default_country,
            "defaultRadius": radius_for_country(default_country)
        }
    except Exception as e:
        # Fallback to global default
        return {
            "ip": "unknown",
            "country": None,
            "defaultRadius": GLOBAL_DEFAULT_RADIUS
        }


@api_router.put("/user/location")
async def update_user_location(
    location_data: dict,
    current_user: dict = Depends(get_current_user)
):
    """
    Update user location (GPS or GeoIP fallback)
    Accepts: country, latitude, longitude, radiusKm
    """
    try:
        # Extract and validate data
        country = location_data.get("country")
        latitude = location_data.get("latitude")
        longitude = location_data.get("longitude")
        radius_km = location_data.get("radiusKm", 25)
        
        # Validate radius (guard against NaN/invalid)
        radius_km = float(radius_km) if radius_km is not None else 25
        if not (0 < radius_km <= 1000):  # Max 1000km
            radius_km = 25
        
        # Validate coordinates if provided
        if latitude is not None and longitude is not None:
            latitude = float(latitude)
            longitude = float(longitude)
            
            # Basic range validation
            if not (-90 <= latitude <= 90):
                raise HTTPException(status_code=400, detail="Invalid latitude")
            if not (-180 <= longitude <= 180):
                raise HTTPException(status_code=400, detail="Invalid longitude")
        
        # Update user country
        if country:
            await db.users.update_one(
                {"id": current_user["id"]},
                {"$set": {"country": country.upper()}}
            )
        
        # Update profile location
        profile = await db.profiles.find_one({"user_id": current_user["id"]})
        
        if profile:
            update_data = {
                "radiusKm": radius_km,
                "updated_at": datetime.now(timezone.utc).isoformat()
            }
            
            if latitude is not None and longitude is not None:
                update_data["latitude"] = latitude
                update_data["longitude"] = longitude
            
            await db.profiles.update_one(
                {"user_id": current_user["id"]},
                {"$set": update_data}
            )
        else:
            # Create profile if doesn't exist (edge case)
            new_profile = {
                "id": str(uuid.uuid4()),
                "user_id": current_user["id"],
                "display_name": current_user.get("name", "User"),
                "latitude": latitude,
                "longitude": longitude,
                "radiusKm": radius_km,
                "created_at": datetime.now(timezone.utc).isoformat(),
                "updated_at": datetime.now(timezone.utc).isoformat()
            }
            await db.profiles.insert_one(new_profile)
        
        return {
            "message": "Location updated successfully",
            "country": country,
            "hasCoordinates": latitude is not None and longitude is not None,
            "radiusKm": radius_km
        }
        
    except ValueError as e:
        raise HTTPException(status_code=400, detail=f"Invalid number format: {str(e)}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to update location: {str(e)}")


# ==========================================
# Premium Gating & Upsell Endpoints
# ==========================================

@api_router.get("/upsell/context")
async def get_upsell_context(current_user: dict = Depends(get_current_user)):
    """
    Get current user's premium status and limits for gating
    """
    try:
        # Check if user has premium subscription
        subscription = await db.subscriptions.find_one({"user_id": current_user["id"]})
        is_premium = False
        
        if subscription:
            # Check if subscription is active
            if subscription.get("status") == "active":
                is_premium = True
        
        # Get today's swipe count (stub - can be tracked in DB)
        viewed_today = 0
        
        # Super likes (stub - can be from subscription tier)
        super_like_left = 5 if is_premium else 1
        
        return {
            "isPremium": is_premium,
            "dailyLimit": 10,  # Free users get 10 swipes/day
            "viewedToday": viewed_today,
            "superLikeLeft": super_like_left,
            "tier": subscription.get("plan_id", "free") if subscription else "free"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get upsell context: {str(e)}")


@api_router.get("/premium/eligibility")
async def get_premium_eligibility(current_user: dict = Depends(get_current_user)):
    """
    Check if user can upgrade and return available plans
    """
    try:
        # Check current subscription
        subscription = await db.subscriptions.find_one({"user_id": current_user["id"]})
        current_tier = subscription.get("plan_id", "free") if subscription else "free"
        
        # Define available plans
        plans = [
            {
                "id": "gold",
                "name": "Pizoo Gold",
                "price": 9.99,
                "currency": "USD",
                "interval": "month",
                "features": [
                    "unlimited_likes",
                    "see_who_likes_you",
                    "super_likes_weekly",
                    "rewind"
                ]
            },
            {
                "id": "platinum",
                "name": "Pizoo Platinum",
                "price": 19.99,
                "currency": "USD",
                "interval": "month",
                "features": [
                    "all_gold_features",
                    "priority_likes",
                    "top_profiles",
                    "message_before_match"
                ]
            },
            {
                "id": "plus",
                "name": "Pizoo Plus",
                "price": 7.99,
                "currency": "USD",
                "interval": "month",
                "features": [
                    "unlimited_likes",
                    "passport",
                    "rewind",
                    "hide_ads"
                ]
            }
        ]
        
        return {
            "canUpgrade": current_tier == "free",
            "currentTier": current_tier,
            "plans": plans
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get eligibility: {str(e)}")


# ==========================================
# User Settings Endpoints
# ==========================================

@api_router.put("/user/settings")
async def update_user_settings(payload: dict, current_user: dict = Depends(get_current_user)):
    """
    Update user settings (safety consent, preferences, etc.)
    """
    try:
        safety_accepted = payload.get("safetyAccepted")
        
        if safety_accepted is not None:
            await db.users.update_one(
                {"id": current_user["id"]},
                {"$set": {"safetyAccepted": bool(safety_accepted)}}
            )
        
        return {"ok": True, "message": "Settings updated successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to update settings: {str(e)}")


@api_router.get("/relation/can-chat")
async def can_chat(userId: str, current_user: dict = Depends(get_current_user)):
    """
    Check if current user can chat with target user (requires like/match)
    """
    try:
        # Check if current user has liked the target user
        liked = await db.swipes.find_one({
            "user_id": current_user["id"],
            "swiped_user_id": userId,
            "action": {"$in": ["like", "super_like"]}
        })
        
        if not liked:
            return {"canChat": False, "reason": "لم تقم بالإعجاب بهذا المستخدم بعد"}
        
        return {"canChat": True}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to check chat eligibility: {str(e)}")


# ============================================================================
# DAILY USAGE QUOTAS SYSTEM
# ============================================================================

def today_str():
    """Get today's date as string in YYYY-MM-DD format"""
    return datetime.now(timezone.utc).strftime('%Y-%m-%d')

# Default limits for free users
DEFAULT_VIEW_LIMIT = 20
DEFAULT_LIKE_LIMIT = 10

async def get_usage(user_id: str):
    """Get or create today's usage document for user"""
    day = today_str()
    doc = await db.user_usage.find_one({"user_id": user_id, "day": day})
    if not doc:
        doc = {
            "id": str(uuid.uuid4()),
            "user_id": user_id,
            "day": day,
            "views": 0,
            "likes": 0
        }
        await db.user_usage.insert_one(doc)
    return doc

@api_router.get("/usage/context")
async def usage_context(current_user: dict = Depends(get_current_user)):
    """Get user's daily usage statistics"""
    try:
        usage = await get_usage(current_user["id"])
        
        # Premium users have no limits
        user = await db.users.find_one({"id": current_user["id"]}, {"_id": 0, "premium_tier": 1})
        is_premium = user and user.get('premium_tier') in ['gold', 'platinum', 'plus']
        
        if is_premium:
            return {
                "day": usage["day"],
                "views": usage["views"],
                "viewLimit": -1,  # -1 means unlimited
                "likes": usage["likes"],
                "likeLimit": -1,
                "remainingViews": -1,
                "remainingLikes": -1,
                "isPremium": True
            }
        
        return {
            "day": usage["day"],
            "views": usage["views"],
            "viewLimit": DEFAULT_VIEW_LIMIT,
            "likes": usage["likes"],
            "likeLimit": DEFAULT_LIKE_LIMIT,
            "remainingViews": max(0, DEFAULT_VIEW_LIMIT - usage["views"]),
            "remainingLikes": max(0, DEFAULT_LIKE_LIMIT - usage["likes"]),
            "isPremium": False
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get usage context: {str(e)}")

class UsageIncrementPayload(BaseModel):
    kind: str  # 'view' or 'like'

@api_router.post("/usage/increment")
async def usage_increment(payload: UsageIncrementPayload, current_user: dict = Depends(get_current_user)):
    """Increment usage counter for views or likes"""
    try:
        # Premium users bypass limits
        user = await db.users.find_one({"id": current_user["id"]}, {"_id": 0, "premium_tier": 1})
        is_premium = user and user.get('premium_tier') in ['gold', 'platinum', 'plus']
        
        if is_premium:
            # Still track usage but don't enforce limits
            usage = await get_usage(current_user["id"])
            if payload.kind == 'view':
                await db.user_usage.update_one(
                    {"id": usage["id"]}, 
                    {"$inc": {"views": 1}}
                )
            elif payload.kind == 'like':
                await db.user_usage.update_one(
                    {"id": usage["id"]}, 
                    {"$inc": {"likes": 1}}
                )
            return {"ok": True, "premium": True}
        
        # For free users, check and enforce limits
        usage = await get_usage(current_user["id"])
        
        if payload.kind == 'view':
            if usage["views"] >= DEFAULT_VIEW_LIMIT:
                raise HTTPException(
                    status_code=status.HTTP_429_TOO_MANY_REQUESTS, 
                    detail="view_limit_reached"
                )
            await db.user_usage.update_one(
                {"id": usage["id"]}, 
                {"$inc": {"views": 1}}
            )
        elif payload.kind == 'like':
            if usage["likes"] >= DEFAULT_LIKE_LIMIT:
                raise HTTPException(
                    status_code=status.HTTP_429_TOO_MANY_REQUESTS, 
                    detail="like_limit_reached"
                )
            await db.user_usage.update_one(
                {"id": usage["id"]}, 
                {"$inc": {"likes": 1}}
            )
        else:
            raise HTTPException(status_code=400, detail="Invalid kind. Must be 'view' or 'like'")
        
        return {"ok": True, "premium": False}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to increment usage: {str(e)}")


# ============================================================================
# USER LANGUAGE PREFERENCE
# ============================================================================

class LanguagePayload(BaseModel):
    language: str = 'en'

@api_router.put("/user/language")
async def update_user_language(payload: LanguagePayload, current_user: dict = Depends(get_current_user)):
    """Update user's preferred language"""
    try:
        # Validate language code
        supported_languages = ['en', 'ar', 'fr', 'es', 'de', 'tr', 'it', 'pt-BR', 'ru']
        lang = payload.language if payload.language in supported_languages else 'en'
        
        # Update user's language preference
        await db.users.update_one(
            {"id": current_user["id"]},
            {"$set": {"language": lang}}
        )
        
        return {"ok": True, "language": lang}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to update language: {str(e)}")


# ===== Explore & Personal Moments Endpoints =====

@api_router.get("/explore/sections")
async def get_explore_sections(current_user: dict = Depends(get_current_user)):
    """
    Get explore sections with trending, nearby, and new profiles
    Enhanced with 8 sections: Most Active, Ready to Chat, Near You, New Faces, 
    Serious Love, Fun Date Today, Smart Talks, Friends Only
    """
    try:
        # Get user's location for nearby calculation
        user_profile = await db.profiles.find_one({"user_id": current_user["id"]})
        user_lat = user_profile.get("latitude") if user_profile else None
        user_lon = user_profile.get("longitude") if user_profile else None
        
        # Fetch all profiles (excluding current user)
        all_profiles = await db.profiles.find({
            "user_id": {"$ne": current_user["id"]}
        }).to_list(length=100)
        
        sections = []
        
        # Section 1: Most Active (الأكثر تفاعلاً)
        # Mock: profiles with most photos or most recent activity
        active_profiles = sorted(all_profiles, key=lambda p: len(p.get('photos', [])), reverse=True)[:10]
        sections.append({
            "type": "most_active",
            "title": "Most Active",
            "profiles": [format_profile_for_explore(p, user_lat, user_lon) for p in active_profiles]
        })
        
        # Section 2: Ready to Chat (متاحون الآن)
        # Mock: online users or recently active
        ready_profiles = [p for p in all_profiles if p.get('online', False)][:10]
        if not ready_profiles:
            ready_profiles = all_profiles[:10]
        sections.append({
            "type": "ready_chat",
            "title": "Ready to Chat",
            "profiles": [format_profile_for_explore(p, user_lat, user_lon) for p in ready_profiles]
        })
        
        # Section 3: Near You (بالقرب منك)
        if user_lat and user_lon:
            nearby_profiles = []
            for profile in all_profiles:
                if profile.get('latitude') and profile.get('longitude'):
                    distance = calculate_distance(
                        user_lat, user_lon,
                        profile['latitude'], profile['longitude']
                    )
                    if distance <= 25:  # Within 25km
                        profile['distance'] = round(distance, 1)
                        nearby_profiles.append(profile)
            
            nearby_profiles = sorted(nearby_profiles, key=lambda p: p.get('distance', 999))[:10]
            sections.append({
                "type": "near_you",
                "title": "Near You",
                "profiles": [format_profile_for_explore(p, user_lat, user_lon) for p in nearby_profiles]
            })
        
        # Section 4: New Faces (وجوه جديدة)
        newcomers = sorted(
            all_profiles,
            key=lambda p: p.get('created_at', ''),
            reverse=True
        )[:10]
        sections.append({
            "type": "new_faces",
            "title": "New Faces",
            "profiles": [format_profile_for_explore(p, user_lat, user_lon) for p in newcomers]
        })
        
        # Section 5: Serious Love (بحث جدي)
        # Mock: profiles with "serious" interest or relationship goal
        serious_profiles = [p for p in all_profiles if 'serious' in str(p.get('interests', [])).lower() or p.get('relationship_goal') == 'serious'][:10]
        if not serious_profiles:
            serious_profiles = all_profiles[10:20]
        sections.append({
            "type": "serious_love",
            "title": "Serious Love",
            "profiles": [format_profile_for_explore(p, user_lat, user_lon) for p in serious_profiles]
        })
        
        # Section 6: Fun Date Today (موعد ممتع اليوم)
        # Mock: profiles with fun interests
        fun_profiles = [p for p in all_profiles if any(x in str(p.get('interests', [])).lower() for x in ['fun', 'party', 'music', 'dance'])][:10]
        if not fun_profiles:
            fun_profiles = all_profiles[20:30]
        sections.append({
            "type": "fun_date",
            "title": "Fun Date Today",
            "profiles": [format_profile_for_explore(p, user_lat, user_lon) for p in fun_profiles]
        })
        
        # Section 7: Smart Talks (دردشات ذكية)
        # Mock: profiles with intellectual interests
        smart_profiles = [p for p in all_profiles if any(x in str(p.get('interests', [])).lower() for x in ['books', 'art', 'science', 'philosophy', 'technology'])][:10]
        if not smart_profiles:
            smart_profiles = all_profiles[30:40]
        sections.append({
            "type": "smart_talks",
            "title": "Smart Talks",
            "profiles": [format_profile_for_explore(p, user_lat, user_lon) for p in smart_profiles]
        })
        
        # Section 8: Friends Only (أصدقاء فقط)
        # Mock: profiles looking for friends
        friends_profiles = [p for p in all_profiles if 'friend' in str(p.get('interests', [])).lower() or p.get('relationship_goal') == 'friends'][:10]
        if not friends_profiles:
            friends_profiles = all_profiles[40:50]
        sections.append({
            "type": "friends_only",
            "title": "Friends Only",
            "profiles": [format_profile_for_explore(p, user_lat, user_lon) for p in friends_profiles]
        })
        
        return {"sections": sections}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch explore sections: {str(e)}")


def format_profile_for_explore(profile: dict, user_lat: float = None, user_lon: float = None) -> dict:
    """Format profile for explore display"""
    formatted = {
        "id": profile.get("user_id"),
        "name": profile.get("name", "Unknown"),
        "age": profile.get("age", 0),
        "location": profile.get("location", ""),
        "photos": profile.get("photos", [])
    }
    
    # Calculate distance if coordinates available
    if user_lat and user_lon and profile.get('latitude') and profile.get('longitude'):
        distance = calculate_distance(
            user_lat, user_lon,
            profile['latitude'], profile['longitude']
        )
        formatted["distance"] = round(distance, 1)
    
    return formatted


@api_router.get("/personal/list")
async def get_personal_moments(current_user: dict = Depends(get_current_user)):
    """
    Get personalized moments/opportunities for the user
    Safe categories for app stores: Flatshare, Travel, Outing, Activities
    """
    try:
        # Mock data for personal moments - safe categories only
        moments = [
            {
                "id": "moment_flatshare_1",
                "title": "Looking for Flatshare",
                "description": "Searching for a tidy, respectful roommate in the city center. Shared apartment with modern amenities.",
                "image": "https://images.unsplash.com/photo-1502672260266-1c1ef2d93688?w=400",
                "isPremium": False,
                "isNew": True,
                "action": "open_link",
                "link": "#",
                "ctaText": "View Details",
                "category": "flatshare"
            },
            {
                "id": "moment_travel_1",
                "title": "Travel Buddy Needed",
                "description": "Planning a weekend trip to the mountains. Tickets and accommodation ready. Looking for an adventure partner!",
                "image": "https://images.unsplash.com/photo-1469854523086-cc02fe5d8800?w=400",
                "isPremium": False,
                "isNew": True,
                "action": "open_link",
                "link": "#",
                "ctaText": "Join Trip",
                "category": "travel"
            },
            {
                "id": "moment_outing_1",
                "title": "Tonight's Elegant Dinner",
                "description": "Reservation at a nice restaurant downtown. Great food, good atmosphere. Who wants to join?",
                "image": "https://images.unsplash.com/photo-1414235077428-338989a2e8c0?w=400",
                "isPremium": False,
                "isNew": False,
                "action": "open_link",
                "link": "#",
                "ctaText": "Reserve Spot",
                "category": "outing"
            },
            {
                "id": "moment_activity_1",
                "title": "Try VR Gaming Together",
                "description": "New VR arcade opened! Let's try the latest games and have fun. Perfect for gaming enthusiasts!",
                "image": "https://images.unsplash.com/photo-1535223289827-42f1e9919769?w=400",
                "isPremium": True,
                "isNew": True,
                "action": "open_link",
                "link": "#",
                "ctaText": "Book Session",
                "category": "activity"
            },
            {
                "id": "moment_flatshare_2",
                "title": "Roommate Wanted",
                "description": "Nice 2-bedroom apartment available. Quiet neighborhood, close to public transport. Looking for a long-term roommate.",
                "image": "https://images.unsplash.com/photo-1560448204-e02f11c3d0e2?w=400",
                "isPremium": False,
                "isNew": False,
                "action": "open_link",
                "link": "#",
                "ctaText": "Contact",
                "category": "flatshare"
            },
            {
                "id": "moment_travel_2",
                "title": "Beach Weekend Escape",
                "description": "Coastal getaway this weekend. Relaxing by the beach, good food, and great company. Join us!",
                "image": "https://images.unsplash.com/photo-1507525428034-b723cf961d3e?w=400",
                "isPremium": True,
                "isNew": False,
                "action": "open_link",
                "link": "#",
                "ctaText": "Join Adventure",
                "category": "travel"
            }
        ]
        
        return {"moments": moments}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch personal moments: {str(e)}")


# OTP Stubs
@api_router.post("/auth/otp/send")
async def otp_send(payload: dict):
    """Send OTP to phone number"""
    phone = payload.get("phone")
    if not phone:
        raise HTTPException(status_code=400, detail="phone required")
    # TODO: Implement actual OTP sending logic
    return {"ok": True, "message": "OTP sent successfully"}


@api_router.post("/auth/otp/verify")
async def otp_verify(payload: dict):
    """Verify OTP code"""
    phone = payload.get("phone")
    code = payload.get("code")
    if not code:
        raise HTTPException(status_code=400, detail="code required")
    # TODO: Implement actual OTP verification logic
    return {"ok": True, "message": "OTP verified successfully"}


@api_router.post("/messages/send")
async def msg_send(payload: dict, current_user: dict = Depends(optional_auth)):
    """Send a message"""
    text = payload.get("body")
    conversation_id = payload.get("conversationId")
    if not text:
        raise HTTPException(status_code=400, detail="body required")
    
    # Return a mock message
    return {
        "message": {
            "id": f"msg-{int(time.time())}",
            "body": text,
            "mine": True,
            "status": "sent",
            "createdAt": datetime.now(timezone.utc).isoformat()
        }
    }


# AI Matching Algorithm
@api_router.get("/ai/match")
async def ai_match_profiles(
    current_user: dict = Depends(get_current_user)
):
    """
    AI-powered matching algorithm that ranks profiles based on:
    - Common interests
    - Location proximity
    - Age compatibility
    - Activity level
    - Personality match score
    """
    try:
        user_id = current_user.get('id')
        
        # Get current user's profile
        user_profile = await db.users.find_one({"id": user_id})
        if not user_profile:
            raise HTTPException(status_code=404, detail="User profile not found")
        
        # Get user preferences
        user_interests = user_profile.get('interests', [])
        user_age = user_profile.get('age', 25)
        user_location = user_profile.get('location', {})
        user_gender = user_profile.get('gender', '')
        user_looking_for = user_profile.get('lookingFor', '')
        
        # Fetch potential matches
        query = {
            "id": {"$ne": user_id},
            "profileSetupComplete": True
        }
        
        # Filter by gender preference
        if user_looking_for:
            query["gender"] = user_looking_for
        
        potential_matches = await db.users.find(query).to_list(length=100)
        
        # AI Scoring Algorithm
        scored_matches = []
        for profile in potential_matches:
            score = 0
            reasons = []
            
            # 1. Interest Match (40% weight)
            profile_interests = profile.get('interests', [])
            common_interests = set(user_interests) & set(profile_interests)
            interest_score = (len(common_interests) / max(len(user_interests), 1)) * 40
            score += interest_score
            if common_interests:
                reasons.append(f"Shares {len(common_interests)} interests")
            
            # 2. Age Compatibility (20% weight)
            profile_age = profile.get('age', 25)
            age_diff = abs(user_age - profile_age)
            if age_diff <= 3:
                age_score = 20
            elif age_diff <= 5:
                age_score = 15
            elif age_diff <= 10:
                age_score = 10
            else:
                age_score = 5
            score += age_score
            if age_diff <= 5:
                reasons.append("Perfect age match")
            
            # 3. Location Proximity (15% weight)
            profile_location = profile.get('location', {})
            if user_location.get('city') == profile_location.get('city'):
                location_score = 15
                reasons.append("Same city")
            elif user_location.get('country') == profile_location.get('country'):
                location_score = 10
                reasons.append("Same country")
            else:
                location_score = 5
            score += location_score
            
            # 4. Activity Level (10% weight)
            user_last_active = user_profile.get('lastActive', datetime.now(timezone.utc))
            profile_last_active = profile.get('lastActive', datetime.now(timezone.utc))
            if isinstance(profile_last_active, str):
                try:
                    profile_last_active = datetime.fromisoformat(profile_last_active.replace('Z', '+00:00'))
                except:
                    profile_last_active = datetime.now(timezone.utc)
            
            hours_since_active = (datetime.now(timezone.utc) - profile_last_active).total_seconds() / 3600
            if hours_since_active < 24:
                activity_score = 10
                reasons.append("Active today")
            elif hours_since_active < 72:
                activity_score = 7
            else:
                activity_score = 3
            score += activity_score
            
            # 5. Profile Completeness (15% weight)
            profile_fields = ['bio', 'photos', 'occupation', 'education']
            completed_fields = sum(1 for field in profile_fields if profile.get(field))
            completeness_score = (completed_fields / len(profile_fields)) * 15
            score += completeness_score
            if completed_fields >= 3:
                reasons.append("Complete profile")
            
            # Add to scored matches
            scored_matches.append({
                "profile": {
                    "id": profile.get('id'),
                    "name": profile.get('name'),
                    "age": profile.get('age'),
                    "bio": profile.get('bio', ''),
                    "photos": profile.get('photos', []),
                    "interests": profile.get('interests', []),
                    "location": profile.get('location', {}),
                    "occupation": profile.get('occupation', ''),
                    "verified": profile.get('verified', False)
                },
                "matchScore": round(score, 1),
                "matchReasons": reasons[:3],  # Top 3 reasons
                "compatibility": "high" if score >= 70 else "medium" if score >= 50 else "good"
            })
        
        # Sort by score (highest first)
        scored_matches.sort(key=lambda x: x['matchScore'], reverse=True)
        
        # Return top 20 matches
        return {
            "matches": scored_matches[:20],
            "total": len(scored_matches),
            "algorithm": "AI-powered compatibility matching"
        }
        
    except Exception as e:
        logging.error(f"AI matching error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to generate AI matches: {str(e)}")


# ==================== ADMIN ENDPOINTS ====================
# Simple admin endpoints for dashboard - TODO: Add proper authentication

@api_router.get("/admin/users")
async def admin_list_users(
    skip: int = 0,
    limit: int = 50,
    search: Optional[str] = None
):
    """
    List all users for admin dashboard
    TODO: Add admin authentication middleware
    """
    query = {"is_deleted": {"$ne": True}}
    
    if search:
        query["$or"] = [
            {"email": {"$regex": search, "$options": "i"}},
            {"name": {"$regex": search, "$options": "i"}},
            {"id": search}
        ]
    
    users_cursor = db.users.find(
        query,
        {
            "id": 1,
            "email": 1,
            "name": 1,
            "created_at": 1,
            "is_deleted": 1,
            "email_verified": 1,
            "subscription_type": 1,
            "_id": 0
        }
    ).skip(skip).limit(limit)
    
    users = [serialize_mongo_doc(user) async for user in users_cursor]
    total = await db.users.count_documents(query)
    
    return {
        "items": users,
        "total": total,
        "skip": skip,
        "limit": limit
    }


@api_router.get("/admin/stats")
async def admin_stats():
    """
    Get platform statistics for admin dashboard
    TODO: Add admin authentication middleware
    """
    try:
        # Count users
        total_users = await db.users.count_documents({})
        active_users = await db.users.count_documents({"is_deleted": {"$ne": True}})
        verified_users = await db.users.count_documents({"email_verified": True})
        
        # Count profiles
        profiles = await db.profiles.count_documents({})
        complete_profiles = await db.profiles.count_documents({"profileSetupComplete": True})
        
        # Count interactions
        messages = await db.messages.count_documents({})
        matches = await db.matches.count_documents({})
        likes = await db.likes.count_documents({})
        swipes = await db.swipes.count_documents({})
        
        # Count subscriptions
        free_users = await db.users.count_documents({"subscription_type": "free"})
        gold_users = await db.users.count_documents({"subscription_type": "gold"})
        platinum_users = await db.users.count_documents({"subscription_type": "platinum"})
        
        return {
            "users": {
                "total": total_users,
                "active": active_users,
                "verified": verified_users,
                "deleted": total_users - active_users
            },
            "profiles": {
                "total": profiles,
                "complete": complete_profiles,
                "incomplete": profiles - complete_profiles
            },
            "interactions": {
                "messages": messages,
                "matches": matches,
                "likes": likes,
                "swipes": swipes
            },
            "subscriptions": {
                "free": free_users,
                "gold": gold_users,
                "platinum": platinum_users
            }
        }
    except Exception as e:
        logging.error(f"Failed to get admin stats: {e}")
        raise HTTPException(status_code=500, detail="Failed to retrieve statistics")


# Mount the API router
app.include_router(api_router)

