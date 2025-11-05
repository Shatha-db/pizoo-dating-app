# Vercel Deployment Setup for Pizoo

## 🚀 Quick Setup Guide

### Step 1: Vercel Project Settings

Go to your Vercel project dashboard and configure:

#### Root Directory
- **Leave as:** `.` (root)
- Or set to: `frontend` if you want to deploy only frontend

#### Framework Preset
- Select: **Create React App**

#### Build & Development Settings

**Build Command:**
```bash
yarn build
```

**Output Directory:**
```bash
build
```

**Install Command:**
```bash
yarn install
```

**Development Command:**
```bash
yarn start
```

---

### Step 2: Environment Variables

Add these in Vercel Dashboard → Settings → Environment Variables:

```env
REACT_APP_BACKEND_URL=https://datemaps.emergent.host
REACT_APP_SENTRY_DSN=your_sentry_dsn
REACT_APP_SENTRY_TRACES_SAMPLE=0.2
REACT_APP_ENVIRONMENT=production
ENABLE_HEALTH_CHECK=false
```

---

### Step 3: Deploy

#### Option A: From Vercel Dashboard
1. Go to Deployments tab
2. Click "Deploy"
3. Wait for build to complete

#### Option B: From GitHub
1. Push changes to main branch
2. Vercel auto-deploys

#### Option C: From CLI
```bash
# Install Vercel CLI
npm i -g vercel

# Login
vercel login

# Deploy
vercel --prod
```

---

## 🔧 Troubleshooting

### Issue: 404 on Routes

**Solution:** Add `vercel.json` in `/frontend` directory:

```json
{
  "rewrites": [
    {
      "source": "/(.*)",
      "destination": "/index.html"
    }
  ]
}
```

### Issue: Build Fails

**Check:**
1. Node.js version (should be 18.x or 20.x)
2. Build command is correct
3. Output directory is `build`
4. All dependencies in `package.json`

### Issue: Environment Variables Not Loading

**Solution:**
1. Go to Vercel Dashboard → Settings → Environment Variables
2. Add all `REACT_APP_*` variables
3. Redeploy

---

## 📁 Project Structure for Vercel

```
/app/
├── frontend/              ← This is what Vercel builds
│   ├── public/
│   ├── src/
│   ├── package.json       ← Build configuration
│   └── vercel.json        ← Routing rules
├── backend/               ← Ignored by Vercel
├── vercel.json            ← Root config (optional)
└── package.json           ← Root package (optional)
```

---

## ✅ Verify Deployment

After deployment, test:

```bash
# Test homepage
curl -I https://pizoo.ch

# Test routing
curl -I https://pizoo.ch/login
curl -I https://pizoo.ch/register

# Test static assets
curl -I https://pizoo.ch/static/css/main.css
```

All should return `200 OK`.

---

## 🔗 Custom Domain (pizoo.ch)

### Add Domain in Vercel

1. Go to Settings → Domains
2. Add domain: `pizoo.ch`
3. Add domain: `www.pizoo.ch`

### Configure DNS

Add these records at your domain provider:

```
Type    Name    Value                    TTL
CNAME   @       cname.vercel-dns.com     3600
CNAME   www     cname.vercel-dns.com     3600
```

### Wait for SSL

- SSL certificate automatically provisioned
- Takes 5-60 minutes
- Status shows in Vercel dashboard

---

## 📊 Monitoring

### Vercel Analytics

Automatically enabled. View at:
- Dashboard → Analytics tab

### Logs

```bash
# Real-time logs
vercel logs --follow

# Specific deployment
vercel logs <deployment-url>
```

---

## 🔄 CI/CD

Automatic deployment on:
- ✅ Push to `main` branch
- ✅ Pull request (preview deployments)
- ✅ Tag creation

---

## 📞 Support

- **Vercel Docs:** https://vercel.com/docs
- **Support:** support@vercel.com
- **Pizoo:** support@pizoo.ch

---

**Last Updated:** November 2024  
**Version:** 2.0
