# 🎥 LiveKit Integration - Real-Time Communication Migration

## ✅ Migration Complete

Successfully migrated from **Jitsi Meet** to **LiveKit** for video and voice calling.

---

## 🚀 What Was Implemented

### 1. Backend Setup ✅

**New Files:**
- `/app/backend/livekit_service.py` - LiveKit service with token generation
- Added LiveKit SDK dependencies to `requirements.txt`

**New API Endpoints:**
- `POST /api/livekit/token` - Generate access token for calls
- `GET /api/livekit/status` - Check LiveKit configuration status

**Features:**
- ✅ Secure JWT token generation
- ✅ Room-based 1-to-1 calls
- ✅ Support for video and audio-only calls
- ✅ 24-hour token validity
- ✅ Automatic participant naming
- ✅ Future-ready for group calls

---

### 2. Frontend Setup ✅

**New Files:**
- `/app/frontend/src/modules/chat/LiveKitCallModal.jsx` - New LiveKit-based call component

**Updated Files:**
- `/app/frontend/src/pages/ChatRoom.js` - Switched from Jitsi to LiveKit

**Features:**
- ✅ Modern LiveKit React components
- ✅ Automatic video/audio layout
- ✅ Built-in controls (mute, camera toggle, end call)
- ✅ Voice-only mode support
- ✅ Connection state handling (connecting, connected, failed)
- ✅ Responsive design matching app theme

**UI Components:**
- Video conference with automatic grid layout
- Participant tiles with name badges
- Audio renderer for voice-only participants
- Control bar with mute/unmute, camera toggle
- Custom header with call type indicator
- End call button
- Connection error handling

---

### 3. Environment Variables ✅

**Added to `/app/backend/.env`:**
```bash
# LiveKit Configuration (Real-Time Communication)
LIVEKIT_API_KEY=your_api_key_here
LIVEKIT_API_SECRET=your_api_secret_here
LIVEKIT_URL=wss://your-livekit-server.livekit.cloud
```

**Status:** ⏳ Waiting for credentials from user

---

## 📦 Dependencies Installed

### Backend (Python):
```bash
livekit==1.0.17
livekit-api==1.0.7
livekit-protocol==1.0.8
protobuf==6.33.0
```

### Frontend (React):
```bash
@livekit/components-react@2.9.15
livekit-client@2.15.14
@livekit/components-core@0.12.10
@livekit/protocol@1.42.2
```

---

## 🔧 How It Works

### Call Flow:

1. **User clicks Video/Voice button** in ChatRoom
2. **Frontend requests token** from backend:
   ```javascript
   POST /api/livekit/token
   {
     "match_id": "abc123",
     "call_type": "video" // or "audio"
   }
   ```

3. **Backend generates LiveKit token**:
   - Creates room: `pizoo-match-{matchId}`
   - Generates JWT with user identity
   - Returns token + server URL

4. **Frontend joins LiveKit room**:
   - Uses `<LiveKitRoom>` component
   - Connects to LiveKit server
   - Enables camera/microphone
   - Renders video/audio tracks

5. **Call ends**:
   - User clicks end button
   - Room disconnects
   - Modal closes

---

## 🎨 UI Features

### Call Modal:
- **Header:**
  - Red recording indicator
  - Call type badge (🎥 Video / 🎤 Voice)
  - End call button

- **Video Area:**
  - Full-screen video conference
  - Automatic grid layout for participants
  - Participant name badges
  - Video quality indicators

- **Controls:**
  - Mute/unmute microphone
  - Toggle camera on/off
  - End call button
  - Screen share (built-in)

- **States:**
  - Loading spinner during connection
  - Error message if connection fails
  - "Connecting..." indicator

---

## 🔐 Security Features

- ✅ **JWT-based authentication** - Tokens signed with API secret
- ✅ **User-specific tokens** - Each user gets unique identity
- ✅ **24-hour token expiry** - Automatic expiration
- ✅ **Room isolation** - Each match gets separate room
- ✅ **Participant verification** - Only authorized users can join
- ✅ **Secure WebSocket** - wss:// connection

---

## ⚙️ Configuration Required

To activate LiveKit, you need to:

### Option 1: LiveKit Cloud (Recommended for MVP)
1. Sign up at https://livekit.io
2. Create a new project
3. Get credentials from dashboard:
   - API Key
   - API Secret
   - WebSocket URL (e.g., `wss://your-project.livekit.cloud`)

### Option 2: Self-Hosted LiveKit
1. Deploy LiveKit server: https://docs.livekit.io/guides/deploy/
2. Configure server with domain and SSL
3. Generate API Key/Secret
4. Set LIVEKIT_URL to your server (e.g., `wss://livekit.yourdomain.com`)

### Update Environment Variables:
```bash
# In production environment (not in code!):
LIVEKIT_API_KEY=your_actual_api_key
LIVEKIT_API_SECRET=your_actual_api_secret
LIVEKIT_URL=wss://your-livekit-server.livekit.cloud
```

---

## 🧪 Testing Checklist

### Backend Testing:
```bash
# 1. Check LiveKit status
curl https://your-backend/api/livekit/status

# Expected: {"configured": false, "message": "LiveKit credentials not configured"}

# 2. After adding credentials:
curl https://your-backend/api/livekit/status

# Expected: {"configured": true, "url": "wss://...", "message": "LiveKit is ready"}

# 3. Test token generation:
curl -X POST https://your-backend/api/livekit/token \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"match_id": "test123", "call_type": "video"}'

# Expected: {"success": true, "token": "eyJ...", "url": "wss://...", ...}
```

### Frontend Testing:
1. **Video Call Test:**
   - Open a chat
   - Click video call button 🎥
   - Verify:
     - Loading spinner appears
     - Token is fetched
     - LiveKit room loads
     - Camera/mic permissions requested
     - Your video appears
     - Controls work (mute, camera toggle)

2. **Voice Call Test:**
   - Open a chat
   - Click voice call button 🎤
   - Verify:
     - Camera stays off
     - Audio works
     - Mic controls work

3. **Error Handling:**
   - Before adding credentials, try to call
   - Verify error message appears
   - Click close button works

---

## 🆚 Comparison: Jitsi vs LiveKit

| Feature | Jitsi (Old) | LiveKit (New) |
|---------|-------------|---------------|
| Control | Third-party iframe | Full SDK control |
| Customization | Limited | Complete |
| Mobile Support | Basic | Excellent |
| Quality | Good | Excellent |
| Latency | Medium | Low |
| Recording | External | Built-in |
| Screen Share | Yes | Yes |
| Group Calls | Yes | Yes |
| Analytics | Limited | Built-in |
| UI Customization | Minimal | Complete |

---

## 📊 Architecture

```
┌─────────────┐
│   User A    │
│  (Browser)  │
└──────┬──────┘
       │
       │ 1. Click Video Call
       │
       ▼
┌─────────────────┐
│   Frontend      │
│   ChatRoom.js   │
└──────┬──────────┘
       │
       │ 2. POST /api/livekit/token
       │    {match_id, call_type}
       │
       ▼
┌─────────────────┐
│   Backend       │
│   server.py     │
└──────┬──────────┘
       │
       │ 3. Generate JWT Token
       │
       ▼
┌─────────────────┐
│ LiveKit Service │
│ livekit_service.py │
└──────┬──────────┘
       │
       │ 4. Return token
       │
       ▼
┌─────────────────┐
│   Frontend      │
│ LiveKitCallModal│
└──────┬──────────┘
       │
       │ 5. Connect to LiveKit
       │
       ▼
┌─────────────────┐
│ LiveKit Server  │
│ (Cloud/Self-Hosted)│
└──────┬──────────┘
       │
       │ 6. WebRTC Connection
       │
       ▼
┌─────────────┐
│   User B    │
│  (Browser)  │
└─────────────┘
```

---

## 🚀 Future Enhancements (Ready for Implementation)

### Phase 2 Features:
1. **Call Recording:**
   ```python
   # In livekit_service.py - already structured for this
   token.add_grant(api.VideoGrants(
       room_join=True,
       room=room_name,
       can_update_own_metadata=True,
       can_publish=True,
       can_subscribe=True,
       can_publish_data=True,
       record=True  # ← Add recording permission
   ))
   ```

2. **Push Notifications:**
   - Send notification when call starts
   - Notify other user to join room
   - Display incoming call UI

3. **Group Calls:**
   ```python
   # Already implemented in livekit_service.py:
   LiveKitService.create_group_room_token(
       room_id="group123",
       user_id="user1",
       user_name="John"
   )
   ```

4. **Call History:**
   - Store call records in MongoDB
   - Track duration, participants, timestamps
   - Display in chat history

5. **Network Quality Indicator:**
   - Show connection quality
   - Adapt video quality based on network
   - Alert on poor connection

6. **Virtual Backgrounds:**
   - Use LiveKit's background blur
   - Custom background images
   - Background removal

---

## 🐛 Troubleshooting

### Issue: "Service Unavailable" Error
**Solution:** Add LiveKit credentials to `.env`

### Issue: Camera/Mic Not Working
**Solution:** 
- Check browser permissions
- Ensure HTTPS (required for WebRTC)
- Test on another browser

### Issue: Poor Video Quality
**Solution:**
- Check network connection
- LiveKit auto-adapts quality
- Consider reducing max video bitrate

### Issue: Can't Hear Other Participant
**Solution:**
- Check audio output device
- Verify RoomAudioRenderer is rendered
- Test browser audio settings

---

## 📝 API Reference

### POST /api/livekit/token

**Request:**
```json
{
  "match_id": "string (required)",
  "call_type": "video | audio (default: video)",
  "participant_name": "string (optional)"
}
```

**Response (Success):**
```json
{
  "success": true,
  "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "url": "wss://your-server.livekit.cloud",
  "room_name": "pizoo-match-abc123",
  "participant": {
    "identity": "user123",
    "name": "John Doe"
  },
  "call_type": "video",
  "video_enabled": true,
  "audio_enabled": true
}
```

**Response (Error):**
```json
{
  "detail": "خدمة المكالمات غير متاحة حالياً"
}
```

### GET /api/livekit/status

**Response:**
```json
{
  "configured": true,
  "url": "wss://your-server.livekit.cloud",
  "message": "LiveKit is ready"
}
```

---

## ✅ Summary

**Status:** ✅ Implementation Complete - Waiting for Credentials

**What's Done:**
- ✅ Backend LiveKit service
- ✅ Token generation endpoints
- ✅ Frontend LiveKit component
- ✅ ChatRoom integration
- ✅ Environment variables setup
- ✅ Dependencies installed
- ✅ Error handling
- ✅ UI design

**What's Needed:**
- ⏳ LiveKit API credentials (Key, Secret, URL)
- ⏳ Testing with real credentials
- ⏳ Demo call verification

**Next Steps:**
1. User provides LiveKit credentials
2. Update `.env` with real values
3. Restart backend
4. Test video/voice calls
5. Verify call quality
6. Deploy to production

---

## 📞 Contact

Once you provide the LiveKit credentials, I can:
- Test the integration end-to-end
- Create a demo room
- Share test call link
- Verify audio/video quality
- Confirm mobile compatibility

**Ready to test as soon as credentials are available!** 🚀
