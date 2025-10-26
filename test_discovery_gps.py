#!/usr/bin/env python3
"""
Test discovery endpoint with GPS profiles
"""

import requests
import json
import uuid

BASE_URL = "https://dating-ui-refresh.preview.emergentagent.com/api"
HEADERS = {"Content-Type": "application/json"}

def test_discovery_with_gps():
    # Create a test user with Basel coordinates
    unique_id = str(uuid.uuid4())[:8]
    user_data = {
        "name": f"Discovery Test User {unique_id}",
        "email": f"discovery{unique_id}@pizoo.com",
        "phone_number": f"+41791234{unique_id[:4]}",
        "password": "Discovery123!",
        "terms_accepted": True
    }
    
    print("🔧 Creating test user for discovery...")
    response = requests.post(f"{BASE_URL}/auth/register", headers=HEADERS, json=user_data, timeout=30)
    
    if response.status_code != 200:
        print(f"❌ User registration failed: {response.status_code}")
        return
    
    reg_data = response.json()
    auth_token = reg_data["access_token"]
    user_id = reg_data["user"]["id"]
    print(f"✅ User created: {user_id}")
    
    # Update profile with Basel coordinates
    auth_headers = HEADERS.copy()
    auth_headers["Authorization"] = f"Bearer {auth_token}"
    
    profile_data = {
        "display_name": "مستخدم اكتشاف GPS",
        "bio": "اختبار اكتشاف المواقع الجغرافية",
        "date_of_birth": "1992-03-20",
        "gender": "male",
        "height": 175,
        "looking_for": "علاقة جدية",
        "interests": ["السفر", "التكنولوجيا"],
        "location": "Basel, Switzerland",
        "latitude": 47.5596,  # Basel coordinates
        "longitude": 7.5886,
        "occupation": "مهندس",
        "relationship_goals": "serious",
        "languages": ["العربية", "الإنجليزية"]
    }
    
    print("\n🔧 Updating profile with GPS coordinates...")
    response = requests.put(f"{BASE_URL}/profile/update", headers=auth_headers, json=profile_data, timeout=30)
    
    if response.status_code != 200:
        print(f"❌ Profile update failed: {response.status_code}")
        return
    
    print("✅ Profile updated with GPS coordinates")
    
    # Test discovery without distance filter
    print("\n🔧 Testing discovery without distance filter...")
    response = requests.get(f"{BASE_URL}/profiles/discover?limit=10", headers=auth_headers, timeout=30)
    
    if response.status_code == 200:
        data = response.json()
        profiles = data.get("profiles", [])
        print(f"Found {len(profiles)} profiles")
        
        profiles_with_distance = 0
        for i, profile in enumerate(profiles):
            print(f"\nProfile {i+1}:")
            print(f"  - Name: {profile.get('display_name', 'N/A')}")
            print(f"  - Location: {profile.get('location', 'N/A')}")
            print(f"  - Distance: {profile.get('distance', 'N/A')} km")
            print(f"  - Latitude: {profile.get('latitude', 'N/A')}")
            print(f"  - Longitude: {profile.get('longitude', 'N/A')}")
            
            if profile.get('distance') is not None:
                profiles_with_distance += 1
        
        print(f"\n📊 Profiles with distance data: {profiles_with_distance}/{len(profiles)}")
    else:
        print(f"❌ Discovery failed: {response.status_code}")
        print(f"Response: {response.text}")
    
    # Test discovery with distance filter
    print("\n🔧 Testing discovery with 50km distance filter...")
    response = requests.get(f"{BASE_URL}/profiles/discover?max_distance=50&limit=10", headers=auth_headers, timeout=30)
    
    if response.status_code == 200:
        data = response.json()
        profiles = data.get("profiles", [])
        print(f"Found {len(profiles)} profiles within 50km")
        
        for i, profile in enumerate(profiles):
            distance = profile.get('distance', 'N/A')
            print(f"  Profile {i+1}: {profile.get('display_name', 'N/A')} - {distance} km")
    else:
        print(f"❌ Distance filtered discovery failed: {response.status_code}")
        print(f"Response: {response.text}")

if __name__ == "__main__":
    test_discovery_with_gps()