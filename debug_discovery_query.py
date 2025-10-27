#!/usr/bin/env python3
"""
Debug the discovery query by checking what's being filtered
"""

import requests
import json
import uuid

BASE_URL = "https://datemaps.preview.emergentagent.com/api"
HEADERS = {"Content-Type": "application/json"}

def debug_discovery_query():
    # Create a user
    unique_id = str(uuid.uuid4())[:8]
    user_data = {
        "name": f"Debug Query User {unique_id}",
        "email": f"debugquery{unique_id}@pizoo.com",
        "phone_number": f"+41791234{unique_id[:4]}",
        "password": "DebugQuery123!",
        "terms_accepted": True
    }
    
    print("🔧 Creating user...")
    response = requests.post(f"{BASE_URL}/auth/register", headers=HEADERS, json=user_data, timeout=30)
    
    if response.status_code != 200:
        print(f"❌ User registration failed: {response.status_code}")
        return
    
    reg_data = response.json()
    auth_token = reg_data["access_token"]
    user_id = reg_data["user"]["id"]
    
    auth_headers = HEADERS.copy()
    auth_headers["Authorization"] = f"Bearer {auth_token}"
    
    print(f"✅ User created with ID: {user_id}")
    
    # Update profile
    profile_data = {
        "display_name": "مستخدم تصحيح الاستعلام",
        "age": 30,
        "latitude": 47.5596,
        "longitude": 7.5886,
        "location": "Basel, Switzerland",
        "gender": "male"
    }
    
    requests.put(f"{BASE_URL}/profile/update", headers=auth_headers, json=profile_data, timeout=30)
    
    # Test discovery with different parameters
    test_cases = [
        {"params": "limit=100", "desc": "High limit"},
        {"params": "limit=100&min_age=18&max_age=50", "desc": "Age range 18-50"},
        {"params": "limit=100&gender=female", "desc": "Female only"},
        {"params": "limit=100&max_distance=1000", "desc": "Large distance"},
    ]
    
    for test_case in test_cases:
        print(f"\n🔧 Testing discovery: {test_case['desc']}")
        response = requests.get(f"{BASE_URL}/profiles/discover?{test_case['params']}", headers=auth_headers, timeout=30)
        
        if response.status_code == 200:
            data = response.json()
            profiles = data.get("profiles", [])
            
            # Count different types of profiles
            with_age = len([p for p in profiles if p.get('age') is not None])
            with_gps = len([p for p in profiles if p.get('latitude') is not None])
            with_distance = len([p for p in profiles if p.get('distance') is not None])
            
            print(f"  Total: {len(profiles)}, Age: {with_age}, GPS: {with_gps}, Distance: {with_distance}")
            
            # Look for recent profiles (created today)
            recent_profiles = []
            for profile in profiles:
                name = profile.get('display_name', '')
                if any(keyword in name for keyword in ['اختبار', 'تجريبي', 'فحص', 'تصحيح', 'مسافة', 'عمر']):
                    recent_profiles.append(profile)
            
            if recent_profiles:
                print(f"  Recent test profiles found: {len(recent_profiles)}")
                for profile in recent_profiles:
                    print(f"    - {profile.get('display_name')}: Age {profile.get('age')}, Distance {profile.get('distance')}")
            else:
                print(f"  No recent test profiles found")
        else:
            print(f"  ❌ Failed: {response.status_code}")
    
    # Check if there are any swipes or blocks for this user
    print(f"\n🔧 Checking if user has any swipes or blocks...")
    
    # This is just to see what the discovery endpoint returns
    # We can't directly query swipes/blocks without additional endpoints

if __name__ == "__main__":
    debug_discovery_query()