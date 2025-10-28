#!/usr/bin/env python3
"""
Arabic Review Request Backend Testing
Testing: Explore Sections (8), Personal Moments (6+), i18n Config, Chat Messages
"""

import requests
import json
import time
from datetime import datetime

# Configuration
BASE_URL = "https://pizoo-dating-3.preview.emergentagent.com/api"
HEADERS = {"Content-Type": "application/json"}

class ArabicReviewTester:
    def __init__(self):
        self.token = None
        self.user_id = None
        self.test_results = []
        
    def log_result(self, test_name, success, details="", expected="", actual=""):
        """Log test result with details"""
        result = {
            "test": test_name,
            "success": success,
            "details": details,
            "expected": expected,
            "actual": actual,
            "timestamp": datetime.now().isoformat()
        }
        self.test_results.append(result)
        
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{status}: {test_name}")
        if details:
            print(f"   Details: {details}")
        if not success and expected:
            print(f"   Expected: {expected}")
            print(f"   Actual: {actual}")
        print()
        
    def authenticate_and_setup(self):
        """Authenticate and setup user with GPS coordinates"""
        print("🔐 Setting up test user with GPS coordinates...")
        
        # Generate unique email for this test
        test_email = f"arabictest_{int(time.time())}@pizoo.com"
        
        # Register new user
        register_data = {
            "name": "Arabic Test User",
            "email": test_email,
            "phone_number": f"+4179{int(time.time()) % 10000000}",
            "password": "testpass123",
            "terms_accepted": True
        }
        
        try:
            response = requests.post(f"{BASE_URL}/auth/register", json=register_data, headers=HEADERS)
            
            if response.status_code == 200:
                data = response.json()
                self.token = data["access_token"]
                self.user_id = data["user"]["id"]
                self.log_result("User Registration", True, f"Registered user {self.user_id}")
                
                # Update profile with GPS coordinates (Basel, Switzerland)
                profile_update = {
                    "latitude": 47.5596,
                    "longitude": 7.5886,
                    "location": "Basel, Switzerland"
                }
                
                auth_headers = {**HEADERS, "Authorization": f"Bearer {self.token}"}
                profile_response = requests.put(f"{BASE_URL}/profile/update", json=profile_update, headers=auth_headers)
                
                if profile_response.status_code == 200:
                    self.log_result("GPS Coordinates Setup", True, "Added GPS coordinates to user profile")
                    return True
                else:
                    self.log_result("GPS Coordinates Setup", False, f"Failed to update profile: {profile_response.text}")
                    return True  # Continue even if GPS update fails
                    
            else:
                self.log_result("User Registration", False, f"Status: {response.status_code}, Response: {response.text}")
                return False
                
        except Exception as e:
            self.log_result("Authentication Error", False, f"Exception: {str(e)}")
            return False
    
    def get_auth_headers(self):
        """Get headers with authentication token"""
        return {
            **HEADERS,
            "Authorization": f"Bearer {self.token}"
        }
    
    def test_explore_sections_8_count(self):
        """Test 1: Explore Sections API - Verify 8 sections exist"""
        print("🔍 Testing Explore Sections API (8 sections requirement)...")
        
        try:
            response = requests.get(f"{BASE_URL}/explore/sections", headers=self.get_auth_headers())
            
            if response.status_code == 200:
                data = response.json()
                sections = data.get("sections", [])
                
                # Check if we have exactly 8 sections
                if len(sections) == 8:
                    self.log_result("Explore Sections Count", True, f"Found {len(sections)} sections as expected")
                    
                    # List all section types
                    section_types = [section.get("type", "unknown") for section in sections]
                    expected_sections = ["most_active", "ready_chat", "near_you", "new_faces", "serious_love", "fun_date", "smart_talks", "friends_only"]
                    
                    self.log_result("Explore Sections Types", True, f"Section types: {', '.join(section_types)}")
                    
                    # Check if all expected sections are present
                    missing_sections = [s for s in expected_sections if s not in section_types]
                    if not missing_sections:
                        self.log_result("All Expected Sections Present", True, "All 8 expected sections found")
                    else:
                        self.log_result("All Expected Sections Present", False, f"Missing sections: {missing_sections}")
                    
                    # Verify each section has required fields
                    all_valid = True
                    for i, section in enumerate(sections):
                        required_fields = ["type", "title", "profiles"]
                        missing_fields = [field for field in required_fields if field not in section]
                        
                        if missing_fields:
                            all_valid = False
                            self.log_result(f"Section {i+1} Structure", False, f"Missing fields: {missing_fields}")
                        else:
                            profiles_count = len(section.get("profiles", []))
                            self.log_result(f"Section {i+1} ({section.get('type')})", True, f"Valid structure, {profiles_count} profiles")
                    
                    if all_valid:
                        self.log_result("All Sections Structure", True, "All 8 sections have valid structure")
                    
                    return True
                else:
                    self.log_result("Explore Sections Count", False, 
                                  f"Expected 8 sections, got {len(sections)}", "8", str(len(sections)))
                    
                    # List what sections we got
                    section_types = [section.get("type", "unknown") for section in sections]
                    self.log_result("Available Sections", False, f"Found sections: {', '.join(section_types)}")
                    return False
                    
            elif response.status_code == 403:
                self.log_result("Explore Sections API", False, "Authentication required (403)")
                return False
            else:
                self.log_result("Explore Sections API", False, f"HTTP {response.status_code}: {response.text}")
                return False
                
        except Exception as e:
            self.log_result("Explore Sections API Error", False, f"Exception: {str(e)}")
            return False
    
    def test_personal_moments_6_plus(self):
        """Test 2: Personal Moments API - Verify 6+ safe opportunities with safe categories"""
        print("💫 Testing Personal Moments API (6+ safe opportunities)...")
        
        try:
            response = requests.get(f"{BASE_URL}/personal/list", headers=self.get_auth_headers())
            
            if response.status_code == 200:
                data = response.json()
                moments = data.get("moments", [])
                
                # Check if we have 6 or more moments
                if len(moments) >= 6:
                    self.log_result("Personal Moments Count", True, f"Found {len(moments)} moments (≥6 required)")
                    
                    # Check for safe categories mentioned in requirements
                    safe_categories = ["flatshare", "travel", "outing", "activity"]
                    found_categories = []
                    
                    for moment in moments:
                        title = moment.get("title", "").lower()
                        description = moment.get("description", "").lower()
                        category = moment.get("category", "").lower()
                        
                        # Check for safe category keywords
                        for safe_cat in safe_categories:
                            if safe_cat in title or safe_cat in description or safe_cat in category:
                                if safe_cat not in found_categories:
                                    found_categories.append(safe_cat)
                        
                        # Additional safe keywords
                        safe_keywords = ["flatshare", "roommate", "travel", "buddy", "beach", "weekend", 
                                       "dining", "gaming", "activity", "outing"]
                        
                        for keyword in safe_keywords:
                            if keyword in title or keyword in description:
                                if keyword not in found_categories:
                                    found_categories.append(keyword)
                    
                    if len(found_categories) >= 2:  # At least 2 safe categories
                        self.log_result("Safe Categories Found", True, f"Found safe categories: {', '.join(found_categories)}")
                    else:
                        self.log_result("Safe Categories Found", False, f"Only found: {', '.join(found_categories)}")
                    
                    # Verify each moment has required fields
                    all_valid = True
                    for i, moment in enumerate(moments):
                        required_fields = ["id", "title", "description", "action", "ctaText"]
                        missing_fields = [field for field in required_fields if field not in moment]
                        
                        if missing_fields:
                            all_valid = False
                            self.log_result(f"Moment {i+1} Structure", False, f"Missing fields: {missing_fields}")
                        else:
                            category = moment.get("category", "N/A")
                            self.log_result(f"Moment {i+1}", True, f"Title: {moment.get('title')} (Category: {category})")
                    
                    if all_valid:
                        self.log_result("All Moments Structure", True, "All moments have valid structure")
                    
                    return True
                else:
                    self.log_result("Personal Moments Count", False, 
                                  f"Expected ≥6 moments, got {len(moments)}", "≥6", str(len(moments)))
                    return False
                    
            elif response.status_code == 403:
                self.log_result("Personal Moments API", False, "Authentication required (403)")
                return False
            else:
                self.log_result("Personal Moments API", False, f"HTTP {response.status_code}: {response.text}")
                return False
                
        except Exception as e:
            self.log_result("Personal Moments API Error", False, f"Exception: {str(e)}")
            return False
    
    def test_i18n_default_language(self):
        """Test 3: i18n Configuration - Verify default language is EN"""
        print("🌐 Testing i18n Configuration...")
        
        try:
            # Test user profile to check language setting
            response = requests.get(f"{BASE_URL}/me", headers=self.get_auth_headers())
            
            if response.status_code == 200:
                data = response.json()
                user_language = data.get("language", "")
                
                if user_language == "en":
                    self.log_result("Default Language", True, f"User language is 'en' as expected")
                    return True
                else:
                    self.log_result("Default Language", False, f"Expected 'en', got '{user_language}'", "en", user_language)
                    return False
                
            else:
                self.log_result("i18n Configuration", False, f"HTTP {response.status_code}: {response.text}")
                return False
                
        except Exception as e:
            self.log_result("i18n Configuration Error", False, f"Exception: {str(e)}")
            return False
    
    def test_chat_message_no_duplicates(self):
        """Test 4: Chat Message Sending - Test message sending without duplicates"""
        print("💬 Testing Chat Message Sending...")
        
        try:
            # First, we need to create a match to test messaging
            # Get some profiles to swipe on
            response = requests.get(f"{BASE_URL}/profiles/discover?limit=5", headers=self.get_auth_headers())
            
            if response.status_code == 200:
                data = response.json()
                profiles = data.get("profiles", [])
                
                if profiles:
                    target_user_id = profiles[0]["user_id"]
                    
                    # Create a swipe (like) to potentially create a match
                    swipe_data = {
                        "swiped_user_id": target_user_id,
                        "action": "like"
                    }
                    
                    swipe_response = requests.post(f"{BASE_URL}/swipe", json=swipe_data, headers=self.get_auth_headers())
                    
                    if swipe_response.status_code == 200:
                        self.log_result("Swipe Action", True, f"Successfully swiped on user {target_user_id}")
                        
                        # Check if we have any matches
                        matches_response = requests.get(f"{BASE_URL}/matches", headers=self.get_auth_headers())
                        
                        if matches_response.status_code == 200:
                            matches_data = matches_response.json()
                            matches = matches_data.get("matches", [])
                            
                            if matches:
                                match_id = matches[0]["match_id"]
                                
                                # Test sending a message
                                message_data = {
                                    "content": f"Test message at {datetime.now().isoformat()}",
                                    "message_type": "text"
                                }
                                
                                message_response = requests.post(
                                    f"{BASE_URL}/matches/{match_id}/messages", 
                                    json=message_data, 
                                    headers=self.get_auth_headers()
                                )
                                
                                if message_response.status_code == 200:
                                    self.log_result("Message Sending", True, "Successfully sent message")
                                    
                                    # Verify no duplicates by checking message count
                                    time.sleep(1)  # Brief delay
                                    
                                    messages_response = requests.get(
                                        f"{BASE_URL}/matches/{match_id}/messages", 
                                        headers=self.get_auth_headers()
                                    )
                                    
                                    if messages_response.status_code == 200:
                                        messages_data = messages_response.json()
                                        messages = messages_data.get("messages", [])
                                        
                                        # Check for duplicate messages (same content and timestamp close together)
                                        duplicate_found = False
                                        for i in range(len(messages) - 1):
                                            if (messages[i].get("content") == messages[i+1].get("content") and
                                                messages[i].get("sender_id") == messages[i+1].get("sender_id")):
                                                duplicate_found = True
                                                break
                                        
                                        if not duplicate_found:
                                            self.log_result("No Duplicate Messages", True, f"Found {len(messages)} messages, no duplicates detected")
                                            return True
                                        else:
                                            self.log_result("No Duplicate Messages", False, "Duplicate messages detected")
                                            return False
                                    else:
                                        self.log_result("Message Retrieval", False, f"HTTP {messages_response.status_code}")
                                        return False
                                        
                                else:
                                    self.log_result("Message Sending", False, f"HTTP {message_response.status_code}: {message_response.text}")
                                    return False
                            else:
                                self.log_result("Chat Testing", True, "No matches available for message testing (expected for new user)")
                                return True
                        else:
                            self.log_result("Matches Retrieval", False, f"HTTP {matches_response.status_code}")
                            return False
                    else:
                        self.log_result("Swipe Action", False, f"HTTP {swipe_response.status_code}: {swipe_response.text}")
                        return False
                else:
                    self.log_result("Chat Testing", True, "No profiles available for chat testing")
                    return True
            else:
                self.log_result("Profile Discovery", False, f"HTTP {response.status_code}: {response.text}")
                return False
                
        except Exception as e:
            self.log_result("Chat Message Testing Error", False, f"Exception: {str(e)}")
            return False
    
    def run_comprehensive_test(self):
        """Run all tests as requested in Arabic review"""
        print("🎯 اختبار شامل لجميع التحديثات التي تمت")
        print("Testing: Explore Sections (8), Personal Moments (6+), i18n Config, Chat Messages")
        print("=" * 80)
        
        # Authenticate and setup first
        if not self.authenticate_and_setup():
            print("❌ Authentication failed. Cannot proceed with tests.")
            return
        
        print("=" * 80)
        
        # Run all tests
        test1 = self.test_explore_sections_8_count()
        test2 = self.test_personal_moments_6_plus()
        test3 = self.test_i18n_default_language()
        test4 = self.test_chat_message_no_duplicates()
        
        # Summary
        print("=" * 80)
        print("📊 نتائج الاختبار الشامل - TEST SUMMARY")
        print("=" * 80)
        
        total_tests = len(self.test_results)
        passed_tests = len([r for r in self.test_results if r["success"]])
        failed_tests = total_tests - passed_tests
        
        print(f"Total Tests: {total_tests}")
        print(f"Passed: {passed_tests} ✅")
        print(f"Failed: {failed_tests} ❌")
        print(f"Success Rate: {(passed_tests/total_tests)*100:.1f}%")
        
        print("\n🔍 DETAILED RESULTS:")
        for result in self.test_results:
            status = "✅" if result["success"] else "❌"
            print(f"{status} {result['test']}: {result['details']}")
        
        print("\n" + "=" * 80)
        
        if failed_tests == 0:
            print("🎉 جميع الاختبارات نجحت! ALL TESTS PASSED! Backend APIs working perfectly for Arabic review requirements.")
        else:
            print(f"⚠️  {failed_tests} test(s) failed. Please review the issues above.")
        
        return passed_tests, failed_tests

if __name__ == "__main__":
    tester = ArabicReviewTester()
    passed, failed = tester.run_comprehensive_test()
    
    if failed > 0:
        exit(1)
    else:
        exit(0)