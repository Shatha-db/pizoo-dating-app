# 🔧 Environment Variable Update Failure - Troubleshooting Guide

**Error**: "Environment Variable Update Failed — Operation Cancelled"

---

## ✅ Validation Results

All `.env` files have been validated and are **CORRECTLY FORMATTED**:
- ✅ No duplicate variables
- ✅ No invalid characters
- ✅ No formatting issues
- ✅ Proper encoding
- ✅ No excessively long values
- ✅ Total: 128 backend variables, 7 frontend variables

---

## 🎯 Root Cause Analysis

The "Operation Cancelled" error is typically caused by:

### 1. **Platform Timeout** (Most Likely)
- Updating 128+ variables at once can timeout
- **Solution**: Update in smaller batches

### 2. **Required Variables Missing**
- Platform needs specific variables to start
- **Solution**: Set critical variables first

### 3. **Platform-Specific Limits**
- Some platforms limit total env var size
- **Solution**: Use minimal required set

---

## 🚀 SOLUTION: Minimal Required Environment Variables

### Step 1: Start with CRITICAL ONLY (10 variables)

```bash
# Core Database
MONGO_URL=mongodb+srv://user:pass@cluster.mongodb.net/pizoo
DB_NAME=pizoo_database

# Authentication
SECRET_KEY=your-32-char-minimum-secret-key-here

# LiveKit (Video Calls)
LIVEKIT_URL=wss://your-app.livekit.cloud
LIVEKIT_API_KEY=APIxxxxxxxxxx
LIVEKIT_API_SECRET=your-secret

# Cloudinary (Images)
CLOUDINARY_URL=cloudinary://key:secret@cloudname

# Email (can be mock)
EMAIL_MODE=mock
EMAIL_FROM=Pizoo <noreply@pizoo.app>

# CORS
CORS_ORIGINS=*
```

### Step 2: Verify Deployment Works ✅

### Step 3: Add Optional Variables in Batches

**Batch 1 - Monitoring (3 variables):**
```bash
SENTRY_DSN_BACKEND=https://xxx@sentry.io/xxx
SENTRY_ENVIRONMENT=production
SENTRY_TRACES_SAMPLE=0.2
```

**Batch 2 - Email (if needed):**
```bash
EMAIL_MODE=smtp
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=your-email@gmail.com
SMTP_PASS=your-app-password
```

**Batch 3 - Phone Verification:**
```bash
TELNYX_API_KEY=your-telnyx-key
```

---

## 📋 Quick Fix Checklist

### Option A: Use Platform UI
1. Clear ALL existing environment variables
2. Add ONLY the 10 critical variables above
3. Deploy and verify it works
4. Add remaining variables in batches of 10-20

### Option B: Use Configuration File
If platform supports it:
1. Export current variables to file
2. Clean and validate with our script
3. Re-import in smaller batches

### Option C: Use Code Defaults
Update server.py to have sensible defaults:
```python
# Already implemented in current code!
mongo_url = os.environ.get('MONGO_URL') or os.environ.get('MONGODB_URI')
email_mode = os.environ.get('EMAIL_MODE', 'mock')
cors_origins = os.environ.get('CORS_ORIGINS', '*')
```

---

## 🔍 Verification Commands

After updating variables, verify:

```bash
# Check if critical variables are set
echo $MONGO_URL
echo $LIVEKIT_URL
echo $CLOUDINARY_URL

# Test database connection
mongosh "$MONGO_URL" --eval "db.adminCommand('ping')"

# Validate environment
python validate_env.py
```

---

## 📊 Environment Variable Breakdown

### Critical (Must Have) - 10 variables
| Variable | Purpose | Example |
|----------|---------|---------|
| MONGO_URL | Database connection | mongodb+srv://... |
| DB_NAME | Database name | pizoo_database |
| SECRET_KEY | JWT signing | 32+ char string |
| LIVEKIT_URL | Video calls | wss://app.livekit.cloud |
| LIVEKIT_API_KEY | LiveKit auth | APIxxxx |
| LIVEKIT_API_SECRET | LiveKit auth | secret |
| CLOUDINARY_URL | Image storage | cloudinary://... |
| EMAIL_MODE | Email type | mock or smtp |
| EMAIL_FROM | Sender email | Pizoo <email> |
| CORS_ORIGINS | CORS policy | * or domains |

### Important (Recommended) - 5 variables
- SENTRY_DSN_BACKEND (error tracking)
- FRONTEND_URL (for emails/callbacks)
- REACT_APP_BACKEND_URL (frontend config)
- JWT_ACCESS_TOKEN_EXPIRE_MINUTES (session length)
- ENVIRONMENT (production/staging)

### Optional (Nice to Have) - 15 variables
- SMTP_* (if using real email)
- TELNYX_API_KEY (phone verification)
- GITHUB_* (integrations)
- Feature flags
- Additional configs

### Auto-Generated (Don't Set) - 98 variables
These are automatically set by the platform or have defaults in code.

---

## 🎯 Recommended Deployment Strategy

### Phase 1: Minimal Deployment ✅
```bash
# Set only 10 critical variables
# Deploy
# Verify: curl https://your-app.emergent.host/health
```

### Phase 2: Add Monitoring ✅
```bash
# Add Sentry variables
# Redeploy
# Verify error tracking works
```

### Phase 3: Full Configuration ✅
```bash
# Add remaining optional variables
# Final deployment
```

---

## ⚠️ Platform-Specific Issues

### If using Emergent Platform:

1. **Check Platform Limits:**
   - Max variables: Usually 200-500
   - Max value size: Usually 4KB per variable
   - Total size limit: Usually 32KB-64KB

2. **Check Variable Names:**
   - Must start with letter or underscore
   - Only alphanumeric and underscore
   - Case sensitive

3. **Check for Conflicts:**
   - Platform may reserve certain variable names
   - Check if MONGO_URL conflicts with platform defaults

4. **Try Smaller Batches:**
   - Update 10 variables at a time
   - Wait 30 seconds between batches
   - Refresh page between updates

---

## 🔧 Emergency Workaround

If platform update keeps failing, use this approach:

### 1. Hardcode Critical Values Temporarily
In `packages/backend/server.py`:

```python
# TEMPORARY WORKAROUND - Remove after platform fix
if not os.environ.get('MONGO_URL'):
    os.environ['MONGO_URL'] = 'mongodb+srv://user:pass@cluster.mongodb.net/pizoo'
if not os.environ.get('LIVEKIT_URL'):
    os.environ['LIVEKIT_URL'] = 'wss://your-app.livekit.cloud'
# ... etc
```

### 2. Use Config File
Create `config.py` with all settings:
```python
class Settings:
    MONGO_URL = os.getenv('MONGO_URL', 'default-value')
    # ... all settings
```

### 3. Use External Config Service
- Store configs in GitHub secrets
- Use HashiCorp Vault
- Use AWS Secrets Manager

---

## 📞 Support Actions

If issue persists:

1. **Check Platform Status Page**
   - Look for known issues with environment variables

2. **Contact Emergent Support**
   - Mention: "Environment Variable Update Failed — Operation Cancelled"
   - Provide: Number of variables (128)
   - Attach: This troubleshooting guide

3. **Try Alternative Method**
   - Use CLI if available
   - Use API if available
   - Use infrastructure-as-code (Terraform, etc.)

---

## ✅ Current Status

- ✅ All environment files validated
- ✅ No formatting issues found
- ✅ Code handles missing variables gracefully
- ✅ Application can start with minimal variables
- ⚠️ Platform update mechanism needs troubleshooting

**Next Action**: Try updating with minimal 10-variable set first.

---

**Last Updated**: November 2, 2025  
**Validation Script**: `validate_env.py` (included)  
**Status**: Ready for deployment with minimal env vars

