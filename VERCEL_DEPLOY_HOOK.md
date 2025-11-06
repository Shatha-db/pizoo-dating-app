# 🚀 Vercel Deploy Hook Integration - Pizoo

**Status:** ✅ **ACTIVE**

---

## 📋 Deploy Hook Details

### Hook URL:
```
https://api.vercel.com/v1/integrations/deploy/prj_8ZKPw4z3kOreyIVPywFD4OE3EdxJ/2im8oZHyQW
```

### Project:
- **Name:** Pizoo Dating App
- **Repository:** `Shatha-db/pizoo-dating-app`
- **Branch:** `main`
- **Domains:**
  - https://pizoo.ch
  - https://www.pizoo.ch
  - https://pizoo.vercel.app

---

## 🤖 Automatic Deployment

### GitHub Actions Workflow:
✅ Configured in `.github/workflows/deploy-vercel.yml`

### Triggers:
1. **Push to main branch** - Automatic deployment
2. **Manual trigger** - Via GitHub Actions UI

### Workflow Steps:
1. Checkout code
2. Trigger Vercel Deploy Hook
3. Wait 90 seconds
4. Verify deployment on all domains

---

## 🔧 Manual Deployment

### Using cURL:
```bash
curl -X POST "https://api.vercel.com/v1/integrations/deploy/prj_8ZKPw4z3kOreyIVPywFD4OE3EdxJ/2im8oZHyQW" \
  -H "Content-Type: application/json"
```

### Expected Response:
```json
{
  "job": {
    "id": "DXJQOvQc0kdabxaxxUHV",
    "state": "PENDING",
    "createdAt": 1762436957146
  }
}
```

---

## 📊 Deployment Process

### Timeline:
| Step | Duration | Status |
|------|----------|--------|
| Trigger Hook | 1 second | ✅ |
| Vercel receives | 2-5 seconds | ✅ |
| Build starts | 10-30 seconds | ✅ |
| Build completes | 1-3 minutes | ⏳ |
| Deploy to production | 30 seconds | ⏳ |
| **Total** | **2-4 minutes** | |

### States:
1. **PENDING** - Hook received, queuing build
2. **BUILDING** - Installing dependencies & building
3. **READY** - Deployed to production ✅
4. **ERROR** - Build failed ❌

---

## ✅ Verification

### Check Deployment Status:

#### 1. Check pizoo.ch:
```bash
curl -I https://pizoo.ch
# Expected: HTTP/2 200 OK
```

#### 2. Check www.pizoo.ch:
```bash
curl -I https://www.pizoo.ch
# Expected: HTTP/2 200 OK or 301 (redirect)
```

#### 3. Check Vercel app:
```bash
curl -I https://pizoo.vercel.app
# Expected: HTTP/2 200 OK
```

---

## 🔄 How It Works

### Automatic Flow:

```
Developer pushes to main branch
         ↓
GitHub detects push
         ↓
GitHub Actions triggers
         ↓
Calls Vercel Deploy Hook
         ↓
Vercel receives hook
         ↓
Vercel pulls latest code from GitHub
         ↓
Vercel builds project
         ↓
Vercel deploys to production
         ↓
pizoo.ch updates automatically ✅
```

---

## 🛠️ Configuration Files

### 1. GitHub Actions Workflow:
**Location:** `.github/workflows/deploy-vercel.yml`

### 2. Vercel Configuration:
**Location:** `/app/vercel.json`
```json
{
  "version": 2,
  "buildCommand": "cd frontend && yarn install && yarn build",
  "outputDirectory": "frontend/build",
  "rewrites": [
    {"source": "/(.*)", "destination": "/index.html"}
  ]
}
```

### 3. Frontend Routing:
**Location:** `/app/frontend/vercel.json`
```json
{
  "rewrites": [
    {"source": "/(.*)", "destination": "/index.html"}
  ]
}
```

---

## 📈 Monitoring

### GitHub Actions:
View deployment logs at:
```
https://github.com/Shatha-db/pizoo-dating-app/actions
```

### Vercel Dashboard:
View deployments at:
```
https://vercel.com/dashboard
```

---

## 🆘 Troubleshooting

### Issue: Hook returns "SOMETHING_WENT_WRONG"

**Possible Causes:**
1. Invalid hook URL
2. Project not found
3. Temporary Vercel issue

**Solution:**
- Verify hook URL is correct
- Check Vercel project exists
- Try again after 1 minute

---

### Issue: Build fails

**Check:**
1. Vercel build logs
2. `vercel.json` configuration
3. `package.json` scripts
4. Environment variables

---

### Issue: 404 on domains

**Causes:**
1. Build succeeded but routing misconfigured
2. Missing `rewrites` in vercel.json
3. Wrong output directory

**Fix:**
1. Ensure `frontend/vercel.json` exists with rewrites
2. Verify `outputDirectory: "frontend/build"`
3. Redeploy

---

## 🎯 Success Criteria

Deployment is successful when:

- [x] Deploy Hook returns valid Job ID
- [x] GitHub Actions workflow completes
- [x] Vercel build succeeds (1-3 minutes)
- [x] pizoo.ch returns 200 OK
- [x] www.pizoo.ch returns 200 OK or 301
- [x] All React routes work (no 404 on refresh)

---

## 📝 Notes

### Security:
- Deploy Hook URL is semi-public (safe to share)
- No authentication required
- Only triggers deployment, cannot access code
- Rate limited by Vercel

### Limitations:
- One deployment at a time per project
- Build timeout: 45 minutes (Hobby plan)
- Bandwidth limits apply

---

## 🔗 Related Links

- **Vercel Dashboard:** https://vercel.com/dashboard
- **GitHub Repository:** https://github.com/Shatha-db/pizoo-dating-app
- **Production Site:** https://pizoo.ch
- **Vercel Docs:** https://vercel.com/docs/concepts/deploy-hooks

---

## ✅ Integration Status

**Deploy Hook:** ✅ Active  
**GitHub Actions:** ✅ Configured  
**Auto-Deploy:** ✅ Enabled  
**Domains:** ✅ Connected  

**Last Updated:** November 6, 2024  
**Status:** Production Ready 🚀
