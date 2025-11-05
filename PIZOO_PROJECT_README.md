# 🎯 Pizoo Dating App - Project Documentation

**Version:** 2.0  
**Last Updated:** November 2024  
**Status:** Production Ready ✅

---

## 📋 Table of Contents

1. [Project Overview](#project-overview)
2. [Tech Stack](#tech-stack)
3. [Project Structure](#project-structure)
4. [Features](#features)
5. [Setup Instructions](#setup-instructions)
6. [Environment Variables](#environment-variables)
7. [Deployment](#deployment)
8. [API Documentation](#api-documentation)
9. [Testing](#testing)
10. [Troubleshooting](#troubleshooting)

---

## 🎯 Project Overview

Pizoo is a modern dating application designed for the MENA region with support for 9 languages. The app features AI-powered matching, real-time video/voice calls, and a comprehensive user verification system.

**Key Features:**
- 🌍 Multi-language support (9 languages including Arabic)
- 📱 Progressive Web App (PWA)
- 🎥 Real-time video/voice calls (LiveKit)
- 🔒 Account verification (Google OAuth + Email Magic Link)
- 💬 Real-time chat
- 🖼️ Image upload with Cloudinary
- 🌐 RTL support for Arabic
- 📊 Analytics and monitoring

---

## 🛠️ Tech Stack

### Frontend
- **Framework:** React 18
- **Build Tool:** Create React App
- **UI Library:** Tailwind CSS + shadcn/ui
- **State Management:** React Context
- **Routing:** React Router v6
- **i18n:** react-i18next
- **Real-time:** LiveKit React Components

### Backend
- **Framework:** FastAPI (Python 3.11+)
- **Database:** MongoDB
- **Authentication:** JWT + OAuth2
- **Email:** SMTP (SendGrid/Mailjet)
- **Image Storage:** Cloudinary
- **Video/Voice:** LiveKit
- **Monitoring:** Sentry

### DevOps
- **Hosting:** Vercel (Frontend) + Emergent (Backend)
- **Process Manager:** Supervisor
- **Version Control:** Git + GitHub

---

## 📁 Project Structure

```
/app/
├── backend/                 # FastAPI Backend
│   ├── server.py           # Main FastAPI app
│   ├── auth_service.py     # Authentication logic
│   ├── livekit_service.py  # LiveKit integration
│   ├── email_service.py    # Email sending
│   ├── requirements.txt    # Python dependencies
│   └── .env               # Backend environment variables
│
├── frontend/               # React Frontend
│   ├── public/
│   │   ├── locales/       # Translation files (9 languages)
│   │   ├── icons/         # PWA icons
│   │   └── logo/          # Brand assets
│   ├── src/
│   │   ├── components/    # Reusable components
│   │   │   ├── ui/        # shadcn/ui components
│   │   │   └── branding/  # Logo components
│   │   ├── pages/         # Page components
│   │   ├── modules/       # Feature modules
│   │   ├── contexts/      # React contexts
│   │   ├── i18n.js       # i18n configuration
│   │   └── App.js        # Main app component
│   ├── package.json       # Node dependencies
│   └── .env              # Frontend environment variables
│
├── livekit-stack/         # LiveKit configuration
├── vercel.json           # Vercel deployment config
├── .vercelignore         # Vercel ignore rules
└── README.md             # This file

```

---

## ✨ Features

### 1. Authentication & Verification ✅
- **Email/Password** registration and login
- **Phone Number** login with country code selector (240+ countries)
- **Google OAuth** via Emergent integration
- **Email Magic Link** verification (15-min TTL)
- **One-time account verification** required for video calls
- **JWT tokens** with refresh capability

### 2. User Profile ✅
- Profile creation with photos (Cloudinary)
- Bio, interests, and preferences
- Location-based matching
- Profile editing and management

### 3. Matching System ✅
- AI-powered matching algorithm
- Swipe interface
- Match notifications
- Match history

### 4. Real-Time Chat ✅
- One-on-one messaging
- Message history
- Read receipts
- Typing indicators
- Image/video sharing

### 5. Video/Voice Calls ✅
- **LiveKit integration** for high-quality calls
- Video and audio calls
- Screen sharing capability
- Call history
- **Verification required** (30 calls/hour limit)

### 6. Subscription Plans ✅
- **Free Tier:** Basic features
- **Gold Tier:** Enhanced features
- **Platinum Tier:** Premium features
- Payment integration ready

### 7. Internationalization ✅
- **9 Languages:** English, Arabic, French, German, Spanish, Italian, Turkish, Portuguese, Hindi
- **RTL Support:** Full right-to-left layout for Arabic
- **Dynamic switching:** No page reload required

### 8. Legal & Compliance ✅
- Terms and Conditions
- Privacy Policy
- Cookie Policy
- Community Guidelines
- Safety Center
- GDPR-ready data handling

---

## 🚀 Setup Instructions

### Prerequisites
- Node.js 18+
- Python 3.11+
- MongoDB 5.0+
- Yarn package manager

### Backend Setup

```bash
cd /app/backend

# Install dependencies
pip install -r requirements.txt

# Configure environment variables
cp .env.example .env
# Edit .env with your credentials

# Start the backend
python server.py
```

### Frontend Setup

```bash
cd /app/frontend

# Install dependencies
yarn install

# Configure environment variables
cp .env.example .env
# Edit .env with your backend URL

# Start development server
yarn start

# Build for production
yarn build
```

### Full Stack Start

```bash
# Restart all services
sudo supervisorctl restart all

# Check status
sudo supervisorctl status

# View logs
tail -f /var/log/supervisor/backend.err.log
tail -f /var/log/supervisor/frontend.err.log
```

---

## 🔐 Environment Variables

### Backend (.env)

```env
# MongoDB
MONGO_URL=mongodb://localhost:27017/pizoo

# JWT Authentication
JWT_SECRET=your_secure_random_secret_key
JWT_ALGORITHM=HS256
JWT_EXPIRATION_MINUTES=30
REFRESH_TOKEN_EXPIRATION_DAYS=7

# Email Configuration (SendGrid/Mailjet)
EMAIL_SENDER_NAME=info Pizoo
EMAIL_SENDER=support@pizoo.ch
EMAIL_REPLY_TO=support@pizoo.ch
SMTP_HOST=smtp.mailjet.com
SMTP_PORT=587
SMTP_USERNAME=your_mailjet_api_key
SMTP_PASSWORD=your_mailjet_secret_key

# Cloudinary (Image Upload)
CLOUDINARY_URL=cloudinary://api_key:api_secret@cloud_name

# LiveKit (Video/Voice)
LIVEKIT_URL=wss://your-project.livekit.cloud
LIVEKIT_API_KEY=your_livekit_api_key
LIVEKIT_API_SECRET=your_livekit_api_secret

# Google OAuth (via Emergent)
EMERGENT_GOOGLE_OAUTH_CLIENT_ID=your_client_id
EMERGENT_GOOGLE_OAUTH_CLIENT_SECRET=your_client_secret

# CORS
CORS_ORIGINS=https://pizoo.ch,https://www.pizoo.ch,http://localhost:3000

# Sentry (Optional)
SENTRY_DSN=your_sentry_dsn
SENTRY_ENVIRONMENT=production
```

### Frontend (.env)

```env
# Backend API URL
REACT_APP_BACKEND_URL=https://your-backend-url.com

# Sentry (Optional)
REACT_APP_SENTRY_DSN=your_sentry_dsn
REACT_APP_SENTRY_TRACES_SAMPLE=0.2
REACT_APP_ENVIRONMENT=production
```

### Frontend (.env.production)

```env
# Production-specific variables
REACT_APP_BACKEND_URL=https://datemaps.emergent.host
REACT_APP_ENVIRONMENT=production
ENABLE_HEALTH_CHECK=false
```

---

## 🌐 Deployment

### Vercel (Frontend)

The frontend is configured for Vercel deployment:

```bash
# Deploy to Vercel
vercel deploy

# Deploy to production
vercel --prod
```

**Configuration:** See `vercel.json` for build and deployment settings.

### Backend Deployment

Backend is hosted on Emergent platform with supervisor:

```bash
# Restart backend
sudo supervisorctl restart backend

# View backend logs
tail -f /var/log/supervisor/backend.err.log
```

---

## 📚 API Documentation

### Base URL
```
Production: https://datemaps.emergent.host/api
Development: http://localhost:8001/api
```

### Authentication Endpoints

#### 1. Register
```http
POST /api/auth/register
Content-Type: application/json

{
  "name": "John Doe",
  "email": "john@example.com",
  "password": "secure_password",
  "phone": "+41791234567"
}
```

#### 2. Login
```http
POST /api/auth/login
Content-Type: application/json

{
  "email": "john@example.com",
  "password": "secure_password"
}
```

#### 3. Google OAuth
```http
POST /api/auth/oauth/google
Content-Type: application/json

{
  "session_id": "emergent_oauth_session_id"
}
```

#### 4. Email Magic Link
```http
# Send verification link
POST /api/auth/email/send-link
Content-Type: application/json

{
  "email": "john@example.com",
  "name": "John Doe"
}

# Verify token
POST /api/auth/email/verify
Content-Type: application/json

{
  "token": "verification_token"
}
```

### LiveKit Endpoints

#### Get Call Token
```http
POST /api/livekit/token
Authorization: Bearer <jwt_token>
Content-Type: application/json

{
  "match_id": "match_123",
  "call_type": "video"
}
```

**Response:**
```json
{
  "success": true,
  "token": "livekit_jwt_token",
  "url": "wss://your-project.livekit.cloud",
  "room_name": "match_123",
  "participant_identity": "user_123"
}
```

### User Endpoints

#### Get Current User
```http
GET /api/users/me
Authorization: Bearer <jwt_token>
```

#### Update Profile
```http
PUT /api/users/me
Authorization: Bearer <jwt_token>
Content-Type: application/json

{
  "bio": "Updated bio",
  "interests": ["travel", "music"]
}
```

### Image Upload

#### Upload Profile Image
```http
POST /api/media/upload
Authorization: Bearer <jwt_token>
Content-Type: multipart/form-data

file: <image_file>
```

---

## 🧪 Testing

### Backend Testing

```bash
# Run comprehensive backend tests
python /app/deep_testing_backend_v2.py

# Test specific endpoint
curl -X POST https://datemaps.emergent.host/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"test@pizoo.ch","password":"test123"}'
```

### Frontend Testing

```bash
# Run frontend tests
yarn test

# Run E2E tests
yarn test:e2e
```

### LiveKit Testing

```bash
# Test LiveKit token generation
python /app/livekit_verification_test.py
```

---

## 🔧 Troubleshooting

### Common Issues

#### 1. Backend Not Starting
```bash
# Check logs
tail -f /var/log/supervisor/backend.err.log

# Restart backend
sudo supervisorctl restart backend

# Check Python dependencies
pip install -r /app/backend/requirements.txt
```

#### 2. Frontend Build Errors
```bash
# Clear cache
rm -rf /app/frontend/node_modules
rm -rf /app/frontend/build
rm /app/frontend/yarn.lock

# Reinstall
cd /app/frontend
yarn install
yarn build
```

#### 3. MongoDB Connection Issues
```bash
# Check MongoDB status
sudo systemctl status mongodb

# Restart MongoDB
sudo systemctl restart mongodb

# Check connection string in .env
echo $MONGO_URL
```

#### 4. LiveKit Calls Not Working
- Verify LIVEKIT_URL, LIVEKIT_API_KEY, LIVEKIT_API_SECRET in backend/.env
- Ensure user account is verified (verified=true)
- Check rate limiting (30 calls/hour per user)
- Test token generation: `POST /api/livekit/token`

#### 5. Images Not Uploading
- Verify CLOUDINARY_URL in backend/.env
- Check file size (max 10MB)
- Supported formats: JPG, PNG, GIF, WebP
- Test: `curl -X POST -F "file=@test.jpg" -H "Authorization: Bearer <token>" <backend_url>/api/media/upload`

---

## 📊 Monitoring

### Sentry Integration

Both frontend and backend are configured with Sentry for error tracking:

- **Frontend:** Errors automatically reported to Sentry
- **Backend:** API errors and exceptions tracked
- **Dashboard:** https://sentry.io/organizations/your-org/

### Logs

```bash
# Backend logs
tail -f /var/log/supervisor/backend.err.log
tail -f /var/log/supervisor/backend.out.log

# Frontend logs
tail -f /var/log/supervisor/frontend.err.log
tail -f /var/log/supervisor/frontend.out.log

# All logs
sudo supervisorctl tail -f backend stderr
sudo supervisorctl tail -f frontend stderr
```

---

## 🔄 Updates & Maintenance

### Updating Dependencies

#### Backend
```bash
cd /app/backend
pip install --upgrade -r requirements.txt
pip freeze > requirements.txt
```

#### Frontend
```bash
cd /app/frontend
yarn upgrade
yarn upgrade-interactive
```

### Database Migrations

```bash
# Run migration scripts
python /app/backend/migrate_verification.py
```

---

## 📞 Support

For issues or questions:
- **Email:** support@pizoo.ch
- **Website:** https://pizoo.ch
- **Documentation:** This file

---

## 📝 License

Copyright © 2024 Pizoo. All rights reserved.

---

## 🎉 Credits

- **Development:** Emergent AI Platform
- **Design:** Pizoo Team
- **Infrastructure:** Emergent + Vercel
- **Real-time:** LiveKit
- **Image Storage:** Cloudinary
- **Monitoring:** Sentry

---

**Last Updated:** November 5, 2024  
**Version:** 2.0  
**Status:** ✅ Production Ready
