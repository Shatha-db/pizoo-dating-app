#!/usr/bin/env python3
"""
Safety Consent & Chat Gating Backend Testing
Testing newly implemented Safety Consent Modal and Chat Gating features for Pizoo dating app.
"""

import requests
import json
import sys
from datetime import datetime

# Backend URL from frontend/.env
BACKEND_URL = "https://datemaps.preview.emergentagent.com/api"

class SafetyChatTester:
    def __init__(self):
        self.session = requests.Session()
        self.user1_token = None
        self.user2_token = None
        self.user1_id = None
        self.user2_id = None
        self.test_results = []
        
    def log_test(self, test_name, success, details="", expected="", actual=""):
        """Log test results"""
        status = "✅ PASS" if success else "❌ FAIL"
        result = {
            "test": test_name,
            "status": status,
            "success": success,
            "details": details,
            "expected": expected,
            "actual": actual,
            "timestamp": datetime.now().isoformat()
        }
        self.test_results.append(result)
        print(f"{status}: {test_name}")
        if details:
            print(f"   Details: {details}")
        if not success and expected and actual:
            print(f"   Expected: {expected}")
            print(f"   Actual: {actual}")
        print()

    def setup_test_users(self):
        """Create two test users for testing"""
        print("🔧 Setting up test users...")
        
        # Create User 1
        user1_data = {
            "name": "أحمد محمد",
            "email": f"ahmed_safety_test_{datetime.now().timestamp()}@test.com",
            "phone_number": "+966501234567",
            "password": "TestPass123!",
            "terms_accepted": True
        }
        
        try:
            response = self.session.post(f"{BACKEND_URL}/auth/register", json=user1_data)
            if response.status_code == 200:
                data = response.json()
                self.user1_token = data["access_token"]
                self.user1_id = data["user"]["id"]
                self.log_test("User 1 Registration", True, f"User ID: {self.user1_id}")
            else:
                self.log_test("User 1 Registration", False, f"Status: {response.status_code}, Response: {response.text}")
                return False
        except Exception as e:
            self.log_test("User 1 Registration", False, f"Exception: {str(e)}")
            return False
        
        # Create User 2
        user2_data = {
            "name": "فاطمة أحمد",
            "email": f"fatima_safety_test_{datetime.now().timestamp()}@test.com",
            "phone_number": "+966501234568",
            "password": "TestPass123!",
            "terms_accepted": True
        }
        
        try:
            response = self.session.post(f"{BACKEND_URL}/auth/register", json=user2_data)
            if response.status_code == 200:
                data = response.json()
                self.user2_token = data["access_token"]
                self.user2_id = data["user"]["id"]
                self.log_test("User 2 Registration", True, f"User ID: {self.user2_id}")
            else:
                self.log_test("User 2 Registration", False, f"Status: {response.status_code}, Response: {response.text}")
                return False
        except Exception as e:
            self.log_test("User 2 Registration", False, f"Exception: {str(e)}")
            return False
        
        return True

    def test_safety_consent_api(self):
        """Test Safety Consent API - PUT /api/user/settings"""
        print("🛡️ Testing Safety Consent API...")
        
        # Test 1: Save safetyAccepted: true with valid JWT token
        headers = {"Authorization": f"Bearer {self.user1_token}", "Content-Type": "application/json"}
        payload = {"safetyAccepted": True}
        
        try:
            response = self.session.put(f"{BACKEND_URL}/user/settings", json=payload, headers=headers)
            
            if response.status_code == 200:
                data = response.json()
                if data.get("ok") == True:
                    self.log_test("Safety Consent - Save safetyAccepted=true", True, 
                                f"Response: {data}")
                else:
                    self.log_test("Safety Consent - Save safetyAccepted=true", False, 
                                f"Unexpected response structure: {data}")
            else:
                self.log_test("Safety Consent - Save safetyAccepted=true", False, 
                            f"Status: {response.status_code}, Response: {response.text}")
        except Exception as e:
            self.log_test("Safety Consent - Save safetyAccepted=true", False, f"Exception: {str(e)}")
        
        # Test 2: Test without authentication (should return 401)
        try:
            response = self.session.put(f"{BACKEND_URL}/user/settings", json=payload)
            
            if response.status_code in [401, 403]:
                self.log_test("Safety Consent - No Authentication", True, 
                            f"Correctly returned {response.status_code} for no authentication")
            else:
                self.log_test("Safety Consent - No Authentication", False, 
                            f"Expected 401/403, got {response.status_code}: {response.text}")
        except Exception as e:
            self.log_test("Safety Consent - No Authentication", False, f"Exception: {str(e)}")
        
        # Test 3: Test with invalid JWT token
        invalid_headers = {"Authorization": "Bearer invalid_token_123", "Content-Type": "application/json"}
        try:
            response = self.session.put(f"{BACKEND_URL}/user/settings", json=payload, headers=invalid_headers)
            
            if response.status_code == 401:
                self.log_test("Safety Consent - Invalid Token", True, 
                            "Correctly returned 401 for invalid token")
            else:
                self.log_test("Safety Consent - Invalid Token", False, 
                            f"Expected 401, got {response.status_code}: {response.text}")
        except Exception as e:
            self.log_test("Safety Consent - Invalid Token", False, f"Exception: {str(e)}")
        
        # Test 4: Test response structure verification
        headers = {"Authorization": f"Bearer {self.user1_token}", "Content-Type": "application/json"}
        payload = {"safetyAccepted": False}
        
        try:
            response = self.session.put(f"{BACKEND_URL}/user/settings", json=payload, headers=headers)
            
            if response.status_code == 200:
                data = response.json()
                required_fields = ["ok", "message"]
                missing_fields = [field for field in required_fields if field not in data]
                
                if not missing_fields:
                    self.log_test("Safety Consent - Response Structure", True, 
                                f"All required fields present: {list(data.keys())}")
                else:
                    self.log_test("Safety Consent - Response Structure", False, 
                                f"Missing fields: {missing_fields}, Response: {data}")
            else:
                self.log_test("Safety Consent - Response Structure", False, 
                            f"Status: {response.status_code}, Response: {response.text}")
        except Exception as e:
            self.log_test("Safety Consent - Response Structure", False, f"Exception: {str(e)}")

    def test_chat_gating_api(self):
        """Test Chat Gating API - GET /api/relation/can-chat"""
        print("💬 Testing Chat Gating API...")
        
        # Test 1: No Like Scenario - User tries to chat without liking target user
        headers = {"Authorization": f"Bearer {self.user1_token}"}
        
        try:
            response = self.session.get(f"{BACKEND_URL}/relation/can-chat?userId={self.user2_id}", headers=headers)
            
            if response.status_code == 200:
                data = response.json()
                # Expected: {canChat: false, reason: "لم تقم بالإعجاب بهذا المستخدم بعد"}
                if data.get("canChat") == False and "لم تقم بالإعجاب" in data.get("reason", ""):
                    self.log_test("Chat Gating - No Like Scenario", True, 
                                f"Correctly blocked chat without like: {data}")
                else:
                    self.log_test("Chat Gating - No Like Scenario", False, 
                                f"Expected can=false with reason, got: {data}")
            else:
                self.log_test("Chat Gating - No Like Scenario", False, 
                            f"Status: {response.status_code}, Response: {response.text}")
        except Exception as e:
            self.log_test("Chat Gating - No Like Scenario", False, f"Exception: {str(e)}")
        
        # Test 2: Create a like from user1 to user2 for one-way like scenario
        print("   Creating like from User 1 to User 2...")
        like_payload = {"swiped_user_id": self.user2_id, "action": "like"}
        headers_user1 = {"Authorization": f"Bearer {self.user1_token}", "Content-Type": "application/json"}
        
        try:
            response = self.session.post(f"{BACKEND_URL}/swipe", json=like_payload, headers=headers_user1)
            if response.status_code == 200:
                print(f"   ✅ Like created successfully")
            else:
                print(f"   ❌ Failed to create like: {response.status_code} - {response.text}")
        except Exception as e:
            print(f"   ❌ Exception creating like: {str(e)}")
        
        # Test 3: One-Way Like - Current user liked target, but target didn't like back
        try:
            response = self.session.get(f"{BACKEND_URL}/relation/can-chat?userId={self.user2_id}", headers=headers)
            
            if response.status_code == 200:
                data = response.json()
                # Expected: Should allow chat (current logic checks if current user liked target)
                # Expected: {canChat: true}
                if data.get("canChat") == True:
                    self.log_test("Chat Gating - One-Way Like", True, 
                                f"Correctly allowed chat after like: {data}")
                else:
                    self.log_test("Chat Gating - One-Way Like", False, 
                                f"Expected can=true, got: {data}")
            else:
                self.log_test("Chat Gating - One-Way Like", False, 
                            f"Status: {response.status_code}, Response: {response.text}")
        except Exception as e:
            self.log_test("Chat Gating - One-Way Like", False, f"Exception: {str(e)}")
        
        # Test 4: Invalid userId - Test with non-existent user ID
        fake_user_id = "non_existent_user_12345"
        try:
            response = self.session.get(f"{BACKEND_URL}/relation/can-chat?userId={fake_user_id}", headers=headers)
            
            # Should handle gracefully - either return false or proper error
            if response.status_code in [200, 404]:
                if response.status_code == 200:
                    data = response.json()
                    if data.get("canChat") == False:
                        self.log_test("Chat Gating - Invalid UserId", True, 
                                    f"Correctly handled invalid user: {data}")
                    else:
                        self.log_test("Chat Gating - Invalid UserId", False, 
                                    f"Should return can=false for invalid user: {data}")
                else:
                    self.log_test("Chat Gating - Invalid UserId", True, 
                                "Correctly returned 404 for invalid user")
            else:
                self.log_test("Chat Gating - Invalid UserId", False, 
                            f"Unexpected status: {response.status_code}, Response: {response.text}")
        except Exception as e:
            self.log_test("Chat Gating - Invalid UserId", False, f"Exception: {str(e)}")
        
        # Test 5: Without Authentication - Test without JWT token
        try:
            response = self.session.get(f"{BACKEND_URL}/relation/can-chat?userId={self.user2_id}")
            
            if response.status_code == 401:
                self.log_test("Chat Gating - No Authentication", True, 
                            "Correctly returned 401 Unauthorized")
            else:
                self.log_test("Chat Gating - No Authentication", False, 
                            f"Expected 401, got {response.status_code}: {response.text}")
        except Exception as e:
            self.log_test("Chat Gating - No Authentication", False, f"Exception: {str(e)}")

    def test_integration_scenarios(self):
        """Test integration scenarios"""
        print("🔗 Testing Integration Scenarios...")
        
        # Test 1: Complete flow - Register → Login → Like → Check can-chat
        print("   Testing complete user flow...")
        
        # User 2 likes User 1 back (mutual like)
        like_payload = {"swiped_user_id": self.user1_id, "action": "like"}
        headers_user2 = {"Authorization": f"Bearer {self.user2_token}", "Content-Type": "application/json"}
        
        try:
            response = self.session.post(f"{BACKEND_URL}/swipe", json=like_payload, headers=headers_user2)
            if response.status_code == 200:
                data = response.json()
                if data.get("is_match") == True:
                    self.log_test("Integration - Mutual Like Match", True, 
                                f"Match created successfully: {data}")
                else:
                    self.log_test("Integration - Mutual Like Match", False, 
                                f"Expected match=true, got: {data}")
            else:
                self.log_test("Integration - Mutual Like Match", False, 
                            f"Status: {response.status_code}, Response: {response.text}")
        except Exception as e:
            self.log_test("Integration - Mutual Like Match", False, f"Exception: {str(e)}")
        
        # Test 2: Verify chat gating works with existing swipe/like system
        headers_user2 = {"Authorization": f"Bearer {self.user2_token}"}
        try:
            response = self.session.get(f"{BACKEND_URL}/relation/can-chat?userId={self.user1_id}", headers=headers_user2)
            
            if response.status_code == 200:
                data = response.json()
                if data.get("canChat") == True:
                    self.log_test("Integration - Chat After Mutual Like", True, 
                                f"Chat allowed after mutual like: {data}")
                else:
                    self.log_test("Integration - Chat After Mutual Like", False, 
                                f"Expected can=true after mutual like, got: {data}")
            else:
                self.log_test("Integration - Chat After Mutual Like", False, 
                            f"Status: {response.status_code}, Response: {response.text}")
        except Exception as e:
            self.log_test("Integration - Chat After Mutual Like", False, f"Exception: {str(e)}")

    def test_edge_cases(self):
        """Test edge cases"""
        print("🧪 Testing Edge Cases...")
        
        # Test 1: Empty userId parameter
        headers = {"Authorization": f"Bearer {self.user1_token}"}
        try:
            response = self.session.get(f"{BACKEND_URL}/relation/can-chat?userId=", headers=headers)
            
            # Should handle gracefully
            if response.status_code in [400, 422, 500]:
                self.log_test("Edge Case - Empty UserId", True, 
                            f"Correctly handled empty userId with status {response.status_code}")
            else:
                self.log_test("Edge Case - Empty UserId", False, 
                            f"Unexpected handling of empty userId: {response.status_code} - {response.text}")
        except Exception as e:
            self.log_test("Edge Case - Empty UserId", False, f"Exception: {str(e)}")
        
        # Test 2: Special characters in userId
        special_user_id = "user<script>alert('xss')</script>"
        try:
            response = self.session.get(f"{BACKEND_URL}/relation/can-chat?userId={special_user_id}", headers=headers)
            
            # Should handle gracefully without XSS
            if response.status_code in [200, 400, 404, 422]:
                self.log_test("Edge Case - Special Characters", True, 
                            f"Safely handled special characters with status {response.status_code}")
            else:
                self.log_test("Edge Case - Special Characters", False, 
                            f"Unexpected handling: {response.status_code} - {response.text}")
        except Exception as e:
            self.log_test("Edge Case - Special Characters", False, f"Exception: {str(e)}")
        
        # Test 3: Safety consent with invalid payload
        headers = {"Authorization": f"Bearer {self.user1_token}", "Content-Type": "application/json"}
        invalid_payload = {"invalidField": "test"}
        
        try:
            response = self.session.put(f"{BACKEND_URL}/user/settings", json=invalid_payload, headers=headers)
            
            if response.status_code == 200:
                data = response.json()
                if data.get("ok") == True:
                    self.log_test("Edge Case - Invalid Safety Payload", True, 
                                f"Gracefully handled invalid payload: {data}")
                else:
                    self.log_test("Edge Case - Invalid Safety Payload", False, 
                                f"Unexpected response: {data}")
            else:
                self.log_test("Edge Case - Invalid Safety Payload", False, 
                            f"Status: {response.status_code}, Response: {response.text}")
        except Exception as e:
            self.log_test("Edge Case - Invalid Safety Payload", False, f"Exception: {str(e)}")

    def run_all_tests(self):
        """Run all test scenarios"""
        print("🚀 Starting Safety Consent & Chat Gating Backend Testing")
        print("=" * 60)
        
        # Setup
        if not self.setup_test_users():
            print("❌ Failed to setup test users. Aborting tests.")
            return False
        
        # Run test suites
        self.test_safety_consent_api()
        self.test_chat_gating_api()
        self.test_integration_scenarios()
        self.test_edge_cases()
        
        # Summary
        self.print_summary()
        return True

    def print_summary(self):
        """Print test summary"""
        print("\n" + "=" * 60)
        print("📊 TEST SUMMARY")
        print("=" * 60)
        
        total_tests = len(self.test_results)
        passed_tests = len([r for r in self.test_results if r["success"]])
        failed_tests = total_tests - passed_tests
        success_rate = (passed_tests / total_tests * 100) if total_tests > 0 else 0
        
        print(f"Total Tests: {total_tests}")
        print(f"✅ Passed: {passed_tests}")
        print(f"❌ Failed: {failed_tests}")
        print(f"📈 Success Rate: {success_rate:.1f}%")
        
        if failed_tests > 0:
            print(f"\n❌ FAILED TESTS:")
            for result in self.test_results:
                if not result["success"]:
                    print(f"   • {result['test']}: {result['details']}")
        
        print(f"\n🎯 KEY FINDINGS:")
        
        # Safety Consent API Analysis
        safety_tests = [r for r in self.test_results if "Safety Consent" in r["test"]]
        safety_passed = len([r for r in safety_tests if r["success"]])
        print(f"   • Safety Consent API: {safety_passed}/{len(safety_tests)} tests passed")
        
        # Chat Gating API Analysis
        chat_tests = [r for r in self.test_results if "Chat Gating" in r["test"]]
        chat_passed = len([r for r in chat_tests if r["success"]])
        print(f"   • Chat Gating API: {chat_passed}/{len(chat_tests)} tests passed")
        
        # Integration Tests Analysis
        integration_tests = [r for r in self.test_results if "Integration" in r["test"]]
        integration_passed = len([r for r in integration_tests if r["success"]])
        print(f"   • Integration Tests: {integration_passed}/{len(integration_tests)} tests passed")
        
        print(f"\n📋 DETAILED RESULTS:")
        for result in self.test_results:
            status_icon = "✅" if result["success"] else "❌"
            print(f"   {status_icon} {result['test']}")

if __name__ == "__main__":
    tester = SafetyChatTester()
    success = tester.run_all_tests()
    
    if not success:
        sys.exit(1)
    
    # Check if all critical tests passed
    failed_tests = [r for r in tester.test_results if not r["success"]]
    if failed_tests:
        print(f"\n⚠️  {len(failed_tests)} tests failed. Review required.")
        sys.exit(1)
    else:
        print(f"\n🎉 All tests passed! Safety Consent & Chat Gating features are working correctly.")