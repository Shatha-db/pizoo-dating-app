#!/usr/bin/env python3
"""
Create test profiles with GPS coordinates for testing
"""

import requests
import json
import uuid

BASE_URL = "https://pizoo-dating-1.preview.emergentagent.com/api"
HEADERS = {"Content-Type": "application/json"}

def create_gps_test_profiles():
    """Create test profiles with different GPS locations"""
    
    test_locations = [
        {
            "name": "Profile A - Nearby Basel",
            "display_name": "أحمد القريب",
            "latitude": 47.5500,  # ~2km from Basel center
            "longitude": 7.5800,
            "location": "Near Basel, Switzerland",
            "bio": "مهندس يعيش بالقرب من بازل"
        },
        {
            "name": "Profile B - Basel Suburbs", 
            "display_name": "فاطمة الضواحي",
            "latitude": 47.6000,  # ~10km from Basel
            "longitude": 7.6500,
            "location": "Basel Suburbs, Switzerland",
            "bio": "طبيبة تعيش في ضواحي بازل"
        },
        {
            "name": "Profile C - Zurich",
            "display_name": "محمد زيورخ",
            "latitude": 47.3769,  # Zurich ~85km
            "longitude": 8.5417,
            "location": "Zurich, Switzerland", 
            "bio": "مبرمج يعيش في زيورخ"
        },
        {
            "name": "Profile D - Munich Far",
            "display_name": "سارة ميونخ",
            "latitude": 48.1351,  # Munich, Germany ~250km
            "longitude": 11.5820,
            "location": "Munich, Germany",
            "bio": "مصممة تعيش في ميونخ"
        }
    ]
    
    created_profiles = []
    
    for i, location_data in enumerate(test_locations):
        print(f"\n🔧 Creating {location_data['name']}...")
        
        # Create a user for this profile
        unique_id = str(uuid.uuid4())[:8]
        user_data = {
            "name": f"GPS Test User {i+1}",
            "email": f"gpstest{i+1}{unique_id}@pizoo.com",
            "phone_number": f"+41791{i+1:03d}{unique_id[:4]}",
            "password": "GPSTest123!",
            "terms_accepted": True
        }
        
        # Register user
        response = requests.post(f"{BASE_URL}/auth/register", headers=HEADERS, json=user_data, timeout=30)
        if response.status_code != 200:
            print(f"❌ Failed to register user: {response.status_code}")
            continue
        
        try:
            reg_data = response.json()
            temp_token = reg_data["access_token"]
            temp_user_id = reg_data["user"]["id"]
            print(f"✅ User registered: {temp_user_id}")
        except:
            print(f"❌ Invalid registration response")
            continue
        
        # Create profile with GPS coordinates
        profile_data = {
            "display_name": location_data["display_name"],
            "bio": location_data["bio"],
            "date_of_birth": f"{1990 + i}-06-15",
            "gender": "female" if i % 2 == 0 else "male",
            "height": 165 + i * 5,
            "looking_for": "علاقة جدية",
            "interests": ["السفر", "التكنولوجيا", "الرياضة"],
            "location": location_data["location"],
            "latitude": location_data["latitude"],
            "longitude": location_data["longitude"],
            "occupation": "مهندس" if i % 2 == 0 else "طبيب",
            "relationship_goals": "serious",
            "languages": ["العربية", "الإنجليزية"]
        }
        
        # Set auth header for this user
        temp_headers = HEADERS.copy()
        temp_headers["Authorization"] = f"Bearer {temp_token}"
        
        # Try to update profile (since registration creates empty profile)
        response = requests.put(
            f"{BASE_URL}/profile/update",
            headers=temp_headers,
            json=profile_data,
            timeout=30
        )
        
        if response and response.status_code == 200:
            created_profiles.append({
                "user_id": temp_user_id,
                "name": location_data["name"],
                "latitude": location_data["latitude"],
                "longitude": location_data["longitude"],
                "location": location_data["location"]
            })
            print(f"✅ Profile created at {location_data['location']}")
        else:
            print(f"❌ Failed to create profile: {response.status_code if response else 'No response'}")
            if response:
                print(f"   Response: {response.text}")
    
    print(f"\n🎉 Created {len(created_profiles)} GPS test profiles")
    return created_profiles

if __name__ == "__main__":
    create_gps_test_profiles()