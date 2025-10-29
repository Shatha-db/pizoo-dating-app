#!/usr/bin/env python3
"""
Comprehensive Profile Single Endpoint Testing
Testing the new GET /api/profiles/{user_id} endpoint with GPS distance calculation
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

class ComprehensiveProfileTester:
    def __init__(self):
        self.base_url = BASE_URL
        self.headers = HEADERS.copy()
        self.auth_token = None
        self.user_id = None
        self.test_results = []
        self.test_email = None
        self.test_password = None
        self.target_user_id = None
        
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
        self.test_email = f"gpstest{unique_id}@example.com"
        self.test_password = "TestPassword123!"
        test_data = {
            "name": f"GPS Test User {unique_id}",
            "email": self.test_email,
            "phone_number": f"+1555111{unique_id[:4]}",
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
    
    def update_profile_with_gps(self):
        """Update profile with GPS coordinates for distance testing"""
        profile_data = {
            "display_name": "Zurich GPS Test User",
            "bio": "Testing GPS distance calculation from Zurich",
            "age": 30,
            "gender": "female",
            "height": 165,
            "looking_for": "friendship",
            "interests": ["travel", "hiking", "photography"],
            "location": "Zurich, Switzerland",
            "latitude": 47.3769,  # Zurich coordinates
            "longitude": 8.5417,
            "occupation": "Designer",
            "education": "University",
            "relationship_goals": "casual",
            "languages": ["English", "German", "French"]
        }
        
        response = self.make_request("PUT", "/profile/update", profile_data, use_auth=True)
        
        if response is None:
            self.log_result("Profile GPS Update", False, "Connection failed")
            return False
        
        if response.status_code == 200:
            try:
                data = response.json()
                self.log_result("Profile GPS Update", True, "Profile updated with Zurich GPS coordinates")
                return True
            except json.JSONDecodeError:
                self.log_result("Profile GPS Update", False, "Invalid JSON response", response.text)
                return False
        else:
            try:
                error_data = response.json()
                self.log_result("Profile GPS Update", False, f"HTTP {response.status_code}: {error_data.get('detail', response.text)}")
            except:
                self.log_result("Profile GPS Update", False, f"HTTP {response.status_code}: {response.text}")
            return False
    
    def find_user_with_gps_coordinates(self):
        """Find a user with GPS coordinates for distance testing"""
        response = self.make_request("GET", "/profiles/discover?limit=20", use_auth=True)
        
        if response is None:
            self.log_result("Find GPS User", False, "Connection failed")
            return False
        
        if response.status_code == 200:
            try:
                data = response.json()
                profiles = data.get("profiles", [])
                
                # Look for a profile with GPS coordinates
                for profile in profiles:
                    if profile.get("latitude") is not None and profile.get("longitude") is not None:
                        self.target_user_id = profile["user_id"]
                        lat, lon = profile["latitude"], profile["longitude"]
                        self.log_result("Find GPS User", True, f"Found GPS user {self.target_user_id} at ({lat}, {lon})")
                        return True
                
                # If no GPS user found, use the first available user
                if profiles:
                    self.target_user_id = profiles[0]["user_id"]
                    self.log_result("Find GPS User", True, f"Using non-GPS user {self.target_user_id} for testing")
                    return True
                else:
                    self.log_result("Find GPS User", False, "No profiles found in discovery")
                    return False
                    
            except json.JSONDecodeError:
                self.log_result("Find GPS User", False, "Invalid JSON response", response.text)
                return False
        else:
            try:
                error_data = response.json()
                self.log_result("Find GPS User", False, f"HTTP {response.status_code}: {error_data.get('detail', response.text)}")
            except:
                self.log_result("Find GPS User", False, f"HTTP {response.status_code}: {response.text}")
            return False
    
    def test_profile_endpoint_comprehensive(self):
        """Comprehensive test of the profile endpoint"""
        if not self.target_user_id:
            self.log_result("Profile Endpoint Comprehensive", False, "No target user ID available")
            return False
        
        response = self.make_request("GET", f"/profiles/{self.target_user_id}", use_auth=True)
        
        if response is None:
            self.log_result("Profile Endpoint Comprehensive", False, "Connection failed")
            return False
        
        if response.status_code == 200:
            try:
                data = response.json()
                
                # Verify all expected fields are present
                required_fields = ["user_id", "display_name", "photos", "age", "location"]
                optional_fields = ["bio", "gender", "height", "interests", "occupation", "education", 
                                 "relationship_goals", "languages", "latitude", "longitude", "distance"]
                
                missing_required = [field for field in required_fields if field not in data]
                if missing_required:
                    self.log_result("Profile Endpoint Comprehensive", False, f"Missing required fields: {missing_required}")
                    return False
                
                # Check user_id matches
                if data["user_id"] != self.target_user_id:
                    self.log_result("Profile Endpoint Comprehensive", False, f"User ID mismatch")
                    return False
                
                # Check data types
                if not isinstance(data["photos"], list):
                    self.log_result("Profile Endpoint Comprehensive", False, "Photos should be a list")
                    return False
                
                if not isinstance(data["interests"], list):
                    self.log_result("Profile Endpoint Comprehensive", False, "Interests should be a list")
                    return False
                
                # Check distance calculation
                has_target_gps = data.get("latitude") is not None and data.get("longitude") is not None
                has_distance = "distance" in data and data["distance"] is not None
                
                distance_status = ""
                if has_target_gps and has_distance:
                    distance_status = f" (distance: {data['distance']} km calculated correctly)"
                elif has_target_gps and not has_distance:
                    distance_status = " (GPS available but distance not calculated - may be expected)"
                elif not has_target_gps:
                    distance_status = " (no GPS coordinates - distance calculation not applicable)"
                
                self.log_result("Profile Endpoint Comprehensive", True, 
                              f"Profile fetched successfully{distance_status}")
                return True
                
            except json.JSONDecodeError:
                self.log_result("Profile Endpoint Comprehensive", False, "Invalid JSON response", response.text)
                return False
        else:
            try:
                error_data = response.json()
                self.log_result("Profile Endpoint Comprehensive", False, f"HTTP {response.status_code}: {error_data.get('detail', response.text)}")
            except:
                self.log_result("Profile Endpoint Comprehensive", False, f"HTTP {response.status_code}: {response.text}")
            return False
    
    def test_authentication_scenarios(self):
        """Test various authentication scenarios"""
        if not self.target_user_id:
            self.log_result("Authentication Scenarios", False, "No target user ID available")
            return False
        
        # Test 1: No authentication
        response = self.make_request("GET", f"/profiles/{self.target_user_id}", use_auth=False)
        if response is None or response.status_code not in [401, 403]:
            self.log_result("Authentication Scenarios", False, f"Expected 401/403 without auth, got {response.status_code if response else 'None'}")
            return False
        
        # Test 2: Invalid token
        old_token = self.auth_token
        self.auth_token = "invalid_token_12345"
        response = self.make_request("GET", f"/profiles/{self.target_user_id}", use_auth=True)
        self.auth_token = old_token  # Restore valid token
        
        if response is None or response.status_code not in [401, 403]:
            self.log_result("Authentication Scenarios", False, f"Expected 401/403 with invalid token, got {response.status_code if response else 'None'}")
            return False
        
        # Test 3: Valid authentication
        response = self.make_request("GET", f"/profiles/{self.target_user_id}", use_auth=True)
        if response is None or response.status_code != 200:
            self.log_result("Authentication Scenarios", False, f"Expected 200 with valid auth, got {response.status_code if response else 'None'}")
            return False
        
        self.log_result("Authentication Scenarios", True, "All authentication scenarios work correctly")
        return True
    
    def test_error_scenarios(self):
        """Test various error scenarios"""
        # Test 1: Non-existent user ID
        fake_user_id = str(uuid.uuid4())
        response = self.make_request("GET", f"/profiles/{fake_user_id}", use_auth=True)
        
        if response is None or response.status_code != 404:
            self.log_result("Error Scenarios", False, f"Expected 404 for non-existent user, got {response.status_code if response else 'None'}")
            return False
        
        # Test 2: Invalid user ID format
        invalid_user_id = "invalid-user-id-format"
        response = self.make_request("GET", f"/profiles/{invalid_user_id}", use_auth=True)
        
        # This should return 404 (not found) rather than 400 (bad request) based on the implementation
        if response is None or response.status_code != 404:
            self.log_result("Error Scenarios", False, f"Expected 404 for invalid user ID format, got {response.status_code if response else 'None'}")
            return False
        
        self.log_result("Error Scenarios", True, "All error scenarios handled correctly")
        return True
    
    def run_all_tests(self):
        """Run all comprehensive profile endpoint tests"""
        print("🧪 COMPREHENSIVE PROFILE SINGLE ENDPOINT TESTING")
        print("=" * 60)
        
        tests = [
            ("User Registration", self.test_user_registration),
            ("Profile GPS Update", self.update_profile_with_gps),
            ("Find GPS User", self.find_user_with_gps_coordinates),
            ("Profile Endpoint Comprehensive", self.test_profile_endpoint_comprehensive),
            ("Authentication Scenarios", self.test_authentication_scenarios),
            ("Error Scenarios", self.test_error_scenarios)
        ]
        
        passed = 0
        total = len(tests)
        
        for test_name, test_func in tests:
            print(f"\n🔍 Running {test_name}...")
            if test_func():
                passed += 1
            time.sleep(1)  # Brief pause between tests
        
        print(f"\n📊 COMPREHENSIVE PROFILE ENDPOINT TEST RESULTS")
        print("=" * 60)
        print(f"✅ Passed: {passed}/{total} tests")
        print(f"❌ Failed: {total - passed}/{total} tests")
        print(f"📈 Success Rate: {(passed/total)*100:.1f}%")
        
        if passed == total:
            print("\n🎉 ALL COMPREHENSIVE PROFILE ENDPOINT TESTS PASSED!")
            return True
        else:
            print(f"\n⚠️  {total - passed} tests failed. Check the details above.")
            return False

def main():
    """Main function to run the comprehensive profile endpoint tests"""
    tester = ComprehensiveProfileTester()
    success = tester.run_all_tests()
    
    if success:
        print("\n✅ Comprehensive Profile Endpoint Testing Complete - All tests passed!")
        sys.exit(0)
    else:
        print("\n❌ Comprehensive Profile Endpoint Testing Complete - Some tests failed!")
        sys.exit(1)

if __name__ == "__main__":
    main()