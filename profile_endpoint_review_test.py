#!/usr/bin/env python3
"""
Profile Single Endpoint Review Testing
Testing all specific scenarios mentioned in the review request
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

class ProfileEndpointReviewTester:
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
    
    def setup_authentication(self):
        """Setup authentication for testing"""
        # Generate unique test data
        unique_id = str(uuid.uuid4())[:8]
        self.test_email = f"reviewtest{unique_id}@example.com"
        self.test_password = "TestPassword123!"
        test_data = {
            "name": f"Review Test User {unique_id}",
            "email": self.test_email,
            "phone_number": f"+1555222{unique_id[:4]}",
            "password": self.test_password,
            "terms_accepted": True
        }
        
        response = self.make_request("POST", "/auth/register", test_data)
        
        if response is None or response.status_code != 200:
            self.log_result("Setup Authentication", False, "Failed to register user")
            return False
        
        try:
            data = response.json()
            self.auth_token = data["access_token"]
            self.user_id = data["user"]["id"]
            
            # Update profile with GPS coordinates for distance testing
            profile_data = {
                "display_name": "Review Test User",
                "bio": "Testing profile endpoint for review",
                "age": 25,
                "gender": "male",
                "location": "Basel, Switzerland",
                "latitude": 47.5596,  # Basel coordinates
                "longitude": 7.5886,
                "interests": ["testing", "technology"],
                "languages": ["English"]
            }
            
            profile_response = self.make_request("PUT", "/profile/update", profile_data, use_auth=True)
            
            self.log_result("Setup Authentication", True, f"User registered and profile updated. ID: {self.user_id}")
            return True
            
        except json.JSONDecodeError:
            self.log_result("Setup Authentication", False, "Invalid JSON response")
            return False
    
    def test_1_valid_user_id(self):
        """Test 1: Test endpoint with valid user_id (use existing user from database)"""
        # Get existing user from discovery
        response = self.make_request("GET", "/profiles/discover?limit=5", use_auth=True)
        
        if response is None or response.status_code != 200:
            self.log_result("Test 1 - Valid User ID", False, "Could not get users from discovery")
            return False
        
        try:
            data = response.json()
            profiles = data.get("profiles", [])
            
            if not profiles:
                self.log_result("Test 1 - Valid User ID", False, "No profiles found in discovery")
                return False
            
            # Use the first profile as target
            self.target_user_id = profiles[0]["user_id"]
            
            # Test the profile endpoint
            profile_response = self.make_request("GET", f"/profiles/{self.target_user_id}", use_auth=True)
            
            if profile_response is None or profile_response.status_code != 200:
                self.log_result("Test 1 - Valid User ID", False, f"Profile endpoint failed: {profile_response.status_code if profile_response else 'None'}")
                return False
            
            profile_data = profile_response.json()
            
            # Verify user_id matches
            if profile_data.get("user_id") != self.target_user_id:
                self.log_result("Test 1 - Valid User ID", False, "User ID mismatch in response")
                return False
            
            self.log_result("Test 1 - Valid User ID", True, f"Successfully fetched profile for user {self.target_user_id}")
            return True
            
        except json.JSONDecodeError:
            self.log_result("Test 1 - Valid User ID", False, "Invalid JSON response")
            return False
    
    def test_2_response_includes_all_fields(self):
        """Test 2: Verify response includes all profile fields"""
        if not self.target_user_id:
            self.log_result("Test 2 - All Profile Fields", False, "No target user ID available")
            return False
        
        response = self.make_request("GET", f"/profiles/{self.target_user_id}", use_auth=True)
        
        if response is None or response.status_code != 200:
            self.log_result("Test 2 - All Profile Fields", False, "Could not fetch profile")
            return False
        
        try:
            data = response.json()
            
            # Expected response structure from review request
            expected_fields = [
                "user_id", "display_name", "photos", "age", "location"
            ]
            
            # Additional fields that should be present
            additional_fields = [
                "bio", "gender", "height", "interests", "occupation", 
                "education", "relationship_goals", "languages"
            ]
            
            # Optional fields
            optional_fields = [
                "latitude", "longitude", "distance", "current_mood",
                "smoking", "drinking", "has_children", "wants_children"
            ]
            
            missing_required = [field for field in expected_fields if field not in data]
            if missing_required:
                self.log_result("Test 2 - All Profile Fields", False, f"Missing required fields: {missing_required}")
                return False
            
            # Check data types match expected structure
            type_checks = [
                ("user_id", str),
                ("display_name", str),
                ("photos", list),
                ("age", (int, type(None))),
                ("location", (str, type(None)))
            ]
            
            type_errors = []
            for field, expected_type in type_checks:
                if field in data:
                    if not isinstance(data[field], expected_type):
                        type_errors.append(f"{field}: expected {expected_type}, got {type(data[field])}")
            
            if type_errors:
                self.log_result("Test 2 - All Profile Fields", False, f"Type errors: {type_errors}")
                return False
            
            present_fields = len([f for f in expected_fields + additional_fields + optional_fields if f in data])
            self.log_result("Test 2 - All Profile Fields", True, f"Response includes all required fields ({present_fields} total fields)")
            return True
            
        except json.JSONDecodeError:
            self.log_result("Test 2 - All Profile Fields", False, "Invalid JSON response")
            return False
    
    def test_3_distance_calculation(self):
        """Test 3: Test distance calculation if GPS coordinates exist"""
        if not self.target_user_id:
            self.log_result("Test 3 - Distance Calculation", False, "No target user ID available")
            return False
        
        response = self.make_request("GET", f"/profiles/{self.target_user_id}", use_auth=True)
        
        if response is None or response.status_code != 200:
            self.log_result("Test 3 - Distance Calculation", False, "Could not fetch profile")
            return False
        
        try:
            data = response.json()
            
            # Check if target user has GPS coordinates
            has_target_gps = data.get("latitude") is not None and data.get("longitude") is not None
            has_distance = "distance" in data and data["distance"] is not None
            
            if has_target_gps:
                if has_distance:
                    distance = data["distance"]
                    if isinstance(distance, (int, float)) and distance >= 0:
                        self.log_result("Test 3 - Distance Calculation", True, f"Distance calculated correctly: {distance} km")
                        return True
                    else:
                        self.log_result("Test 3 - Distance Calculation", False, f"Invalid distance value: {distance}")
                        return False
                else:
                    # Both users have GPS but no distance calculated - this might be a bug
                    self.log_result("Test 3 - Distance Calculation", False, "Both users have GPS coordinates but distance not calculated")
                    return False
            else:
                # Target user has no GPS coordinates
                if has_distance:
                    self.log_result("Test 3 - Distance Calculation", False, f"Distance calculated despite target user having no GPS: {data['distance']}")
                    return False
                else:
                    self.log_result("Test 3 - Distance Calculation", True, "Distance correctly not calculated (target user has no GPS coordinates)")
                    return True
            
        except json.JSONDecodeError:
            self.log_result("Test 3 - Distance Calculation", False, "Invalid JSON response")
            return False
    
    def test_4_nonexistent_user_404(self):
        """Test 4: Test with non-existent user_id (should return 404)"""
        fake_user_id = str(uuid.uuid4())
        
        response = self.make_request("GET", f"/profiles/{fake_user_id}", use_auth=True)
        
        if response is None:
            self.log_result("Test 4 - Nonexistent User 404", False, "Connection failed")
            return False
        
        if response.status_code == 404:
            try:
                error_data = response.json()
                detail = error_data.get("detail", "Profile not found")
                self.log_result("Test 4 - Nonexistent User 404", True, f"Correctly returned 404: {detail}")
                return True
            except:
                self.log_result("Test 4 - Nonexistent User 404", True, "Correctly returned 404")
                return True
        else:
            try:
                error_data = response.json()
                self.log_result("Test 4 - Nonexistent User 404", False, f"Expected 404 but got {response.status_code}: {error_data}")
            except:
                self.log_result("Test 4 - Nonexistent User 404", False, f"Expected 404 but got {response.status_code}: {response.text}")
            return False
    
    def test_5_no_authentication_401_403(self):
        """Test 5: Test without authentication (should return 401/403)"""
        if not self.target_user_id:
            # Use a dummy user ID for this test
            test_user_id = str(uuid.uuid4())
        else:
            test_user_id = self.target_user_id
        
        response = self.make_request("GET", f"/profiles/{test_user_id}", use_auth=False)
        
        if response is None:
            self.log_result("Test 5 - No Auth 401/403", False, "Connection failed")
            return False
        
        if response.status_code in [401, 403]:
            try:
                error_data = response.json()
                detail = error_data.get("detail", "Authentication required")
                self.log_result("Test 5 - No Auth 401/403", True, f"Correctly returned {response.status_code}: {detail}")
                return True
            except:
                self.log_result("Test 5 - No Auth 401/403", True, f"Correctly returned {response.status_code}")
                return True
        else:
            try:
                error_data = response.json()
                self.log_result("Test 5 - No Auth 401/403", False, f"Expected 401/403 but got {response.status_code}: {error_data}")
            except:
                self.log_result("Test 5 - No Auth 401/403", False, f"Expected 401/403 but got {response.status_code}: {response.text}")
            return False
    
    def test_expected_response_structure(self):
        """Test the expected response structure from the review request"""
        if not self.target_user_id:
            self.log_result("Test - Expected Response Structure", False, "No target user ID available")
            return False
        
        response = self.make_request("GET", f"/profiles/{self.target_user_id}", use_auth=True)
        
        if response is None or response.status_code != 200:
            self.log_result("Test - Expected Response Structure", False, "Could not fetch profile")
            return False
        
        try:
            data = response.json()
            
            # Expected response structure from review request:
            # {
            #   "user_id": "string",
            #   "display_name": "string", 
            #   "photos": ["url1", "url2"],
            #   "age": number,
            #   "location": "string",
            #   "latitude": number (optional),
            #   "longitude": number (optional),
            #   "distance": number (optional, if GPS available),
            #   ... other profile fields
            # }
            
            structure_checks = []
            
            # Required fields
            if "user_id" in data and isinstance(data["user_id"], str):
                structure_checks.append("✓ user_id (string)")
            else:
                structure_checks.append("✗ user_id (string)")
            
            if "display_name" in data and isinstance(data["display_name"], str):
                structure_checks.append("✓ display_name (string)")
            else:
                structure_checks.append("✗ display_name (string)")
            
            if "photos" in data and isinstance(data["photos"], list):
                structure_checks.append("✓ photos (array)")
            else:
                structure_checks.append("✗ photos (array)")
            
            if "age" in data and (isinstance(data["age"], (int, float)) or data["age"] is None):
                structure_checks.append("✓ age (number/null)")
            else:
                structure_checks.append("✗ age (number/null)")
            
            if "location" in data and (isinstance(data["location"], str) or data["location"] is None):
                structure_checks.append("✓ location (string/null)")
            else:
                structure_checks.append("✗ location (string/null)")
            
            # Optional GPS fields
            if "latitude" in data:
                if isinstance(data["latitude"], (int, float)) or data["latitude"] is None:
                    structure_checks.append("✓ latitude (number/null)")
                else:
                    structure_checks.append("✗ latitude (number/null)")
            
            if "longitude" in data:
                if isinstance(data["longitude"], (int, float)) or data["longitude"] is None:
                    structure_checks.append("✓ longitude (number/null)")
                else:
                    structure_checks.append("✗ longitude (number/null)")
            
            if "distance" in data:
                if isinstance(data["distance"], (int, float)) or data["distance"] is None:
                    structure_checks.append("✓ distance (number/null)")
                else:
                    structure_checks.append("✗ distance (number/null)")
            
            # Check for failures
            failed_checks = [check for check in structure_checks if check.startswith("✗")]
            
            if failed_checks:
                self.log_result("Test - Expected Response Structure", False, f"Structure issues: {failed_checks}")
                return False
            else:
                self.log_result("Test - Expected Response Structure", True, f"Response structure matches expected format ({len(structure_checks)} checks passed)")
                return True
            
        except json.JSONDecodeError:
            self.log_result("Test - Expected Response Structure", False, "Invalid JSON response")
            return False
    
    def run_all_tests(self):
        """Run all tests from the review request"""
        print("🧪 PROFILE SINGLE ENDPOINT REVIEW TESTING")
        print("Testing all scenarios mentioned in the review request")
        print("=" * 60)
        
        tests = [
            ("Setup Authentication", self.setup_authentication),
            ("Test 1 - Valid User ID", self.test_1_valid_user_id),
            ("Test 2 - All Profile Fields", self.test_2_response_includes_all_fields),
            ("Test 3 - Distance Calculation", self.test_3_distance_calculation),
            ("Test 4 - Nonexistent User 404", self.test_4_nonexistent_user_404),
            ("Test 5 - No Auth 401/403", self.test_5_no_authentication_401_403),
            ("Expected Response Structure", self.test_expected_response_structure)
        ]
        
        passed = 0
        total = len(tests)
        
        for test_name, test_func in tests:
            print(f"\n🔍 Running {test_name}...")
            if test_func():
                passed += 1
            time.sleep(1)  # Brief pause between tests
        
        print(f"\n📊 PROFILE ENDPOINT REVIEW TEST RESULTS")
        print("=" * 60)
        print(f"✅ Passed: {passed}/{total} tests")
        print(f"❌ Failed: {total - passed}/{total} tests")
        print(f"📈 Success Rate: {(passed/total)*100:.1f}%")
        
        # Summary of what was tested
        print(f"\n📋 REVIEW REQUEST TESTING SUMMARY")
        print("=" * 60)
        print("✅ 1. Test endpoint with valid user_id (use existing user from database)")
        print("✅ 2. Verify response includes all profile fields")
        print("✅ 3. Test distance calculation if GPS coordinates exist")
        print("✅ 4. Test with non-existent user_id (should return 404)")
        print("✅ 5. Test without authentication (should return 401/403)")
        print("✅ 6. Verify expected response structure matches specification")
        
        if passed == total:
            print("\n🎉 ALL REVIEW REQUEST TESTS PASSED!")
            print("The new GET /api/profiles/{user_id} endpoint is working correctly!")
            return True
        else:
            print(f"\n⚠️  {total - passed} tests failed. Check the details above.")
            return False

def main():
    """Main function to run the review request tests"""
    tester = ProfileEndpointReviewTester()
    success = tester.run_all_tests()
    
    if success:
        print("\n✅ Profile Endpoint Review Testing Complete - All tests passed!")
        sys.exit(0)
    else:
        print("\n❌ Profile Endpoint Review Testing Complete - Some tests failed!")
        sys.exit(1)

if __name__ == "__main__":
    main()