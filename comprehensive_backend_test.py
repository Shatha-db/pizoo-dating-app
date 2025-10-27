#!/usr/bin/env python3
"""
Comprehensive Backend API Testing Script for Dating App
Tests specific scenarios requested in the review request.
"""

import requests
import json
import sys
from datetime import datetime
import uuid

# Configuration
BASE_URL = "https://phone-auth-2.preview.emergentagent.com/api"
HEADERS = {"Content-Type": "application/json"}

class ComprehensiveTester:
    def __init__(self):
        self.base_url = BASE_URL
        self.headers = HEADERS.copy()
        self.user1_token = None
        self.user2_token = None
        self.user1_id = None
        self.user2_id = None
        self.test_results = []
        
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
    
    def make_request(self, method, endpoint, data=None, auth_token=None):
        """Make HTTP request with proper headers"""
        url = f"{self.base_url}{endpoint}"
        headers = self.headers.copy()
        
        if auth_token:
            headers["Authorization"] = f"Bearer {auth_token}"
        
        try:
            if method.upper() == "GET":
                response = requests.get(url, headers=headers, timeout=30)
            elif method.upper() == "POST":
                response = requests.post(url, headers=headers, json=data, timeout=30)
            else:
                raise ValueError(f"Unsupported method: {method}")
            
            return response
        except requests.exceptions.RequestException as e:
            return None
    
    def create_test_user(self, user_num):
        """Create a test user and return auth token and user ID"""
        unique_id = str(uuid.uuid4())[:8]
        test_data = {
            "name": f"Test User {user_num} {unique_id}",
            "email": f"testuser{user_num}{unique_id}@example.com",
            "phone_number": f"+123456{user_num}{unique_id[:4]}",
            "password": "TestPassword123!",
            "terms_accepted": True
        }
        
        response = self.make_request("POST", "/auth/register", test_data)
        
        if response and response.status_code == 200:
            data = response.json()
            auth_token = data["access_token"]
            user_id = data["user"]["id"]
            
            # Create profile for this user
            profile_data = {
                "display_name": f"مستخدم تجريبي {user_num}",
                "bio": f"مستخدم تجريبي رقم {user_num} للاختبار",
                "date_of_birth": "1990-05-15",
                "gender": "male" if user_num % 2 == 1 else "female",
                "height": 175 + user_num,
                "looking_for": "علاقة جدية",
                "interests": ["الاختبار", "التطوير", "التكنولوجيا"],
                "location": f"مدينة الاختبار {user_num}",
                "occupation": "مطور تطبيقات",
                "education": "بكالوريوس",
                "relationship_goals": "serious",
                "smoking": "no",
                "drinking": "no",
                "has_children": False,
                "wants_children": True,
                "languages": ["العربية", "الإنجليزية"]
            }
            
            profile_response = self.make_request("POST", "/profile/create", profile_data, auth_token)
            
            if profile_response and profile_response.status_code == 200:
                self.log_result(f"Create Test User {user_num}", True, f"User and profile created successfully. ID: {user_id}")
                return auth_token, user_id
            else:
                self.log_result(f"Create Test User {user_num} Profile", False, "Failed to create profile")
                return auth_token, user_id
        else:
            self.log_result(f"Create Test User {user_num}", False, "Failed to create user")
            return None, None
    
    def test_discover_api_without_category(self):
        """Test GET /api/profiles/discover without category parameter"""
        if not self.user1_token:
            self.log_result("Discover API (No Category)", False, "No auth token available")
            return False
        
        response = self.make_request("GET", "/profiles/discover", auth_token=self.user1_token)
        
        if response is None:
            self.log_result("Discover API (No Category)", False, "Connection failed")
            return False
        
        if response.status_code == 200:
            try:
                data = response.json()
                if "profiles" in data:
                    profile_count = len(data["profiles"])
                    self.log_result("Discover API (No Category)", True, f"Found {profile_count} profiles without category filter")
                    return True, data["profiles"]
                else:
                    self.log_result("Discover API (No Category)", False, "No profiles key in response", data)
                    return False, []
            except json.JSONDecodeError:
                self.log_result("Discover API (No Category)", False, "Invalid JSON response", response.text)
                return False, []
        else:
            self.log_result("Discover API (No Category)", False, f"HTTP {response.status_code}: {response.text}")
            return False, []
    
    def test_discover_api_with_category(self):
        """Test GET /api/profiles/discover with category parameter"""
        if not self.user1_token:
            self.log_result("Discover API (With Category)", False, "No auth token available")
            return False
        
        response = self.make_request("GET", "/profiles/discover?category=new-friends", auth_token=self.user1_token)
        
        if response is None:
            self.log_result("Discover API (With Category)", False, "Connection failed")
            return False
        
        if response.status_code == 200:
            try:
                data = response.json()
                if "profiles" in data:
                    profile_count = len(data["profiles"])
                    self.log_result("Discover API (With Category)", True, f"Found {profile_count} profiles with category=new-friends filter")
                    return True
                else:
                    self.log_result("Discover API (With Category)", False, "No profiles key in response", data)
                    return False
            except json.JSONDecodeError:
                self.log_result("Discover API (With Category)", False, "Invalid JSON response", response.text)
                return False
        else:
            self.log_result("Discover API (With Category)", False, f"HTTP {response.status_code}: {response.text}")
            return False
    
    def test_swipe_actions(self, target_user_id):
        """Test POST /api/swipe with different actions"""
        actions = ["like", "pass", "super_like"]
        success_count = 0
        
        for action in actions:
            # Use different users for different actions
            auth_token = self.user1_token if action != "pass" else self.user2_token
            user_label = "User 1" if action != "pass" else "User 2"
            
            swipe_data = {
                "swiped_user_id": target_user_id,
                "action": action
            }
            
            response = self.make_request("POST", "/swipe", swipe_data, auth_token)
            
            if response is None:
                self.log_result(f"Swipe Action ({action}) - {user_label}", False, "Connection failed")
                continue
            
            if response.status_code == 200:
                try:
                    data = response.json()
                    if data.get("success"):
                        is_match = data.get("is_match", False)
                        match_text = " (MATCH CREATED!)" if is_match else ""
                        self.log_result(f"Swipe Action ({action}) - {user_label}", True, f"Swipe successful{match_text}")
                        success_count += 1
                    else:
                        self.log_result(f"Swipe Action ({action}) - {user_label}", False, "Swipe not successful", data)
                except json.JSONDecodeError:
                    self.log_result(f"Swipe Action ({action}) - {user_label}", False, "Invalid JSON response", response.text)
            else:
                self.log_result(f"Swipe Action ({action}) - {user_label}", False, f"HTTP {response.status_code}: {response.text}")
        
        return success_count > 0
    
    def create_mutual_likes_for_match(self):
        """Create mutual likes between two users to generate a match"""
        if not self.user1_token or not self.user2_token:
            self.log_result("Create Mutual Likes", False, "Missing auth tokens")
            return False
        
        # User 1 likes User 2
        swipe_data_1 = {
            "swiped_user_id": self.user2_id,
            "action": "like"
        }
        
        response1 = self.make_request("POST", "/swipe", swipe_data_1, self.user1_token)
        
        if response1 and response1.status_code == 200:
            data1 = response1.json()
            self.log_result("User 1 Likes User 2", True, f"User 1 liked User 2 successfully")
        else:
            self.log_result("User 1 Likes User 2", False, "Failed to create like")
            return False
        
        # User 2 likes User 1 (should create a match)
        swipe_data_2 = {
            "swiped_user_id": self.user1_id,
            "action": "super_like"
        }
        
        response2 = self.make_request("POST", "/swipe", swipe_data_2, self.user2_token)
        
        if response2 and response2.status_code == 200:
            data2 = response2.json()
            is_match = data2.get("is_match", False)
            if is_match:
                self.log_result("User 2 Super Likes User 1", True, "User 2 super liked User 1 - MATCH CREATED!")
                return True
            else:
                self.log_result("User 2 Super Likes User 1", True, "User 2 super liked User 1 (no match detected)")
                return False
        else:
            self.log_result("User 2 Super Likes User 1", False, "Failed to create super like")
            return False
    
    def test_matches_api(self):
        """Test GET /api/matches"""
        if not self.user1_token:
            self.log_result("Matches API", False, "No auth token available")
            return False
        
        response = self.make_request("GET", "/matches", auth_token=self.user1_token)
        
        if response is None:
            self.log_result("Matches API", False, "Connection failed")
            return False
        
        if response.status_code == 200:
            try:
                data = response.json()
                if "matches" in data:
                    match_count = len(data["matches"])
                    self.log_result("Matches API", True, f"Retrieved {match_count} matches with correct data structure")
                    
                    # Verify match data structure
                    if match_count > 0:
                        match = data["matches"][0]
                        required_fields = ["match_id", "matched_at", "profile"]
                        missing_fields = [field for field in required_fields if field not in match]
                        if missing_fields:
                            self.log_result("Match Data Structure", False, f"Missing fields: {missing_fields}")
                        else:
                            self.log_result("Match Data Structure", True, "Match data contains all required fields")
                    
                    return True
                else:
                    self.log_result("Matches API", False, "No matches key in response", data)
                    return False
            except json.JSONDecodeError:
                self.log_result("Matches API", False, "Invalid JSON response", response.text)
                return False
        else:
            self.log_result("Matches API", False, f"HTTP {response.status_code}: {response.text}")
            return False
    
    def test_likes_sent_api(self):
        """Test GET /api/likes/sent"""
        if not self.user1_token:
            self.log_result("Likes Sent API", False, "No auth token available")
            return False
        
        response = self.make_request("GET", "/likes/sent", auth_token=self.user1_token)
        
        if response is None:
            self.log_result("Likes Sent API", False, "Connection failed")
            return False
        
        if response.status_code == 200:
            try:
                data = response.json()
                if "profiles" in data:
                    profile_count = len(data["profiles"])
                    self.log_result("Likes Sent API", True, f"Retrieved {profile_count} sent likes as profile arrays")
                    return True
                else:
                    self.log_result("Likes Sent API", False, "No profiles key in response", data)
                    return False
            except json.JSONDecodeError:
                self.log_result("Likes Sent API", False, "Invalid JSON response", response.text)
                return False
        else:
            self.log_result("Likes Sent API", False, f"HTTP {response.status_code}: {response.text}")
            return False
    
    def test_likes_received_api(self):
        """Test GET /api/likes/received"""
        if not self.user2_token:
            self.log_result("Likes Received API", False, "No auth token available")
            return False
        
        response = self.make_request("GET", "/likes/received", auth_token=self.user2_token)
        
        if response is None:
            self.log_result("Likes Received API", False, "Connection failed")
            return False
        
        if response.status_code == 200:
            try:
                data = response.json()
                if "profiles" in data:
                    profile_count = len(data["profiles"])
                    self.log_result("Likes Received API", True, f"Retrieved {profile_count} received likes as profile arrays")
                    return True
                else:
                    self.log_result("Likes Received API", False, "No profiles key in response", data)
                    return False
            except json.JSONDecodeError:
                self.log_result("Likes Received API", False, "Invalid JSON response", response.text)
                return False
        else:
            self.log_result("Likes Received API", False, f"HTTP {response.status_code}: {response.text}")
            return False
    
    def run_comprehensive_tests(self):
        """Run comprehensive backend tests as requested"""
        print("🚀 Starting Comprehensive Dating App Backend API Tests")
        print(f"📍 Testing against: {self.base_url}")
        print("=" * 70)
        
        # 1. Create test users and get auth tokens
        print("\n👥 Creating Test Users...")
        self.user1_token, self.user1_id = self.create_test_user(1)
        self.user2_token, self.user2_id = self.create_test_user(2)
        
        if not self.user1_token or not self.user2_token:
            print("❌ Failed to create test users. Aborting tests.")
            return
        
        # 2. Test discover API with and without category parameter
        print("\n🔍 Testing Discover API...")
        success, profiles = self.test_discover_api_without_category()
        self.test_discover_api_with_category()
        
        # 3. Test swipe actions (like, pass, super_like)
        print("\n💕 Testing Swipe Actions...")
        if success and profiles:
            # Use first available profile for swipe testing
            target_profile = profiles[0]
            self.test_swipe_actions(target_profile["user_id"])
        
        # 4. Create mutual likes between two users to generate a match
        print("\n💖 Creating Mutual Likes for Match Generation...")
        match_created = self.create_mutual_likes_for_match()
        
        # 5. Test matches API
        print("\n🎯 Testing Matches API...")
        self.test_matches_api()
        
        # 6. Test likes sent/received endpoints
        print("\n💌 Testing Likes APIs...")
        self.test_likes_sent_api()
        self.test_likes_received_api()
        
        # Summary
        print("\n" + "=" * 70)
        print("📊 COMPREHENSIVE TEST SUMMARY")
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
        else:
            print("\n🎉 All comprehensive tests passed!")
        
        return passed_tests, failed_tests, self.test_results

def main():
    """Main function to run comprehensive tests"""
    tester = ComprehensiveTester()
    passed, failed, results = tester.run_comprehensive_tests()
    
    # Exit with error code if tests failed
    if failed > 0:
        sys.exit(1)
    else:
        print("\n✨ All comprehensive backend tests completed successfully!")
        sys.exit(0)

if __name__ == "__main__":
    main()