#!/usr/bin/env python3
"""
Test GPS functionality in Explore Sections API
"""

import requests
import json
from datetime import datetime

BACKEND_URL = "https://pizoo-chat-fix.preview.emergentagent.com/api"

def test_gps_explore():
    """Test GPS functionality with explore sections"""
    session = requests.Session()
    
    try:
        # Create user with unique email
        timestamp = datetime.now().timestamp()
        register_data = {
            "name": "GPS Test User",
            "email": f"gps_test_{timestamp}@test.com",
            "phone_number": "+41791234568",
            "password": "TestPass123!",
            "terms_accepted": True
        }
        
        response = session.post(f"{BACKEND_URL}/auth/register", json=register_data)
        if response.status_code != 200:
            print(f"❌ Registration failed: {response.text}")
            return
        
        data = response.json()
        auth_token = data["access_token"]
        user_id = data["user"]["id"]
        session.headers.update({"Authorization": f"Bearer {auth_token}"})
        
        print(f"✅ Created user: {user_id}")
        
        # Update profile with GPS coordinates (Basel, Switzerland)
        profile_update = {
            "display_name": "GPS Tester",
            "bio": "Testing GPS functionality",
            "age": 30,
            "gender": "female",
            "location": "Basel, Switzerland",
            "latitude": 47.5596,
            "longitude": 7.5886,
            "interests": ["travel", "technology"]
        }
        
        response = session.put(f"{BACKEND_URL}/profile/update", json=profile_update)
        if response.status_code == 200:
            print("✅ Profile updated with GPS coordinates")
        else:
            print(f"❌ Profile update failed: {response.text}")
            return
        
        # Test explore sections
        response = session.get(f"{BACKEND_URL}/explore/sections")
        if response.status_code == 200:
            data = response.json()
            sections = data.get("sections", [])
            
            print(f"\n📍 Explore Sections with GPS coordinates:")
            print(f"Total sections: {len(sections)}")
            
            for section in sections:
                section_type = section.get("type")
                title = section.get("title")
                profiles = section.get("profiles", [])
                
                print(f"\n🔍 Section: {section_type} - {title}")
                print(f"   Profiles: {len(profiles)}")
                
                if section_type == "nearby":
                    print("   🎯 NEARBY SECTION FOUND!")
                    for i, profile in enumerate(profiles[:3]):  # Show first 3
                        distance = profile.get("distance")
                        name = profile.get("name", "Unknown")
                        location = profile.get("location", "Unknown")
                        print(f"   Profile {i+1}: {name} in {location} - Distance: {distance} km")
                
                elif profiles:
                    # Check if any profiles have distance field
                    profiles_with_distance = [p for p in profiles if p.get("distance") is not None]
                    if profiles_with_distance:
                        print(f"   📏 {len(profiles_with_distance)} profiles have distance data")
                        sample_profile = profiles_with_distance[0]
                        print(f"   Sample: {sample_profile.get('name')} - {sample_profile.get('distance')} km")
            
            # Check if nearby section exists
            nearby_sections = [s for s in sections if s.get("type") == "nearby"]
            if nearby_sections:
                print("\n✅ GPS FUNCTIONALITY WORKING: Nearby section found!")
            else:
                print("\n⚠️  No nearby section found (may be due to no other users with GPS coordinates)")
        
        else:
            print(f"❌ Explore sections failed: {response.text}")
    
    except Exception as e:
        print(f"❌ Test failed: {str(e)}")

if __name__ == "__main__":
    test_gps_explore()