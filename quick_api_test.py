#!/usr/bin/env python3
"""
Quick API Test for Explore Sections and Personal Moments
Testing the new APIs as requested by the user
"""

import requests
import json
import sys
from datetime import datetime

# Configuration
BACKEND_URL = "https://pizoo-dating-3.preview.emergentagent.com/api"

def test_user_auth():
    """Create or login a test user to get authentication token"""
    print("🔐 Setting up authentication...")
    
    # Try to register a new user
    register_data = {
        "name": "أحمد محمد",
        "email": "ahmed.test@example.com", 
        "phone_number": "+966501234567",
        "password": "TestPass123!",
        "terms_accepted": True
    }
    
    try:
        response = requests.post(f"{BACKEND_URL}/auth/register", json=register_data)
        if response.status_code == 200:
            print("✅ New user registered successfully")
            return response.json()["access_token"]
        elif response.status_code == 400 and "مسجل مسبقاً" in response.text:
            print("ℹ️ User already exists, trying login...")
            # Try login
            login_data = {
                "email": "ahmed.test@example.com",
                "password": "TestPass123!"
            }
            login_response = requests.post(f"{BACKEND_URL}/auth/login", json=login_data)
            if login_response.status_code == 200:
                print("✅ Login successful")
                return login_response.json()["access_token"]
            else:
                print(f"❌ Login failed: {login_response.status_code} - {login_response.text}")
                return None
        else:
            print(f"❌ Registration failed: {response.status_code} - {response.text}")
            return None
    except Exception as e:
        print(f"❌ Authentication error: {str(e)}")
        return None

def test_explore_sections_api(token):
    """Test GET /api/explore/sections endpoint"""
    print("\n🔍 Testing GET /api/explore/sections...")
    
    headers = {"Authorization": f"Bearer {token}"}
    
    try:
        response = requests.get(f"{BACKEND_URL}/explore/sections", headers=headers)
        
        if response.status_code != 200:
            print(f"❌ API call failed: {response.status_code} - {response.text}")
            return False
        
        data = response.json()
        print(f"✅ API call successful (200)")
        
        # Check if sections exist
        if "sections" not in data:
            print("❌ Response missing 'sections' field")
            return False
        
        sections = data["sections"]
        print(f"📊 Found {len(sections)} sections")
        
        # Expected section types
        expected_sections = [
            "most_active", "ready_chat", "near_you", "new_faces", 
            "serious_love", "fun_date", "smart_talks", "friends_only"
        ]
        
        found_sections = []
        for section in sections:
            if "type" in section:
                found_sections.append(section["type"])
                print(f"   📂 {section['type']}: {section.get('title', 'No title')} - {len(section.get('profiles', []))} profiles")
                
                # Check if profiles array exists
                if "profiles" not in section:
                    print(f"   ❌ Section {section['type']} missing 'profiles' array")
                    return False
        
        # Check if we have the expected sections
        missing_sections = set(expected_sections) - set(found_sections)
        if missing_sections:
            print(f"⚠️ Missing expected sections: {missing_sections}")
            print(f"   Found sections: {found_sections}")
        
        if len(found_sections) >= 8:
            print("✅ Found 8+ sections as expected")
        else:
            print(f"⚠️ Expected 8 sections, found {len(found_sections)}")
        
        # Check profiles structure
        total_profiles = 0
        for section in sections:
            profiles = section.get("profiles", [])
            total_profiles += len(profiles)
            if profiles:
                # Check first profile structure
                profile = profiles[0]
                required_fields = ["id", "name", "age"]
                missing_fields = [field for field in required_fields if field not in profile]
                if missing_fields:
                    print(f"   ⚠️ Profile missing fields: {missing_fields}")
        
        print(f"📈 Total profiles across all sections: {total_profiles}")
        return True
        
    except Exception as e:
        print(f"❌ Error testing explore sections: {str(e)}")
        return False

def test_personal_moments_api(token):
    """Test GET /api/personal/list endpoint"""
    print("\n💫 Testing GET /api/personal/list...")
    
    headers = {"Authorization": f"Bearer {token}"}
    
    try:
        response = requests.get(f"{BACKEND_URL}/personal/list", headers=headers)
        
        if response.status_code != 200:
            print(f"❌ API call failed: {response.status_code} - {response.text}")
            return False
        
        data = response.json()
        print(f"✅ API call successful (200)")
        
        # Check if moments exist
        if "moments" not in data:
            print("❌ Response missing 'moments' field")
            return False
        
        moments = data["moments"]
        print(f"📊 Found {len(moments)} moments")
        
        if len(moments) < 6:
            print(f"⚠️ Expected at least 6 moments, found {len(moments)}")
        else:
            print("✅ Found 6+ moments as expected")
        
        # Check safe categories
        safe_categories = ["flatshare", "travel", "outing", "activity"]
        found_categories = []
        
        for i, moment in enumerate(moments):
            print(f"   💫 Moment {i+1}: {moment.get('title', 'No title')}")
            print(f"      📝 Description: {moment.get('description', 'No description')[:50]}...")
            print(f"      🏷️ Action: {moment.get('action', 'No action')}")
            print(f"      🆕 New: {moment.get('isNew', False)}")
            print(f"      💎 Premium: {moment.get('isPremium', False)}")
            
            # Check for safe categories in title/description
            moment_text = f"{moment.get('title', '')} {moment.get('description', '')}".lower()
            for category in safe_categories:
                if category in moment_text:
                    found_categories.append(category)
        
        if found_categories:
            print(f"✅ Found safe categories: {set(found_categories)}")
        else:
            print("ℹ️ No specific safe categories found in moment text (this may be normal)")
        
        # Check moment structure
        if moments:
            moment = moments[0]
            required_fields = ["id", "title", "description", "action", "ctaText"]
            missing_fields = [field for field in required_fields if field not in moment]
            if missing_fields:
                print(f"   ⚠️ Moment missing fields: {missing_fields}")
            else:
                print("✅ Moment structure looks good")
        
        return True
        
    except Exception as e:
        print(f"❌ Error testing personal moments: {str(e)}")
        return False

def main():
    """Main test function"""
    print("🚀 Starting Quick API Test for Explore Sections and Personal Moments")
    print("=" * 70)
    
    # Get authentication token
    token = test_user_auth()
    if not token:
        print("❌ Failed to authenticate. Cannot proceed with API tests.")
        sys.exit(1)
    
    # Test both APIs
    explore_success = test_explore_sections_api(token)
    personal_success = test_personal_moments_api(token)
    
    # Summary
    print("\n" + "=" * 70)
    print("📋 TEST SUMMARY")
    print("=" * 70)
    
    if explore_success:
        print("✅ GET /api/explore/sections - WORKING")
    else:
        print("❌ GET /api/explore/sections - FAILED")
    
    if personal_success:
        print("✅ GET /api/personal/list - WORKING")
    else:
        print("❌ GET /api/personal/list - FAILED")
    
    if explore_success and personal_success:
        print("\n🎉 All tests passed! Both APIs are working correctly.")
        return True
    else:
        print("\n⚠️ Some tests failed. Check the details above.")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)