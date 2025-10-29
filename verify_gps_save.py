#!/usr/bin/env python3
"""
Verify GPS coordinates are being saved correctly
"""

import requests
import json
import uuid

BASE_URL = "https://dating-app-bugfix.preview.emergentagent.com/api"
HEADERS = {"Content-Type": "application/json"}

def verify_gps_save():
    # Create a test user
    unique_id = str(uuid.uuid4())[:8]
    user_data = {
        "name": f"Verify User {unique_id}",
        "email": f"verify{unique_id}@pizoo.com",
        "phone_number": f"+41791234{unique_id[:4]}",
        "password": "Verify123!",
        "terms_accepted": True
    }
    
    print("🔧 Creating test user...")
    response = requests.post(f"{BASE_URL}/auth/register", headers=HEADERS, json=user_data, timeout=30)
    
    if response.status_code != 200:
        print(f"❌ User registration failed: {response.status_code}")
        return
    
    reg_data = response.json()
    auth_token = reg_data["access_token"]
    user_id = reg_data["user"]["id"]
    
    auth_headers = HEADERS.copy()
    auth_headers["Authorization"] = f"Bearer {auth_token}"
    
    # Update profile with GPS coordinates
    profile_data = {
        "display_name": "مستخدم تحقق GPS",
        "bio": "اختبار حفظ الإحداثيات",
        "latitude": 47.5596,  # Basel coordinates
        "longitude": 7.5886,
        "location": "Basel, Switzerland"
    }
    
    print("\n🔧 Updating profile with GPS coordinates...")
    response = requests.put(f"{BASE_URL}/profile/update", headers=auth_headers, json=profile_data, timeout=30)
    
    if response.status_code == 200:
        print("✅ Profile update successful")
        update_data = response.json()
        profile = update_data.get("profile", {})
        print(f"Returned latitude: {profile.get('latitude')}")
        print(f"Returned longitude: {profile.get('longitude')}")
    else:
        print(f"❌ Profile update failed: {response.status_code}")
        print(f"Response: {response.text}")
        return
    
    # Get profile to verify
    print("\n🔧 Getting profile to verify GPS coordinates...")
    response = requests.get(f"{BASE_URL}/profile/me", headers=auth_headers, timeout=30)
    
    if response.status_code == 200:
        profile = response.json()
        print("✅ Profile retrieved successfully")
        print(f"Stored latitude: {profile.get('latitude')}")
        print(f"Stored longitude: {profile.get('longitude')}")
        print(f"Location: {profile.get('location')}")
        
        # Check if coordinates are properly stored
        if profile.get('latitude') == 47.5596 and profile.get('longitude') == 7.5886:
            print("✅ GPS coordinates saved correctly!")
            
            # Now create another user to test discovery
            print("\n🔧 Creating second user to test discovery...")
            unique_id2 = str(uuid.uuid4())[:8]
            user_data2 = {
                "name": f"Discovery User {unique_id2}",
                "email": f"disc{unique_id2}@pizoo.com",
                "phone_number": f"+41791235{unique_id2[:4]}",
                "password": "Disc123!",
                "terms_accepted": True
            }
            
            response = requests.post(f"{BASE_URL}/auth/register", headers=HEADERS, json=user_data2, timeout=30)
            if response.status_code == 200:
                reg_data2 = response.json()
                auth_token2 = reg_data2["access_token"]
                
                auth_headers2 = HEADERS.copy()
                auth_headers2["Authorization"] = f"Bearer {auth_token2}"
                
                # Update second user profile with nearby coordinates
                profile_data2 = {
                    "display_name": "مستخدم اكتشاف",
                    "latitude": 47.5500,  # Nearby Basel
                    "longitude": 7.5800,
                    "location": "Near Basel, Switzerland"
                }
                
                requests.put(f"{BASE_URL}/profile/update", headers=auth_headers2, json=profile_data2, timeout=30)
                
                # Test discovery from second user
                print("\n🔧 Testing discovery from second user...")
                response = requests.get(f"{BASE_URL}/profiles/discover?limit=10", headers=auth_headers2, timeout=30)
                
                if response.status_code == 200:
                    data = response.json()
                    profiles = data.get("profiles", [])
                    print(f"Discovery found {len(profiles)} profiles")
                    
                    # Look for our first user
                    found_first_user = False
                    for profile in profiles:
                        if profile.get('user_id') == user_id:
                            found_first_user = True
                            print(f"✅ Found first user in discovery!")
                            print(f"  - Distance: {profile.get('distance')} km")
                            break
                    
                    if not found_first_user:
                        print("❌ First user not found in discovery results")
                        
                    # Check if any profiles have distance
                    profiles_with_distance = [p for p in profiles if p.get('distance') is not None]
                    print(f"Profiles with distance: {len(profiles_with_distance)}")
                    
                else:
                    print(f"❌ Discovery failed: {response.status_code}")
            
        else:
            print("❌ GPS coordinates not saved correctly")
    else:
        print(f"❌ Failed to get profile: {response.status_code}")

if __name__ == "__main__":
    verify_gps_save()