#!/usr/bin/env python3
"""
Check if profiles exist by accessing them directly
"""

import requests
import json
import uuid

BASE_URL = "https://pizoo-dating-3.preview.emergentagent.com/api"
HEADERS = {"Content-Type": "application/json"}

def check_profile_direct():
    # Create a user and immediately check if it appears in discovery
    unique_id = str(uuid.uuid4())[:8]
    user_data = {
        "name": f"Direct Check User {unique_id}",
        "email": f"directcheck{unique_id}@pizoo.com",
        "phone_number": f"+41791234{unique_id[:4]}",
        "password": "DirectCheck123!",
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
    
    # Check initial profile
    print("\n🔧 Checking initial profile...")
    response = requests.get(f"{BASE_URL}/profile/me", headers=auth_headers, timeout=30)
    if response.status_code == 200:
        profile = response.json()
        print(f"Initial profile exists: {profile.get('display_name', 'N/A')}")
    
    # Update profile with GPS
    profile_data = {
        "display_name": "مستخدم فحص مباشر",
        "bio": "اختبار الفحص المباشر للملف الشخصي",
        "latitude": 47.5596,
        "longitude": 7.5886,
        "location": "Basel, Switzerland",
        "gender": "male",
        "interests": ["السفر", "التكنولوجيا"]
    }
    
    print("\n🔧 Updating profile with GPS...")
    response = requests.put(f"{BASE_URL}/profile/update", headers=auth_headers, json=profile_data, timeout=30)
    
    if response.status_code == 200:
        print("✅ Profile updated successfully")
        
        # Verify the update
        response = requests.get(f"{BASE_URL}/profile/me", headers=auth_headers, timeout=30)
        if response.status_code == 200:
            profile = response.json()
            print(f"Updated profile: {profile.get('display_name')}")
            print(f"GPS coordinates: ({profile.get('latitude')}, {profile.get('longitude')})")
        
        # Now create a second user to test discovery
        print("\n🔧 Creating second user for discovery test...")
        unique_id2 = str(uuid.uuid4())[:8]
        user_data2 = {
            "name": f"Discovery Test User {unique_id2}",
            "email": f"disctest{unique_id2}@pizoo.com",
            "phone_number": f"+41791235{unique_id2[:4]}",
            "password": "DiscTest123!",
            "terms_accepted": True
        }
        
        response = requests.post(f"{BASE_URL}/auth/register", headers=HEADERS, json=user_data2, timeout=30)
        if response.status_code == 200:
            reg_data2 = response.json()
            auth_token2 = reg_data2["access_token"]
            user_id2 = reg_data2["user"]["id"]
            
            auth_headers2 = HEADERS.copy()
            auth_headers2["Authorization"] = f"Bearer {auth_token2}"
            
            # Update second user profile
            profile_data2 = {
                "display_name": "مستخدم اكتشاف ثاني",
                "latitude": 47.5500,
                "longitude": 7.5800,
                "location": "Near Basel, Switzerland",
                "gender": "female"
            }
            
            requests.put(f"{BASE_URL}/profile/update", headers=auth_headers2, json=profile_data2, timeout=30)
            
            # Test discovery immediately
            print("\n🔧 Testing discovery immediately after creation...")
            response = requests.get(f"{BASE_URL}/profiles/discover?limit=50", headers=auth_headers2, timeout=30)
            
            if response.status_code == 200:
                data = response.json()
                profiles = data.get("profiles", [])
                print(f"Discovery found {len(profiles)} profiles")
                
                # Look for first user
                found_first = False
                for profile in profiles:
                    if profile.get('user_id') == user_id:
                        found_first = True
                        print(f"✅ Found first user in discovery!")
                        print(f"  Name: {profile.get('display_name')}")
                        print(f"  Distance: {profile.get('distance')} km")
                        break
                
                if not found_first:
                    print("❌ First user NOT found in discovery")
                    
                    # Show some profiles that were found
                    print("Sample profiles found:")
                    for i, profile in enumerate(profiles[:5]):
                        print(f"  {i+1}. {profile.get('display_name', 'N/A')} (User: {profile.get('user_id', 'N/A')[:8]}...)")
                
                # Check GPS profiles
                gps_profiles = [p for p in profiles if p.get('latitude') is not None]
                print(f"Profiles with GPS coordinates: {len(gps_profiles)}")
                
            else:
                print(f"❌ Discovery failed: {response.status_code}")
    
    else:
        print(f"❌ Profile update failed: {response.status_code}")
        print(f"Response: {response.text}")

if __name__ == "__main__":
    check_profile_direct()