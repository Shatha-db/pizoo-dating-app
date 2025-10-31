# Cloudinary Configuration Guide for Pizoo Dating App

## 📝 Overview
Pizoo uses Cloudinary for image storage and optimization. All photo uploads are handled through the backend for security and proper organization.

## 🔐 Required Environment Variable

Add the following to `/app/backend/.env`:

```bash
CLOUDINARY_URL="cloudinary://API_KEY:API_SECRET@CLOUD_NAME"
```

### How to Get Your CLOUDINARY_URL:

1. **Sign up for Cloudinary** (if you haven't already):
   - Go to https://cloudinary.com/users/register/free
   - Sign up for a free account

2. **Get your credentials**:
   - Log in to your Cloudinary dashboard
   - Go to "Dashboard" → "Account Details"
   - Look for "API Environment variable"
   - Copy the full `CLOUDINARY_URL` string

3. **Add to .env file**:
   ```bash
   # Example format:
   CLOUDINARY_URL="cloudinary://API_KEY:API_SECRET@CLOUD_NAME-cloud-name"
   ```

4. **Restart the backend**:
   ```bash
   sudo supervisorctl restart backend
   ```

## 📁 Folder Organization

Images are automatically organized in Cloudinary:

```
pizoo/
├── users/
│   ├── avatars/{user_id}/     # Primary profile photos
│   └── profiles/{user_id}/    # Additional profile photos
├── stories/{user_id}/          # Story photos/videos
└── verification/{user_id}/     # Verification photos
```

## ✨ Features

- **Automatic Compression**: Images are compressed client-side before upload
- **Quality Optimization**: Backend further optimizes for best quality/size ratio
- **Progress Tracking**: Real-time upload progress with percentage
- **Retry Logic**: Automatic retry (up to 3 attempts) on failure
- **File Validation**: 
  - Max size: 10MB
  - Supported formats: JPEG, PNG, WebP, HEIC
- **Primary Photo**: First uploaded photo is automatically set as primary

## 🔧 Testing

To test the image upload system:

1. Ensure CLOUDINARY_URL is set in `/app/backend/.env`
2. Restart backend: `sudo supervisorctl restart backend`
3. Register a new user or login
4. Go to Profile Setup (Step 4) or Edit Profile
5. Upload a photo
6. Verify:
   - Progress bar shows upload progress
   - Photo appears immediately after upload
   - Photo is stored in Cloudinary (check your dashboard)
   - Photo URL is saved in user profile

## 🚨 Troubleshooting

### Error: "Cloudinary not configured"
- Check if CLOUDINARY_URL is set in .env
- Verify the URL format is correct
- Restart backend after adding CLOUDINARY_URL

### Upload fails with timeout
- Check internet connection
- Verify Cloudinary account is active
- Check file size (must be < 10MB)

### Photos not appearing
- Check browser console for errors
- Verify backend logs: `tail -f /var/log/supervisor/backend.err.log`
- Ensure CORS is properly configured

## 📊 Free Tier Limits

Cloudinary free tier includes:
- 25 GB storage
- 25 GB bandwidth/month
- 25,000 transformations/month

This is sufficient for development and small-scale production.

## 🔒 Security Notes

- CLOUDINARY_URL contains sensitive credentials - never commit to git
- Always use environment variables, not hardcoded values
- All uploads go through backend authentication
- Client never has direct access to Cloudinary credentials

---

**Need help?** Check Cloudinary documentation: https://cloudinary.com/documentation
