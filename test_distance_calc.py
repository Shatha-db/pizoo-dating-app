#!/usr/bin/env python3
"""
Test distance calculation directly
"""

import requests
import json
import uuid

BASE_URL = "https://datemaps.preview.emergentagent.com/api"
HEADERS = {"Content-Type": "application/json"}

def test_distance_calculation():
    # Create two users with known coordinates
    users = []
    
    for i in range(2):
        unique_id = str(uuid.uuid4())[:8]
        user_data = {
            "name": f"Distance Test User {i+1}",
            "email": f"disttest{i+1}{unique_id}@pizoo.com",
            "phone_number": f"+41791{i+1:03d}{unique_id[:4]}",
            "password": "DistTest123!",
            "terms_accepted": True
        }
        
        print(f"🔧 Creating user {i+1}...")
        response = requests.post(f"{BASE_URL}/auth/register", headers=HEADERS, json=user_data, timeout=30)
        
        if response.status_code != 200:
            print(f"❌ User {i+1} registration failed: {response.status_code}")
            continue
        
        reg_data = response.json()
        auth_token = reg_data["access_token"]
        user_id = reg_data["user"]["id"]
        
        # Set coordinates - User 1 in Basel, User 2 nearby
        coordinates = [
            {"lat": 47.5596, "lon": 7.5886, "location": "Basel, Switzerland"},  # User 1
            {"lat": 47.5500, "lon": 7.5800, "location": "Near Basel, Switzerland"}  # User 2 (~2km away)
        ]
        
        profile_data = {
            "display_name": f"مستخدم مسافة {i+1}",
            "bio": f"اختبار حساب المسافة - المستخدم {i+1}",
            "latitude": coordinates[i]["lat"],
            "longitude": coordinates[i]["lon"],
            "location": coordinates[i]["location"],
            "gender": "male" if i == 0 else "female",
            "interests": ["السفر", "التكنولوجيا"]
        }
        
        auth_headers = HEADERS.copy()
        auth_headers["Authorization"] = f"Bearer {auth_token}"
        
        print(f"🔧 Updating profile for user {i+1} with coordinates...")
        response = requests.put(f"{BASE_URL}/profile/update", headers=auth_headers, json=profile_data, timeout=30)
        
        if response.status_code == 200:
            print(f"✅ User {i+1} profile updated")
            users.append({
                "user_id": user_id,
                "auth_token": auth_token,
                "coordinates": coordinates[i]
            })
        else:
            print(f"❌ User {i+1} profile update failed: {response.status_code}")
    
    if len(users) < 2:
        print("❌ Need at least 2 users for distance testing")
        return
    
    # Test discovery from user 1 to see user 2
    print(f"\n🔧 Testing discovery from user 1...")
    auth_headers = HEADERS.copy()
    auth_headers["Authorization"] = f"Bearer {users[0]['auth_token']}"
    
    # Test without distance filter first
    response = requests.get(f"{BASE_URL}/profiles/discover?limit=20", headers=auth_headers, timeout=30)
    
    if response.status_code == 200:
        data = response.json()
        profiles = data.get("profiles", [])
        print(f"Discovery returned {len(profiles)} profiles")
        
        # Look for user 2
        found_user2 = False
        for profile in profiles:
            if profile.get('user_id') == users[1]['user_id']:
                found_user2 = True
                print(f"✅ Found user 2 in discovery!")
                print(f"  - Name: {profile.get('display_name')}")
                print(f"  - Distance: {profile.get('distance')} km")
                print(f"  - Latitude: {profile.get('latitude')}")
                print(f"  - Longitude: {profile.get('longitude')}")
                break
        
        if not found_user2:
            print("❌ User 2 not found in discovery")
            # Show what profiles were returned
            print("Returned profiles:")
            for i, profile in enumerate(profiles[:5]):
                print(f"  {i+1}. {profile.get('display_name', 'N/A')} - Distance: {profile.get('distance', 'N/A')}")
        
        # Count profiles with distance
        profiles_with_distance = [p for p in profiles if p.get('distance') is not None]
        print(f"Profiles with distance data: {len(profiles_with_distance)}/{len(profiles)}")
        
    else:
        print(f"❌ Discovery failed: {response.status_code}")
        print(f"Response: {response.text}")

if __name__ == "__main__":
    test_distance_calculation()