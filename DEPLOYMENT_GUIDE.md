# 🚀 Pizoo Dating App - Deployment Guide

## Overview

This guide covers deploying the Pizoo Dating App to Emergent's Kubernetes platform. The application consists of:
- **Backend**: FastAPI (Python) REST API
- **Frontend**: React SPA (JavaScript)
- **Database**: MongoDB Atlas (provided by Emergent)

---

## 📋 Pre-Deployment Checklist

### Required Environment Variables

#### Backend (Required)
```bash
# Database (Auto-provided by Emergent if MongoDB is enabled)
MONGODB_URI=mongodb+srv://username:password@cluster.mongodb.net/pizoo_database
DB_NAME=pizoo_database

# Authentication
SECRET_KEY=<generate-a-secure-32-char-random-string>
JWT_ACCESS_TOKEN_EXPIRE_MINUTES=60

# CORS & Frontend
FRONTEND_URL=https://<your-frontend-app>.emergent.host
CORS_ORIGINS=https://<your-frontend-app>.emergent.host,https://pizoo.ch

# Cloudinary (for image uploads)
CLOUDINARY_CLOUD_NAME=<your-cloudinary-cloud-name>
CLOUDINARY_API_KEY=<your-cloudinary-api-key>
CLOUDINARY_API_SECRET=<your-cloudinary-api-secret>

# reCAPTCHA (for bot protection)
RECAPTCHA_SITE_KEY=<your-recaptcha-site-key>
RECAPTCHA_SECRET_KEY=<your-recaptcha-secret-key>
```

#### Frontend (Required)
```bash
# Backend API URL
REACT_APP_BACKEND_URL=https://<your-backend-app>.emergent.host

# reCAPTCHA
REACT_APP_RECAPTCHA_SITE_KEY=<your-recaptcha-site-key>

# Environment
REACT_APP_ENVIRONMENT=production
```

#### Optional Services
```bash
# LiveKit (for video/voice calls)
LIVEKIT_API_KEY=<your-livekit-key>
LIVEKIT_API_SECRET=<your-livekit-secret>
LIVEKIT_URL=wss://your-livekit-server.livekit.cloud

# Sentry (error tracking)
SENTRY_DSN_BACKEND=<your-sentry-dsn>
REACT_APP_SENTRY_DSN=<your-sentry-dsn>

# Telnyx (SMS OTP)
TELNYX_API_KEY=<your-telnyx-key>
TELNYX_PUBLIC_KEY=<your-telnyx-public-key>
```

---

## 🗂️ Project Structure

The repository supports both old and new structures:

### Current Structure (Local Development)
```
/app/
├── packages/
│   └── backend/          # FastAPI backend
│       ├── server.py
│       ├── requirements.txt
│       └── .env.example
└── apps/
    └── web/              # React frontend
        ├── src/
        ├── package.json
        └── .env.example
```

### GitHub/Deployment Structure
```
/
├── backend/              # FastAPI backend
│   ├── server.py
│   ├── requirements.txt
│   └── .env.example
└── frontend/             # React frontend
    ├── src/
    ├── package.json
    └── .env.example
```

**Note**: The deployment system reads from the GitHub structure (`backend/` and `frontend/` directories).

---

## 🔧 Environment Variable Configuration

### Option 1: Using Emergent Platform UI

1. Navigate to your deployment settings
2. Click "Environment Variables"
3. Add each variable from the checklist above
4. Mark sensitive variables (like API keys) as "Secret"
5. Save and trigger a new deployment

### Option 2: Using .env Files (Local Development Only)

1. Copy `.env.example` to `.env` in both `backend/` and `frontend/`
2. Fill in your actual values
3. **NEVER commit `.env` files to version control**

---

## 🗄️ Database Configuration

### Emergent MongoDB Atlas Integration

If you enable MongoDB in your Emergent deployment:

1. **Auto-Configuration**: Emergent automatically provides:
   - `MONGODB_URI`: Connection string
   - `MONGODB_DB_NAME`: Database name

2. **Database Name**: The app uses `pizoo_database` by default

3. **Collections Created Automatically**:
   - `users`: User accounts and authentication
   - `profiles`: User profile information
   - `matches`: Match relationships
   - `conversations`: Chat conversations
   - `messages`: Chat messages
   - `user_locations`: User location data
   - `fcm_tokens`: Push notification tokens

### Database Seeding (Optional)

To seed the database with demo users for testing:

```bash
# From backend directory
python seed_demo_users.py --count 400 --female-ratio 0.875
```

---

## 🚀 Deployment Steps

### Step 1: Configure Environment Variables

In your Emergent deployment settings, add all required environment variables listed in the checklist above.

**Critical Variables:**
- `MONGODB_URI` (auto-provided if MongoDB enabled)
- `SECRET_KEY` (generate with: `python -c "import secrets; print(secrets.token_urlsafe(32))"`)
- `CLOUDINARY_*` (for image uploads)
- `REACT_APP_BACKEND_URL` (frontend env)
- `FRONTEND_URL` and `CORS_ORIGINS` (backend env)

### Step 2: Enable MongoDB Atlas

1. In Emergent deployment settings, enable "MongoDB Atlas"
2. Emergent will automatically:
   - Create a MongoDB Atlas cluster
   - Inject `MONGODB_URI` into your backend
   - Configure network access

### Step 3: Deploy Backend

1. The deployment system will:
   - Detect `backend/requirements.txt`
   - Install Python dependencies
   - Start FastAPI server on port 8001

2. Backend will be available at: `https://<your-backend-app>.emergent.host`

### Step 4: Deploy Frontend

1. The deployment system will:
   - Detect `frontend/package.json`
   - Run `npm install` or `yarn install`
   - Build production bundle with `npm run build`
   - Serve static files

2. Frontend will be available at: `https://<your-frontend-app>.emergent.host`

### Step 5: Verify Deployment

Check the following endpoints:

```bash
# Backend health check
curl https://<your-backend-app>.emergent.host/health

# Expected response:
{"db":"ok","otp":"ok","ai":"ok","status":"healthy"}

# Frontend
curl https://<your-frontend-app>.emergent.host/

# Expected: HTML page loads
```

---

## 🔍 Troubleshooting

### Issue: "MONGO_URL or MONGODB_URI environment variable is required"

**Solution**: Ensure MongoDB Atlas is enabled in Emergent deployment settings. The `MONGODB_URI` will be automatically injected.

### Issue: CORS errors in browser console

**Solution**: Update `CORS_ORIGINS` in backend environment variables to include your frontend URL:
```bash
CORS_ORIGINS=https://<your-frontend-app>.emergent.host,https://pizoo.ch
```

### Issue: reCAPTCHA showing "Invalid domain for site key"

**Solution**: 
1. Go to https://www.google.com/recaptcha/admin
2. Add your Emergent domain to the allowed domains list
3. Add: `<your-app-name>.emergent.host`

### Issue: Images not uploading

**Solution**: Verify Cloudinary credentials are correctly set:
```bash
CLOUDINARY_CLOUD_NAME=your-cloud-name
CLOUDINARY_API_KEY=your-api-key
CLOUDINARY_API_SECRET=your-api-secret
```

### Issue: Backend returns 500 errors

**Solution**: Check backend logs in Emergent dashboard. Common causes:
- Missing required environment variables
- MongoDB connection timeout
- Invalid API credentials

---

## 📊 Health Checks

The backend provides a health check endpoint:

**Endpoint**: `GET /health`

**Response**:
```json
{
  "db": "ok",           // MongoDB connection status
  "otp": "ok",          // SMS service status
  "ai": "ok",           // AI service status  
  "status": "healthy"
}
```

**Status Codes**:
- `200 OK`: All services healthy
- `503 Service Unavailable`: One or more services down

---

## 🔐 Security Considerations

1. **Environment Variables**:
   - Never commit `.env` files
   - Use "Secret" type for sensitive variables in Emergent
   - Rotate API keys regularly

2. **Database**:
   - MongoDB Atlas provides automatic encryption at rest
   - Use strong passwords
   - Enable IP whitelisting if needed

3. **CORS**:
   - Only allow trusted domains in `CORS_ORIGINS`
   - Don't use `*` in production

4. **reCAPTCHA**:
   - Register domain in Google reCAPTCHA admin
   - Keep secret key confidential
   - Backend always validates tokens

---

## 🔄 Updating the Application

### Code Changes

1. Push changes to your GitHub repository
2. Emergent will auto-detect changes
3. Trigger redeployment in Emergent dashboard

### Environment Variable Changes

1. Update variables in Emergent deployment settings
2. Restart the deployment for changes to take effect

### Database Migrations

For schema changes:
1. Create migration script in `backend/migrations/`
2. Run migration after deployment:
   ```bash
   python migrations/your_migration.py
   ```

---

## 📈 Monitoring

### Application Logs

View logs in Emergent dashboard:
- **Backend logs**: Server requests, errors, database queries
- **Frontend logs**: Build output, runtime errors

### Error Tracking

If Sentry is configured:
- View errors at: https://sentry.io
- Errors are automatically captured from both frontend and backend

### Performance Monitoring

Monitor:
- API response times
- Database query performance
- Frontend page load times
- User session duration

---

## 🆘 Support

### Emergent Platform Support
- Discord: https://discord.gg/VzKfwCXC4A
- Email: support@emergent.sh
- Documentation: https://docs.emergent.sh

### Application Issues
- Check backend logs in Emergent dashboard
- Review health check endpoint: `/health`
- Verify all environment variables are set correctly

---

## 📚 Additional Resources

- **FastAPI Documentation**: https://fastapi.tiangolo.com/
- **React Documentation**: https://react.dev/
- **MongoDB Atlas**: https://www.mongodb.com/docs/atlas/
- **Cloudinary**: https://cloudinary.com/documentation
- **LiveKit**: https://docs.livekit.io/
- **Google reCAPTCHA**: https://developers.google.com/recaptcha

---

**Last Updated**: January 2025  
**Version**: 1.0  
**Application**: Pizoo Dating App
