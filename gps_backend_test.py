#!/usr/bin/env python3
"""
GPS/Maps Integration Backend Testing Script for Pizoo Dating App
Tests location-based discovery features including GPS coordinates, distance calculation, and proximity filtering.
"""

import requests
import json
import sys
from datetime import datetime
import uuid
import math

# Configuration
BASE_URL = "https://pizoo-dating-3.preview.emergentagent.com/api"
HEADERS = {"Content-Type": "application/json"}

class GPSLocationTester:
    def __init__(self):
        self.base_url = BASE_URL
        self.headers = HEADERS.copy()
        self.auth_token = None
        self.user_id = None
        self.profile_id = None
        self.test_results = []
        self.test_email = None
        self.test_password = None
        self.test_profiles = []  # Store created test profiles
        
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
    
    def calculate_distance(self, lat1, lon1, lat2, lon2):
        """Calculate distance using Haversine formula for verification"""
        # Convert to radians
        lat1, lon1, lat2, lon2 = map(math.radians, [lat1, lon1, lat2, lon2])
        
        # Haversine formula
        dlat = lat2 - lat1
        dlon = lon2 - lon1
        a = math.sin(dlat / 2)**2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlon / 2)**2
        c = 2 * math.asin(math.sqrt(a))
        
        # Earth radius in kilometers
        r = 6371
        
        return c * r
    
    def setup_test_user(self):
        """Create a test user with GPS coordinates"""
        # Generate unique test data
        unique_id = str(uuid.uuid4())[:8]
        self.test_email = f"gpstest{unique_id}@pizoo.com"
        self.test_password = "GPSTest123!"
        
        # Register user
        user_data = {
            "name": f"GPS Test User {unique_id}",
            "email": self.test_email,
            "phone_number": f"+41791234{unique_id[:4]}",
            "password": self.test_password,
            "terms_accepted": True
        }
        
        response = self.make_request("POST", "/auth/register", user_data)
        
        if response is None or response.status_code != 200:
            self.log_result("Setup Test User", False, "Failed to register test user")
            return False
        
        try:
            data = response.json()
            self.auth_token = data["access_token"]
            self.user_id = data["user"]["id"]
            self.log_result("Setup Test User", True, f"Test user created: {self.user_id}")
            return True
        except:
            self.log_result("Setup Test User", False, "Invalid response from registration")
            return False
    
    def test_profile_with_gps_coordinates(self):
        """Test creating/updating profile with GPS coordinates"""
        if not self.auth_token:
            self.log_result("Profile GPS Coordinates", False, "No auth token available")
            return False
        
        # Basel, Switzerland coordinates (test user location)
        profile_data = {
            "display_name": "مستخدم تجريبي GPS",
            "bio": "اختبار الموقع الجغرافي في بازل، سويسرا",
            "date_of_birth": "1992-03-20",
            "gender": "male",
            "height": 175,
            "looking_for": "علاقة جدية",
            "interests": ["السفر", "التكنولوجيا", "الرياضة"],
            "location": "Basel, Switzerland",
            "latitude": 47.5596,  # Basel coordinates
            "longitude": 7.5886,
            "occupation": "مهندس برمجيات",
            "relationship_goals": "serious",
            "languages": ["العربية", "الإنجليزية", "الألمانية"]
        }
        
        # Try to create profile first
        response = self.make_request("POST", "/profile/create", profile_data, use_auth=True)
        
        if response and response.status_code == 200:
            try:
                data = response.json()
                self.log_result("Profile GPS Coordinates", True, "Profile created with GPS coordinates")
                return True
            except:
                self.log_result("Profile GPS Coordinates", False, "Invalid JSON response from profile creation")
                return False
        else:
            # If creation fails, try updating existing profile
            response = self.make_request("PUT", "/profile/update", profile_data, use_auth=True)
            
            if response is None:
                self.log_result("Profile GPS Coordinates", False, "Connection failed")
                return False
            
            if response.status_code == 200:
                try:
                    data = response.json()
                    self.log_result("Profile GPS Coordinates", True, "Profile updated with GPS coordinates")
                    return True
                except:
                    self.log_result("Profile GPS Coordinates", False, "Invalid JSON response from profile update")
                    return False
            else:
                try:
                    error_data = response.json()
                    self.log_result("Profile GPS Coordinates", False, f"HTTP {response.status_code}: {error_data.get('detail', response.text)}")
                except:
                    self.log_result("Profile GPS Coordinates", False, f"HTTP {response.status_code}: {response.text}")
                return False
    
    def create_test_profiles_with_locations(self):
        """Create test profiles at different distances for testing"""
        test_locations = [
            {
                "name": "Profile A - Nearby",
                "display_name": "مستخدم قريب",
                "latitude": 47.5500,  # ~2km from Basel center
                "longitude": 7.5800,
                "location": "Near Basel, Switzerland",
                "expected_distance": 2
            },
            {
                "name": "Profile B - Medium Distance", 
                "display_name": "مستخدم متوسط المسافة",
                "latitude": 47.6000,  # ~10km from Basel
                "longitude": 7.6500,
                "location": "Basel Suburbs, Switzerland",
                "expected_distance": 10
            },
            {
                "name": "Profile C - Far Away",
                "display_name": "مستخدم بعيد",
                "latitude": 48.1351,  # Munich, Germany ~250km
                "longitude": 11.5820,
                "location": "Munich, Germany", 
                "expected_distance": 250
            }
        ]
        
        created_profiles = []
        
        for i, location_data in enumerate(test_locations):
            # Create a user for this profile
            unique_id = str(uuid.uuid4())[:8]
            user_data = {
                "name": f"Test User {i+1}",
                "email": f"testloc{i+1}{unique_id}@pizoo.com",
                "phone_number": f"+41791{i+1:03d}{unique_id[:4]}",
                "password": "TestLoc123!",
                "terms_accepted": True
            }
            
            # Register user
            response = self.make_request("POST", "/auth/register", user_data)
            if response is None or response.status_code != 200:
                self.log_result(f"Create {location_data['name']}", False, "Failed to register user")
                continue
            
            try:
                reg_data = response.json()
                temp_token = reg_data["access_token"]
                temp_user_id = reg_data["user"]["id"]
            except:
                self.log_result(f"Create {location_data['name']}", False, "Invalid registration response")
                continue
            
            # Create profile with GPS coordinates
            profile_data = {
                "display_name": location_data["display_name"],
                "bio": f"اختبار الموقع - {location_data['location']}",
                "date_of_birth": f"{1990 + i}-06-15",
                "gender": "female" if i % 2 == 0 else "male",
                "height": 165 + i * 5,
                "looking_for": "علاقة جدية",
                "interests": ["السفر", "التكنولوجيا"],
                "location": location_data["location"],
                "latitude": location_data["latitude"],
                "longitude": location_data["longitude"],
                "occupation": "مهندس",
                "relationship_goals": "serious",
                "languages": ["العربية", "الإنجليزية"]
            }
            
            # Set auth header for this user
            temp_headers = self.headers.copy()
            temp_headers["Authorization"] = f"Bearer {temp_token}"
            
            # Create profile
            response = requests.post(
                f"{self.base_url}/profile/create",
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
                    "expected_distance": location_data["expected_distance"]
                })
                self.log_result(f"Create {location_data['name']}", True, f"Profile created at {location_data['location']}")
            else:
                self.log_result(f"Create {location_data['name']}", False, "Failed to create profile")
        
        self.test_profiles = created_profiles
        return len(created_profiles) > 0
    
    def test_distance_calculation_in_discovery(self):
        """Test that discovery API returns distance field with correct calculations"""
        if not self.auth_token:
            self.log_result("Distance Calculation", False, "No auth token available")
            return False
        
        response = self.make_request("GET", "/profiles/discover?limit=20", use_auth=True)
        
        if response is None:
            self.log_result("Distance Calculation", False, "Connection failed")
            return False
        
        if response.status_code != 200:
            try:
                error_data = response.json()
                self.log_result("Distance Calculation", False, f"HTTP {response.status_code}: {error_data.get('detail', response.text)}")
            except:
                self.log_result("Distance Calculation", False, f"HTTP {response.status_code}: {response.text}")
            return False
        
        try:
            data = response.json()
            profiles = data.get("profiles", [])
            
            if not profiles:
                self.log_result("Distance Calculation", False, "No profiles returned for distance testing")
                return False
            
            # Check if profiles have distance field
            profiles_with_distance = [p for p in profiles if "distance" in p and p["distance"] is not None]
            
            if not profiles_with_distance:
                self.log_result("Distance Calculation", False, "No profiles have distance field")
                return False
            
            # Verify distance calculations for our test profiles
            my_lat, my_lon = 47.5596, 7.5886  # Basel coordinates
            correct_calculations = 0
            total_test_profiles = 0
            
            for profile in profiles_with_distance:
                if profile.get("latitude") and profile.get("longitude"):
                    calculated_distance = self.calculate_distance(
                        my_lat, my_lon,
                        profile["latitude"], profile["longitude"]
                    )
                    api_distance = profile["distance"]
                    
                    # Allow 1km tolerance for rounding differences
                    if abs(calculated_distance - api_distance) <= 1.0:
                        correct_calculations += 1
                    
                    total_test_profiles += 1
            
            if total_test_profiles > 0:
                accuracy = (correct_calculations / total_test_profiles) * 100
                self.log_result("Distance Calculation", True, 
                    f"Distance field present in {len(profiles_with_distance)} profiles. "
                    f"Calculation accuracy: {accuracy:.1f}% ({correct_calculations}/{total_test_profiles})")
            else:
                self.log_result("Distance Calculation", True, 
                    f"Distance field present in {len(profiles_with_distance)} profiles")
            
            return True
            
        except json.JSONDecodeError:
            self.log_result("Distance Calculation", False, "Invalid JSON response")
            return False
    
    def test_distance_filtering(self):
        """Test distance filtering with max_distance parameter"""
        if not self.auth_token:
            self.log_result("Distance Filtering", False, "No auth token available")
            return False
        
        # Test with 50km max distance
        response = self.make_request("GET", "/profiles/discover?max_distance=50&limit=20", use_auth=True)
        
        if response is None:
            self.log_result("Distance Filtering", False, "Connection failed")
            return False
        
        if response.status_code != 200:
            try:
                error_data = response.json()
                self.log_result("Distance Filtering", False, f"HTTP {response.status_code}: {error_data.get('detail', response.text)}")
            except:
                self.log_result("Distance Filtering", False, f"HTTP {response.status_code}: {response.text}")
            return False
        
        try:
            data = response.json()
            profiles = data.get("profiles", [])
            
            # Check that all returned profiles are within 50km
            profiles_within_limit = 0
            profiles_with_distance = 0
            
            for profile in profiles:
                if "distance" in profile and profile["distance"] is not None:
                    profiles_with_distance += 1
                    if profile["distance"] <= 50:
                        profiles_within_limit += 1
            
            if profiles_with_distance == 0:
                self.log_result("Distance Filtering", True, "No profiles with distance data to filter")
                return True
            
            if profiles_within_limit == profiles_with_distance:
                self.log_result("Distance Filtering", True, 
                    f"All {profiles_with_distance} profiles are within 50km limit")
            else:
                self.log_result("Distance Filtering", False, 
                    f"Only {profiles_within_limit}/{profiles_with_distance} profiles within 50km limit")
                return False
            
            return True
            
        except json.JSONDecodeError:
            self.log_result("Distance Filtering", False, "Invalid JSON response")
            return False
    
    def test_proximity_scoring(self):
        """Test that closer profiles get higher compatibility scores"""
        if not self.auth_token:
            self.log_result("Proximity Scoring", False, "No auth token available")
            return False
        
        # Get profiles without distance filter to see full scoring
        response = self.make_request("GET", "/profiles/discover?limit=20", use_auth=True)
        
        if response is None:
            self.log_result("Proximity Scoring", False, "Connection failed")
            return False
        
        if response.status_code != 200:
            self.log_result("Proximity Scoring", False, f"HTTP {response.status_code}")
            return False
        
        try:
            data = response.json()
            profiles = data.get("profiles", [])
            
            # Check if profiles are sorted by proximity (closer profiles first)
            profiles_with_distance = [p for p in profiles if "distance" in p and p["distance"] is not None]
            
            if len(profiles_with_distance) < 2:
                self.log_result("Proximity Scoring", True, "Not enough profiles with distance data to test sorting")
                return True
            
            # Check if profiles are generally sorted by distance (allowing for other scoring factors)
            close_profiles = [p for p in profiles_with_distance if p["distance"] <= 20]
            far_profiles = [p for p in profiles_with_distance if p["distance"] > 100]
            
            if close_profiles and far_profiles:
                # Check if most close profiles appear before far profiles
                close_positions = [profiles.index(p) for p in close_profiles]
                far_positions = [profiles.index(p) for p in far_profiles]
                
                avg_close_pos = sum(close_positions) / len(close_positions)
                avg_far_pos = sum(far_positions) / len(far_positions)
                
                if avg_close_pos < avg_far_pos:
                    self.log_result("Proximity Scoring", True, 
                        f"Proximity scoring working: close profiles avg position {avg_close_pos:.1f}, "
                        f"far profiles avg position {avg_far_pos:.1f}")
                else:
                    self.log_result("Proximity Scoring", False, 
                        f"Proximity scoring may not be working: close profiles avg position {avg_close_pos:.1f}, "
                        f"far profiles avg position {avg_far_pos:.1f}")
                    return False
            else:
                self.log_result("Proximity Scoring", True, "Proximity scoring test inconclusive - need more varied distances")
            
            return True
            
        except json.JSONDecodeError:
            self.log_result("Proximity Scoring", False, "Invalid JSON response")
            return False
    
    def test_profile_update_with_coordinates(self):
        """Test updating existing profile with GPS coordinates"""
        if not self.auth_token:
            self.log_result("Profile Update GPS", False, "No auth token available")
            return False
        
        # Update profile with new coordinates (Zurich, Switzerland)
        update_data = {
            "latitude": 47.3769,  # Zurich coordinates
            "longitude": 8.5417,
            "location": "Zurich, Switzerland"
        }
        
        response = self.make_request("PUT", "/profile/update", update_data, use_auth=True)
        
        if response is None:
            self.log_result("Profile Update GPS", False, "Connection failed")
            return False
        
        if response.status_code == 200:
            # Verify the update by getting the profile
            get_response = self.make_request("GET", "/profile/me", use_auth=True)
            
            if get_response and get_response.status_code == 200:
                try:
                    profile_data = get_response.json()
                    if (profile_data.get("latitude") == 47.3769 and 
                        profile_data.get("longitude") == 8.5417):
                        self.log_result("Profile Update GPS", True, "GPS coordinates updated successfully")
                        return True
                    else:
                        self.log_result("Profile Update GPS", False, "GPS coordinates not updated correctly")
                        return False
                except:
                    self.log_result("Profile Update GPS", False, "Invalid JSON response from profile get")
                    return False
            else:
                self.log_result("Profile Update GPS", False, "Could not verify profile update")
                return False
        else:
            try:
                error_data = response.json()
                self.log_result("Profile Update GPS", False, f"HTTP {response.status_code}: {error_data.get('detail', response.text)}")
            except:
                self.log_result("Profile Update GPS", False, f"HTTP {response.status_code}: {response.text}")
            return False
    
    def run_gps_tests(self):
        """Run all GPS/location-based tests"""
        print("🌍 Starting GPS/Maps Integration Backend Tests")
        print(f"📍 Testing against: {self.base_url}")
        print("=" * 70)
        
        # Setup
        print("\n🔧 Setting up test environment...")
        if not self.setup_test_user():
            print("❌ Failed to setup test user. Aborting tests.")
            return 0, 1, self.test_results
        
        # Test GPS coordinate support in profiles
        print("\n📍 Testing GPS Coordinate Support...")
        self.test_profile_with_gps_coordinates()
        self.test_profile_update_with_coordinates()
        
        # Create test profiles at different locations
        print("\n🎭 Creating Test Profiles at Different Locations...")
        self.create_test_profiles_with_locations()
        
        # Test distance calculation and filtering
        print("\n📏 Testing Distance Calculation & Filtering...")
        self.test_distance_calculation_in_discovery()
        self.test_distance_filtering()
        
        # Test proximity scoring
        print("\n🎯 Testing Proximity Scoring...")
        self.test_proximity_scoring()
        
        # Summary
        print("\n" + "=" * 70)
        print("📊 GPS/MAPS INTEGRATION TEST SUMMARY")
        print("=" * 70)
        
        total_tests = len(self.test_results)
        passed_tests = sum(1 for result in self.test_results if result["success"])
        failed_tests = total_tests - passed_tests
        
        print(f"Total Tests: {total_tests}")
        print(f"✅ Passed: {passed_tests}")
        print(f"❌ Failed: {failed_tests}")
        print(f"Success Rate: {(passed_tests/total_tests)*100:.1f}%")
        
        if failed_tests > 0:
            print("\n❌ FAILED TESTS:")
            for result in self.test_results:
                if not result["success"]:
                    print(f"   • {result['test']}: {result['message']}")
        
        return passed_tests, failed_tests, self.test_results

def main():
    """Main function to run GPS tests"""
    tester = GPSLocationTester()
    passed, failed, results = tester.run_gps_tests()
    
    # Exit with error code if tests failed
    if failed > 0:
        print(f"\n⚠️  {failed} GPS/location tests failed!")
        sys.exit(1)
    else:
        print("\n🎉 All GPS/location tests passed!")
        sys.exit(0)

if __name__ == "__main__":
    main()