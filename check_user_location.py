#!/usr/bin/env python3
"""
Check if test user has GPS coordinates
"""

import requests
import json

# Configuration
BACKEND_URL = "https://pizoo-dating-3.preview.emergentagent.com/api"

def get_auth_token():
    """Get authentication token"""
    login_data = {
        "email": "ahmed.test@example.com",
        "password": "TestPass123!"
    }
    response = requests.post(f"{BACKEND_URL}/auth/login", json=login_data)
    if response.status_code == 200:
        return response.json()["access_token"]
    return None

def check_user_profile(token):
    """Check user profile for GPS coordinates"""
    headers = {"Authorization": f"Bearer {token}"}
    response = requests.get(f"{BACKEND_URL}/profile/me", headers=headers)
    
    if response.status_code == 200:
        profile = response.json()
        print("📍 User Profile Location Data:")
        print(f"   Location: {profile.get('location', 'Not set')}")
        print(f"   Latitude: {profile.get('latitude', 'Not set')}")
        print(f"   Longitude: {profile.get('longitude', 'Not set')}")
        
        if profile.get('latitude') and profile.get('longitude'):
            print("✅ User has GPS coordinates - near_you section should appear")
        else:
            print("❌ User missing GPS coordinates - near_you section will not appear")
            
        return profile.get('latitude') and profile.get('longitude')
    else:
        print(f"❌ Failed to get profile: {response.status_code}")
        return False

def add_location_to_user(token):
    """Add GPS coordinates to user profile"""
    headers = {"Authorization": f"Bearer {token}"}
    
    # Add Basel, Switzerland coordinates
    update_data = {
        "location": "Basel, Switzerland",
        "latitude": 47.5596,
        "longitude": 7.5886
    }
    
    response = requests.put(f"{BACKEND_URL}/profile/update", json=update_data, headers=headers)
    
    if response.status_code == 200:
        print("✅ Added GPS coordinates to user profile")
        return True
    else:
        print(f"❌ Failed to update profile: {response.status_code} - {response.text}")
        return False

def main():
    token = get_auth_token()
    if not token:
        print("❌ Failed to authenticate")
        return
    
    has_location = check_user_profile(token)
    
    if not has_location:
        print("\n🔧 Adding GPS coordinates to enable near_you section...")
        if add_location_to_user(token):
            print("✅ Location added successfully")
            check_user_profile(token)
        else:
            print("❌ Failed to add location")

if __name__ == "__main__":
    main()