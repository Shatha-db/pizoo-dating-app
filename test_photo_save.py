"""
Test script to verify profile photo save functionality
"""
import requests
import json

BACKEND_URL = "http://localhost:8001"  # Internal backend URL

# Test data
test_email = "test_photo_user@example.com"
test_password = "TestPassword123"

print("=" * 60)
print("Testing Profile Photo Save Functionality")
print("=" * 60)

# Step 1: Register or login
print("\n1. Attempting to login/register...")
try:
    login_response = requests.post(
        f"{BACKEND_URL}/api/auth/login",
        json={"email": test_email, "password": test_password}
    )
    
    if login_response.status_code == 401:
        print("   User doesn't exist, registering...")
        register_response = requests.post(
            f"{BACKEND_URL}/api/auth/register",
            json={
                "name": "Test Photo User",
                "email": test_email,
                "phone_number": "+1234567890",
                "password": test_password,
                "terms_accepted": True
            }
        )
        register_response.raise_for_status()
        token = register_response.json()["access_token"]
        print("   ✅ User registered successfully")
    else:
        login_response.raise_for_status()
        token = login_response.json()["access_token"]
        print("   ✅ User logged in successfully")
    
except Exception as e:
    print(f"   ❌ Error: {e}")
    exit(1)

# Step 2: Update profile with photos
print("\n2. Updating profile with test photos...")
test_photos = [
    "https://images.unsplash.com/photo-1507003211169-0a1dd7228f2d?w=400",
    "https://images.unsplash.com/photo-1500648767791-00dcc994a43e?w=400",
    "https://images.unsplash.com/photo-1506794778202-cad84cf45f1d?w=400"
]

try:
    update_response = requests.put(
        f"{BACKEND_URL}/api/profile/update",
        json={
            "display_name": "Test User",
            "photos": test_photos,
            "primary_photo_index": 0,
            "bio": "Test bio for photo functionality",
            "interests": ["Photography", "Testing"]
        },
        headers={"Authorization": f"Bearer {token}"}
    )
    update_response.raise_for_status()
    print("   ✅ Profile updated successfully")
    print(f"   Response: {update_response.json()}")
except Exception as e:
    print(f"   ❌ Error: {e}")
    if hasattr(e, 'response'):
        print(f"   Response: {e.response.text}")
    exit(1)

# Step 3: Fetch profile to verify photos are saved
print("\n3. Fetching profile to verify photos...")
try:
    profile_response = requests.get(
        f"{BACKEND_URL}/api/profile/me",
        headers={"Authorization": f"Bearer {token}"}
    )
    profile_response.raise_for_status()
    profile = profile_response.json()
    
    if profile.get('photos'):
        print(f"   ✅ Photos saved! Count: {len(profile['photos'])}")
        print(f"   Photos: {profile['photos']}")
        print(f"   Primary index: {profile.get('primary_photo_index', 0)}")
    else:
        print("   ❌ No photos found in profile!")
        
except Exception as e:
    print(f"   ❌ Error: {e}")
    exit(1)

# Step 4: Logout and re-login to verify persistence
print("\n4. Testing persistence after re-login...")
try:
    # Simulate new session
    new_login_response = requests.post(
        f"{BACKEND_URL}/api/auth/login",
        json={"email": test_email, "password": test_password}
    )
    new_login_response.raise_for_status()
    new_token = new_login_response.json()["access_token"]
    
    # Fetch profile again
    new_profile_response = requests.get(
        f"{BACKEND_URL}/api/profile/me",
        headers={"Authorization": f"Bearer {new_token}"}
    )
    new_profile_response.raise_for_status()
    new_profile = new_profile_response.json()
    
    if new_profile.get('photos') and len(new_profile['photos']) == len(test_photos):
        print(f"   ✅ Photos persisted after re-login! Count: {len(new_profile['photos'])}")
        print(f"   ✅ All tests passed!")
    else:
        print(f"   ❌ Photos not persisted correctly!")
        print(f"   Expected: {len(test_photos)} photos")
        print(f"   Got: {len(new_profile.get('photos', []))} photos")
        
except Exception as e:
    print(f"   ❌ Error: {e}")
    exit(1)

print("\n" + "=" * 60)
print("Test completed!")
print("=" * 60)
