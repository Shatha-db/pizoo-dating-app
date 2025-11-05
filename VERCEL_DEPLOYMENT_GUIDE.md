# 🚀 Vercel Deployment Guide for PiZOO

**Domain**: pizoo.ch  
**Status**: Configuration Ready ✅  
**Date**: November 5, 2025

---

## 📋 Files Created

✅ `/app/vercel.json` - Vercel configuration  
✅ `/app/.vercelignore` - Ignore patterns  
✅ `/app/frontend/.env.production` - Production environment variables

---

## 🔧 Configuration Details

### vercel.json
```json
{
  "version": 2,
  "buildCommand": "cd frontend && yarn install && yarn build",
  "outputDirectory": "frontend/build",
  "installCommand": "cd frontend && yarn install",
  "framework": null,
  "rewrites": [...]
}
```

**Key Features:**
- ✅ Rewrites all routes to /index.html (for React Router)
- ✅ Security headers configured
- ✅ Cache optimization for static assets
- ✅ Redirects index.html to root

---

## 🚀 Deployment Steps

### Option 1: Deploy via Vercel Dashboard (Recommended)

1. **Push to GitHub**:
   ```bash
   # Use Emergent's "Save to GitHub" feature or:
   git add .
   git commit -m "feat: Add Vercel deployment configuration"
   git push origin main
   ```

2. **Connect to Vercel**:
   - Go to [vercel.com/dashboard](https://vercel.com/dashboard)
   - Click "Add New Project"
   - Import your GitHub repository: `Shatha-db/pizoo-dating-app`
   - Select "main" branch

3. **Configure Build Settings**:
   - **Framework Preset**: Other (or None)
   - **Root Directory**: Leave empty (project root)
   - **Build Command**: `cd frontend && yarn install && yarn build`
   - **Output Directory**: `frontend/build`
   - **Install Command**: `cd frontend && yarn install`

4. **Environment Variables** (Important!):
   Add these in Vercel dashboard under Settings → Environment Variables:
   ```
   REACT_APP_BACKEND_URL=https://datemaps.emergent.host
   REACT_APP_SENTRY_DSN=https://79c952777d037f686f42fc61e99b96a5@o4510285399195648.ingest.de.sentry.io/4510285752107088
   REACT_APP_ENVIRONMENT=production
   REACT_APP_ENABLE_VISUAL_EDITS=false
   ```

5. **Domain Configuration**:
   - Go to Settings → Domains
   - Add domain: `pizoo.ch`
   - Add domain: `www.pizoo.ch`
   - Configure DNS records as instructed by Vercel

6. **Deploy**:
   - Click "Deploy"
   - Wait for build to complete (~2-3 minutes)

### Option 2: Deploy via Vercel CLI

```bash
# Install Vercel CLI
npm i -g vercel

# Login to Vercel
vercel login

# Deploy to production
vercel --prod
```

---

## 🔍 Troubleshooting 404 Errors

### Common Issues & Solutions

#### 1. **404 on Routes (e.g., /login, /register)**
**Cause**: Missing rewrites configuration  
**Solution**: ✅ Already fixed in `vercel.json` with rewrites

#### 2. **404 on Initial Load**
**Cause**: Wrong output directory  
**Solution**: ✅ Configured to `frontend/build`

#### 3. **Build Fails**
**Possible Causes**:
- Missing dependencies
- Build errors in code
- Wrong Node.js version

**Check**:
```bash
# Test build locally
cd /app/frontend
yarn install
yarn build

# Check for errors
ls -la build/
```

#### 4. **Blank Page / White Screen**
**Causes**:
- Wrong REACT_APP_BACKEND_URL
- Missing environment variables
- Build artifacts not generated

**Solution**: 
- Check browser console for errors
- Verify environment variables in Vercel
- Check build logs

---

## ✅ Verification Checklist

After deployment, verify:

- [ ] https://pizoo.ch loads successfully
- [ ] https://www.pizoo.ch loads successfully
- [ ] Login page accessible: https://pizoo.ch/login
- [ ] Register page accessible: https://pizoo.ch/register
- [ ] Static assets load (logo, images)
- [ ] No console errors in browser
- [ ] API calls work (check Network tab)

---

## 🧪 Test Build Locally

Before deploying, test the production build:

```bash
# Navigate to frontend
cd /app/frontend

# Install dependencies
yarn install

# Create production build
yarn build

# Check build output
ls -la build/
du -sh build/

# Serve locally (optional)
npx serve -s build -p 3000
```

**Expected Output**:
```
build/
├── index.html
├── static/
│   ├── css/
│   ├── js/
│   └── media/
├── favicon.ico
├── site.webmanifest
└── ...
```

**Build Size**: Should be ~2-5 MB

---

## 📊 Deployment Status Indicators

### ✅ Successful Deployment
- Status: "Ready"
- Build time: 1-3 minutes
- Deployment URL accessible
- Custom domain working

### ❌ Failed Deployment
Common errors:
- `Command failed: yarn build`
- `Error: ENOENT: no such file or directory`
- `Module not found`

**Check**:
1. Build logs in Vercel dashboard
2. Environment variables
3. vercel.json configuration

---

## 🔄 Continuous Deployment

Vercel automatically deploys when you push to GitHub:

- **Production**: `main` branch → pizoo.ch
- **Preview**: Other branches → unique URL

To trigger redeployment:
```bash
# Make a change and push
git commit --allow-empty -m "trigger deployment"
git push origin main
```

Or use Vercel dashboard:
- Go to Deployments
- Click "..." on latest deployment
- Select "Redeploy"

---

## 🌐 DNS Configuration

### For pizoo.ch (Root Domain)

**Type**: A Record  
**Name**: `@`  
**Value**: Vercel's IP (provided in dashboard)

**Or CNAME (if registrar supports)**:  
**Type**: ALIAS/ANAME  
**Name**: `@`  
**Value**: `cname.vercel-dns.com`

### For www.pizoo.ch (Subdomain)

**Type**: CNAME  
**Name**: `www`  
**Value**: `cname.vercel-dns.com`

**DNS Propagation**: 10 minutes to 48 hours

---

## ⚠️ Important Notes

### Backend Deployment
**Note**: Vercel configuration only deploys the **frontend** (React app).

The **backend** (FastAPI) is currently hosted on:
- Production: `https://datemaps.emergent.host`

If you want to deploy the backend to Vercel:
1. Vercel supports serverless functions
2. FastAPI full app needs adaptation
3. **Better alternatives**: Railway, Render, Fly.io, Heroku

Or use **Emergent Native Deployment** for full-stack:
- Handles both frontend + backend
- Custom domain support (50 credits/month)
- No separate configurations needed

### CORS Configuration
Make sure backend allows pizoo.ch:
```python
# In backend/server.py
CORS_ORIGINS = [
    "https://pizoo.ch",
    "https://www.pizoo.ch",
    "https://datemaps.emergent.host"
]
```

---

## 📞 Support

If deployment fails after following this guide:

1. **Check Vercel Build Logs**:
   - Dashboard → Deployments → Click on failed deployment
   - View "Build Logs"

2. **Common Build Errors**:
   ```
   Error: Command "yarn build" exited with 1
   → Check for TypeScript errors
   → Check for missing dependencies
   ```

3. **404 Still Appearing**:
   - Verify vercel.json is in project root
   - Check "Output Directory" in Vercel settings
   - Ensure rewrites are configured

4. **Contact**:
   - Vercel Support: [vercel.com/support](https://vercel.com/support)
   - PiZOO Support: support@pizoo.ch

---

## 🎯 Quick Commands Reference

```bash
# Test build locally
cd /app/frontend && yarn build

# Check build size
du -sh /app/frontend/build

# Serve production build
npx serve -s /app/frontend/build

# Deploy via CLI
vercel --prod

# Check Vercel project
vercel ls

# View deployment logs
vercel logs [deployment-url]

# Remove deployment
vercel rm [deployment-name]
```

---

## 📈 Performance Optimization

After deployment, consider:

1. **Enable Vercel Analytics**:
   - Dashboard → Analytics → Enable

2. **Configure Edge Caching**:
   - Already configured in vercel.json headers

3. **Optimize Images**:
   - Use Vercel Image Optimization
   - Add `<Image>` component from `next/image` (if migrating to Next.js)

4. **Monitor Performance**:
   - Use Vercel Speed Insights
   - Check Lighthouse scores

---

**Last Updated**: November 5, 2025  
**Version**: 1.0  
**Status**: Ready for Deployment ✅

---

_For questions or issues, contact: support@pizoo.ch_
