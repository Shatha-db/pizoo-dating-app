#!/usr/bin/env python3
"""
LiveKit Token Verification Test
Tests LiveKit token generation with a verified user
"""

import asyncio
import httpx
import os
import sys
import json
from datetime import datetime

# Add backend directory to path for imports
sys.path.append('/app/backend')

# Test configuration
BACKEND_URL = os.getenv('REACT_APP_BACKEND_URL', 'https://pizoo-rebrand.preview.emergentagent.com')
API_BASE = f"{BACKEND_URL}/api"

async def test_livekit_with_verified_user():
    """Test LiveKit token generation with a verified user"""
    
    async with httpx.AsyncClient(timeout=30.0) as client:
        print("🧪 Testing LiveKit Token Generation with Verified User")
        print("=" * 60)
        
        # Step 1: Create a new user via email verification
        print("📧 Step 1: Sending email verification...")
        email_data = {
            "email": f"verified_test_{int(datetime.now().timestamp())}@pizoo.ch",
            "name": "Verified Test User"
        }
        
        response = await client.post(f"{API_BASE}/auth/email/send-link", json=email_data)
        
        if response.status_code != 200:
            print(f"❌ Failed to send verification email: {response.status_code}")
            return
        
        print("✅ Verification email sent successfully")
        
        # Step 2: Extract token from backend logs (since we're in mock mode)
        print("🔍 Step 2: Extracting verification token from logs...")
        
        # Get the latest token from logs
        import subprocess
        result = subprocess.run(
            ["tail", "-n", "20", "/var/log/supervisor/backend.err.log"],
            capture_output=True, text=True
        )
        
        token = None
        for line in result.stdout.split('\n'):
            if "Token:" in line and email_data["email"] in result.stdout:
                token = line.split("Token: ")[1].strip()
                break
        
        if not token:
            print("❌ Could not extract verification token from logs")
            return
        
        print(f"✅ Extracted token: {token[:20]}...")
        
        # Step 3: Verify the email to create a verified user
        print("✅ Step 3: Verifying email...")
        
        verify_response = await client.post(
            f"{API_BASE}/auth/email/verify",
            json={"token": token}
        )
        
        if verify_response.status_code != 200:
            print(f"❌ Email verification failed: {verify_response.status_code}")
            print(verify_response.text)
            return
        
        verify_data = verify_response.json()
        access_token = verify_data.get('access_token')
        
        if not access_token:
            print("❌ No access token received from verification")
            return
        
        print("✅ Email verified successfully, user is now verified")
        
        # Step 4: Test LiveKit token generation
        print("🎥 Step 4: Testing LiveKit token generation...")
        
        headers = {"Authorization": f"Bearer {access_token}"}
        livekit_data = {
            "match_id": "verified_test_match_123",
            "call_type": "video"
        }
        
        livekit_response = await client.post(
            f"{API_BASE}/livekit/token",
            json=livekit_data,
            headers=headers
        )
        
        print(f"LiveKit Response Status: {livekit_response.status_code}")
        
        if livekit_response.status_code == 200:
            livekit_result = livekit_response.json()
            
            if livekit_result.get('success'):
                print("✅ LiveKit token generated successfully!")
                print(f"   Room: {livekit_result.get('room_name')}")
                print(f"   URL: {livekit_result.get('url')}")
                print(f"   Participant: {livekit_result.get('participant_identity')}")
                print(f"   Token length: {len(livekit_result.get('token', ''))}")
                
                # Verify token format (JWT should have 3 parts separated by dots)
                token_parts = livekit_result.get('token', '').split('.')
                if len(token_parts) == 3:
                    print("✅ Token format is valid JWT")
                else:
                    print("❌ Token format is invalid")
                
            else:
                print(f"❌ LiveKit token generation failed: {livekit_result}")
        
        elif livekit_response.status_code == 429:
            print("✅ Rate limiting is working (expected behavior)")
            
        else:
            print(f"❌ Unexpected response: {livekit_response.status_code}")
            print(livekit_response.text)
        
        print("=" * 60)
        print("🏁 LiveKit verification test completed")

if __name__ == "__main__":
    asyncio.run(test_livekit_with_verified_user())