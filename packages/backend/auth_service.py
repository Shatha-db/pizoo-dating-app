"""
Authentication Service for Pizoo Dating App
Handles Google OAuth, Email Magic Link, Phone OTP verification
"""

import os
import httpx
import secrets
import string
from datetime import datetime, timezone, timedelta
from typing import Optional, Dict, Tuple
from jose import JWTError, jwt
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import logging

# JWT Settings
SECRET_KEY = os.environ.get('SECRET_KEY', 'dev-secret-key-do-not-use-in-production')
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60  # 1 hour
REFRESH_TOKEN_EXPIRE_DAYS = 7  # 7 days

# Email Settings
SMTP_HOST = os.environ.get('SMTP_HOST', 'smtp.gmail.com')
SMTP_PORT = int(os.environ.get('SMTP_PORT', '587'))
SMTP_USER = os.environ.get('SMTP_USER', '')
SMTP_PASS = os.environ.get('SMTP_PASS', '')
EMAIL_FROM = os.environ.get('EMAIL_FROM', 'Pizoo App <noreply@pizoo.app>')
EMAIL_MODE = os.environ.get('EMAIL_MODE', 'mock')  # 'smtp' or 'mock'

# Frontend URL for magic links
FRONTEND_URL = os.environ.get('FRONTEND_URL', 'http://localhost:3000')

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class AuthService:
    """Authentication service for OAuth, email, and phone verification"""
    
    @staticmethod
    def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
        """Create JWT access token"""
        to_encode = data.copy()
        if expires_delta:
            expire = datetime.now(timezone.utc) + expires_delta
        else:
            expire = datetime.now(timezone.utc) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        
        to_encode.update({
            "exp": expire,
            "iat": datetime.now(timezone.utc),
            "type": "access"
        })
        encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
        return encoded_jwt
    
    @staticmethod
    def create_refresh_token(data: dict) -> str:
        """Create JWT refresh token (7 days)"""
        to_encode = data.copy()
        expire = datetime.now(timezone.utc) + timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS)
        
        to_encode.update({
            "exp": expire,
            "iat": datetime.now(timezone.utc),
            "type": "refresh"
        })
        encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
        return encoded_jwt
    
    @staticmethod
    def verify_token(token: str, token_type: str = "access") -> Optional[Dict]:
        """Verify JWT token and return payload"""
        try:
            payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
            
            # Verify token type
            if payload.get("type") != token_type:
                logger.warning(f"Token type mismatch: expected {token_type}, got {payload.get('type')}")
                return None
            
            return payload
        except JWTError as e:
            logger.error(f"JWT verification failed: {e}")
            return None
    
    @staticmethod
    async def get_emergent_oauth_session_data(session_id: str) -> Optional[Dict]:
        """
        Get user data from Emergent OAuth session
        Returns: {"id": str, "email": str, "name": str, "picture": str, "session_token": str}
        """
        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                response = await client.get(
                    "https://demobackend.emergentagent.com/auth/v1/env/oauth/session-data",
                    headers={"X-Session-ID": session_id}
                )
                
                if response.status_code == 200:
                    return response.json()
                else:
                    logger.error(f"Emergent OAuth session fetch failed: {response.status_code} - {response.text}")
                    return None
        except Exception as e:
            logger.error(f"Error fetching Emergent OAuth session: {e}")
            return None
    
    @staticmethod
    def generate_verification_token() -> str:
        """Generate a secure random token for email verification"""
        return secrets.token_urlsafe(32)
    
    @staticmethod
    def generate_otp() -> str:
        """Generate a 6-digit OTP for phone verification"""
        return ''.join(secrets.choice(string.digits) for _ in range(6))
    
    @staticmethod
    async def send_verification_email(email: str, token: str, user_name: str) -> bool:
        """Send magic link verification email"""
        
        # MOCK MODE - for testing without real SMTP
        if EMAIL_MODE == 'mock':
            verification_link = f"{FRONTEND_URL}/verify-email?token={token}"
            logger.info(f"📧 [MOCK EMAIL] Verification link for {email}:")
            logger.info(f"   User: {user_name}")
            logger.info(f"   Link: {verification_link}")
            logger.info(f"   Token: {token}")
            logger.info(f"   Expires: 15 minutes")
            logger.info(f"")
            logger.info(f"   ✅ To test: Copy the token above and call POST /api/auth/email/verify")
            return True
        
        # REAL SMTP MODE
        try:
            # Create verification link
            verification_link = f"{FRONTEND_URL}/verify-email?token={token}"
            
            # Email content (bilingual: English + Arabic)
            html_content = f"""
            <!DOCTYPE html>
            <html dir="ltr">
            <head>
                <meta charset="UTF-8">
                <style>
                    body {{ font-family: Arial, sans-serif; background-color: #f4f4f4; padding: 20px; }}
                    .container {{ max-width: 600px; margin: 0 auto; background: white; padding: 40px; border-radius: 10px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }}
                    .header {{ text-align: center; margin-bottom: 30px; }}
                    .logo {{ font-size: 32px; font-weight: bold; color: #FF4458; }}
                    .button {{ display: inline-block; padding: 15px 40px; background: #FF4458; color: white; text-decoration: none; border-radius: 5px; margin: 20px 0; }}
                    .footer {{ text-align: center; margin-top: 30px; color: #666; font-size: 12px; }}
                    .ar-section {{ direction: rtl; text-align: right; margin-top: 40px; padding-top: 40px; border-top: 1px solid #eee; }}
                </style>
            </head>
            <body>
                <div class="container">
                    <div class="header">
                        <div class="logo">💘 Pizoo</div>
                    </div>
                    
                    <div>
                        <h2>Welcome to Pizoo, {user_name}!</h2>
                        <p>Click the button below to verify your email and activate your account:</p>
                        <a href="{verification_link}" class="button">Verify Email</a>
                        <p style="color: #666; font-size: 14px;">This link expires in 15 minutes.</p>
                        <p style="color: #666; font-size: 12px;">If you didn't request this, please ignore this email.</p>
                    </div>
                    
                    <div class="ar-section">
                        <h2>مرحبًا بك في Pizoo، {user_name}!</h2>
                        <p>اضغط على الزر أدناه للتحقق من بريدك الإلكتروني وتفعيل حسابك:</p>
                        <a href="{verification_link}" class="button">تحقق من البريد الإلكتروني</a>
                        <p style="color: #666; font-size: 14px;">ينتهي صلاحية هذا الرابط خلال 15 دقيقة.</p>
                        <p style="color: #666; font-size: 12px;">إذا لم تطلب ذلك، يرجى تجاهل هذا البريد الإلكتروني.</p>
                    </div>
                    
                    <div class="footer">
                        <p>© 2025 Pizoo. All rights reserved.</p>
                    </div>
                </div>
            </body>
            </html>
            """
            
            # Create message
            message = MIMEMultipart('alternative')
            message['Subject'] = 'Verify Your Pizoo Account | تحقق من حساب Pizoo'
            message['From'] = EMAIL_FROM
            message['To'] = email
            
            html_part = MIMEText(html_content, 'html', 'utf-8')
            message.attach(html_part)
            
            # Send email
            with smtplib.SMTP(SMTP_HOST, SMTP_PORT) as server:
                server.starttls()
                server.login(SMTP_USER, SMTP_PASS)
                server.send_message(message)
            
            logger.info(f"✅ Verification email sent to {email}")
            return True
            
        except Exception as e:
            logger.error(f"❌ Failed to send verification email to {email}: {e}")
            return False
    
    @staticmethod
    async def send_otp_sms(phone_number: str, otp_code: str) -> bool:
        """
        Send OTP via Telnyx SMS
        TODO: Implement when Telnyx credentials are provided
        """
        # Placeholder for Telnyx integration
        logger.warning(f"SMS OTP sending not yet implemented. Would send {otp_code} to {phone_number}")
        return False
    
    @staticmethod
    def calculate_session_expiry() -> datetime:
        """Calculate session expiry (7 days from now)"""
        return datetime.now(timezone.utc) + timedelta(days=7)
