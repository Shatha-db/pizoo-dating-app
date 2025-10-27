#!/usr/bin/env python3
"""
Check if GPS profiles exist in discovery
"""

import requests
import json
import uuid

BASE_URL = "https://phone-auth-2.preview.emergentagent.com/api"
HEADERS = {"Content-Type": "application/json"}

def check_gps_profiles():
    # Create a test user
    unique_id = str(uuid.uuid4())[:8]
    user_data = {
        "name": f"Check User {unique_id}",
        "email": f"check{unique_id}@pizoo.com",
        "phone_number": f"+41791234{unique_id[:4]}",
        "password": "Check123!",
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
    
    # Get more profiles to see if GPS ones are there
    print("\n🔧 Checking all available profiles...")
    response = requests.get(f"{BASE_URL}/profiles/discover?limit=50", headers=auth_headers, timeout=30)
    
    if response.status_code == 200:
        data = response.json()
        profiles = data.get("profiles", [])
        print(f"Total profiles found: {len(profiles)}")
        
        gps_profiles = []
        for profile in profiles:
            if profile.get('latitude') is not None and profile.get('longitude') is not None:
                gps_profiles.append(profile)
        
        print(f"Profiles with GPS coordinates: {len(gps_profiles)}")
        
        for i, profile in enumerate(gps_profiles):
            print(f"\nGPS Profile {i+1}:")
            print(f"  - Name: {profile.get('display_name', 'N/A')}")
            print(f"  - Location: {profile.get('location', 'N/A')}")
            print(f"  - Latitude: {profile.get('latitude', 'N/A')}")
            print(f"  - Longitude: {profile.get('longitude', 'N/A')}")
            print(f"  - Distance: {profile.get('distance', 'N/A')}")
        
        # Look for specific names we created
        target_names = ["أحمد القريب", "فاطمة الضواحي", "محمد زيورخ", "سارة ميونخ"]
        found_names = []
        
        for profile in profiles:
            if profile.get('display_name') in target_names:
                found_names.append(profile.get('display_name'))
        
        print(f"\nFound our test profiles: {found_names}")
        
    else:
        print(f"❌ Discovery failed: {response.status_code}")
        print(f"Response: {response.text}")

if __name__ == "__main__":
    check_gps_profiles()