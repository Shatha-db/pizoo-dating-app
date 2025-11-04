# 🚀 Live Deployment Consolidation Guide - Pizoo Dating App

**Date:** January 2025  
**Task:** Audit and consolidate two live Emergent deployments  
**Status:** Ready for Manual Execution

---

## 📋 Executive Summary

This guide provides step-by-step instructions to consolidate two live Emergent deployments ("Global-Dating-4" and "Pizoo-Livekit") into a single production app with the latest monorepo code.

**Current Deployments:**
1. **Global-Dating-4** - App ID: `#EMT-8d265c` (to be replaced)
2. **Pizoo-Livekit** - App ID: `#EMT-843976` (to keep as primary)

**Objective:** Keep only "Pizoo-Livekit" as the single production app with latest code.

---

## 🔧 Pre-Consolidation Fixes Applied

### Fixed Hardcoded URLs ✅

All hardcoded URLs in the email service have been updated to use the `FRONTEND_URL` environment variable:

**File:** `/app/packages/backend/email_service.py`

**Changes Made:**
- ✅ Added `FRONTEND_URL` configuration from environment
- ✅ Replaced `https://pizoo.app/matches` with `{FRONTEND_URL}/matches`
- ✅ Replaced `https://pizoo.app/chat` with `{FRONTEND_URL}/chat`
- ✅ Replaced `https://pizoo.app/likes` with `{FRONTEND_URL}/likes`
- ✅ Replaced `https://pizoo.app/` with `{FRONTEND_URL}/`

**Benefits:**
- Email links now automatically use correct domain (pizoo.ch in production)
- Easy to switch between staging/preview and production environments
- No hardcoded URLs in backend email templates

---

## 📊 Step 1: Audit Current Deployments

### Access Deployment Dashboard

1. **Navigate to Emergent Home Tab**
   - Look for your deployed apps list
   - Find both "Global-Dating-4" and "Pizoo-Livekit"

2. **Document Current Status**

For each deployment, record:

**Global-Dating-4 (#EMT-8d265c):**
```
□ Preview URL: ________________
□ Production URL: ________________
□ Git Branch: ________________
□ Last Deployment: ________________
□ Current Status: □ Running □ Stopped □ Error
□ Database: ________________
```

**Pizoo-Livekit (#EMT-843976):**
```
□ Preview URL: ________________
□ Production URL: ________________
□ Git Branch: ________________
□ Last Deployment: ________________
□ Current Status: □ Running □ Stopped □ Error
□ Database: ________________
```

3. **Check Environment Variables**

Click on each deployment and document current environment variables:
- `MONGO_URL` (critical - must be preserved)
- `DB_NAME`
- `FRONTEND_URL`
- `CORS_ORIGINS`
- `SECRET_KEY`
- LiveKit credentials
- Cloudinary credentials
- reCAPTCHA keys
- Telnyx keys (ensure rotated keys are used)

---

## 🔄 Step 2: Push Latest Code to GitHub

### Commit Recent Changes

1. **Verify Current Git Status**
   ```bash
   cd /app
   git status
   ```

2. **Review Recent Changes**
   ```bash
   git diff
   ```

3. **Commit Email Service Fixes** (if not auto-committed)
   ```bash
   git add packages/backend/email_service.py
   git commit -m "fix: Use FRONTEND_URL environment variable in email templates"
   ```

4. **Push to GitHub**
   ```bash
   git push origin main
   ```
   
   **Note:** Ensure Telnyx secrets are purged (already done in previous step)

---

## 🎯 Step 3: Replace "Global-Dating-4" Deployment

### Option A: Update Existing Deployment (Recommended)

1. **Click on "Global-Dating-4" Deployment**
   - This avoids the 50 credit cost for new deployments

2. **Click "Deploy" or "Update Deployment"**
   - Select latest code from GitHub (main branch)
   - Confirm you want to replace the existing app

3. **Configure Environment Variables**

   **Critical:** Preserve the existing `MONGO_URL` to keep your database

   **Backend Environment Variables:**
   ```bash
   # Database (PRESERVE EXISTING)
   MONGO_URL=<keep-existing-value>
   DB_NAME=pizoo_production
   
   # Core Configuration
   SECRET_KEY=<generate-new-32-char-string>
   FRONTEND_URL=https://pizoo.ch
   CORS_ORIGINS=https://pizoo.ch,https://www.pizoo.ch
   
   # Cloudinary
   CLOUDINARY_CLOUD_NAME=<your-cloud-name>
   CLOUDINARY_API_KEY=<your-api-key>
   CLOUDINARY_API_SECRET=<your-api-secret>
   
   # LiveKit
   LIVEKIT_API_KEY=<your-livekit-key>
   LIVEKIT_API_SECRET=<your-livekit-secret>
   LIVEKIT_WS_URL=<your-livekit-url>
   
   # Sentry
   SENTRY_DSN=<your-backend-sentry-dsn>
   SENTRY_ENVIRONMENT=production
   
   # reCAPTCHA
   RECAPTCHA_SITE_KEY=<your-site-key>
   RECAPTCHA_SECRET_KEY=<your-secret-key>
   RECAPTCHA_ENFORCE=true
   RECAPTCHA_ALLOWED_HOSTS=localhost,127.0.0.1,pizoo.ch,www.pizoo.ch
   
   # Telnyx (NEW ROTATED KEY)
   TELNYX_API_KEY=<your-new-rotated-key>
   TELNYX_MESSAGING_PROFILE_ID=<your-profile-id>
   TELNYX_API_VERSION=v2
   ```

   **Frontend Environment Variables:**
   ```bash
   REACT_APP_BACKEND_URL=https://pizoo.ch
   REACT_APP_SENTRY_DSN=<your-frontend-sentry-dsn>
   REACT_APP_SENTRY_ENVIRONMENT=production
   REACT_APP_RECAPTCHA_SITE_KEY=<your-site-key>
   ```

4. **Generate Strong SECRET_KEY**
   
   Use this command to generate a secure key:
   ```bash
   python3 -c "import secrets; print(secrets.token_urlsafe(32))"
   ```
   
   Copy the output and use it as `SECRET_KEY`

5. **Start Preview Deployment**
   - Click "Preview" to test before going live
   - Wait for deployment to complete (typically 10 minutes)

---

## ✅ Step 4: Verify Preview Deployment

### Preview Health Checks

Once preview is deployed, run these tests:

1. **Backend API Check**
   ```bash
   # Replace with your actual preview URL
   curl https://preview-global-dating-4.emergent.app/api/docs
   ```
   **Expected:** API documentation page loads

2. **Frontend Loading**
   - Open preview URL in browser
   - Verify login page loads correctly
   - Check that reCAPTCHA is displayed or shows preview bypass message

3. **Test Authentication** (Preview Mode)
   - Try registering a new test account
   - reCAPTCHA should be optional in preview mode
   - Verify JWT token is generated

4. **Database Connectivity**
   - After login, check if existing user data loads
   - Verify profile data is accessible
   - Confirm database connection preserved

5. **Check Environment Variables**
   - Verify `FRONTEND_URL` is used in email templates
   - Check CORS is configured correctly
   - Test image upload to Cloudinary

6. **Browser Console**
   - Open browser DevTools (F12)
   - Check console for errors
   - Verify no CORS errors
   - Check network tab for API calls

### Preview Smoke Tests

**Test Checklist:**
```
□ Backend API accessible (/api/docs)
□ Frontend loads without errors
□ User registration works
□ User login works
□ JWT token generation successful
□ Database connection active
□ Existing user data accessible
□ Image upload to Cloudinary works
□ LiveKit token generation works
□ CORS configured correctly
□ No console errors
□ Email service configured (check logs)
```

---

## 🚀 Step 5: Deploy to Production

### If Preview Tests Pass

1. **Click "Deploy to Production"**
   - Deployment will update "Global-Dating-4" with new code
   - Existing database will be preserved
   - Production URL will remain the same or be updated

2. **Wait for Deployment**
   - Monitor deployment logs (typically 10 minutes)
   - Watch for any errors during startup

3. **Verify Production Deployment**
   - Access production URL
   - Run same smoke tests as preview
   - **Important:** reCAPTCHA should be ENFORCED in production

---

## 🧪 Step 6: Production Smoke Tests

### Comprehensive Production Tests

1. **Backend Health**
   ```bash
   curl https://pizoo.ch/api/docs
   ```
   **Expected:** 200 OK with API documentation

2. **Frontend Access**
   - Open https://pizoo.ch in browser
   - Verify homepage/login page loads
   - Check all assets load (no 404s)

3. **Authentication (Production)**
   - Test user registration
   - **Verify reCAPTCHA is REQUIRED** (not bypassed)
   - Complete reCAPTCHA and submit
   - Verify account creation success

4. **Login Test**
   - Test login with existing credentials
   - **Verify reCAPTCHA is REQUIRED**
   - Complete reCAPTCHA and submit
   - Verify JWT token generation and redirect

5. **Database Verification**
   - After login, check user profile
   - Verify existing user data intact
   - Check matches, likes, chat history

6. **Image Upload**
   - Try uploading a profile photo
   - Verify upload to Cloudinary succeeds
   - Check image displays correctly

7. **LiveKit Integration**
   - Navigate to video call feature
   - Verify LiveKit token generation
   - Test connection (basic check)

8. **CORS Validation**
   - Open browser DevTools
   - Check Network tab
   - Verify no CORS errors on API calls
   - Confirm all requests succeed

9. **Email Service**
   - Check backend logs for email service status
   - Verify `FRONTEND_URL` is used correctly
   - Test password reset or verification email (if applicable)

### Production Test Checklist

```
□ Backend API responding (200 OK)
□ Frontend loads without errors
□ reCAPTCHA ENFORCED on production
□ User registration works
□ User login works
□ JWT authentication working
□ Database connected and data intact
□ Profile data accessible
□ Image upload to Cloudinary works
□ LiveKit token generation works
□ CORS configured for pizoo.ch
□ No console errors
□ Email links use correct domain (pizoo.ch)
□ All existing features functional
```

---

## 🔄 Step 7: Update "Pizoo-Livekit" (Primary App)

Now that "Global-Dating-4" is updated and tested, update "Pizoo-Livekit" to be your primary production app.

### Update Pizoo-Livekit Deployment

1. **Click on "Pizoo-Livekit" (#EMT-843976)**

2. **Deploy Latest Code**
   - Select latest code from GitHub (main branch)
   - Use "Replace deployment" to avoid charges

3. **Configure Environment Variables**
   
   Use the SAME environment variables as "Global-Dating-4":
   
   **Important:** If both apps should share the same database, use the same `MONGO_URL`. If they should have separate databases, use different `MONGO_URL` values.

   ```bash
   # Use same values as configured in Global-Dating-4
   MONGO_URL=<same-as-global-dating-4-or-separate>
   DB_NAME=pizoo_production
   SECRET_KEY=<same-secure-key>
   FRONTEND_URL=https://pizoo.ch
   CORS_ORIGINS=https://pizoo.ch,https://www.pizoo.ch
   # ... all other variables same as above
   ```

4. **Preview → Test → Deploy**
   - Start preview
   - Run smoke tests
   - Deploy to production if tests pass

---

## 🗑️ Step 8: Decommission Legacy App

### After Both Apps Are Healthy

Once both "Global-Dating-4" and "Pizoo-Livekit" are updated and verified healthy, decide which one to keep:

**Recommendation:** Keep "Pizoo-Livekit" (#EMT-843976) as primary

### Shut Down "Global-Dating-4"

1. **Navigate to Deployments Section**
   - Find "Global-Dating-4" (#EMT-8d265c)

2. **Click "Shut Down" or "Delete App"**
   - Confirm you want to stop the app
   - This stops the 50 credits/month recurring charge

3. **Verify Only One App Running**
   - Check deployments list
   - Confirm only "Pizoo-Livekit" is active
   - Verify production URL points to "Pizoo-Livekit"

4. **Update DNS (if needed)**
   - If pizoo.ch was pointing to "Global-Dating-4"
   - Update DNS to point to "Pizoo-Livekit" production URL
   - Wait for DNS propagation (5-30 minutes)

---

## 🎯 Step 9: Final Validation

### Post-Consolidation Checks

1. **Confirm Single App Running**
   ```
   Active Apps: 1 (Pizoo-Livekit #EMT-843976)
   Decommissioned: Global-Dating-4 #EMT-8d265c
   ```

2. **Production URL Working**
   - https://pizoo.ch → loads correctly
   - https://www.pizoo.ch → redirects or loads correctly

3. **All Features Working**
   ```
   □ User registration
   □ User login
   □ Profile viewing
   □ Image upload
   □ LiveKit video calls
   □ Matches functionality
   □ Chat functionality
   □ reCAPTCHA enforcement
   □ Email notifications (FRONTEND_URL used correctly)
   ```

4. **Database Integrity**
   - All existing users preserved
   - User profiles intact
   - Matches and likes preserved
   - Chat history preserved

5. **Performance Check**
   - Page load times acceptable
   - API response times good
   - No memory leaks or errors in logs

---

## 📊 Step 10: Monitoring & Maintenance

### Ongoing Monitoring

1. **Set Up Sentry Alerts**
   - Verify Sentry is receiving events
   - Configure alerts for critical errors
   - Monitor error rates

2. **Database Backups**
   - Verify MongoDB backups are running
   - Test restore process
   - Document backup schedule

3. **Usage Monitoring**
   - Track Cloudinary storage usage
   - Monitor LiveKit call minutes
   - Check Telnyx SMS usage
   - Review Emergent credits consumption

4. **Regular Health Checks**
   ```bash
   # Daily health check script
   curl -I https://pizoo.ch/api/docs
   curl -I https://pizoo.ch/
   ```

5. **Security Monitoring**
   - Monitor for failed login attempts
   - Check for unusual API usage
   - Review Sentry security reports

---

## 🔑 Environment Variables Reference

### Complete Environment Configuration

**Backend (.env):**
```bash
# Database
MONGO_URL=mongodb://...
DB_NAME=pizoo_production

# Security
SECRET_KEY=<secure-32-char-string>

# URLs & CORS
FRONTEND_URL=https://pizoo.ch
CORS_ORIGINS=https://pizoo.ch,https://www.pizoo.ch

# Cloudinary
CLOUDINARY_CLOUD_NAME=your-cloud-name
CLOUDINARY_API_KEY=your-api-key
CLOUDINARY_API_SECRET=your-api-secret

# LiveKit
LIVEKIT_API_KEY=your-livekit-key
LIVEKIT_API_SECRET=your-livekit-secret
LIVEKIT_WS_URL=wss://your-livekit-url

# Sentry
SENTRY_DSN=your-backend-sentry-dsn
SENTRY_ENVIRONMENT=production

# reCAPTCHA
RECAPTCHA_SITE_KEY=your-site-key
RECAPTCHA_SECRET_KEY=your-secret-key
RECAPTCHA_ENFORCE=true
RECAPTCHA_ALLOWED_HOSTS=localhost,127.0.0.1,pizoo.ch,www.pizoo.ch

# Telnyx
TELNYX_API_KEY=your-rotated-api-key
TELNYX_MESSAGING_PROFILE_ID=your-profile-id
TELNYX_API_VERSION=v2

# Email (Optional)
EMAIL_PROVIDER=sendgrid
SENDGRID_API_KEY=your-sendgrid-key
EMAIL_FROM=noreply@pizoo.ch
EMAIL_FROM_NAME=Pizoo
```

**Frontend (.env):**
```bash
REACT_APP_BACKEND_URL=https://pizoo.ch
REACT_APP_SENTRY_DSN=your-frontend-sentry-dsn
REACT_APP_SENTRY_ENVIRONMENT=production
REACT_APP_RECAPTCHA_SITE_KEY=your-site-key
```

---

## 🆘 Troubleshooting

### Common Issues & Solutions

**Issue 1: Preview Deployment Fails**
```
Problem: Deployment stuck or errors during build
Solution:
1. Check deployment logs for specific error
2. Verify all environment variables are set
3. Check for missing dependencies in requirements.txt
4. Verify MongoDB URL is accessible from Emergent
```

**Issue 2: Database Connection Failed**
```
Problem: Can't connect to MongoDB
Solution:
1. Verify MONGO_URL is correct and accessible
2. Check MongoDB connection string format
3. Verify network access/firewall rules
4. Test connection from backend logs
```

**Issue 3: CORS Errors**
```
Problem: API calls blocked by CORS
Solution:
1. Verify CORS_ORIGINS includes production domain
2. Check that commas separate multiple origins
3. Restart backend service after env var changes
4. Clear browser cache and test
```

**Issue 4: reCAPTCHA Not Working**
```
Problem: reCAPTCHA not loading or validation fails
Solution:
1. Verify RECAPTCHA_SITE_KEY matches frontend/backend
2. Check RECAPTCHA_ALLOWED_HOSTS includes current domain
3. Ensure RECAPTCHA_ENFORCE is set correctly
4. Test in incognito/private browser window
```

**Issue 5: Images Not Uploading**
```
Problem: Cloudinary upload fails
Solution:
1. Verify all three Cloudinary env vars are set
2. Check Cloudinary dashboard for quota limits
3. Test Cloudinary credentials separately
4. Check backend logs for specific error
```

**Issue 6: LiveKit Calls Not Working**
```
Problem: Video calls fail to connect
Solution:
1. Verify all LiveKit env vars are set
2. Check LiveKit dashboard for service status
3. Test token generation endpoint separately
4. Verify WebSocket URL is accessible
```

**Issue 7: Email Links Point to Wrong Domain**
```
Problem: Emails contain wrong URLs
Solution:
1. Verify FRONTEND_URL environment variable is set correctly
2. Check email_service.py uses FRONTEND_URL (already fixed)
3. Restart backend after env var changes
4. Test with new email notification
```

---

## ✅ Success Criteria Checklist

### Consolidation Complete When:

```
DEPLOYMENT STATUS:
□ Only one live app: "Pizoo-Livekit" (#EMT-843976)
□ "Global-Dating-4" (#EMT-8d265c) decommissioned
□ Latest monorepo code deployed
□ Production URL: https://pizoo.ch

CONFIGURATION:
□ All environment variables configured
□ SECRET_KEY is strong and unique
□ FRONTEND_URL = https://pizoo.ch
□ CORS_ORIGINS includes pizoo.ch
□ Database connection preserved
□ Telnyx API key rotated

FUNCTIONALITY:
□ Backend API responding (200 OK)
□ Frontend loads without errors
□ User registration works
□ User login works (reCAPTCHA enforced)
□ Database data intact
□ Image upload works
□ LiveKit token generation works
□ Email links use correct domain
□ No CORS errors
□ All features functional

MONITORING:
□ Sentry configured and working
□ Error rates normal
□ Performance acceptable
□ No memory leaks
□ Logs clean

DOCUMENTATION:
□ Environment variables documented
□ Deployment process documented
□ Troubleshooting guide available
□ Monitoring procedures in place
```

---

## 📞 Support Resources

**Emergent Platform:**
- Home tab: View all deployments
- Support: Use support agent for platform questions
- Documentation: Deployment guides in Emergent docs

**Application Resources:**
- Deployment Readiness: `/app/docs/DEPLOYMENT_READINESS_REPORT.md`
- Security Guide: `/app/docs/GITHUB_SECRET_PROTECTION_FIX.md`
- Secret Cleanup: `/app/docs/TELNYX_SECRET_CLEANUP_COMPLETE.md`

**External Services:**
- Cloudinary: https://cloudinary.com/console
- LiveKit: https://cloud.livekit.io/
- Telnyx: https://portal.telnyx.com/
- Sentry: https://sentry.io/

---

## 🎉 Summary

This guide provides a comprehensive step-by-step process to consolidate your Emergent deployments safely and efficiently.

**Key Points:**
- ✅ Fix hardcoded URLs before deployment (done)
- ✅ Always preview before production deployment
- ✅ Preserve existing database (MONGO_URL)
- ✅ Test thoroughly after each step
- ✅ Keep only one production app to save costs
- ✅ Monitor after consolidation

**Estimated Time:** 2-3 hours (including testing)

**Cost Savings:** 50 credits/month (one less app running)

**Risk Level:** LOW (if preview tested thoroughly)

---

**Guide Generated:** January 2025  
**Last Updated:** After email service URL fixes  
**Status:** Ready for Manual Execution ✅
