#!/usr/bin/env python3
"""
Detailed check of personal moments for safe categories
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

def check_moments_categories(token):
    """Check personal moments for safe categories"""
    headers = {"Authorization": f"Bearer {token}"}
    response = requests.get(f"{BACKEND_URL}/personal/list", headers=headers)
    
    if response.status_code != 200:
        print(f"❌ API call failed: {response.status_code}")
        return False
    
    data = response.json()
    moments = data.get("moments", [])
    
    print(f"📊 Found {len(moments)} moments")
    print("🔍 Checking for safe categories: flatshare, travel, outing, activity")
    print("=" * 60)
    
    safe_categories = ["flatshare", "travel", "outing", "activity"]
    found_categories = set()
    
    for i, moment in enumerate(moments, 1):
        title = moment.get("title", "")
        description = moment.get("description", "")
        
        print(f"\n💫 Moment {i}:")
        print(f"   📝 Title: {title}")
        print(f"   📄 Description: {description}")
        
        # Check for categories in title and description
        moment_text = f"{title} {description}".lower()
        moment_categories = []
        
        for category in safe_categories:
            if category in moment_text:
                moment_categories.append(category)
                found_categories.add(category)
        
        if moment_categories:
            print(f"   ✅ Categories found: {', '.join(moment_categories)}")
        else:
            print(f"   ℹ️ No specific safe categories detected")
    
    print("\n" + "=" * 60)
    print("📋 SUMMARY:")
    print(f"   Total moments: {len(moments)}")
    print(f"   Safe categories found: {', '.join(sorted(found_categories)) if found_categories else 'None'}")
    
    if len(moments) >= 6:
        print("   ✅ Has 6+ moments as required")
    else:
        print(f"   ❌ Only {len(moments)} moments (expected 6+)")
    
    if found_categories:
        print(f"   ✅ Contains safe categories: {', '.join(sorted(found_categories))}")
    else:
        print("   ⚠️ No explicit safe categories found in text")
    
    return len(moments) >= 6

def main():
    token = get_auth_token()
    if not token:
        print("❌ Failed to authenticate")
        return
    
    check_moments_categories(token)

if __name__ == "__main__":
    main()