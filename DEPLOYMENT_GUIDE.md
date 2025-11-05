# 🚀 Pizoo Deployment Guide

Complete guide for deploying Pizoo Dating App to production.

---

## 📋 Pre-Deployment Checklist

### ✅ Backend Requirements
- [ ] MongoDB connection string
- [ ] JWT secret key
- [ ] Email SMTP credentials (SendGrid/Mailjet)
- [ ] Cloudinary account and API keys
- [ ] LiveKit project and credentials
- [ ] Google OAuth credentials (optional)
- [ ] Sentry DSN (optional)

### ✅ Frontend Requirements
- [ ] Backend URL (production)
- [ ] Vercel account
- [ ] Domain configuration (pizoo.ch)
- [ ] SSL certificate (automatic with Vercel)

### ✅ Domain & DNS
- [ ] Domain purchased (pizoo.ch)
- [ ] DNS configured
- [ ] SSL/TLS certificate

---

## 🌐 Vercel Deployment (Frontend)

### Step 1: Prepare Frontend

```bash
cd /app/frontend

# Install dependencies
yarn install

# Create production build
yarn build

# Test build locally
serve -s build -p 3000
```

### Step 2: Configure Environment Variables

Create `.env.production`:

```env
REACT_APP_BACKEND_URL=https://datemaps.emergent.host
REACT_APP_SENTRY_DSN=your_sentry_dsn
REACT_APP_SENTRY_TRACES_SAMPLE=0.2
REACT_APP_ENVIRONMENT=production
ENABLE_HEALTH_CHECK=false
```

### Step 3: Vercel Configuration

Ensure `vercel.json` is configured:

```json
{
  "version": 2,
  "buildCommand": "cd frontend && yarn install && yarn build",
  "outputDirectory": "frontend/build",
  "installCommand": "cd frontend && yarn install",
  "framework": null,
  "rewrites": [
    {
      "source": "/(.*)",
      "destination": "/index.html"
    }
  ]
}
```

### Step 4: Deploy to Vercel

#### Option A: Vercel CLI

```bash
# Install Vercel CLI
npm install -g vercel

# Login to Vercel
vercel login

# Deploy
cd /app
vercel deploy

# Deploy to production
vercel --prod
```

#### Option B: GitHub Integration

1. Push code to GitHub
2. Connect repository to Vercel
3. Configure build settings:
   - **Framework Preset:** Create React App
   - **Build Command:** `cd frontend && yarn install && yarn build`
   - **Output Directory:** `frontend/build`
   - **Install Command:** `cd frontend && yarn install`
4. Add environment variables in Vercel dashboard
5. Deploy

### Step 5: Configure Custom Domain

1. Go to Vercel Dashboard → Your Project → Settings → Domains
2. Add domain: `pizoo.ch` and `www.pizoo.ch`
3. Configure DNS records:

```
Type    Name    Value                   TTL
CNAME   @       cname.vercel-dns.com    300
CNAME   www     cname.vercel-dns.com    300
```

4. Wait for DNS propagation (5-60 minutes)
5. SSL certificate automatically provisioned

---

## 🖥️ Backend Deployment (Emergent Platform)

### Step 1: Environment Configuration

Update `/app/backend/.env`:

```env
# Production MongoDB
MONGO_URL=mongodb+srv://username:password@cluster.mongodb.net/pizoo_prod

# JWT Configuration
JWT_SECRET=your_super_secure_random_secret_minimum_32_characters
JWT_ALGORITHM=HS256
JWT_EXPIRATION_MINUTES=30
REFRESH_TOKEN_EXPIRATION_DAYS=7

# Email Configuration (Production)
EMAIL_SENDER_NAME=info Pizoo
EMAIL_SENDER=support@pizoo.ch
EMAIL_REPLY_TO=support@pizoo.ch
SMTP_HOST=in-v3.mailjet.com
SMTP_PORT=587
SMTP_USERNAME=your_mailjet_api_key
SMTP_PASSWORD=your_mailjet_secret_key

# Cloudinary
CLOUDINARY_URL=cloudinary://api_key:api_secret@cloud_name

# LiveKit
LIVEKIT_URL=wss://pizoo-app-2jxoavwx.livekit.cloud
LIVEKIT_API_KEY=your_production_api_key
LIVEKIT_API_SECRET=your_production_api_secret

# CORS (Add production domains)
CORS_ORIGINS=https://pizoo.ch,https://www.pizoo.ch,https://datemaps.emergent.host

# Sentry
SENTRY_DSN=your_production_sentry_dsn
SENTRY_ENVIRONMENT=production
SENTRY_TRACES_SAMPLE=0.1
```

### Step 2: Install Dependencies

```bash
cd /app/backend
pip install -r requirements.txt
```

### Step 3: Test Backend

```bash
# Test backend locally
python server.py

# Test endpoints
curl http://localhost:8001/api/health
curl http://localhost:8001/api/auth/test
```

### Step 4: Deploy with Supervisor

```bash
# Restart backend
sudo supervisorctl restart backend

# Check status
sudo supervisorctl status backend

# View logs
tail -f /var/log/supervisor/backend.err.log
```

### Step 5: Verify Deployment

```bash
# Test production backend
curl https://datemaps.emergent.host/api/health

# Test CORS
curl -H "Origin: https://pizoo.ch" \
     -H "Access-Control-Request-Method: POST" \
     -H "Access-Control-Request-Headers: Content-Type" \
     -X OPTIONS \
     https://datemaps.emergent.host/api/auth/login
```

---

## 🗄️ MongoDB Setup

### Option A: MongoDB Atlas (Recommended)

1. **Create Cluster:**
   - Go to https://cloud.mongodb.com
   - Create new cluster (M10+ for production)
   - Region: Choose closest to your users (EU for MENA)

2. **Database User:**
   - Database Access → Add New User
   - Username: `pizoo_app`
   - Password: Generate strong password
   - Role: `readWrite` on `pizoo_prod` database

3. **Network Access:**
   - Network Access → Add IP Address
   - Allow access from anywhere: `0.0.0.0/0` (or restrict to Emergent IPs)

4. **Connection String:**
   ```
   mongodb+srv://pizoo_app:password@cluster.mongodb.net/pizoo_prod?retryWrites=true&w=majority
   ```

5. **Update Backend .env:**
   ```env
   MONGO_URL=mongodb+srv://pizoo_app:password@cluster.mongodb.net/pizoo_prod
   ```

### Option B: Self-Hosted MongoDB

```bash
# Install MongoDB
sudo apt-get install mongodb-org

# Start MongoDB
sudo systemctl start mongod
sudo systemctl enable mongod

# Create database and user
mongo
> use pizoo_prod
> db.createUser({
    user: "pizoo_app",
    pwd: "secure_password",
    roles: [{role: "readWrite", db: "pizoo_prod"}]
  })
```

---

## ☁️ Cloudinary Setup

1. **Create Account:**
   - Go to https://cloudinary.com
   - Sign up for free account

2. **Get Credentials:**
   - Dashboard → Settings → Account
   - Copy: Cloud Name, API Key, API Secret

3. **Configure Backend:**
   ```env
   CLOUDINARY_URL=cloudinary://123456789012345:abcdefghijklmnopqrstuvwxyz@your_cloud_name
   ```

4. **Create Upload Presets:**
   - Settings → Upload → Upload presets
   - Create preset: `pizoo_profiles`
   - Mode: Unsigned
   - Folder: `users/profiles`

---

## 🎥 LiveKit Setup

1. **Create Project:**
   - Go to https://cloud.livekit.io
   - Create new project: "Pizoo Production"

2. **Get Credentials:**
   - Settings → Keys
   - Copy: URL, API Key, API Secret

3. **Configure Backend:**
   ```env
   LIVEKIT_URL=wss://your-project.livekit.cloud
   LIVEKIT_API_KEY=APIxxxxxxxxxxxxxxx
   LIVEKIT_API_SECRET=xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
   ```

4. **Test Integration:**
   ```bash
   # Generate test token
   curl -X POST https://datemaps.emergent.host/api/livekit/token \
     -H "Authorization: Bearer <jwt_token>" \
     -H "Content-Type: application/json" \
     -d '{"match_id":"test_123","call_type":"video"}'
   ```

---

## 📧 Email Setup (Mailjet)

1. **Create Account:**
   - Go to https://www.mailjet.com
   - Sign up (Free: 6,000 emails/month)

2. **Verify Domain:**
   - Account Settings → Domains
   - Add domain: `pizoo.ch`
   - Add DNS records (SPF, DKIM)

3. **Get SMTP Credentials:**
   - Account Settings → SMTP Settings
   - API Key (SMTP Username)
   - Secret Key (SMTP Password)

4. **Configure Backend:**
   ```env
   SMTP_HOST=in-v3.mailjet.com
   SMTP_PORT=587
   SMTP_USERNAME=your_mailjet_api_key
   SMTP_PASSWORD=your_mailjet_secret_key
   EMAIL_SENDER=support@pizoo.ch
   ```

5. **Test Email:**
   ```bash
   # Send test verification email
   curl -X POST https://datemaps.emergent.host/api/auth/email/send-link \
     -H "Content-Type: application/json" \
     -d '{"email":"test@example.com","name":"Test User"}'
   ```

---

## 🔐 SSL/TLS Configuration

### Vercel (Automatic)
- SSL automatically provisioned
- Auto-renewal handled by Vercel
- No configuration needed

### Backend (Emergent)
- SSL handled by platform
- HTTPS enforced
- Certificate auto-renewal

---

## 🧪 Post-Deployment Testing

### 1. Frontend Tests

```bash
# Test frontend URL
curl -I https://pizoo.ch

# Test static assets
curl -I https://pizoo.ch/static/css/main.css

# Test routing
curl -I https://pizoo.ch/login
curl -I https://pizoo.ch/register
```

### 2. Backend Tests

```bash
# Health check
curl https://datemaps.emergent.host/api/health

# Authentication
curl -X POST https://datemaps.emergent.host/api/auth/register \
  -H "Content-Type: application/json" \
  -d '{"name":"Test","email":"test@pizoo.ch","password":"test123"}'

# LiveKit
curl -X POST https://datemaps.emergent.host/api/livekit/token \
  -H "Authorization: Bearer <token>" \
  -d '{"match_id":"test","call_type":"video"}'
```

### 3. Integration Tests

```bash
# End-to-end registration
1. Visit https://pizoo.ch/register
2. Fill form and submit
3. Check email for verification
4. Click verification link
5. Login to app

# Video call test
1. Create two accounts
2. Match users
3. Initiate video call
4. Verify connection
```

---

## 📊 Monitoring Setup

### Sentry Configuration

1. **Create Project:**
   - Go to https://sentry.io
   - Create project: "Pizoo Production"

2. **Get DSN:**
   - Project Settings → Client Keys (DSN)
   - Copy DSN

3. **Configure Frontend:**
   ```env
   REACT_APP_SENTRY_DSN=https://xxx@xxx.ingest.sentry.io/xxx
   REACT_APP_SENTRY_TRACES_SAMPLE=0.2
   REACT_APP_ENVIRONMENT=production
   ```

4. **Configure Backend:**
   ```env
   SENTRY_DSN=https://xxx@xxx.ingest.sentry.io/xxx
   SENTRY_ENVIRONMENT=production
   SENTRY_TRACES_SAMPLE=0.1
   ```

### Log Monitoring

```bash
# Real-time backend logs
tail -f /var/log/supervisor/backend.err.log

# Real-time frontend logs (Vercel)
vercel logs --prod

# Search logs
grep "ERROR" /var/log/supervisor/backend.err.log
grep "500" /var/log/supervisor/backend.err.log
```

---

## 🔄 CI/CD Pipeline (Optional)

### GitHub Actions

Create `.github/workflows/deploy.yml`:

```yaml
name: Deploy to Production

on:
  push:
    branches: [main]

jobs:
  deploy-frontend:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - uses: actions/setup-node@v2
      - run: cd frontend && yarn install
      - run: cd frontend && yarn build
      - uses: amondnet/vercel-action@v20
        with:
          vercel-token: ${{ secrets.VERCEL_TOKEN }}
          vercel-org-id: ${{ secrets.VERCEL_ORG_ID }}
          vercel-project-id: ${{ secrets.VERCEL_PROJECT_ID }}
          vercel-args: '--prod'

  deploy-backend:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - uses: actions/setup-python@v2
      - run: cd backend && pip install -r requirements.txt
      - run: # Deploy to Emergent
```

---

## 🚨 Rollback Procedures

### Frontend Rollback (Vercel)

```bash
# List deployments
vercel ls

# Rollback to previous deployment
vercel rollback <deployment-url>

# Or via dashboard
1. Go to Vercel Dashboard
2. Select project
3. Deployments tab
4. Find previous working deployment
5. Click "Promote to Production"
```

### Backend Rollback

```bash
# Revert code
git revert <commit-hash>
git push

# Or restore from backup
git checkout <previous-commit>
sudo supervisorctl restart backend
```

---

## 📞 Support & Troubleshooting

### Common Issues

#### 1. Vercel 404 Error
- Check `vercel.json` configuration
- Verify build output directory
- Check rewrite rules

#### 2. Backend 502 Error
- Check supervisor status: `sudo supervisorctl status backend`
- View logs: `tail -f /var/log/supervisor/backend.err.log`
- Verify .env variables

#### 3. MongoDB Connection Failed
- Check connection string
- Verify IP whitelist
- Check database user permissions

#### 4. LiveKit Calls Not Working
- Verify credentials
- Check user verification status
- Test token generation endpoint

### Getting Help

- **Documentation:** This file + PIZOO_PROJECT_README.md
- **Email:** support@pizoo.ch
- **Logs:** Check supervisor and Vercel logs

---

## ✅ Deployment Checklist

- [ ] MongoDB production cluster configured
- [ ] Backend .env updated with production values
- [ ] Frontend .env.production configured
- [ ] Vercel project created and configured
- [ ] Custom domain (pizoo.ch) added to Vercel
- [ ] DNS records configured
- [ ] SSL certificate active
- [ ] Email SMTP configured and tested
- [ ] Cloudinary account setup
- [ ] LiveKit project created
- [ ] Sentry monitoring configured
- [ ] Backend deployed and running
- [ ] Frontend deployed to Vercel
- [ ] All endpoints tested
- [ ] Video calls tested
- [ ] Email verification tested
- [ ] Payment integration tested (if applicable)

---

**Deployment Date:** _______________  
**Deployed By:** _______________  
**Version:** 2.0  
**Status:** Production Ready ✅
