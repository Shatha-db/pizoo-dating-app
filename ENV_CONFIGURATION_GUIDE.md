# 📝 Pizoo Environment Configuration Guide

## 🎯 Overview

This document explains the environment configuration for the Pizoo Dating App. The `.env` file contains all necessary API keys, secrets, and configuration values for running the application.

---

## 📂 Files Structure

```
/app/backend/
├── .env                    # Active configuration (DO NOT commit to Git)
├── .env.example            # Template with placeholders (safe to commit)
└── .env.backup.*           # Automatic backups (timestamped)
```

---

## 🔐 Security Best Practices

### ✅ DO:
- Keep `.env` file secure and never commit to Git
- Use strong, random values for `SECRET_KEY`
- Rotate credentials regularly
- Use environment-specific values (dev/staging/production)
- Enable 2FA for all third-party services
- Use `.env.example` as a template for new developers

### ❌ DON'T:
- Commit `.env` files to version control
- Share credentials via email or Slack
- Use default or weak passwords
- Hardcode secrets in source code
- Store production credentials in development environments

---

## 📋 Configuration Sections

### 1. 🧠 Core Project Settings

```env
PROJECT_NAME=Pizoo
AUTOFIX_ENABLED=false
ENVIRONMENT=production
```

**Purpose:** Basic project metadata and behavior control.

---

### 2. 🧰 GitHub Integration

```env
GITHUB_ACCESS_TOKEN=<your-token>
GITHUB_ORG_NAME=Shatha-db
GITHUB_DEFAULT_REPO=pizoo-dating-app
```

**How to get:**
1. Go to GitHub → Settings → Developer Settings
2. Generate new Personal Access Token
3. Select scopes: `repo`, `workflow`, `admin:org`

**Required permissions:** Read/Write repository, Workflows

---

### 3. 🗄️ MongoDB Database

```env
MONGO_URL=mongodb://localhost:27017
DB_NAME=test_database
```

**Environments:**
- **Local:** `mongodb://localhost:27017`
- **Production:** `mongodb+srv://user:pass@cluster.mongodb.net`
- **Docker:** `mongodb://mongo:27017`

**Best practices:**
- Use separate databases for dev/staging/prod
- Enable authentication in production
- Set up automatic backups

---

### 4. 🎥 LiveKit (Video/Voice Calls)

```env
LIVEKIT_URL=wss://pizoo-app-xxxxx.livekit.cloud
LIVEKIT_API_KEY=<your-key>
LIVEKIT_API_SECRET=<your-secret>
```

**How to get:**
1. Sign up at [livekit.io](https://livekit.io)
2. Create new project
3. Copy API Key and Secret from dashboard

**Current setup:** LiveKit Cloud (managed service)

**Alternative:** Self-hosted LiveKit (see `/app/livekit-stack/`)

---

### 5. 📸 Cloudinary (Image Storage)

```env
CLOUDINARY_CLOUD_NAME=<your-cloud>
CLOUDINARY_API_KEY=<your-key>
CLOUDINARY_API_SECRET=<your-secret>
```

**How to get:**
1. Sign up at [cloudinary.com](https://cloudinary.com)
2. Get credentials from Dashboard → Account Details

**Features enabled:**
- Auto-orient images
- EXIF stripping
- WebP conversion
- Resize to 1600px max
- Progressive JPEG

---

### 6. 🔐 JWT Authentication

```env
SECRET_KEY=<generate-secure-key>
JWT_ACCESS_TOKEN_EXPIRE_MINUTES=60
JWT_REFRESH_TOKEN_EXPIRE_DAYS=7
```

**Generate secure key:**
```bash
python3 -c "import secrets; print(secrets.token_urlsafe(64))"
```

**Security:**
- Access token: 1 hour (short-lived)
- Refresh token: 7 days (for renewal)
- Algorithm: HS256 (symmetric)

---

### 7. 📧 Email Service

```env
EMAIL_MODE=mock
SMTP_HOST=smtp.gmail.com
SMTP_USER=<your-email>
SMTP_PASS=<app-password>
```

**Modes:**
- `mock`: Logs to console (for testing)
- `smtp`: Sends real emails

**Gmail setup:**
1. Enable 2-Step Verification
2. Go to [App Passwords](https://myaccount.google.com/apppasswords)
3. Generate password for "Mail"
4. Remove spaces from password

**Alternative providers:**
- SendGrid
- Mailgun
- AWS SES

---

### 8. 📱 Phone Verification (Telnyx)

```env
TELNYX_API_KEY=<your-key>
TELNYX_PUBLIC_KEY=<your-public-key>
```

**Status:** To be implemented

**How to get:**
1. Sign up at [telnyx.com](https://telnyx.com)
2. Get API keys from Portal → Auth

---

### 9. 🔍 Sentry (Error Tracking)

```env
SENTRY_DSN=<your-dsn>
SENTRY_TRACES_SAMPLE=0.2
SENTRY_ENVIRONMENT=production
```

**How to get:**
1. Sign up at [sentry.io](https://sentry.io)
2. Create new project (Python/FastAPI)
3. Copy DSN from Settings → Client Keys

**Features:**
- Error tracking
- Performance monitoring
- Release tracking
- User feedback

---

### 10. 💳 Payment Processing

```env
STRIPE_SECRET_KEY=<your-key>
STRIPE_WEBHOOK_SECRET=<your-webhook>
```

**Status:** To be implemented

**How to get:**
1. Sign up at [stripe.com](https://stripe.com)
2. Get API keys from Developers → API keys
3. Set up webhooks for subscription events

---

### 11. ☁️ Hetzner Cloud

```env
HETZNER_API_TOKEN=<your-token>
HETZNER_SERVER_NAME=ubuntu-8gb-nbg1-3
```

**Purpose:** VPS hosting, self-hosted LiveKit

**How to get:**
1. Sign up at [hetzner.com](https://www.hetzner.com/cloud)
2. Go to Security → API tokens
3. Generate new token with Read & Write permissions

---

### 12. 🧩 Feature Flags

```env
ENABLE_EMAIL_VERIFICATION=true
ENABLE_VIDEO_CALLS=true
ENABLE_AI_MATCHING=true
```

**Purpose:** Enable/disable features without code changes

**Usage:**
```python
if os.getenv('ENABLE_VIDEO_CALLS') == 'true':
    # Enable video call features
```

---

## 🚀 Getting Started

### 1. Initial Setup

```bash
# Copy example file
cp .env.example .env

# Edit with your values
nano .env

# Never commit to Git
echo ".env" >> .gitignore
```

### 2. Fill Required Values

**Minimum required:**
- ✅ MONGO_URL
- ✅ SECRET_KEY
- ✅ LIVEKIT_* (for calls)
- ✅ CLOUDINARY_* (for images)
- ✅ SENTRY_DSN (recommended)

**Optional:**
- Email service (can use mock mode)
- Payment processing (for premium features)
- Analytics (for tracking)

### 3. Verify Configuration

```bash
# Test backend loading
cd /app/backend
python3 -c "from dotenv import load_dotenv; load_dotenv(); import os; print('✅' if os.getenv('SECRET_KEY') else '❌')"

# Restart services
sudo supervisorctl restart backend
```

---

## 🔄 Environment-Specific Configurations

### Development

```env
ENVIRONMENT=development
DEBUG=true
EMAIL_MODE=mock
STRIPE_MODE=test
```

### Staging

```env
ENVIRONMENT=staging
DEBUG=false
EMAIL_MODE=smtp
STRIPE_MODE=test
```

### Production

```env
ENVIRONMENT=production
DEBUG=false
EMAIL_MODE=smtp
STRIPE_MODE=live
ENABLE_AUTO_BACKUP=true
```

---

## 🐛 Troubleshooting

### Issue: "Could not load .env file"
**Solution:** Ensure file exists in `/app/backend/.env`

### Issue: "Invalid credentials"
**Solution:** Check for extra spaces, quotes, or newlines in values

### Issue: "Environment variable not found"
**Solution:** Restart backend after changing .env:
```bash
sudo supervisorctl restart backend
```

### Issue: "Gmail authentication failed"
**Solution:** 
- Use App Password, not regular password
- Remove spaces from password
- Enable 2-Step Verification

---

## 📊 Current Status

| Service | Status | Notes |
|---------|--------|-------|
| MongoDB | ✅ Active | localhost:27017 |
| LiveKit | ✅ Active | Cloud service |
| Cloudinary | ✅ Active | Image storage |
| Email (Mock) | ✅ Active | Logs to console |
| Sentry | ✅ Active | Error tracking |
| Stripe | ⏳ Pending | To be configured |
| Telnyx | ⏳ Pending | To be configured |

---

## 📖 Additional Resources

- **Backend API Docs:** `/app/AUTH_API_DOCUMENTATION.md`
- **LiveKit Guide:** `/app/LIVEKIT_IMPLEMENTATION_COMPLETE.md`
- **Email Setup:** `/app/EMAIL_SETUP_GUIDE.md`

---

## 🆘 Support

**Issues?** 
- Check logs: `tail -f /var/log/supervisor/backend.err.log`
- Sentry: [sentry.io](https://sentry.io) for error details
- GitHub: [pizoo-dating-app/issues](https://github.com/Shatha-db/pizoo-dating-app/issues)

---

**Last Updated:** January 2025  
**Version:** 1.0.0  
**Maintained by:** Pizoo Team
