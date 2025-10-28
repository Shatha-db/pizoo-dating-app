#!/usr/bin/env python3
"""
Debug GPS profile creation issues
"""

import requests
import json
import uuid

BASE_URL = "https://pizoo-chat-fix.preview.emergentagent.com/api"
HEADERS = {"Content-Type": "application/json"}

def test_profile_creation_debug():
    # Create a test user first
    unique_id = str(uuid.uuid4())[:8]
    user_data = {
        "name": f"Debug User {unique_id}",
        "email": f"debug{unique_id}@pizoo.com",
        "phone_number": f"+41791234{unique_id[:4]}",
        "password": "Debug123!",
        "terms_accepted": True
    }
    
    print("🔧 Creating test user...")
    response = requests.post(f"{BASE_URL}/auth/register", headers=HEADERS, json=user_data, timeout=30)
    
    if response.status_code != 200:
        print(f"❌ User registration failed: {response.status_code}")
        print(f"Response: {response.text}")
        return
    
    reg_data = response.json()
    auth_token = reg_data["access_token"]
    user_id = reg_data["user"]["id"]
    print(f"✅ User created: {user_id}")
    
    # Try to create profile with GPS coordinates
    auth_headers = HEADERS.copy()
    auth_headers["Authorization"] = f"Bearer {auth_token}"
    
    profile_data = {
        "display_name": "مستخدم تجريبي GPS",
        "bio": "اختبار الموقع الجغرافي",
        "date_of_birth": "1992-03-20",
        "gender": "male",
        "height": 175,
        "looking_for": "علاقة جدية",
        "interests": ["السفر", "التكنولوجيا"],
        "location": "Basel, Switzerland",
        "latitude": 47.5596,
        "longitude": 7.5886,
        "occupation": "مهندس",
        "relationship_goals": "serious",
        "languages": ["العربية", "الإنجليزية"]
    }
    
    print("\n🔧 Creating profile with GPS coordinates...")
    response = requests.post(f"{BASE_URL}/profile/create", headers=auth_headers, json=profile_data, timeout=30)
    
    print(f"Status Code: {response.status_code}")
    print(f"Response: {response.text}")
    
    if response.status_code == 400:
        print("\n🔧 Trying profile update instead...")
        response = requests.put(f"{BASE_URL}/profile/update", headers=auth_headers, json=profile_data, timeout=30)
        print(f"Update Status Code: {response.status_code}")
        print(f"Update Response: {response.text}")
        
        if response.status_code == 200:
            print("\n🔧 Checking profile after update...")
            response = requests.get(f"{BASE_URL}/profile/me", headers=auth_headers, timeout=30)
            print(f"Get Profile Status: {response.status_code}")
            if response.status_code == 200:
                profile = response.json()
                print(f"Latitude: {profile.get('latitude')}")
                print(f"Longitude: {profile.get('longitude')}")
                print(f"Location: {profile.get('location')}")
    
    # Test discovery endpoint
    print("\n🔧 Testing discovery endpoint...")
    response = requests.get(f"{BASE_URL}/profiles/discover?limit=5", headers=auth_headers, timeout=30)
    print(f"Discovery Status: {response.status_code}")
    if response.status_code == 200:
        data = response.json()
        profiles = data.get("profiles", [])
        print(f"Found {len(profiles)} profiles")
        for i, profile in enumerate(profiles[:2]):
            print(f"Profile {i+1}:")
            print(f"  - Name: {profile.get('display_name', 'N/A')}")
            print(f"  - Distance: {profile.get('distance', 'N/A')}")
            print(f"  - Latitude: {profile.get('latitude', 'N/A')}")
            print(f"  - Longitude: {profile.get('longitude', 'N/A')}")

if __name__ == "__main__":
    test_profile_creation_debug()