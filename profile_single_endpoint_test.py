#!/usr/bin/env python3
"""
Profile Single Endpoint Testing
Testing the new GET /api/profiles/{user_id} endpoint implementation
"""

import requests
import json
import sys
import time
from datetime import datetime
import uuid

# Configuration
BASE_URL = "https://dating-app-bugfix.preview.emergentagent.com/api"
HEADERS = {"Content-Type": "application/json"}

class ProfileSingleEndpointTester:
    def __init__(self):
        self.base_url = BASE_URL
        self.headers = HEADERS.copy()
        self.auth_token = None
        self.user_id = None
        self.test_results = []
        self.test_email = None
        self.test_password = None
        self.target_user_id = None  # Another user to test profile fetching
        
    def log_result(self, test_name, success, message, response_data=None):
        """Log test results"""
        result = {
            "test": test_name,
            "success": success,
            "message": message,
            "timestamp": datetime.now().isoformat(),
            "response_data": response_data
        }
        self.test_results.append(result)
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{status} {test_name}: {message}")
        if not success and response_data:
            print(f"   Response: {response_data}")
    
    def make_request(self, method, endpoint, data=None, use_auth=False):
        """Make HTTP request with proper headers"""
        url = f"{self.base_url}{endpoint}"
        headers = self.headers.copy()
        
        if use_auth and self.auth_token:
            headers["Authorization"] = f"Bearer {self.auth_token}"
        
        try:
            if method.upper() == "GET":
                response = requests.get(url, headers=headers, timeout=30)
            elif method.upper() == "POST":
                response = requests.post(url, headers=headers, json=data, timeout=30)
            elif method.upper() == "PUT":
                response = requests.put(url, headers=headers, json=data, timeout=30)
            elif method.upper() == "DELETE":
                response = requests.delete(url, headers=headers, timeout=30)
            else:
                raise ValueError(f"Unsupported method: {method}")
            
            return response
        except requests.exceptions.RequestException as e:
            return None, str(e)
    
    def test_user_registration(self):
        """Test user registration to get authentication"""
        # Generate unique test data
        unique_id = str(uuid.uuid4())[:8]
        self.test_email = f"profiletest{unique_id}@example.com"
        self.test_password = "TestPassword123!"
        test_data = {
            "name": f"Profile Test User {unique_id}",
            "email": self.test_email,
            "phone_number": f"+1555000{unique_id[:4]}",
            "password": self.test_password,
            "terms_accepted": True
        }
        
        response = self.make_request("POST", "/auth/register", test_data)
        
        if response is None:
            self.log_result("User Registration", False, "Connection failed")
            return False
        
        if response.status_code == 200:
            try:
                data = response.json()
                if "access_token" in data and "user" in data:
                    self.auth_token = data["access_token"]
                    self.user_id = data["user"]["id"]
                    self.log_result("User Registration", True, f"User registered successfully. ID: {self.user_id}")
                    return True
                else:
                    self.log_result("User Registration", False, "Missing access_token or user in response", data)
                    return False
            except json.JSONDecodeError:
                self.log_result("User Registration", False, "Invalid JSON response", response.text)
                return False
        else:
            try:
                error_data = response.json()
                self.log_result("User Registration", False, f"HTTP {response.status_code}: {error_data.get('detail', response.text)}")
            except:
                self.log_result("User Registration", False, f"HTTP {response.status_code}: {response.text}")
            return False
    
    def create_test_profile(self):
        """Create a profile for the current user with GPS coordinates"""
        profile_data = {
            "display_name": "Basel Test User",
            "bio": "Testing profile single endpoint from Basel, Switzerland",
            "age": 28,
            "gender": "male",
            "height": 175,
            "looking_for": "friendship",
            "interests": ["travel", "technology", "coffee"],
            "location": "Basel, Switzerland",
            "latitude": 47.5596,  # Basel coordinates
            "longitude": 7.5886,
            "occupation": "Software Engineer",
            "education": "University",
            "relationship_goals": "casual",
            "languages": ["English", "German", "Arabic"]
        }
        
        response = self.make_request("POST", "/profile/create", profile_data, use_auth=True)
        
        if response is None:
            self.log_result("Profile Creation", False, "Connection failed")
            return False
        
        if response.status_code == 200:
            try:
                data = response.json()
                self.log_result("Profile Creation", True, "Profile created successfully with GPS coordinates")
                return True
            except json.JSONDecodeError:
                self.log_result("Profile Creation", False, "Invalid JSON response", response.text)
                return False
        else:
            try:
                error_data = response.json()
                self.log_result("Profile Creation", False, f"HTTP {response.status_code}: {error_data.get('detail', response.text)}")
            except:
                self.log_result("Profile Creation", False, f"HTTP {response.status_code}: {response.text}")
            return False
    
    def get_existing_user_for_testing(self):
        """Get an existing user from discovery to test profile fetching"""
        response = self.make_request("GET", "/profiles/discover?limit=5", use_auth=True)
        
        if response is None:
            self.log_result("Get Test Target User", False, "Connection failed")
            return False
        
        if response.status_code == 200:
            try:
                data = response.json()
                profiles = data.get("profiles", [])
                if profiles:
                    self.target_user_id = profiles[0]["user_id"]
                    self.log_result("Get Test Target User", True, f"Found target user ID: {self.target_user_id}")
                    return True
                else:
                    self.log_result("Get Test Target User", False, "No profiles found in discovery")
                    return False
            except json.JSONDecodeError:
                self.log_result("Get Test Target User", False, "Invalid JSON response", response.text)
                return False
        else:
            try:
                error_data = response.json()
                self.log_result("Get Test Target User", False, f"HTTP {response.status_code}: {error_data.get('detail', response.text)}")
            except:
                self.log_result("Get Test Target User", False, f"HTTP {response.status_code}: {response.text}")
            return False
    
    def test_profile_endpoint_without_auth(self):
        """Test GET /api/profiles/{user_id} without authentication (should return 401/403)"""
        if not self.target_user_id:
            self.log_result("Profile Endpoint - No Auth", False, "No target user ID available")
            return False
        
        response = self.make_request("GET", f"/profiles/{self.target_user_id}", use_auth=False)
        
        if response is None:
            self.log_result("Profile Endpoint - No Auth", False, "Connection failed")
            return False
        
        if response.status_code in [401, 403]:
            self.log_result("Profile Endpoint - No Auth", True, f"Correctly returned {response.status_code} for unauthenticated request")
            return True
        else:
            try:
                error_data = response.json()
                self.log_result("Profile Endpoint - No Auth", False, f"Expected 401/403 but got {response.status_code}: {error_data}")
            except:
                self.log_result("Profile Endpoint - No Auth", False, f"Expected 401/403 but got {response.status_code}: {response.text}")
            return False
    
    def test_profile_endpoint_with_valid_user(self):
        """Test GET /api/profiles/{user_id} with valid user_id"""
        if not self.target_user_id:
            self.log_result("Profile Endpoint - Valid User", False, "No target user ID available")
            return False
        
        response = self.make_request("GET", f"/profiles/{self.target_user_id}", use_auth=True)
        
        if response is None:
            self.log_result("Profile Endpoint - Valid User", False, "Connection failed")
            return False
        
        if response.status_code == 200:
            try:
                data = response.json()
                
                # Verify required profile fields
                required_fields = ["user_id", "display_name", "photos", "age", "location"]
                missing_fields = [field for field in required_fields if field not in data]
                
                if missing_fields:
                    self.log_result("Profile Endpoint - Valid User", False, f"Missing required fields: {missing_fields}", data)
                    return False
                
                # Verify user_id matches
                if data["user_id"] != self.target_user_id:
                    self.log_result("Profile Endpoint - Valid User", False, f"User ID mismatch: expected {self.target_user_id}, got {data['user_id']}")
                    return False
                
                # Check if distance is calculated (optional, depends on GPS coordinates)
                has_distance = "distance" in data
                distance_info = f" (distance: {data.get('distance', 'N/A')} km)" if has_distance else " (no distance calculated)"
                
                self.log_result("Profile Endpoint - Valid User", True, f"Profile fetched successfully for user {self.target_user_id}{distance_info}")
                return True
                
            except json.JSONDecodeError:
                self.log_result("Profile Endpoint - Valid User", False, "Invalid JSON response", response.text)
                return False
        else:
            try:
                error_data = response.json()
                self.log_result("Profile Endpoint - Valid User", False, f"HTTP {response.status_code}: {error_data.get('detail', response.text)}")
            except:
                self.log_result("Profile Endpoint - Valid User", False, f"HTTP {response.status_code}: {response.text}")
            return False
    
    def test_profile_endpoint_with_nonexistent_user(self):
        """Test GET /api/profiles/{user_id} with non-existent user_id (should return 404)"""
        fake_user_id = str(uuid.uuid4())
        
        response = self.make_request("GET", f"/profiles/{fake_user_id}", use_auth=True)
        
        if response is None:
            self.log_result("Profile Endpoint - Nonexistent User", False, "Connection failed")
            return False
        
        if response.status_code == 404:
            self.log_result("Profile Endpoint - Nonexistent User", True, "Correctly returned 404 for non-existent user")
            return True
        else:
            try:
                error_data = response.json()
                self.log_result("Profile Endpoint - Nonexistent User", False, f"Expected 404 but got {response.status_code}: {error_data}")
            except:
                self.log_result("Profile Endpoint - Nonexistent User", False, f"Expected 404 but got {response.status_code}: {response.text}")
            return False
    
    def test_distance_calculation(self):
        """Test distance calculation when both users have GPS coordinates"""
        if not self.target_user_id:
            self.log_result("Distance Calculation Test", False, "No target user ID available")
            return False
        
        # First, get the target profile to check if it has GPS coordinates
        response = self.make_request("GET", f"/profiles/{self.target_user_id}", use_auth=True)
        
        if response is None or response.status_code != 200:
            self.log_result("Distance Calculation Test", False, "Could not fetch target profile")
            return False
        
        try:
            profile_data = response.json()
            
            # Check if both users have GPS coordinates
            has_target_gps = profile_data.get("latitude") is not None and profile_data.get("longitude") is not None
            
            if has_target_gps:
                # Distance should be calculated and included
                if "distance" in profile_data and isinstance(profile_data["distance"], (int, float)):
                    distance = profile_data["distance"]
                    self.log_result("Distance Calculation Test", True, f"Distance calculated correctly: {distance} km")
                    return True
                else:
                    self.log_result("Distance Calculation Test", False, "Distance not calculated despite both users having GPS coordinates")
                    return False
            else:
                # No GPS coordinates, distance should be None or not present
                if profile_data.get("distance") is None:
                    self.log_result("Distance Calculation Test", True, "Distance correctly not calculated (target user has no GPS coordinates)")
                    return True
                else:
                    self.log_result("Distance Calculation Test", False, f"Unexpected distance value: {profile_data.get('distance')}")
                    return False
                    
        except json.JSONDecodeError:
            self.log_result("Distance Calculation Test", False, "Invalid JSON response")
            return False
    
    def test_profile_response_structure(self):
        """Test that the profile response includes all expected fields"""
        if not self.target_user_id:
            self.log_result("Profile Response Structure", False, "No target user ID available")
            return False
        
        response = self.make_request("GET", f"/profiles/{self.target_user_id}", use_auth=True)
        
        if response is None or response.status_code != 200:
            self.log_result("Profile Response Structure", False, "Could not fetch profile")
            return False
        
        try:
            data = response.json()
            
            # Expected fields based on the Profile model
            expected_fields = [
                "user_id", "display_name", "photos", "age", "location",
                "bio", "gender", "height", "interests", "occupation",
                "education", "relationship_goals", "languages"
            ]
            
            # Optional fields that may or may not be present
            optional_fields = [
                "latitude", "longitude", "distance", "current_mood",
                "smoking", "drinking", "has_children", "wants_children",
                "date_of_birth", "looking_for", "created_at", "updated_at"
            ]
            
            present_fields = list(data.keys())
            missing_required = [field for field in expected_fields if field not in present_fields]
            
            if missing_required:
                self.log_result("Profile Response Structure", False, f"Missing required fields: {missing_required}")
                return False
            
            # Check data types
            type_checks = [
                ("user_id", str),
                ("display_name", str),
                ("photos", list),
                ("interests", list),
                ("languages", list)
            ]
            
            type_errors = []
            for field, expected_type in type_checks:
                if field in data and not isinstance(data[field], expected_type):
                    type_errors.append(f"{field} should be {expected_type.__name__}, got {type(data[field]).__name__}")
            
            if type_errors:
                self.log_result("Profile Response Structure", False, f"Type errors: {type_errors}")
                return False
            
            self.log_result("Profile Response Structure", True, f"Profile response structure is correct ({len(present_fields)} fields present)")
            return True
            
        except json.JSONDecodeError:
            self.log_result("Profile Response Structure", False, "Invalid JSON response")
            return False
    
    def run_all_tests(self):
        """Run all profile single endpoint tests"""
        print("🧪 PROFILE SINGLE ENDPOINT TESTING")
        print("=" * 50)
        
        tests = [
            ("User Registration", self.test_user_registration),
            ("Profile Creation", self.create_test_profile),
            ("Get Target User", self.get_existing_user_for_testing),
            ("No Authentication Test", self.test_profile_endpoint_without_auth),
            ("Valid User Test", self.test_profile_endpoint_with_valid_user),
            ("Nonexistent User Test", self.test_profile_endpoint_with_nonexistent_user),
            ("Distance Calculation Test", self.test_distance_calculation),
            ("Response Structure Test", self.test_profile_response_structure)
        ]
        
        passed = 0
        total = len(tests)
        
        for test_name, test_func in tests:
            print(f"\n🔍 Running {test_name}...")
            if test_func():
                passed += 1
            time.sleep(1)  # Brief pause between tests
        
        print(f"\n📊 PROFILE SINGLE ENDPOINT TEST RESULTS")
        print("=" * 50)
        print(f"✅ Passed: {passed}/{total} tests")
        print(f"❌ Failed: {total - passed}/{total} tests")
        print(f"📈 Success Rate: {(passed/total)*100:.1f}%")
        
        if passed == total:
            print("\n🎉 ALL PROFILE SINGLE ENDPOINT TESTS PASSED!")
            return True
        else:
            print(f"\n⚠️  {total - passed} tests failed. Check the details above.")
            return False

def main():
    """Main function to run the profile single endpoint tests"""
    tester = ProfileSingleEndpointTester()
    success = tester.run_all_tests()
    
    if success:
        print("\n✅ Profile Single Endpoint Testing Complete - All tests passed!")
        sys.exit(0)
    else:
        print("\n❌ Profile Single Endpoint Testing Complete - Some tests failed!")
        sys.exit(1)

if __name__ == "__main__":
    main()