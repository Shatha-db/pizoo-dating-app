# Pizoo Dating App - Authentication API Documentation

## Overview

Pizoo implements a **one-time account verification** system. Users verify their account once during signup using one of three methods:

1. **Google OAuth** (via Emergent) - Recommended
2. **Email Magic Link** (15-minute TTL)
3. **Phone OTP** (via Telnyx) - To be implemented

Once verified, users can access all features (messaging, video/audio calls, live stream) without any per-call verification codes.

## Base URL

```
https://datemaps.emergent.host/api
```

## Authentication Flow

### Method 1: Google OAuth (Emergent)

#### Step 1: Redirect to Emergent Auth
```
https://auth.emergentagent.com/?redirect=https://datemaps.emergent.host/dashboard
```

#### Step 2: Process Session ID
After successful Google login, user lands at:
```
https://datemaps.emergent.host/dashboard#session_id=abc123xyz
```

Frontend extracts `session_id` from URL fragment.

#### Step 3: Exchange Session for JWT

**Endpoint:** `POST /auth/oauth/google`

**Request Body:**
```json
{
  "session_id": "abc123xyz"
}
```

**Response (200 OK):**
```json
{
  "success": true,
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer",
  "expires_in": 3600,
  "user": {
    "id": "uuid-here",
    "name": "John Doe",
    "email": "john@example.com",
    "verified": true,
    "verified_method": "google_oauth"
  }
}
```

**Error Responses:**
- `401 Unauthorized` - Invalid or expired session_id
- `500 Internal Server Error` - Authentication failed

---

### Method 2: Email Magic Link

#### Step 1: Request Magic Link

**Endpoint:** `POST /auth/email/send-link`

**Request Body:**
```json
{
  "email": "user@example.com",
  "name": "John Doe"
}
```

**Response (200 OK):**
```json
{
  "success": true,
  "message": "Verification email sent. Please check your inbox.",
  "expires_in": 900
}
```

**Error Responses:**
- `400 Bad Request` - Email already verified
- `500 Internal Server Error` - Failed to send email

#### Step 2: User Clicks Magic Link
Email contains link:
```
https://datemaps.emergent.host/verify-email?token=abc123xyz
```

#### Step 3: Verify Token

**Endpoint:** `POST /auth/email/verify`

**Request Body:**
```json
{
  "token": "abc123xyz"
}
```

**Response (200 OK):**
```json
{
  "success": true,
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer",
  "expires_in": 3600,
  "user": {
    "id": "uuid-here",
    "name": "John Doe",
    "email": "user@example.com",
    "verified": true,
    "verified_method": "email_link"
  }
}
```

**Error Responses:**
- `400 Bad Request` - Invalid or expired token
- `500 Internal Server Error` - Verification failed

---

### Method 3: Phone OTP (Telnyx - To Be Implemented)

**Endpoint:** `POST /auth/phone/send-otp`

**Request Body:**
```json
{
  "phone": "+41791234567",
  "name": "John Doe"
}
```

**Endpoint:** `POST /auth/phone/verify-otp`

**Request Body:**
```json
{
  "phone": "+41791234567",
  "otp_code": "123456"
}
```

---

## Token Management

### Refresh Access Token

**Endpoint:** `POST /auth/refresh`

**Request Body:**
```json
{
  "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
}
```

**Response (200 OK):**
```json
{
  "success": true,
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer",
  "expires_in": 3600
}
```

**Token Lifetimes:**
- Access Token: 1 hour
- Refresh Token: 7 days
- Session: 7 days

---

## User Management

### Get Current User

**Endpoint:** `GET /auth/me`

**Headers:**
```
Authorization: Bearer <access_token>
```

**Response (200 OK):**
```json
{
  "success": true,
  "user": {
    "id": "uuid-here",
    "name": "John Doe",
    "email": "user@example.com",
    "verified": true,
    "verified_method": "google_oauth",
    "subscription_status": "trial",
    "premium_tier": "free"
  }
}
```

### Logout

**Endpoint:** `POST /auth/logout`

**Headers:**
```
Authorization: Bearer <access_token>
```

**Response (200 OK):**
```json
{
  "success": true,
  "message": "Logged out successfully"
}
```

---

## Protected Endpoints

### LiveKit Token (Video/Audio Calls)

**Endpoint:** `POST /livekit/token`

**Requirements:**
- Valid JWT token
- User must be verified (`verified=true`)
- Rate limit: 30 requests per hour

**Headers:**
```
Authorization: Bearer <access_token>
```

**Request Body:**
```json
{
  "match_id": "match-uuid",
  "call_type": "video",
  "participant_name": "John Doe"
}
```

**Response (200 OK):**
```json
{
  "success": true,
  "token": "livekit-jwt-token",
  "url": "wss://pizoo-app.livekit.cloud",
  "room_name": "pz-room-match-uuid",
  "participant": {
    "identity": "user_uuid",
    "name": "John Doe"
  },
  "call_type": "video",
  "video_enabled": true,
  "audio_enabled": true
}
```

**Error Responses:**
- `403 Forbidden` - User not verified
- `429 Too Many Requests` - Rate limit exceeded (30/hour)
- `503 Service Unavailable` - LiveKit not configured

---

## Frontend Implementation Guide

### 1. Check Existing Session

```javascript
// Check if user has access_token in localStorage
const accessToken = localStorage.getItem('access_token');

if (accessToken) {
  // Verify token by calling /auth/me
  const response = await fetch('/api/auth/me', {
    headers: { 'Authorization': `Bearer ${accessToken}` }
  });
  
  if (response.ok) {
    const data = await response.json();
    if (data.user.verified) {
      // User is authenticated and verified - go to dashboard
    } else {
      // User exists but not verified - show verification screen
    }
  } else {
    // Token expired or invalid - show login screen
  }
}
```

### 2. Google OAuth Flow

```javascript
// Step 1: Redirect to Emergent
const redirectUrl = 'https://datemaps.emergent.host/dashboard';
window.location.href = `https://auth.emergentagent.com/?redirect=${encodeURIComponent(redirectUrl)}`;

// Step 2: Handle callback (in dashboard page)
useEffect(() => {
  const hash = window.location.hash;
  const params = new URLSearchParams(hash.substring(1));
  const sessionId = params.get('session_id');
  
  if (sessionId) {
    // Exchange session_id for JWT
    fetch('/api/auth/oauth/google', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ session_id: sessionId })
    })
    .then(res => res.json())
    .then(data => {
      localStorage.setItem('access_token', data.access_token);
      localStorage.setItem('refresh_token', data.refresh_token);
      // Clean URL and redirect to dashboard
      window.location.hash = '';
      window.location.reload();
    });
  }
}, []);
```

### 3. Email Magic Link Flow

```javascript
// Step 1: Send magic link
const sendMagicLink = async (email, name) => {
  const response = await fetch('/api/auth/email/send-link', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ email, name })
  });
  
  const data = await response.json();
  if (data.success) {
    alert('Verification email sent! Please check your inbox.');
  }
};

// Step 2: Verify token (in /verify-email page)
useEffect(() => {
  const params = new URLSearchParams(window.location.search);
  const token = params.get('token');
  
  if (token) {
    fetch('/api/auth/email/verify', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ token })
    })
    .then(res => res.json())
    .then(data => {
      if (data.success) {
        localStorage.setItem('access_token', data.access_token);
        localStorage.setItem('refresh_token', data.refresh_token);
        window.location.href = '/dashboard';
      }
    });
  }
}, []);
```

### 4. Token Refresh

```javascript
const refreshAccessToken = async () => {
  const refreshToken = localStorage.getItem('refresh_token');
  
  const response = await fetch('/api/auth/refresh', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ refresh_token: refreshToken })
  });
  
  if (response.ok) {
    const data = await response.json();
    localStorage.setItem('access_token', data.access_token);
    return data.access_token;
  } else {
    // Refresh failed - redirect to login
    localStorage.clear();
    window.location.href = '/login';
  }
};

// Use in axios/fetch interceptor
axios.interceptors.response.use(
  response => response,
  async error => {
    if (error.response?.status === 401) {
      const newToken = await refreshAccessToken();
      error.config.headers['Authorization'] = `Bearer ${newToken}`;
      return axios(error.config);
    }
    return Promise.reject(error);
  }
);
```

### 5. Making Authenticated Requests

```javascript
const makeAuthRequest = async (url, options = {}) => {
  const accessToken = localStorage.getItem('access_token');
  
  const response = await fetch(url, {
    ...options,
    headers: {
      ...options.headers,
      'Authorization': `Bearer ${accessToken}`,
      'Content-Type': 'application/json'
    }
  });
  
  if (response.status === 401) {
    // Token expired - try refresh
    await refreshAccessToken();
    // Retry request
    return makeAuthRequest(url, options);
  }
  
  return response;
};

// Example: Get LiveKit token for call
const startVideoCall = async (matchId) => {
  const response = await makeAuthRequest('/api/livekit/token', {
    method: 'POST',
    body: JSON.stringify({
      match_id: matchId,
      call_type: 'video'
    })
  });
  
  if (response.ok) {
    const data = await response.json();
    // Use data.token and data.url to connect to LiveKit
  } else if (response.status === 403) {
    alert('Please verify your account to use video calls');
  }
};
```

---

## Testing with Postman/cURL

### 1. Test Email Magic Link

```bash
# Send magic link
curl -X POST https://datemaps.emergent.host/api/auth/email/send-link \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@example.com",
    "name": "Test User"
  }'

# Check email for token, then verify
curl -X POST https://datemaps.emergent.host/api/auth/email/verify \
  -H "Content-Type: application/json" \
  -d '{
    "token": "token-from-email"
  }'
```

### 2. Test Protected Endpoint

```bash
# Get LiveKit token (requires verified user)
curl -X POST https://datemaps.emergent.host/api/livekit/token \
  -H "Authorization: Bearer your-access-token" \
  -H "Content-Type: application/json" \
  -d '{
    "match_id": "test-match-123",
    "call_type": "video"
  }'
```

### 3. Test Token Refresh

```bash
curl -X POST https://datemaps.emergent.host/api/auth/refresh \
  -H "Content-Type: application/json" \
  -d '{
    "refresh_token": "your-refresh-token"
  }'
```

---

## Database Schema

### Users Collection
```javascript
{
  id: "uuid",
  name: "John Doe",
  email: "user@example.com",
  phone_number: "+41791234567",
  verified: true,  // ✅ New field
  verified_method: "google_oauth",  // ✅ New field: "google_oauth", "email_link", "phone_otp"
  verified_at: "2025-01-15T10:30:00Z",  // ✅ New field
  created_at: "2025-01-15T10:00:00Z"
}
```

### User Sessions Collection
```javascript
{
  id: "uuid",
  user_id: "user-uuid",
  session_token: "emergent-session-token",
  refresh_token: "jwt-refresh-token",
  expires_at: "2025-01-22T10:30:00Z",  // 7 days
  created_at: "2025-01-15T10:30:00Z",
  last_used_at: "2025-01-15T10:30:00Z"
}
```

### Email Verification Tokens Collection
```javascript
{
  id: "uuid",
  user_id: "user-uuid",
  token: "random-secure-token",
  email: "user@example.com",
  expires_at: "2025-01-15T10:45:00Z",  // 15 minutes
  created_at: "2025-01-15T10:30:00Z",
  used: false
}
```

### Rate Limits Collection
```javascript
{
  id: "uuid",
  user_id: "user-uuid",
  endpoint: "/livekit/token",
  count: 5,  // Current count in window
  window_start: "2025-01-15T10:00:00Z",
  last_request: "2025-01-15T10:30:00Z"
}
```

---

## Migration for Existing Users

All existing users have been migrated with `verified=false`. They will see a "Complete Verification" screen on next login with options to verify via:

1. Google OAuth (quickest)
2. Email Magic Link
3. Phone OTP (when available)

Once verified, they regain full access to all features.

---

## Security Notes

1. **Access Tokens** expire in 1 hour - stored in memory or localStorage
2. **Refresh Tokens** expire in 7 days - stored in httpOnly cookie (recommended) or localStorage
3. **Email Magic Links** expire in 15 minutes - one-time use
4. **LiveKit Tokens** expire in 10 minutes - short-lived for security
5. **Rate Limiting** prevents abuse (30 calls/hour per user)
6. **HTTPS** required in production for all endpoints
7. **CORS** configured for allowed origins only

---

## Next Steps (Phone OTP)

To implement Phone OTP verification:

1. Sign up for Telnyx account
2. Add `TELNYX_API_KEY` and `TELNYX_PUBLIC_KEY` to .env
3. Update `auth_service.py` `send_otp_sms()` method
4. Create frontend phone verification flow
5. Test with real phone numbers

---

## Support

For issues or questions:
- Email: support@pizoo.app
- Docs: https://docs.pizoo.app
- Status: https://status.pizoo.app
