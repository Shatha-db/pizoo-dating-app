# Pizoo | Twilio Configuration Guide

**Date:** 2025-01-27  
**Status:** ⚠️ CONFIGURED (Placeholder Credentials)  
**Action Required:** Replace with real Twilio credentials

---

## ✅ What Was Done

Environment variables for Twilio have been added to `/app/backend/.env`:

```bash
TWILIO_ACCOUNT_SID=ACxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
TWILIO_AUTH_TOKEN=your_twilio_auth_token_here
TWILIO_PHONE_FROM=Pizoo
TWILIO_API_URL=https://api.twilio.com/2010-04-01
```

**Backend Status:** ✅ Running successfully

---

## ⚠️ IMPORTANT: Current Status

**The current configuration uses PLACEHOLDER values and will NOT work for production!**

You MUST replace these with your actual Twilio credentials to enable:
- Voice calls
- Video calls
- SMS OTP (if using Twilio instead of Telnyx)
- Twilio Verify

---

## 🔑 How to Get Real Twilio Credentials

### Step 1: Create/Access Twilio Account
1. Go to: https://www.twilio.com/console
2. Sign up or log in to your account
3. Complete account verification

### Step 2: Get Your Credentials

#### **Account SID & Auth Token:**
1. Go to Twilio Console: https://console.twilio.com/
2. Look for "Account Info" section (usually on right side)
3. Copy:
   - **Account SID** (starts with `AC...`, 34 characters)
   - **Auth Token** (click eye icon to reveal)

**Example:**
```
Account SID: AC1234567890abcdef1234567890abcdef
Auth Token: 1234567890abcdef1234567890abcdef
```

#### **Phone Number (From):**
1. Go to: https://console.twilio.com/us1/develop/phone-numbers/manage/incoming
2. If you don't have a number, buy one:
   - Click "Buy a number"
   - Select capabilities: Voice + SMS
   - Choose a number
   - Purchase
3. Copy your phone number (E.164 format)

**Example:**
```
+12125551234
```

### Step 3: Create API Keys (for Voice/Video)

If you want to use Twilio Voice/Video features:

1. Go to: https://console.twilio.com/us1/account/keys-credentials/api-keys
2. Click "Create API key"
3. Name it: "Pizoo Production"
4. Copy and save:
   - **API Key SID** (starts with `SK...`)
   - **API Key Secret** (shown only once!)

**Example:**
```
API Key SID: SK1234567890abcdef1234567890abcdef
API Key Secret: secret1234567890abcdef1234567890
```

### Step 4: Create TwiML App (for Voice)

1. Go to: https://console.twilio.com/us1/develop/voice/manage/twiml-apps
2. Click "Create new TwiML App"
3. Name: "Pizoo Voice"
4. Voice Request URL: `https://your-domain.com/api/twilio/voice/incoming`
5. Voice Method: POST
6. Save
7. Copy **Application SID** (starts with `AP...`)

### Step 5: Create Verify Service (Optional)

If you want to use Twilio Verify for OTP:

1. Go to: https://console.twilio.com/us1/develop/verify/services
2. Click "Create new"
3. Name: "Pizoo OTP"
4. Save
5. Copy **Service SID** (starts with `VA...`)

---

## 📝 Update Configuration

### Option 1: Edit .env File Manually

```bash
# Open the file
nano /app/backend/.env

# Find and update these lines:
TWILIO_ACCOUNT_SID=AC1234567890abcdef1234567890abcdef
TWILIO_AUTH_TOKEN=1234567890abcdef1234567890abcdef
TWILIO_PHONE_FROM=+12125551234
TWILIO_API_KEY_SID=SK1234567890abcdef1234567890abcdef
TWILIO_API_KEY_SECRET=secret1234567890abcdef1234567890
TWILIO_VOICE_APPLICATION_SID=AP1234567890abcdef1234567890abcdef
TWILIO_VERIFY_SERVICE_SID=VA1234567890abcdef1234567890abcdef

# Save and exit (Ctrl+O, Enter, Ctrl+X)

# Restart backend
sudo supervisorctl restart backend
```

### Option 2: Use Echo Commands

```bash
# Remove old placeholder entries
sed -i '/^TWILIO_ACCOUNT_SID=/d' /app/backend/.env
sed -i '/^TWILIO_AUTH_TOKEN=/d' /app/backend/.env
sed -i '/^TWILIO_PHONE_FROM=/d' /app/backend/.env

# Add real credentials
echo "TWILIO_ACCOUNT_SID=AC1234567890abcdef1234567890abcdef" >> /app/backend/.env
echo "TWILIO_AUTH_TOKEN=1234567890abcdef1234567890abcdef" >> /app/backend/.env
echo "TWILIO_PHONE_FROM=+12125551234" >> /app/backend/.env
echo "TWILIO_API_KEY_SID=SK1234567890abcdef1234567890abcdef" >> /app/backend/.env
echo "TWILIO_API_KEY_SECRET=secret1234567890abcdef1234567890" >> /app/backend/.env
echo "TWILIO_VOICE_APPLICATION_SID=AP1234567890abcdef1234567890abcdef" >> /app/backend/.env
echo "TWILIO_VERIFY_SERVICE_SID=VA1234567890abcdef1234567890abcdef" >> /app/backend/.env

# Restart backend
sudo supervisorctl restart backend
```

---

## 🧪 Test Your Configuration

### Test 1: Check Environment Variables Loaded

```bash
# Check backend logs
tail -f /var/log/supervisor/backend.out.log

# Look for Twilio-related output
```

### Test 2: Test Voice Token Generation

```bash
curl -X POST https://your-domain.com/api/twilio/voice/token \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"identity": "user123"}'
```

**Expected Response:**
```json
{
  "ok": true,
  "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ...",
  "identity": "user123"
}
```

### Test 3: Test Video Token Generation

```bash
curl -X POST https://your-domain.com/api/twilio/video/token \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"identity": "user123", "room": "test-room"}'
```

### Test 4: Test SMS Sending (if using Twilio for SMS)

Change SMS provider to Twilio:
```bash
# Edit .env
SMS_PROVIDER=twilio

# Restart backend
sudo supervisorctl restart backend

# Send test OTP
curl -X POST https://your-domain.com/api/auth/phone/send-otp \
  -H "Content-Type: application/json" \
  -d '{"phone": "+YOUR_REAL_NUMBER"}'
```

---

## 📊 Complete Environment Variables Reference

### Required for Basic SMS:
```bash
TWILIO_ACCOUNT_SID=ACxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
TWILIO_AUTH_TOKEN=your_auth_token_here
TWILIO_PHONE_FROM=+1234567890
```

### Required for Voice Calls:
```bash
TWILIO_ACCOUNT_SID=ACxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
TWILIO_API_KEY_SID=SKxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
TWILIO_API_KEY_SECRET=your_api_key_secret_here
TWILIO_VOICE_APPLICATION_SID=APxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
```

### Required for Video Calls:
```bash
TWILIO_ACCOUNT_SID=ACxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
TWILIO_API_KEY_SID=SKxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
TWILIO_API_KEY_SECRET=your_api_key_secret_here
```

### Optional for Verify OTP:
```bash
TWILIO_VERIFY_SERVICE_SID=VAxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
```

### Full Configuration Example:
```bash
# ========================================
# Twilio Configuration
# ========================================
# Basic Account Info
TWILIO_ACCOUNT_SID=AC1234567890abcdef1234567890abcdef
TWILIO_AUTH_TOKEN=1234567890abcdef1234567890abcdef
TWILIO_PHONE_FROM=+12125551234
TWILIO_API_URL=https://api.twilio.com/2010-04-01

# API Keys (for Voice/Video)
TWILIO_API_KEY_SID=SK1234567890abcdef1234567890abcdef
TWILIO_API_KEY_SECRET=secret1234567890abcdef1234567890

# Voice Application
TWILIO_VOICE_APPLICATION_SID=AP1234567890abcdef1234567890abcdef

# Verify Service (Optional)
TWILIO_VERIFY_SERVICE_SID=VA1234567890abcdef1234567890abcdef
```

---

## 🚨 Security Best Practices

### 1. Keep Credentials Secret
- ✅ Never commit credentials to Git
- ✅ Use environment variables only
- ✅ Rotate tokens periodically
- ✅ Use separate accounts for dev/prod

### 2. Use Subaccounts (Recommended)
Create separate Twilio subaccounts for:
- Development
- Staging
- Production

### 3. Monitor Usage
- Set up billing alerts
- Monitor unusual activity
- Review logs regularly

### 4. IP Whitelisting
Consider restricting API access to specific IPs in Twilio Console.

---

## 💰 Pricing Estimates

### Voice Calls:
- **Outbound:** ~$0.013/minute
- **Inbound:** ~$0.0085/minute
- **Recording:** ~$0.0025/minute

### Video Calls:
- **Group Rooms:** $0.0015/participant/minute
- **Recording:** $0.004/minute

### SMS:
- **Outbound:** ~$0.0075/message (US)
- **International:** Varies by country

### Verify OTP:
- **Per verification:** ~$0.05

**Tip:** Consider using **Telnyx** for SMS (cheaper) and **Jitsi** for video (free) as already implemented.

---

## 🔧 Troubleshooting

### Issue: "Invalid credentials" error
**Solution:**
1. Verify Account SID starts with `AC`
2. Check Auth Token is correct (no extra spaces)
3. Ensure credentials are from correct account

### Issue: "Phone number not verified"
**Solution:**
1. Trial accounts can only call/SMS verified numbers
2. Upgrade to paid account for unrestricted use
3. Or add numbers to verified list in console

### Issue: Voice calls not connecting
**Solution:**
1. Verify TwiML App webhook URL is correct
2. Check webhook is publicly accessible
3. Review Twilio debugger logs

### Issue: "Authentication failed" for Voice/Video
**Solution:**
1. Create API Keys (different from Account SID)
2. Use API Key SID (starts with `SK`)
3. Use API Key Secret (not Auth Token)

---

## 📞 Twilio Support

- **Console:** https://console.twilio.com/
- **Documentation:** https://www.twilio.com/docs
- **Support:** https://support.twilio.com/
- **Status Page:** https://status.twilio.com/
- **Community:** https://www.twilio.com/community

---

## ✅ Next Steps Checklist

- [ ] Create Twilio account (if not exists)
- [ ] Get Account SID and Auth Token
- [ ] Purchase phone number
- [ ] Create API Keys (for Voice/Video)
- [ ] Create TwiML App (for Voice)
- [ ] Create Verify Service (optional)
- [ ] Update `/app/backend/.env` with real credentials
- [ ] Restart backend: `sudo supervisorctl restart backend`
- [ ] Test voice token generation
- [ ] Test video token generation
- [ ] Test with real phone calls
- [ ] Configure webhooks in Twilio Console
- [ ] Set up billing alerts
- [ ] Monitor usage and costs

---

## 🎉 Summary

**Current Status:**
- ✅ Twilio environment variables added to .env
- ✅ Backend configured to use Twilio
- ⚠️  Using PLACEHOLDER credentials (must be replaced)
- ✅ Ready for real credentials

**What Works Now:**
- Configuration structure in place
- Code ready to use Twilio
- Endpoints configured

**What Needs Real Credentials:**
- Voice calls
- Video calls
- SMS via Twilio
- Twilio Verify

**Recommended Next Steps:**
1. If using SMS: Use **Telnyx** (cheaper, already configured)
2. If using Video: Use **Jitsi** (free, already integrated)
3. If you need Twilio: Get credentials and update .env
4. Test in development before production

---

**Report Generated:** 2025-01-27  
**Configuration Status:** ⚠️ NEEDS REAL CREDENTIALS  
**Backend Status:** ✅ RUNNING
