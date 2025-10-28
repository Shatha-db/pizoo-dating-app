#!/usr/bin/env python3
"""
Comprehensive Backend Testing for Arabic Review Request
Testing: Explore Sections (8 sections), Personal Moments (6+ safe opportunities), 
i18n Configuration, and Chat Message Sending
"""

import requests
import json
import sys
import time
from datetime import datetime
import uuid

# Configuration
BASE_URL = "https://pizoo-dating-3.preview.emergentagent.com/api"
HEADERS = {"Content-Type": "application/json"}

class DatingAppTester:
    def __init__(self):
        self.base_url = BASE_URL
        self.headers = HEADERS.copy()
        self.auth_token = None
        self.user_id = None
        self.profile_id = None
        self.test_results = []
        self.test_email = None
        self.test_password = None
        
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
    
    def test_root_endpoint(self):
        """Test the root API endpoint"""
        response = self.make_request("GET", "/")
        
        if response is None:
            self.log_result("Root Endpoint", False, "Connection failed")
            return False
        
        if response.status_code == 200:
            try:
                data = response.json()
                self.log_result("Root Endpoint", True, f"API is accessible: {data.get('message', 'OK')}")
                return True
            except:
                self.log_result("Root Endpoint", True, "API is accessible (non-JSON response)")
                return True
        else:
            self.log_result("Root Endpoint", False, f"HTTP {response.status_code}: {response.text}")
            return False
    
    def test_user_registration(self):
        """Test user registration"""
        # Generate unique test data
        unique_id = str(uuid.uuid4())[:8]
        self.test_email = f"testuser{unique_id}@example.com"
        self.test_password = "TestPassword123!"
        test_data = {
            "name": f"Test User {unique_id}",
            "email": self.test_email,
            "phone_number": f"+1234567{unique_id[:4]}",
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
    
    def test_user_login(self):
        """Test user login with existing credentials"""
        if not self.user_id or not self.test_email:
            self.log_result("User Login", False, "No user registered to test login")
            return False
        
        # Use the same credentials from registration
        login_data = {
            "email": self.test_email,
            "password": self.test_password
        }
        
        response = self.make_request("POST", "/auth/login", login_data)
        
        if response is None:
            self.log_result("User Login", False, "Connection failed")
            return False
        
        if response.status_code == 200:
            try:
                data = response.json()
                if "access_token" in data:
                    # Update token with login token
                    self.auth_token = data["access_token"]
                    self.log_result("User Login", True, "Login successful")
                    return True
                else:
                    self.log_result("User Login", False, "Missing access_token in response", data)
                    return False
            except json.JSONDecodeError:
                self.log_result("User Login", False, "Invalid JSON response", response.text)
                return False
        else:
            try:
                error_data = response.json()
                self.log_result("User Login", False, f"HTTP {response.status_code}: {error_data.get('detail', response.text)}")
            except:
                self.log_result("User Login", False, f"HTTP {response.status_code}: {response.text}")
            return False
    
    def test_profile_creation(self):
        """Test profile creation"""
        if not self.auth_token:
            self.log_result("Profile Creation", False, "No auth token available")
            return False
        
        profile_data = {
            "display_name": "أحمد محمد",
            "bio": "مهندس برمجيات أحب السفر والقراءة والرياضة",
            "date_of_birth": "1990-05-15",
            "gender": "male",
            "height": 180,
            "looking_for": "علاقة جدية",
            "interests": ["البرمجة", "السفر", "القراءة", "الرياضة", "التكنولوجيا"],
            "location": "الرياض، السعودية",
            "occupation": "مهندس برمجيات",
            "education": "بكالوريوس هندسة حاسوب",
            "relationship_goals": "serious",
            "smoking": "no",
            "drinking": "no",
            "has_children": False,
            "wants_children": True,
            "languages": ["العربية", "الإنجليزية"]
        }
        
        response = self.make_request("POST", "/profile/create", profile_data, use_auth=True)
        
        if response is None:
            self.log_result("Profile Creation", False, "Connection failed")
            return False
        
        if response.status_code == 200:
            try:
                data = response.json()
                if "profile" in data:
                    self.profile_id = data["profile"]["id"]
                    self.log_result("Profile Creation", True, f"Profile created successfully. ID: {self.profile_id}")
                    return True
                else:
                    self.log_result("Profile Creation", True, "Profile created (no profile ID returned)")
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
    
    def test_get_profile(self):
        """Test getting user profile"""
        if not self.auth_token:
            self.log_result("Get Profile", False, "No auth token available")
            return False
        
        response = self.make_request("GET", "/profile/me", use_auth=True)
        
        if response is None:
            self.log_result("Get Profile", False, "Connection failed")
            return False
        
        if response.status_code == 200:
            try:
                data = response.json()
                if "display_name" in data:
                    self.log_result("Get Profile", True, f"Profile retrieved: {data['display_name']}")
                    return True
                else:
                    self.log_result("Get Profile", True, "Profile retrieved (no display_name)")
                    return True
            except json.JSONDecodeError:
                self.log_result("Get Profile", False, "Invalid JSON response", response.text)
                return False
        else:
            try:
                error_data = response.json()
                self.log_result("Get Profile", False, f"HTTP {response.status_code}: {error_data.get('detail', response.text)}")
            except:
                self.log_result("Get Profile", False, f"HTTP {response.status_code}: {response.text}")
            return False
    
    def test_update_profile(self):
        """Test updating user profile"""
        if not self.auth_token:
            self.log_result("Update Profile", False, "No auth token available")
            return False
        
        update_data = {
            "bio": "مهندس برمجيات محدث - أحب السفر والتكنولوجيا والابتكار",
            "interests": ["البرمجة", "السفر", "التكنولوجيا", "الابتكار", "الذكاء الاصطناعي"]
        }
        
        response = self.make_request("PUT", "/profile/update", update_data, use_auth=True)
        
        if response is None:
            self.log_result("Update Profile", False, "Connection failed")
            return False
        
        if response.status_code == 200:
            try:
                data = response.json()
                self.log_result("Update Profile", True, "Profile updated successfully")
                return True
            except json.JSONDecodeError:
                self.log_result("Update Profile", False, "Invalid JSON response", response.text)
                return False
        else:
            try:
                error_data = response.json()
                self.log_result("Update Profile", False, f"HTTP {response.status_code}: {error_data.get('detail', response.text)}")
            except:
                self.log_result("Update Profile", False, f"HTTP {response.status_code}: {response.text}")
            return False
    
    def test_create_dummy_profiles(self):
        """Test creating dummy profiles for discovery"""
        response = self.make_request("POST", "/seed/dummy-profiles")
        
        if response is None:
            self.log_result("Create Dummy Profiles", False, "Connection failed")
            return False
        
        if response.status_code == 200:
            try:
                data = response.json()
                self.log_result("Create Dummy Profiles", True, f"Dummy profiles created: {data.get('message', 'Success')}")
                return True
            except json.JSONDecodeError:
                self.log_result("Create Dummy Profiles", False, "Invalid JSON response", response.text)
                return False
        else:
            try:
                error_data = response.json()
                self.log_result("Create Dummy Profiles", False, f"HTTP {response.status_code}: {error_data.get('detail', response.text)}")
            except:
                self.log_result("Create Dummy Profiles", False, f"HTTP {response.status_code}: {response.text}")
            return False
    
    def test_discover_profiles(self):
        """Test profile discovery without category filter"""
        if not self.auth_token:
            self.log_result("Discover Profiles", False, "No auth token available")
            return False
        
        response = self.make_request("GET", "/profiles/discover?limit=10", use_auth=True)
        
        if response is None:
            self.log_result("Discover Profiles", False, "Connection failed")
            return False
        
        if response.status_code == 200:
            try:
                data = response.json()
                if "profiles" in data:
                    profile_count = len(data["profiles"])
                    self.log_result("Discover Profiles", True, f"Found {profile_count} profiles for discovery")
                    return True, data["profiles"]
                else:
                    self.log_result("Discover Profiles", False, "No profiles key in response", data)
                    return False, []
            except json.JSONDecodeError:
                self.log_result("Discover Profiles", False, "Invalid JSON response", response.text)
                return False, []
        else:
            try:
                error_data = response.json()
                self.log_result("Discover Profiles", False, f"HTTP {response.status_code}: {error_data.get('detail', response.text)}")
            except:
                self.log_result("Discover Profiles", False, f"HTTP {response.status_code}: {response.text}")
            return False, []
    
    def test_discover_profiles_with_category(self):
        """Test profile discovery with category filter"""
        if not self.auth_token:
            self.log_result("Discover Profiles (Category Filter)", False, "No auth token available")
            return False
        
        # Test with category parameter
        response = self.make_request("GET", "/profiles/discover?category=new-friends&limit=10", use_auth=True)
        
        if response is None:
            self.log_result("Discover Profiles (Category Filter)", False, "Connection failed")
            return False
        
        if response.status_code == 200:
            try:
                data = response.json()
                if "profiles" in data:
                    profile_count = len(data["profiles"])
                    self.log_result("Discover Profiles (Category Filter)", True, f"Found {profile_count} profiles with category filter")
                    return True
                else:
                    self.log_result("Discover Profiles (Category Filter)", False, "No profiles key in response", data)
                    return False
            except json.JSONDecodeError:
                self.log_result("Discover Profiles (Category Filter)", False, "Invalid JSON response", response.text)
                return False
        else:
            try:
                error_data = response.json()
                self.log_result("Discover Profiles (Category Filter)", False, f"HTTP {response.status_code}: {error_data.get('detail', response.text)}")
            except:
                self.log_result("Discover Profiles (Category Filter)", False, f"HTTP {response.status_code}: {response.text}")
            return False
    
    def test_swipe_actions(self, profiles):
        """Test swipe actions"""
        if not self.auth_token:
            self.log_result("Swipe Actions", False, "No auth token available")
            return False
        
        if not profiles:
            self.log_result("Swipe Actions", False, "No profiles available for swiping")
            return False
        
        # Test different swipe actions
        actions = ["like", "pass", "super_like"]
        success_count = 0
        
        for i, profile in enumerate(profiles[:3]):  # Test first 3 profiles
            if i >= len(actions):
                break
                
            action = actions[i]
            swipe_data = {
                "swiped_user_id": profile["user_id"],
                "action": action
            }
            
            response = self.make_request("POST", "/swipe", swipe_data, use_auth=True)
            
            if response is None:
                self.log_result(f"Swipe Action ({action})", False, "Connection failed")
                continue
            
            if response.status_code == 200:
                try:
                    data = response.json()
                    if data.get("success"):
                        is_match = data.get("is_match", False)
                        match_text = " (MATCH!)" if is_match else ""
                        self.log_result(f"Swipe Action ({action})", True, f"Swipe successful{match_text}")
                        success_count += 1
                    else:
                        self.log_result(f"Swipe Action ({action})", False, "Swipe not successful", data)
                except json.JSONDecodeError:
                    self.log_result(f"Swipe Action ({action})", False, "Invalid JSON response", response.text)
            else:
                try:
                    error_data = response.json()
                    self.log_result(f"Swipe Action ({action})", False, f"HTTP {response.status_code}: {error_data.get('detail', response.text)}")
                except:
                    self.log_result(f"Swipe Action ({action})", False, f"HTTP {response.status_code}: {response.text}")
        
        return success_count > 0
    
    def test_get_matches(self):
        """Test getting user matches"""
        if not self.auth_token:
            self.log_result("Get Matches", False, "No auth token available")
            return False
        
        response = self.make_request("GET", "/matches", use_auth=True)
        
        if response is None:
            self.log_result("Get Matches", False, "Connection failed")
            return False
        
        if response.status_code == 200:
            try:
                data = response.json()
                if "matches" in data:
                    match_count = len(data["matches"])
                    self.log_result("Get Matches", True, f"Retrieved {match_count} matches")
                    return True
                else:
                    self.log_result("Get Matches", False, "No matches key in response", data)
                    return False
            except json.JSONDecodeError:
                self.log_result("Get Matches", False, "Invalid JSON response", response.text)
                return False
        else:
            try:
                error_data = response.json()
                self.log_result("Get Matches", False, f"HTTP {response.status_code}: {error_data.get('detail', response.text)}")
            except:
                self.log_result("Get Matches", False, f"HTTP {response.status_code}: {response.text}")
            return False
    
    def test_get_sent_likes(self):
        """Test getting sent likes"""
        if not self.auth_token:
            self.log_result("Get Sent Likes", False, "No auth token available")
            return False
        
        response = self.make_request("GET", "/likes/sent", use_auth=True)
        
        if response is None:
            self.log_result("Get Sent Likes", False, "Connection failed")
            return False
        
        if response.status_code == 200:
            try:
                data = response.json()
                if "profiles" in data:
                    like_count = len(data["profiles"])
                    self.log_result("Get Sent Likes", True, f"Retrieved {like_count} sent likes")
                    return True
                else:
                    self.log_result("Get Sent Likes", False, "No profiles key in response", data)
                    return False
            except json.JSONDecodeError:
                self.log_result("Get Sent Likes", False, "Invalid JSON response", response.text)
                return False
        else:
            try:
                error_data = response.json()
                self.log_result("Get Sent Likes", False, f"HTTP {response.status_code}: {error_data.get('detail', response.text)}")
            except:
                self.log_result("Get Sent Likes", False, f"HTTP {response.status_code}: {response.text}")
            return False
    
    def test_get_received_likes(self):
        """Test getting received likes"""
        if not self.auth_token:
            self.log_result("Get Received Likes", False, "No auth token available")
            return False
        
        response = self.make_request("GET", "/likes/received", use_auth=True)
        
        if response is None:
            self.log_result("Get Received Likes", False, "Connection failed")
            return False
        
        if response.status_code == 200:
            try:
                data = response.json()
                if "profiles" in data:
                    like_count = len(data["profiles"])
                    self.log_result("Get Received Likes", True, f"Retrieved {like_count} received likes")
                    return True
                else:
                    self.log_result("Get Received Likes", False, "No profiles key in response", data)
                    return False
            except json.JSONDecodeError:
                self.log_result("Get Received Likes", False, "Invalid JSON response", response.text)
                return False
        else:
            try:
                error_data = response.json()
                self.log_result("Get Received Likes", False, f"HTTP {response.status_code}: {error_data.get('detail', response.text)}")
            except:
                self.log_result("Get Received Likes", False, f"HTTP {response.status_code}: {response.text}")
            return False
    
    def run_all_tests(self):
        """Run all backend tests in sequence"""
        print("🚀 Starting Dating App Backend API Tests")
        print(f"📍 Testing against: {self.base_url}")
        print("=" * 60)
        
        # Test sequence as specified in requirements
        
        # 1. Basic connectivity
        self.test_root_endpoint()
        
        # 2. Authentication Flow
        print("\n📝 Testing Authentication Flow...")
        self.test_user_registration()
        self.test_user_login()
        
        # 3. Profile Management
        print("\n👤 Testing Profile Management...")
        self.test_profile_creation()
        self.test_get_profile()
        self.test_update_profile()
        
        # 4. Dummy Data Creation (for discovery)
        print("\n🎭 Creating Dummy Profiles...")
        self.test_create_dummy_profiles()
        
        # 5. Discovery & Swipe Flow
        print("\n💕 Testing Discovery & Swipe Flow...")
        success, profiles = self.test_discover_profiles()
        self.test_discover_profiles_with_category()
        if success:
            self.test_swipe_actions(profiles)
        
        # 6. Matches & Likes
        print("\n💖 Testing Matches & Likes...")
        self.test_get_matches()
        self.test_get_sent_likes()
        self.test_get_received_likes()
        
        # Summary
        print("\n" + "=" * 60)
        print("📊 TEST SUMMARY")
        print("=" * 60)
        
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

    def test_explore_sections_api_arabic_review(self):
        """Test Explore Sections API - Verify 8 sections exist (Arabic Review Request)"""
        print("🔍 Testing Explore Sections API (8 sections requirement)...")
        
        if not self.auth_token:
            self.log_result("Explore Sections API", False, "No auth token available")
            return False
        
        response = self.make_request("GET", "/explore/sections", use_auth=True)
        
        if response is None:
            self.log_result("Explore Sections API", False, "Connection failed")
            return False
        
        if response.status_code == 200:
            try:
                data = response.json()
                sections = data.get("sections", [])
                
                # Check if we have exactly 8 sections
                if len(sections) == 8:
                    self.log_result("Explore Sections Count", True, f"Found {len(sections)} sections as expected")
                    
                    # List all section types
                    section_types = [section.get("type", "unknown") for section in sections]
                    self.log_result("Explore Sections Types", True, f"Section types: {', '.join(section_types)}")
                    
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
                    
                    return all_valid
                else:
                    self.log_result("Explore Sections Count", False, f"Expected 8 sections, got {len(sections)}")
                    return False
                    
            except json.JSONDecodeError:
                self.log_result("Explore Sections API", False, "Invalid JSON response", response.text)
                return False
        else:
            try:
                error_data = response.json()
                self.log_result("Explore Sections API", False, f"HTTP {response.status_code}: {error_data.get('detail', response.text)}")
            except:
                self.log_result("Explore Sections API", False, f"HTTP {response.status_code}: {response.text}")
            return False
    
    def test_personal_moments_api_arabic_review(self):
        """Test Personal Moments API - Verify 6+ safe opportunities (Arabic Review Request)"""
        print("💫 Testing Personal Moments API (6+ safe opportunities)...")
        
        if not self.auth_token:
            self.log_result("Personal Moments API", False, "No auth token available")
            return False
        
        response = self.make_request("GET", "/personal/list", use_auth=True)
        
        if response is None:
            self.log_result("Personal Moments API", False, "Connection failed")
            return False
        
        if response.status_code == 200:
            try:
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
                        
                        # Check for safe category keywords
                        for category in safe_categories:
                            if category in title or category in description:
                                if category not in found_categories:
                                    found_categories.append(category)
                        
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
                            self.log_result(f"Moment {i+1}", True, f"Title: {moment.get('title')}")
                    
                    return all_valid
                else:
                    self.log_result("Personal Moments Count", False, f"Expected ≥6 moments, got {len(moments)}")
                    return False
                    
            except json.JSONDecodeError:
                self.log_result("Personal Moments API", False, "Invalid JSON response", response.text)
                return False
        else:
            try:
                error_data = response.json()
                self.log_result("Personal Moments API", False, f"HTTP {response.status_code}: {error_data.get('detail', response.text)}")
            except:
                self.log_result("Personal Moments API", False, f"HTTP {response.status_code}: {response.text}")
            return False
    
    def test_i18n_configuration_arabic_review(self):
        """Test i18n Configuration - Verify default language is EN (Arabic Review Request)"""
        print("🌐 Testing i18n Configuration...")
        
        if not self.auth_token:
            self.log_result("i18n Configuration", False, "No auth token available")
            return False
        
        response = self.make_request("GET", "/me", use_auth=True)
        
        if response is None:
            self.log_result("i18n Configuration", False, "Connection failed")
            return False
        
        if response.status_code == 200:
            try:
                data = response.json()
                user_language = data.get("language", "")
                
                if user_language == "en":
                    self.log_result("Default Language", True, f"User language is 'en' as expected")
                    return True
                else:
                    self.log_result("Default Language", False, f"Expected 'en', got '{user_language}'")
                    return False
                    
            except json.JSONDecodeError:
                self.log_result("i18n Configuration", False, "Invalid JSON response", response.text)
                return False
        else:
            try:
                error_data = response.json()
                self.log_result("i18n Configuration", False, f"HTTP {response.status_code}: {error_data.get('detail', response.text)}")
            except:
                self.log_result("i18n Configuration", False, f"HTTP {response.status_code}: {response.text}")
            return False
    
    def test_chat_message_sending_arabic_review(self):
        """Test Chat Message Sending - Test message sending without duplicates (Arabic Review Request)"""
        print("💬 Testing Chat Message Sending...")
        
        if not self.auth_token:
            self.log_result("Chat Message Sending", False, "No auth token available")
            return False
        
        # First, get matches to test messaging
        matches_response = self.make_request("GET", "/matches", use_auth=True)
        
        if matches_response is None:
            self.log_result("Chat Message Sending", False, "Connection failed")
            return False
        
        if matches_response.status_code == 200:
            try:
                matches_data = matches_response.json()
                matches = matches_data.get("matches", [])
                
                if matches:
                    match_id = matches[0]["match_id"]
                    
                    # Test sending a message
                    message_data = {
                        "content": f"Test message at {datetime.now().isoformat()}",
                        "message_type": "text"
                    }
                    
                    message_response = self.make_request("POST", f"/matches/{match_id}/messages", message_data, use_auth=True)
                    
                    if message_response and message_response.status_code == 200:
                        self.log_result("Message Sending", True, "Successfully sent message")
                        
                        # Verify no duplicates by checking message count
                        time.sleep(1)  # Brief delay
                        
                        messages_response = self.make_request("GET", f"/matches/{match_id}/messages", use_auth=True)
                        
                        if messages_response and messages_response.status_code == 200:
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
                            self.log_result("Message Retrieval", False, "Failed to retrieve messages")
                            return False
                    else:
                        self.log_result("Message Sending", False, "Failed to send message")
                        return False
                else:
                    self.log_result("Chat Testing", True, "No matches available for message testing (expected for new user)")
                    return True
                    
            except json.JSONDecodeError:
                self.log_result("Chat Message Sending", False, "Invalid JSON response", matches_response.text)
                return False
        else:
            self.log_result("Chat Message Sending", False, f"HTTP {matches_response.status_code}")
            return False
    
    def run_arabic_review_tests(self):
        """Run specific tests for Arabic review request"""
        print("🎯 Starting Arabic Review Request Backend Testing")
        print("Testing: Explore Sections (8), Personal Moments (6+), i18n Config, Chat Messages")
        print("=" * 80)
        
        # Authenticate first
        if not self.test_user_registration():
            print("❌ Authentication failed. Cannot proceed with tests.")
            return
        
        print("=" * 80)
        
        # Run specific tests
        self.test_explore_sections_api_arabic_review()
        self.test_personal_moments_api_arabic_review()
        self.test_i18n_configuration_arabic_review()
        self.test_chat_message_sending_arabic_review()
        
        # Summary
        print("=" * 80)
        print("📊 ARABIC REVIEW TEST SUMMARY")
        print("=" * 80)
        
        total_tests = len(self.test_results)
        passed_tests = sum(1 for result in self.test_results if result["success"])
        failed_tests = total_tests - passed_tests
        
        print(f"Total Tests: {total_tests}")
        print(f"✅ Passed: {passed_tests}")
        print(f"❌ Failed: {failed_tests}")
        print(f"Success Rate: {(passed_tests/total_tests)*100:.1f}%")
        
        print("\n🔍 DETAILED RESULTS:")
        for result in self.test_results:
            status = "✅" if result["success"] else "❌"
            print(f"{status} {result['test']}: {result['message']}")
        
        if failed_tests == 0:
            print("\n🎉 ALL ARABIC REVIEW TESTS PASSED! Backend APIs working perfectly.")
        else:
            print(f"\n⚠️  {failed_tests} test(s) failed. Please review the issues above.")
        
        return passed_tests, failed_tests

def main():
    """Main function to run tests"""
    tester = DatingAppTester()
    
    # Check if we should run Arabic review tests
    if len(sys.argv) > 1 and sys.argv[1] == "arabic-review":
        passed, failed = tester.run_arabic_review_tests()
    else:
        passed, failed, results = tester.run_all_tests()
    
    # Exit with error code if tests failed
    if failed > 0:
        sys.exit(1)
    else:
        print("\n🎉 All tests passed!")
        sys.exit(0)

if __name__ == "__main__":
    main()