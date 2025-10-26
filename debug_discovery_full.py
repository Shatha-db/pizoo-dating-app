#!/usr/bin/env python3
"""
Debug discovery with full profile list
"""

import requests
import json
import uuid

BASE_URL = "https://dating-ui-refresh.preview.emergentagent.com/api"
HEADERS = {"Content-Type": "application/json"}

def debug_discovery_full():
    # Create a test user
    unique_id = str(uuid.uuid4())[:8]
    user_data = {
        "name": f"Debug Full User {unique_id}",
        "email": f"debugfull{unique_id}@pizoo.com",
        "phone_number": f"+41791234{unique_id[:4]}",
        "password": "DebugFull123!",
        "terms_accepted": True
    }
    
    print("🔧 Creating test user...")
    response = requests.post(f"{BASE_URL}/auth/register", headers=HEADERS, json=user_data, timeout=30)
    
    if response.status_code != 200:
        print(f"❌ User registration failed: {response.status_code}")
        return
    
    reg_data = response.json()
    auth_token = reg_data["access_token"]
    
    auth_headers = HEADERS.copy()
    auth_headers["Authorization"] = f"Bearer {auth_token}"
    
    # Update profile with GPS coordinates
    profile_data = {
        "display_name": "مستخدم تصحيح شامل",
        "latitude": 47.5596,
        "longitude": 7.5886,
        "location": "Basel, Switzerland"
    }
    
    requests.put(f"{BASE_URL}/profile/update", headers=auth_headers, json=profile_data, timeout=30)
    
    # Get ALL profiles with high limit
    print("\n🔧 Getting all profiles with limit=100...")
    response = requests.get(f"{BASE_URL}/profiles/discover?limit=100", headers=auth_headers, timeout=30)
    
    if response.status_code == 200:
        data = response.json()
        profiles = data.get("profiles", [])
        print(f"Total profiles: {len(profiles)}")
        
        # Group profiles by characteristics
        gps_profiles = []
        non_gps_profiles = []
        recent_profiles = []
        
        target_names = ["أحمد القريب", "فاطمة الضواحي", "محمد زيورخ", "سارة ميونخ", 
                       "مستخدم مسافة 1", "مستخدم مسافة 2", "مستخدم تحقق GPS"]
        
        for profile in profiles:
            if profile.get('latitude') is not None and profile.get('longitude') is not None:
                gps_profiles.append(profile)
            else:
                non_gps_profiles.append(profile)
            
            if profile.get('display_name') in target_names:
                recent_profiles.append(profile)
        
        print(f"Profiles with GPS: {len(gps_profiles)}")
        print(f"Profiles without GPS: {len(non_gps_profiles)}")
        print(f"Our test profiles found: {len(recent_profiles)}")
        
        if gps_profiles:
            print("\n📍 GPS Profiles found:")
            for i, profile in enumerate(gps_profiles):
                print(f"  {i+1}. {profile.get('display_name', 'N/A')}")
                print(f"     Location: {profile.get('location', 'N/A')}")
                print(f"     Coordinates: ({profile.get('latitude')}, {profile.get('longitude')})")
                print(f"     Distance: {profile.get('distance', 'N/A')} km")
        
        if recent_profiles:
            print("\n🎯 Our test profiles:")
            for profile in recent_profiles:
                print(f"  - {profile.get('display_name')}: {profile.get('location', 'N/A')}")
        
        # Check if distance calculation is working for GPS profiles
        if gps_profiles:
            print(f"\n📏 Distance calculation status:")
            with_distance = [p for p in gps_profiles if p.get('distance') is not None]
            print(f"GPS profiles with distance: {len(with_distance)}/{len(gps_profiles)}")
        
    else:
        print(f"❌ Discovery failed: {response.status_code}")
        print(f"Response: {response.text}")

if __name__ == "__main__":
    debug_discovery_full()