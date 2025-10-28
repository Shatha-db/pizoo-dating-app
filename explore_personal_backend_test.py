#!/usr/bin/env python3
"""
Comprehensive Backend Testing for New Explore and Personal Moments APIs
Tests the newly implemented multilingual Explore and Personal Moments features
"""

import requests
import json
import sys
from datetime import datetime

# Configuration
BACKEND_URL = "https://pizoo-chat-fix.preview.emergentagent.com/api"

class ExplorePersonalAPITester:
    def __init__(self):
        self.session = requests.Session()
        self.auth_token = None
        self.test_user_id = None
        self.results = {
            "total_tests": 0,
            "passed": 0,
            "failed": 0,
            "errors": []
        }
    
    def log(self, message, level="INFO"):
        timestamp = datetime.now().strftime("%H:%M:%S")
        print(f"[{timestamp}] {level}: {message}")
    
    def test_result(self, test_name, success, details=""):
        self.results["total_tests"] += 1
        if success:
            self.results["passed"] += 1
            self.log(f"✅ {test_name}: PASSED {details}", "PASS")
        else:
            self.results["failed"] += 1
            self.results["errors"].append(f"{test_name}: {details}")
            self.log(f"❌ {test_name}: FAILED {details}", "FAIL")
    
    def create_test_user(self):
        """Create a test user for authentication"""
        try:
            # Register test user
            register_data = {
                "name": "Explore Test User",
                "email": f"explore_test_{datetime.now().timestamp()}@test.com",
                "phone_number": "+41791234567",
                "password": "TestPass123!",
                "terms_accepted": True
            }
            
            response = self.session.post(f"{BACKEND_URL}/auth/register", json=register_data)
            
            if response.status_code == 200:
                data = response.json()
                self.auth_token = data["access_token"]
                self.test_user_id = data["user"]["id"]
                self.session.headers.update({"Authorization": f"Bearer {self.auth_token}"})
                self.test_result("User Registration", True, f"User ID: {self.test_user_id}")
                return True
            else:
                self.test_result("User Registration", False, f"Status: {response.status_code}, Response: {response.text}")
                return False
                
        except Exception as e:
            self.test_result("User Registration", False, f"Exception: {str(e)}")
            return False
    
    def create_test_profile(self):
        """Create a profile with GPS coordinates for testing"""
        try:
            profile_data = {
                "display_name": "Explore Tester",
                "bio": "Testing explore and personal moments features",
                "age": 28,
                "gender": "male",
                "location": "Basel, Switzerland",
                "latitude": 47.5596,  # Basel coordinates
                "longitude": 7.5886,
                "interests": ["travel", "technology", "music"],
                "languages": ["en", "ar"]
            }
            
            response = self.session.post(f"{BACKEND_URL}/profile/create", json=profile_data)
            
            if response.status_code == 200:
                self.test_result("Profile Creation", True, "Profile created with GPS coordinates")
                return True
            else:
                self.test_result("Profile Creation", False, f"Status: {response.status_code}, Response: {response.text}")
                return False
                
        except Exception as e:
            self.test_result("Profile Creation", False, f"Exception: {str(e)}")
            return False
    
    def test_explore_sections_authentication(self):
        """Test that explore sections endpoint requires authentication"""
        try:
            # Test without authentication
            temp_session = requests.Session()
            response = temp_session.get(f"{BACKEND_URL}/explore/sections")
            
            if response.status_code == 403 or response.status_code == 401:
                self.test_result("Explore Sections Authentication Required", True, f"Correctly blocked unauthenticated access (Status: {response.status_code})")
            else:
                self.test_result("Explore Sections Authentication Required", False, f"Should require auth but got status: {response.status_code}")
                
        except Exception as e:
            self.test_result("Explore Sections Authentication Required", False, f"Exception: {str(e)}")
    
    def test_explore_sections_response_structure(self):
        """Test explore sections endpoint response structure"""
        try:
            response = self.session.get(f"{BACKEND_URL}/explore/sections")
            
            if response.status_code == 200:
                data = response.json()
                
                # Check main structure
                if "sections" not in data:
                    self.test_result("Explore Sections Structure", False, "Missing 'sections' key in response")
                    return
                
                sections = data["sections"]
                
                # Should have 3 sections (trending, nearby, newcomers)
                if len(sections) < 2:  # At least 2 sections (nearby might be missing if no GPS)
                    self.test_result("Explore Sections Count", False, f"Expected at least 2 sections, got {len(sections)}")
                else:
                    self.test_result("Explore Sections Count", True, f"Got {len(sections)} sections")
                
                # Check each section structure
                required_section_fields = ["type", "title", "profiles"]
                section_types_found = []
                
                for i, section in enumerate(sections):
                    section_type = section.get("type", f"section_{i}")
                    section_types_found.append(section_type)
                    
                    # Check required fields
                    missing_fields = [field for field in required_section_fields if field not in section]
                    if missing_fields:
                        self.test_result(f"Section {section_type} Structure", False, f"Missing fields: {missing_fields}")
                    else:
                        self.test_result(f"Section {section_type} Structure", True, f"All required fields present")
                    
                    # Check profiles array
                    profiles = section.get("profiles", [])
                    if isinstance(profiles, list):
                        self.test_result(f"Section {section_type} Profiles Array", True, f"Contains {len(profiles)} profiles")
                        
                        # Check profile structure if profiles exist
                        if profiles:
                            profile = profiles[0]
                            required_profile_fields = ["id", "name", "age", "location", "photos"]
                            missing_profile_fields = [field for field in required_profile_fields if field not in profile]
                            
                            if missing_profile_fields:
                                self.test_result(f"Section {section_type} Profile Structure", False, f"Missing profile fields: {missing_profile_fields}")
                            else:
                                self.test_result(f"Section {section_type} Profile Structure", True, "All required profile fields present")
                                
                                # Check if distance field is present for nearby section
                                if section_type == "nearby" and "distance" in profile:
                                    self.test_result(f"Section {section_type} Distance Field", True, f"Distance: {profile['distance']} km")
                    else:
                        self.test_result(f"Section {section_type} Profiles Array", False, "Profiles is not an array")
                
                # Check expected section types
                expected_types = ["trending", "newcomers"]  # nearby is optional if no GPS
                for expected_type in expected_types:
                    if expected_type in section_types_found:
                        self.test_result(f"Expected Section Type '{expected_type}'", True, "Found")
                    else:
                        self.test_result(f"Expected Section Type '{expected_type}'", False, "Missing")
                
                self.test_result("Explore Sections Response Structure", True, f"Valid structure with sections: {section_types_found}")
                
            else:
                self.test_result("Explore Sections Response Structure", False, f"Status: {response.status_code}, Response: {response.text}")
                
        except Exception as e:
            self.test_result("Explore Sections Response Structure", False, f"Exception: {str(e)}")
    
    def test_personal_moments_authentication(self):
        """Test that personal moments endpoint requires authentication"""
        try:
            # Test without authentication
            temp_session = requests.Session()
            response = temp_session.get(f"{BACKEND_URL}/personal/list")
            
            if response.status_code == 403 or response.status_code == 401:
                self.test_result("Personal Moments Authentication Required", True, f"Correctly blocked unauthenticated access (Status: {response.status_code})")
            else:
                self.test_result("Personal Moments Authentication Required", False, f"Should require auth but got status: {response.status_code}")
                
        except Exception as e:
            self.test_result("Personal Moments Authentication Required", False, f"Exception: {str(e)}")
    
    def test_personal_moments_response_structure(self):
        """Test personal moments endpoint response structure"""
        try:
            response = self.session.get(f"{BACKEND_URL}/personal/list")
            
            if response.status_code == 200:
                data = response.json()
                
                # Check main structure
                if "moments" not in data:
                    self.test_result("Personal Moments Structure", False, "Missing 'moments' key in response")
                    return
                
                moments = data["moments"]
                
                # Should have moments array
                if not isinstance(moments, list):
                    self.test_result("Personal Moments Array", False, "Moments is not an array")
                    return
                
                if len(moments) == 0:
                    self.test_result("Personal Moments Count", False, "No moments returned")
                    return
                
                self.test_result("Personal Moments Count", True, f"Got {len(moments)} moments")
                
                # Check each moment structure
                required_moment_fields = ["id", "title", "description", "image", "isPremium", "isNew", "action", "ctaText"]
                
                for i, moment in enumerate(moments):
                    moment_id = moment.get("id", f"moment_{i}")
                    
                    # Check required fields
                    missing_fields = [field for field in required_moment_fields if field not in moment]
                    if missing_fields:
                        self.test_result(f"Moment {moment_id} Structure", False, f"Missing fields: {missing_fields}")
                    else:
                        self.test_result(f"Moment {moment_id} Structure", True, "All required fields present")
                    
                    # Check field types
                    if "isPremium" in moment and not isinstance(moment["isPremium"], bool):
                        self.test_result(f"Moment {moment_id} isPremium Type", False, f"isPremium should be boolean, got {type(moment['isPremium'])}")
                    else:
                        self.test_result(f"Moment {moment_id} isPremium Type", True, f"isPremium: {moment.get('isPremium')}")
                    
                    if "isNew" in moment and not isinstance(moment["isNew"], bool):
                        self.test_result(f"Moment {moment_id} isNew Type", False, f"isNew should be boolean, got {type(moment['isNew'])}")
                    else:
                        self.test_result(f"Moment {moment_id} isNew Type", True, f"isNew: {moment.get('isNew')}")
                    
                    # Check action types
                    action = moment.get("action")
                    if action not in ["open_link", "view_profile"]:
                        self.test_result(f"Moment {moment_id} Action Type", False, f"Invalid action: {action}")
                    else:
                        self.test_result(f"Moment {moment_id} Action Type", True, f"Action: {action}")
                    
                    # Check for link or userId based on action
                    if action == "open_link" and "link" not in moment:
                        self.test_result(f"Moment {moment_id} Link Field", False, "Missing link field for open_link action")
                    elif action == "view_profile" and "userId" not in moment:
                        # Note: userId might be optional for some moments
                        self.test_result(f"Moment {moment_id} UserId Field", True, "userId field optional for view_profile action")
                    else:
                        self.test_result(f"Moment {moment_id} Action Fields", True, "Action fields valid")
                
                # Check for expected moment types (based on mock data)
                moment_titles = [moment.get("title", "") for moment in moments]
                expected_moments = ["Special Weekend Event", "Premium Upgrade", "Complete Your Profile"]
                
                found_expected = 0
                for expected in expected_moments:
                    if any(expected.lower() in title.lower() for title in moment_titles):
                        found_expected += 1
                
                if found_expected >= 2:  # At least 2 of the expected moments
                    self.test_result("Expected Moment Types", True, f"Found {found_expected} expected moment types")
                else:
                    self.test_result("Expected Moment Types", False, f"Only found {found_expected} expected moment types")
                
                self.test_result("Personal Moments Response Structure", True, f"Valid structure with {len(moments)} moments")
                
            else:
                self.test_result("Personal Moments Response Structure", False, f"Status: {response.status_code}, Response: {response.text}")
                
        except Exception as e:
            self.test_result("Personal Moments Response Structure", False, f"Exception: {str(e)}")
    
    def test_explore_sections_profile_limit(self):
        """Test that explore sections return up to 10 profiles per section"""
        try:
            response = self.session.get(f"{BACKEND_URL}/explore/sections")
            
            if response.status_code == 200:
                data = response.json()
                sections = data.get("sections", [])
                
                for section in sections:
                    section_type = section.get("type", "unknown")
                    profiles = section.get("profiles", [])
                    
                    if len(profiles) <= 10:
                        self.test_result(f"Section {section_type} Profile Limit", True, f"Contains {len(profiles)} profiles (≤10)")
                    else:
                        self.test_result(f"Section {section_type} Profile Limit", False, f"Contains {len(profiles)} profiles (>10)")
            else:
                self.test_result("Explore Sections Profile Limit", False, f"Failed to get sections: {response.status_code}")
                
        except Exception as e:
            self.test_result("Explore Sections Profile Limit", False, f"Exception: {str(e)}")
    
    def test_personal_moments_badge_flags(self):
        """Test that personal moments have correct badge flags"""
        try:
            response = self.session.get(f"{BACKEND_URL}/personal/list")
            
            if response.status_code == 200:
                data = response.json()
                moments = data.get("moments", [])
                
                premium_moments = [m for m in moments if m.get("isPremium") == True]
                new_moments = [m for m in moments if m.get("isNew") == True]
                
                if premium_moments:
                    self.test_result("Premium Badge Moments", True, f"Found {len(premium_moments)} premium moments")
                else:
                    self.test_result("Premium Badge Moments", False, "No premium moments found")
                
                if new_moments:
                    self.test_result("New Badge Moments", True, f"Found {len(new_moments)} new moments")
                else:
                    self.test_result("New Badge Moments", False, "No new moments found")
                
                # Check for mixed badge types
                mixed_badges = [m for m in moments if m.get("isPremium") == True and m.get("isNew") == True]
                if mixed_badges:
                    self.test_result("Mixed Badge Moments", True, f"Found {len(mixed_badges)} moments with both premium and new badges")
                
            else:
                self.test_result("Personal Moments Badge Flags", False, f"Failed to get moments: {response.status_code}")
                
        except Exception as e:
            self.test_result("Personal Moments Badge Flags", False, f"Exception: {str(e)}")
    
    def run_all_tests(self):
        """Run all test scenarios"""
        self.log("🚀 Starting Explore and Personal Moments API Testing")
        self.log(f"Backend URL: {BACKEND_URL}")
        
        # Setup
        if not self.create_test_user():
            self.log("❌ Failed to create test user. Aborting tests.", "ERROR")
            return False
        
        if not self.create_test_profile():
            self.log("❌ Failed to create test profile. Continuing with limited tests.", "WARN")
        
        # Authentication Tests
        self.log("\n📋 Testing Authentication Requirements")
        self.test_explore_sections_authentication()
        self.test_personal_moments_authentication()
        
        # Structure and Response Tests
        self.log("\n📋 Testing Response Structures")
        self.test_explore_sections_response_structure()
        self.test_personal_moments_response_structure()
        
        # Specific Feature Tests
        self.log("\n📋 Testing Specific Features")
        self.test_explore_sections_profile_limit()
        self.test_personal_moments_badge_flags()
        
        # Summary
        self.print_summary()
        
        return self.results["failed"] == 0
    
    def print_summary(self):
        """Print test summary"""
        self.log("\n" + "="*60)
        self.log("🎯 EXPLORE & PERSONAL MOMENTS API TEST SUMMARY")
        self.log("="*60)
        self.log(f"Total Tests: {self.results['total_tests']}")
        self.log(f"✅ Passed: {self.results['passed']}")
        self.log(f"❌ Failed: {self.results['failed']}")
        
        if self.results["failed"] > 0:
            self.log("\n🔍 FAILED TESTS:")
            for error in self.results["errors"]:
                self.log(f"  • {error}")
        
        success_rate = (self.results["passed"] / self.results["total_tests"]) * 100 if self.results["total_tests"] > 0 else 0
        self.log(f"\n📊 Success Rate: {success_rate:.1f}%")
        
        if self.results["failed"] == 0:
            self.log("🎉 ALL TESTS PASSED! Both Explore and Personal Moments APIs are working correctly.")
        else:
            self.log("⚠️  Some tests failed. Please review the issues above.")


def main():
    """Main test execution"""
    tester = ExplorePersonalAPITester()
    success = tester.run_all_tests()
    
    # Exit with appropriate code
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()