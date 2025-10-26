#!/usr/bin/env python3
"""
Debug test to isolate specific endpoint issues
"""

import requests
import json
import uuid

BASE_URL = "https://pizoo-dating-1.preview.emergentagent.com/api"
HEADERS = {"Content-Type": "application/json"}

def test_single_endpoint():
    # First register and login
    unique_id = str(uuid.uuid4())[:8]
    test_email = f"debug_test_{unique_id}@example.com"
    test_password = "DebugTest123!"
    
    # Register
    register_data = {
        "name": f"Debug User {unique_id}",
        "email": test_email,
        "phone_number": f"+966555{unique_id[:6]}",
        "password": test_password,
        "terms_accepted": True
    }
    
    response = requests.post(f"{BASE_URL}/auth/register", json=register_data, headers=HEADERS)
    if response.status_code != 200:
        print(f"Registration failed: {response.status_code} - {response.text}")
        return
    
    data = response.json()
    auth_token = data["access_token"]
    user_id = data["user"]["id"]
    
    print(f"✅ Registered user: {user_id}")
    
    # Test usage-stats endpoint
    headers_with_auth = HEADERS.copy()
    headers_with_auth["Authorization"] = f"Bearer {auth_token}"
    
    print("\n🔍 Testing usage-stats endpoint...")
    response = requests.get(f"{BASE_URL}/usage-stats", headers=headers_with_auth)
    print(f"Status: {response.status_code}")
    print(f"Response: {response.text}")
    
    if response.status_code != 200:
        print("❌ Usage-stats failed")
        return
    
    print("✅ Usage-stats working")
    
    # Test discovery-settings endpoint
    print("\n🔍 Testing discovery-settings endpoint...")
    response = requests.get(f"{BASE_URL}/discovery-settings", headers=headers_with_auth)
    print(f"Status: {response.status_code}")
    print(f"Response: {response.text}")
    
    if response.status_code != 200:
        print("❌ Discovery-settings failed")
        return
    
    print("✅ Discovery-settings working")
    
    # Test swipe endpoint - first get profiles
    print("\n🔍 Getting profiles for swipe test...")
    response = requests.get(f"{BASE_URL}/profiles/discover", headers=headers_with_auth)
    if response.status_code != 200:
        print(f"❌ Discover profiles failed: {response.status_code} - {response.text}")
        return
    
    profiles = response.json().get("profiles", [])
    if not profiles:
        print("❌ No profiles found")
        return
    
    print(f"✅ Found {len(profiles)} profiles")
    
    # Test swipe
    print("\n🔍 Testing swipe endpoint...")
    swipe_data = {
        "swiped_user_id": profiles[0]["user_id"],
        "action": "like"
    }
    
    response = requests.post(f"{BASE_URL}/swipe", json=swipe_data, headers=headers_with_auth)
    print(f"Status: {response.status_code}")
    print(f"Response: {response.text}")
    
    if response.status_code != 200:
        print("❌ Swipe failed")
        return
    
    print("✅ Swipe working")

if __name__ == "__main__":
    test_single_endpoint()