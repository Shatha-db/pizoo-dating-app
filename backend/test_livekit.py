#!/usr/bin/env python3
"""
Test LiveKit Connection and Token Generation
Verifies that LiveKit credentials are working correctly
"""

import sys
sys.path.append('/app/backend')

from livekit_service import LiveKitService
import os

def test_livekit_connection():
    """Test LiveKit configuration and token generation"""
    print("🧪 Testing LiveKit Connection...")
    print("=" * 60)
    
    # 1. Check configuration
    print("\n1️⃣ Checking LiveKit configuration...")
    is_configured = LiveKitService.is_configured()
    
    if is_configured:
        print("   ✅ LiveKit is configured")
        print(f"   • API Key: {os.environ.get('LIVEKIT_API_KEY', 'Not set')[:20]}...")
        print(f"   • API Secret: {os.environ.get('LIVEKIT_API_SECRET', 'Not set')[:20]}...")
        print(f"   • URL: {os.environ.get('LIVEKIT_URL', 'Not set')}")
    else:
        print("   ❌ LiveKit is NOT configured")
        print("   • Check environment variables in .env file")
        return False
    
    # 2. Test token generation for video call
    print("\n2️⃣ Testing video call token generation...")
    video_result = LiveKitService.create_room_token(
        match_id="test-match-123",
        user_id="test-user-456",
        user_name="Test User",
        call_type="video"
    )
    
    if video_result.get("success"):
        print("   ✅ Video token generated successfully")
        print(f"   • Room: {video_result.get('room_name')}")
        print(f"   • Participant: {video_result.get('participant_name')}")
        print(f"   • Token length: {len(video_result.get('token', ''))} chars")
        print(f"   • Server URL: {video_result.get('url')}")
        print(f"   • Video enabled: {video_result.get('video_enabled')}")
        print(f"   • Audio enabled: {video_result.get('audio_enabled')}")
    else:
        print(f"   ❌ Video token generation failed: {video_result.get('error')}")
        return False
    
    # 3. Test token generation for audio call
    print("\n3️⃣ Testing audio call token generation...")
    audio_result = LiveKitService.create_room_token(
        match_id="test-match-789",
        user_id="test-user-456",
        user_name="Test User",
        call_type="audio"
    )
    
    if audio_result.get("success"):
        print("   ✅ Audio token generated successfully")
        print(f"   • Room: {audio_result.get('room_name')}")
        print(f"   • Video enabled: {audio_result.get('video_enabled')}")
        print(f"   • Audio enabled: {audio_result.get('audio_enabled')}")
    else:
        print(f"   ❌ Audio token generation failed: {audio_result.get('error')}")
        return False
    
    # 4. Test group call token (future feature)
    print("\n4️⃣ Testing group call token generation...")
    group_result = LiveKitService.create_group_room_token(
        room_id="test-group-001",
        user_id="test-user-456",
        user_name="Test User"
    )
    
    if group_result.get("success"):
        print("   ✅ Group token generated successfully")
        print(f"   • Room: {group_result.get('room_name')}")
    else:
        print(f"   ❌ Group token generation failed: {group_result.get('error')}")
        return False
    
    # 5. Display sample token (for debugging)
    print("\n5️⃣ Sample Token Structure:")
    print(f"   • Token starts with: {video_result.get('token', '')[:50]}...")
    print(f"   • Token ends with: ...{video_result.get('token', '')[-30:]}")
    
    return True

if __name__ == "__main__":
    print("\n" + "=" * 60)
    print("  LIVEKIT CONNECTION TEST")
    print("=" * 60)
    
    success = test_livekit_connection()
    
    print("\n" + "=" * 60)
    if success:
        print("✅ ALL TESTS PASSED - LiveKit is ready!")
        print("\nYou can now:")
        print("1. Start a video call from the app")
        print("2. Test with real users")
        print("3. Monitor call quality")
    else:
        print("❌ TEST FAILED - Please check configuration")
        print("\nTroubleshooting:")
        print("1. Verify .env file has correct credentials")
        print("2. Restart backend: sudo supervisorctl restart backend")
        print("3. Check backend logs for errors")
    print("=" * 60 + "\n")
    
    sys.exit(0 if success else 1)
