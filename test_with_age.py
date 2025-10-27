#!/usr/bin/env python3
"""
Test profile creation with age data
"""

import requests
import json
import uuid

BASE_URL = "https://datemaps.preview.emergentagent.com/api"
HEADERS = {"Content-Type": "application/json"}

def test_with_age():
    # Create a user
    unique_id = str(uuid.uuid4())[:8]
    user_data = {
        "name": f"Age Test User {unique_id}",
        "email": f"agetest{unique_id}@pizoo.com",
        "phone_number": f"+41791234{unique_id[:4]}",
        "password": "AgeTest123!",
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
    
    # Update profile with GPS and age
    profile_data = {
        "display_name": "مستخدم اختبار العمر",
        "bio": "اختبار مع بيانات العمر",
        "date_of_birth": "1992-03-20",
        "age": 32,  # Explicitly set age
        "latitude": 47.5596,
        "longitude": 7.5886,
        "location": "Basel, Switzerland",
        "gender": "male",
        "interests": ["السفر", "التكنولوجيا"]
    }
    
    print("\n🔧 Updating profile with GPS and age...")
    response = requests.put(f"{BASE_URL}/profile/update", headers=auth_headers, json=profile_data, timeout=30)
    
    if response.status_code == 200:
        print("✅ Profile updated successfully")
        
        # Verify the update
        response = requests.get(f"{BASE_URL}/profile/me", headers=auth_headers, timeout=30)
        if response.status_code == 200:
            profile = response.json()
            print(f"Updated profile: {profile.get('display_name')}")
            print(f"Age: {profile.get('age')}")
            print(f"GPS coordinates: ({profile.get('latitude')}, {profile.get('longitude')})")
        
        # Create second user for discovery
        print("\n🔧 Creating second user for discovery test...")
        unique_id2 = str(uuid.uuid4())[:8]
        user_data2 = {
            "name": f"Discovery Age Test {unique_id2}",
            "email": f"discage{unique_id2}@pizoo.com",
            "phone_number": f"+41791235{unique_id2[:4]}",
            "password": "DiscAge123!",
            "terms_accepted": True
        }
        
        response = requests.post(f"{BASE_URL}/auth/register", headers=HEADERS, json=user_data2, timeout=30)
        if response.status_code == 200:
            reg_data2 = response.json()
            auth_token2 = reg_data2["access_token"]
            user_id2 = reg_data2["user"]["id"]
            
            auth_headers2 = HEADERS.copy()
            auth_headers2["Authorization"] = f"Bearer {auth_token2}"
            
            # Update second user profile with age
            profile_data2 = {
                "display_name": "مستخدم اكتشاف العمر",
                "age": 30,
                "latitude": 47.5500,
                "longitude": 7.5800,
                "location": "Near Basel, Switzerland",
                "gender": "female"
            }
            
            requests.put(f"{BASE_URL}/profile/update", headers=auth_headers2, json=profile_data2, timeout=30)
            
            # Test discovery
            print("\n🔧 Testing discovery with age data...")
            response = requests.get(f"{BASE_URL}/profiles/discover?limit=20", headers=auth_headers2, timeout=30)
            
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
                        print(f"  Age: {profile.get('age')}")
                        print(f"  Distance: {profile.get('distance')} km")
                        break
                
                if not found_first:
                    print("❌ First user NOT found in discovery")
                
                # Check profiles with age and GPS
                profiles_with_age = [p for p in profiles if p.get('age') is not None]
                profiles_with_gps = [p for p in profiles if p.get('latitude') is not None]
                
                print(f"Profiles with age: {len(profiles_with_age)}")
                print(f"Profiles with GPS: {len(profiles_with_gps)}")
                
                if profiles_with_gps:
                    print("GPS profiles found:")
                    for profile in profiles_with_gps:
                        print(f"  - {profile.get('display_name')}: Distance {profile.get('distance')} km")
                
            else:
                print(f"❌ Discovery failed: {response.status_code}")
    
    else:
        print(f"❌ Profile update failed: {response.status_code}")
        print(f"Response: {response.text}")

if __name__ == "__main__":
    test_with_age()