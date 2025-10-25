"""
Email Service for Pizoo Dating App
Handles email verification, notifications, and marketing emails
"""
import os
import random
import string
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail
from typing import Optional
from datetime import datetime, timezone, timedelta

# Store OTP codes temporarily (in production, use Redis or database)
otp_storage = {}

class EmailService:
    def __init__(self):
        self.api_key = os.getenv('SENDGRID_API_KEY')
        self.sender_email = os.getenv('SENDER_EMAIL', 'noreply@pizoo.app')
        self.sg = SendGridAPIClient(self.api_key) if self.api_key else None
    
    def generate_otp(self, length=6):
        """Generate random OTP code"""
        return ''.join(random.choices(string.digits, k=length))
    
    def send_email(self, to_email: str, subject: str, html_content: str, plain_text_content: Optional[str] = None):
        """Send email via SendGrid"""
        if not self.sg:
            print(f"⚠️  SendGrid not configured. Would send email to {to_email}: {subject}")
            return True
        
        try:
            message = Mail(
                from_email=self.sender_email,
                to_emails=to_email,
                subject=subject,
                html_content=html_content,
                plain_text_content=plain_text_content
            )
            
            response = self.sg.send(message)
            return response.status_code == 202
        except Exception as e:
            print(f"❌ Error sending email: {str(e)}")
            return False
    
    def send_verification_otp(self, email: str):
        """Send OTP verification email"""
        otp = self.generate_otp()
        
        # Store OTP with expiry (5 minutes)
        otp_storage[email] = {
            'code': otp,
            'expires_at': datetime.now(timezone.utc) + timedelta(minutes=5)
        }
        
        subject = "تأكيد بريدك الإلكتروني - Pizoo"
        
        html_content = f"""
        <!DOCTYPE html>
        <html dir="rtl" lang="ar">
        <head>
            <meta charset="UTF-8">
            <style>
                body {{ font-family: Arial, sans-serif; background-color: #f9f9f9; padding: 20px; }}
                .container {{ max-width: 600px; margin: 0 auto; background-color: white; border-radius: 10px; overflow: hidden; box-shadow: 0 4px 6px rgba(0,0,0,0.1); }}
                .header {{ background: linear-gradient(135deg, #ec4899, #f472b6); color: white; padding: 30px; text-align: center; }}
                .content {{ padding: 30px; text-align: center; }}
                .otp-code {{ font-size: 36px; font-weight: bold; color: #ec4899; letter-spacing: 8px; margin: 20px 0; }}
                .footer {{ background-color: #f3f4f6; padding: 20px; text-align: center; font-size: 14px; color: #6b7280; }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>❤️‍🔥 Pizoo</h1>
                    <p>مرحباً بك في تطبيق المواعدة الأول</p>
                </div>
                <div class="content">
                    <h2>تأكيد بريدك الإلكتروني</h2>
                    <p>استخدم الرمز التالي لتأكيد حسابك:</p>
                    <div class="otp-code">{otp}</div>
                    <p style="color: #6b7280; font-size: 14px;">الرمز صالح لمدة 5 دقائق</p>
                    <p style="margin-top: 30px;">إذا لم تطلب هذا الرمز، يرجى تجاهل هذه الرسالة.</p>
                </div>
                <div class="footer">
                    <p>© 2025 Pizoo. جميع الحقوق محفوظة.</p>
                </div>
            </div>
        </body>
        </html>
        """
        
        plain_text = f"رمز التحقق الخاص بك هو: {otp}. صالح لمدة 5 دقائق."
        
        return self.send_email(email, subject, html_content, plain_text)
    
    def verify_otp(self, email: str, code: str):
        """Verify OTP code"""
        if email not in otp_storage:
            return False
        
        stored = otp_storage[email]
        
        # Check expiry
        if datetime.now(timezone.utc) > stored['expires_at']:
            del otp_storage[email]
            return False
        
        # Check code
        if stored['code'] == code:
            del otp_storage[email]
            return True
        
        return False
    
    def send_new_match_notification(self, email: str, match_name: str, match_photo: str):
        """Send new match notification email"""
        subject = f"🎉 لديك تطابق جديد مع {match_name}!"
        
        html_content = f"""
        <!DOCTYPE html>
        <html dir="rtl" lang="ar">
        <head>
            <meta charset="UTF-8">
            <style>
                body {{ font-family: Arial, sans-serif; background-color: #f9f9f9; padding: 20px; }}
                .container {{ max-width: 600px; margin: 0 auto; background-color: white; border-radius: 10px; overflow: hidden; box-shadow: 0 4px 6px rgba(0,0,0,0.1); }}
                .header {{ background: linear-gradient(135deg, #ec4899, #f472b6); color: white; padding: 20px; text-align: center; }}
                .content {{ padding: 30px; text-align: center; }}
                .match-photo {{ width: 150px; height: 150px; border-radius: 50%; object-fit: cover; margin: 20px auto; }}
                .cta-button {{ display: inline-block; background: linear-gradient(135deg, #ec4899, #f472b6); color: white; padding: 15px 40px; border-radius: 50px; text-decoration: none; font-weight: bold; margin: 20px 0; }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>❤️‍🔥 Pizoo</h1>
                </div>
                <div class="content">
                    <h2>🎉 تطابق جديد!</h2>
                    <img src="{match_photo}" alt="{match_name}" class="match-photo">
                    <p style="font-size: 18px;">لديك تطابق جديد مع <strong>{match_name}</strong></p>
                    <p>ابدأ المحادثة الآن واكتشف المزيد!</p>
                    <a href="https://pizoo.app/matches" class="cta-button">شاهد التطابق</a>
                </div>
            </div>
        </body>
        </html>
        """
        
        return self.send_email(email, subject, html_content)
    
    def send_new_message_notification(self, email: str, sender_name: str, message_preview: str):
        """Send new message notification"""
        subject = f"💬 رسالة جديدة من {sender_name}"
        
        html_content = f"""
        <!DOCTYPE html>
        <html dir="rtl" lang="ar">
        <head>
            <meta charset="UTF-8">
            <style>
                body {{ font-family: Arial, sans-serif; background-color: #f9f9f9; padding: 20px; }}
                .container {{ max-width: 600px; margin: 0 auto; background-color: white; border-radius: 10px; overflow: hidden; }}
                .header {{ background: linear-gradient(135deg, #ec4899, #f472b6); color: white; padding: 20px; text-align: center; }}
                .content {{ padding: 30px; }}
                .message-box {{ background: #f3f4f6; padding: 15px; border-radius: 10px; margin: 20px 0; font-style: italic; }}
                .cta-button {{ display: inline-block; background: linear-gradient(135deg, #ec4899, #f472b6); color: white; padding: 12px 30px; border-radius: 50px; text-decoration: none; }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>❤️‍🔥 Pizoo</h1>
                </div>
                <div class="content">
                    <h2>رسالة جديدة من {sender_name}</h2>
                    <div class="message-box">"{message_preview}"</div>
                    <a href="https://pizoo.app/chat" class="cta-button">الرد الآن</a>
                </div>
            </div>
        </body>
        </html>
        """
        
        return self.send_email(email, subject, html_content)
    
    def send_new_like_notification(self, email: str, liker_name: str):
        """Send new like notification"""
        subject = f"❤️ {liker_name} أعجب بك!"
        
        html_content = f"""
        <!DOCTYPE html>
        <html dir="rtl" lang="ar">
        <head>
            <meta charset="UTF-8">
            <style>
                body {{ font-family: Arial, sans-serif; background-color: #f9f9f9; padding: 20px; }}
                .container {{ max-width: 600px; margin: 0 auto; background-color: white; border-radius: 10px; overflow: hidden; }}
                .header {{ background: linear-gradient(135deg, #ec4899, #f472b6); color: white; padding: 20px; text-align: center; }}
                .content {{ padding: 30px; text-align: center; }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>❤️‍🔥 Pizoo</h1>
                </div>
                <div class="content">
                    <h2>❤️ إعجاب جديد!</h2>
                    <p style="font-size: 18px;">{liker_name} أعجب بملفك الشخصي</p>
                    <p>اضغط "أعجبني" أيضاً لإنشاء تطابق!</p>
                    <a href="https://pizoo.app/likes" style="display: inline-block; background: linear-gradient(135deg, #ec4899, #f472b6); color: white; padding: 12px 30px; border-radius: 50px; text-decoration: none; margin-top: 20px;">عرض الإعجابات</a>
                </div>
            </div>
        </body>
        </html>
        """
        
        return self.send_email(email, subject, html_content)
    
    def send_reengagement_email(self, email: str, user_name: str):
        """Send re-engagement email to inactive users"""
        subject = f"{user_name}، نحن نفتقدك! 💖"
        
        html_content = f"""
        <!DOCTYPE html>
        <html dir="rtl" lang="ar">
        <head>
            <meta charset="UTF-8">
            <style>
                body {{ font-family: Arial, sans-serif; background-color: #f9f9f9; padding: 20px; }}
                .container {{ max-width: 600px; margin: 0 auto; background-color: white; border-radius: 10px; overflow: hidden; }}
                .header {{ background: linear-gradient(135deg, #ec4899, #f472b6); color: white; padding: 30px; text-align: center; }}
                .content {{ padding: 30px; text-align: center; }}
                .stats {{ display: flex; justify-content: space-around; margin: 30px 0; }}
                .stat {{ text-align: center; }}
                .stat-number {{ font-size: 32px; font-weight: bold; color: #ec4899; }}
                .cta-button {{ display: inline-block; background: linear-gradient(135deg, #ec4899, #f472b6); color: white; padding: 15px 40px; border-radius: 50px; text-decoration: none; font-weight: bold; margin-top: 20px; }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>❤️‍🔥 Pizoo</h1>
                    <p>نحن نفتقدك يا {user_name}!</p>
                </div>
                <div class="content">
                    <h2>هناك الكثير يحدث أثناء غيابك!</h2>
                    <div class="stats">
                        <div class="stat">
                            <div class="stat-number">5+</div>
                            <p>إعجابات جديدة</p>
                        </div>
                        <div class="stat">
                            <div class="stat-number">15+</div>
                            <p>زوار للملف</p>
                        </div>
                        <div class="stat">
                            <div class="stat-number">3</div>
                            <p>تطابقات محتملة</p>
                        </div>
                    </div>
                    <p style="font-size: 18px;">لا تدع الفرصة تفوتك!</p>
                    <a href="https://pizoo.app/" class="cta-button">عودة إلى Pizoo</a>
                </div>
            </div>
        </body>
        </html>
        """
        
        return self.send_email(email, subject, html_content)

# Singleton instance
email_service = EmailService()
