# 📧 Email Configuration Guide - Pizoo Dating App

## Current Status

✅ **MOCK MODE ENABLED** - Email verification links are printed to backend logs for testing

## How to Enable Real SMTP (Gmail)

### Step 1: Get Your Gmail App Password

1. Go to: https://myaccount.google.com/apppasswords
2. Sign in to your Gmail account
3. Click **"Select app"** → Choose **"Mail"**
4. Click **"Select device"** → Choose **"Other (Custom name)"**
5. Enter name: **"Pizoo Dating App"**
6. Click **"Generate"**
7. Copy the 16-character password (e.g., `abcd efgh ijkl mnop`)

### Step 2: Update Backend Environment Variables

Open `/app/backend/.env` and update these lines:

```bash
# Change EMAIL_MODE from 'mock' to 'smtp'
EMAIL_MODE=smtp

# Keep these as is:
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=mahmuodalsamana@gmail.com

# Replace with your actual Gmail App Password (remove spaces)
SMTP_PASS=abcdefghijklmnop

# Keep this:
EMAIL_FROM="Pizoo App <mahmuodalsamana@gmail.com>"
```

**Important:** Remove all spaces from the App Password!
- ✅ Correct: `abcdefghijklmnop`
- ❌ Wrong: `abcd efgh ijkl mnop`

### Step 3: Restart Backend

After saving the `.env` file, restart the backend:

```bash
sudo supervisorctl restart backend
```

### Step 4: Test Email Sending

```bash
# Send test verification email
curl -X POST https://datemaps.emergent.host/api/auth/email/send-link \
  -H "Content-Type: application/json" \
  -d '{
    "email": "your-test-email@gmail.com",
    "name": "Test User"
  }'

# Check your email inbox for the verification link
```

## Testing with MOCK Mode (Current Setup)

When `EMAIL_MODE=mock`, verification tokens are logged to backend console instead of sent via email.

### How to Test:

1. **Send verification request:**
```bash
curl -X POST http://localhost:8001/api/auth/email/send-link \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@example.com",
    "name": "Test User"
  }'
```

2. **Check backend logs for the token:**
```bash
tail -f /var/log/supervisor/backend.err.log | grep "MOCK EMAIL"
```

You'll see output like:
```
📧 [MOCK EMAIL] Verification link for test@example.com:
   User: Test User
   Link: https://datemaps.emergent.host/verify-email?token=abc123xyz...
   Token: abc123xyz...
   Expires: 15 minutes
```

3. **Copy the token and verify:**
```bash
curl -X POST http://localhost:8001/api/auth/email/verify \
  -H "Content-Type: application/json" \
  -d '{
    "token": "abc123xyz..."
  }'
```

## Troubleshooting

### Error: "Username and Password not accepted"

**Causes:**
1. App Password has spaces (must remove them)
2. App Password was revoked or expired
3. 2-Step Verification not enabled in Gmail
4. Using regular password instead of App Password

**Solutions:**
1. Remove all spaces from `SMTP_PASS`
2. Generate a new App Password
3. Enable 2-Step Verification: https://myaccount.google.com/security
4. Use App Password, not your Gmail password

### Error: "Failed to send verification email"

**Check:**
1. Is `EMAIL_MODE=smtp`? (not 'mock')
2. Is `SMTP_USER` correct email?
3. Is `SMTP_PASS` the 16-character App Password?
4. Did you restart backend after changing .env?

### View Backend Logs

```bash
# Real-time logs
tail -f /var/log/supervisor/backend.err.log

# Last 50 lines
tail -n 50 /var/log/supervisor/backend.err.log

# Search for errors
tail -n 100 /var/log/supervisor/backend.err.log | grep ERROR
```

## When to Switch to Professional Email

Once you're ready to use a professional email (e.g., `info@pizoo.ch`):

1. Purchase domain email service
2. Get SMTP credentials from your email provider
3. Update `/app/backend/.env`:
```bash
SMTP_HOST=smtp.your-provider.com
SMTP_PORT=587
SMTP_USER=info@pizoo.ch
SMTP_PASS=your-email-password
EMAIL_FROM="Pizoo App <info@pizoo.ch>"
```
4. Restart backend

## Current Configuration

✅ **Active Mode:** MOCK (logs to console)
📍 **Config File:** `/app/backend/.env`
🔧 **Service:** Gmail SMTP (credentials needed)
📨 **From Address:** mahmuodalsamana@gmail.com

---

**Need Help?** 
Check the logs and API documentation in `/app/AUTH_API_DOCUMENTATION.md`
