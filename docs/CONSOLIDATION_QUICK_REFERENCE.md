# 🚀 Quick Reference: Deployment Consolidation

**Task:** Consolidate two live apps into one production deployment

---

## 📱 Your Live Apps

1. **Global-Dating-4** - `#EMT-8d265c` → Replace with latest code
2. **Pizoo-Livekit** - `#EMT-843976` → Keep as primary

---

## ✅ Pre-Work Completed

- [x] Fixed hardcoded URLs in email_service.py
- [x] All email links now use `FRONTEND_URL` environment variable
- [x] Deployment readiness check passed (95/100)
- [x] Telnyx secrets purged from Git history
- [x] Latest code committed to Git

---

## 🎯 Quick Steps

### 1. Push to GitHub
```bash
cd /app
git push origin main
```

### 2. Update Global-Dating-4
1. Open "Global-Dating-4" in Emergent dashboard
2. Click "Deploy" → Select latest code from GitHub
3. **Keep existing MONGO_URL** (preserve database)
4. Set all environment variables (see full guide)
5. Preview → Test → Deploy

### 3. Verify Production
- Test: `curl https://pizoo.ch/api/docs`
- Check: Registration/login works
- Verify: reCAPTCHA enforced
- Confirm: Database data intact

### 4. Update Pizoo-Livekit (Optional)
- Deploy same code and env vars
- Test thoroughly

### 5. Decommission Legacy App
- Once one app is confirmed healthy
- Shut down the other app
- Saves 50 credits/month

---

## 🔑 Critical Environment Variables

```bash
# Must Set
MONGO_URL=<preserve-existing>
SECRET_KEY=<generate-32-chars>
FRONTEND_URL=https://pizoo.ch
CORS_ORIGINS=https://pizoo.ch,https://www.pizoo.ch

# Your Services
CLOUDINARY_*=<your-keys>
LIVEKIT_*=<your-keys>
RECAPTCHA_*=<your-keys>
TELNYX_API_KEY=<rotated-key>
```

**Generate SECRET_KEY:**
```bash
python3 -c "import secrets; print(secrets.token_urlsafe(32))"
```

---

## ✅ Smoke Test Checklist

After deployment:
```
□ Backend API responds: /api/docs
□ Frontend loads correctly
□ Registration works (reCAPTCHA required)
□ Login works
□ Database connected (existing data loads)
□ Image upload to Cloudinary works
□ LiveKit tokens generate
□ No CORS errors
□ Email links use pizoo.ch (not pizoo.app)
```

---

## 🆘 Quick Troubleshooting

**Can't connect to database?**
→ Verify MONGO_URL is correct and preserved from old deployment

**CORS errors?**
→ Check CORS_ORIGINS includes pizoo.ch and restart backend

**reCAPTCHA not working?**
→ Verify RECAPTCHA_SITE_KEY and RECAPTCHA_ALLOWED_HOSTS

**Images not uploading?**
→ Check all three Cloudinary env vars are set

---

## 📚 Full Documentation

**Detailed Guide:** `/app/docs/DEPLOYMENT_CONSOLIDATION_GUIDE.md`

**Other Resources:**
- Deployment Readiness: `DEPLOYMENT_READINESS_REPORT.md`
- Secret Cleanup: `TELNYX_SECRET_CLEANUP_COMPLETE.md`
- Security Fix: `GITHUB_SECRET_PROTECTION_FIX.md`

---

## 🎯 Goal

**Start:** 2 apps running (100 credits/month)  
**End:** 1 app running (50 credits/month) with latest code ✅

---

**Time Required:** 2-3 hours  
**Risk Level:** LOW (with proper testing)  
**Cost Savings:** 50 credits/month
