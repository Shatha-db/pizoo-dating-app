# ⚡ Pizoo - Quick Deployment Guide for Emergent

## 🚀 Deploy in 3 Steps

### Step 1: Enable MongoDB Atlas
In Emergent deployment settings, enable **MongoDB Atlas**.  
This auto-provides: `MONGODB_URI` and `MONGODB_DB_NAME`

### Step 2: Add Environment Variables

**Backend Environment Variables:**
```bash
SECRET_KEY=<generate-with: python -c "import secrets; print(secrets.token_urlsafe(32))">
FRONTEND_URL=https://<your-frontend-app>.emergent.host
CORS_ORIGINS=https://<your-frontend-app>.emergent.host,https://pizoo.ch
CLOUDINARY_CLOUD_NAME=<your-cloudinary-cloud>
CLOUDINARY_API_KEY=<your-cloudinary-key>
CLOUDINARY_API_SECRET=<your-cloudinary-secret>
RECAPTCHA_SITE_KEY=6LfYOgIsAAAAAOyBbzOngPQyj0S9etDZ-fHuD8Mk
RECAPTCHA_SECRET_KEY=6LfYOgIsAAAAANyy5WwSJnEBTe6QsLcapTx6xL7V
```

**Frontend Environment Variables:**
```bash
REACT_APP_BACKEND_URL=https://<your-backend-app>.emergent.host
REACT_APP_RECAPTCHA_SITE_KEY=6LfYOgIsAAAAAOyBbzOngPQyj0S9etDZ-fHuD8Mk
REACT_APP_ENVIRONMENT=production
```

### Step 3: Deploy
Click **Deploy** in Emergent dashboard and wait for build to complete.

---

## ✅ Verify Deployment

**Backend health check:**
```bash
curl https://<your-backend-app>.emergent.host/health
```
Expected: `{"db":"ok","otp":"ok","ai":"ok","status":"healthy"}`

**Frontend:**
```bash
curl https://<your-frontend-app>.emergent.host/
```
Expected: HTML page loads

---

## 🔧 Optional Services

Add these if needed:

**LiveKit (Video Calls):**
```bash
LIVEKIT_API_KEY=<key>
LIVEKIT_API_SECRET=<secret>
LIVEKIT_URL=wss://your-server.livekit.cloud
```

**Sentry (Error Tracking):**
```bash
SENTRY_DSN_BACKEND=<backend-dsn>
REACT_APP_SENTRY_DSN=<frontend-dsn>
```

**Telnyx (SMS OTP):**
```bash
TELNYX_API_KEY=<key>
TELNYX_PUBLIC_KEY=<public-key>
```

---

## 📝 Important Notes

1. **No .env files needed** - All config through Emergent UI
2. **MongoDB auto-configured** - Just enable Atlas integration
3. **CORS must include** your frontend URL
4. **reCAPTCHA domain** - Add emergent.host domain to Google reCAPTCHA admin

---

## 🆘 Troubleshooting

**CORS errors?**  
→ Add frontend URL to `CORS_ORIGINS`

**Database connection failed?**  
→ Ensure MongoDB Atlas is enabled

**reCAPTCHA "Invalid domain"?**  
→ Add domain to https://www.google.com/recaptcha/admin

**Images not uploading?**  
→ Check Cloudinary credentials

---

**Full Documentation:** See `/app/docs/EMERGENT_DEPLOYMENT_FIX_REPORT.md`
