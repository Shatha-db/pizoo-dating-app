#!/usr/bin/env python3
"""
Arabic Review Comprehensive Backend API Testing
اختبار شامل ومتقدم للـAPIs الجديدة والمحدثة

This test includes authentication and tests all endpoints thoroughly:
1. OTP APIs (new) - POST /api/auth/otp/send, POST /api/auth/otp/verify  
2. Messages API (new) - POST /api/messages/send
3. Explore Sections - GET /api/explore/sections (with authentication)
4. Personal Moments - GET /api/personal/list (with authentication)
"""

import requests
import json
import sys
import uuid
from datetime import datetime

# Get backend URL from frontend env
try:
    with open('/app/frontend/.env', 'r') as f:
        for line in f:
            if line.startswith('REACT_APP_BACKEND_URL='):
                BACKEND_URL = line.split('=')[1].strip()
                break
        else:
            BACKEND_URL = "http://localhost:8001"
except:
    BACKEND_URL = "http://localhost:8001"

API_BASE = f"{BACKEND_URL}/api"

class TestResults:
    def __init__(self):
        self.total_tests = 0
        self.passed_tests = 0
        self.failed_tests = []
        
    def add_test(self, test_name, passed, details=""):
        self.total_tests += 1
        if passed:
            self.passed_tests += 1
            print(f"✅ {test_name}")
        else:
            self.failed_tests.append(f"{test_name}: {details}")
            print(f"❌ {test_name}: {details}")
    
    def print_summary(self):
        print(f"\n{'='*60}")
        print(f"TESTING SUMMARY")
        print(f"{'='*60}")
        print(f"Total Tests: {self.total_tests}")
        print(f"Passed: {self.passed_tests}")
        print(f"Failed: {len(self.failed_tests)}")
        print(f"Success Rate: {(self.passed_tests/self.total_tests)*100:.1f}%")
        
        if self.failed_tests:
            print(f"\n❌ FAILED TESTS:")
            for failure in self.failed_tests:
                print(f"  - {failure}")
        
        return len(self.failed_tests) == 0

def create_test_user():
    """Create a test user and return authentication token"""
    try:
        # Generate unique test user
        test_id = str(uuid.uuid4())[:8]
        user_data = {
            "name": f"Test User {test_id}",
            "email": f"testuser{test_id}@example.com",
            "phone_number": f"+4179{test_id[:7]}",
            "password": "TestPassword123!",
            "terms_accepted": True
        }
        
        response = requests.post(f"{API_BASE}/auth/register", json=user_data)
        
        if response.status_code == 200:
            data = response.json()
            token = data.get("access_token")
            user_id = data.get("user", {}).get("id")
            print(f"✅ Created test user: {user_data['email']}")
            return token, user_id
        else:
            print(f"❌ Failed to create test user: {response.status_code} - {response.text}")
            return None, None
            
    except Exception as e:
        print(f"❌ Error creating test user: {str(e)}")
        return None, None

def test_otp_apis_comprehensive():
    """Comprehensive test of OTP APIs"""
    results = TestResults()
    
    print(f"\n🔐 COMPREHENSIVE OTP APIs TESTING")
    print(f"{'='*50}")
    
    # Test 1: OTP send without phone → should fail
    try:
        response = requests.post(f"{API_BASE}/auth/otp/send", json={})
        if response.status_code == 400:
            results.add_test("OTP send without phone (should fail)", True)
        else:
            results.add_test("OTP send without phone (should fail)", False, 
                           f"Expected 400, got {response.status_code}")
    except Exception as e:
        results.add_test("OTP send without phone (should fail)", False, str(e))
    
    # Test 2: OTP send with invalid phone formats → should fail
    invalid_phones = ["", "123", "invalid", "+", "+123", "123456789"]
    for phone in invalid_phones:
        try:
            response = requests.post(f"{API_BASE}/auth/otp/send", json={"phone": phone})
            if response.status_code == 400:
                results.add_test(f"OTP send with invalid phone '{phone}' (should fail)", True)
            else:
                results.add_test(f"OTP send with invalid phone '{phone}' (should fail)", False,
                               f"Expected 400, got {response.status_code}")
        except Exception as e:
            results.add_test(f"OTP send with invalid phone '{phone}' (should fail)", False, str(e))
    
    # Test 3: OTP send with valid phone formats → should succeed
    valid_phones = ["+41791234567", "+966501234567", "+971501234567"]
    for phone in valid_phones:
        try:
            response = requests.post(f"{API_BASE}/auth/otp/send", json={"phone": phone})
            if response.status_code == 200:
                data = response.json()
                if data.get("ok") and "message" in data:
                    results.add_test(f"OTP send with valid phone '{phone}' (should succeed)", True)
                else:
                    results.add_test(f"OTP send with valid phone '{phone}' (should succeed)", False,
                                   f"Invalid response structure: {data}")
            else:
                results.add_test(f"OTP send with valid phone '{phone}' (should succeed)", False,
                               f"Expected 200, got {response.status_code}: {response.text}")
        except Exception as e:
            results.add_test(f"OTP send with valid phone '{phone}' (should succeed)", False, str(e))
    
    # Test 4: OTP verify without required fields → should fail
    verify_test_cases = [
        ({}, "no data"),
        ({"phone": "+41791234567"}, "no code"),
        ({"code": "123456"}, "no phone"),
        ({"phone": "", "code": "123456"}, "empty phone"),
        ({"phone": "+41791234567", "code": ""}, "empty code")
    ]
    
    for payload, description in verify_test_cases:
        try:
            response = requests.post(f"{API_BASE}/auth/otp/verify", json=payload)
            if response.status_code == 400:
                results.add_test(f"OTP verify with {description} (should fail)", True)
            else:
                results.add_test(f"OTP verify with {description} (should fail)", False,
                               f"Expected 400, got {response.status_code}")
        except Exception as e:
            results.add_test(f"OTP verify with {description} (should fail)", False, str(e))
    
    # Test 5: OTP verify with valid data → should succeed (mock implementation)
    try:
        response = requests.post(f"{API_BASE}/auth/otp/verify", json={
            "phone": "+41791234567", 
            "code": "123456"
        })
        if response.status_code == 200:
            data = response.json()
            if data.get("ok") and "message" in data:
                results.add_test("OTP verify with valid data (should succeed)", True)
            else:
                results.add_test("OTP verify with valid data (should succeed)", False,
                               f"Invalid response structure: {data}")
        else:
            results.add_test("OTP verify with valid data (should succeed)", False,
                           f"Expected 200, got {response.status_code}: {response.text}")
    except Exception as e:
        results.add_test("OTP verify with valid data (should succeed)", False, str(e))
    
    return results

def test_messages_api_comprehensive():
    """Comprehensive test of Messages API"""
    results = TestResults()
    
    print(f"\n💬 COMPREHENSIVE MESSAGES API TESTING")
    print(f"{'='*50}")
    
    # Test 1: Messages send without body → should fail
    try:
        response = requests.post(f"{API_BASE}/messages/send", json={})
        if response.status_code == 400:
            results.add_test("Messages send without body (should fail)", True)
        else:
            results.add_test("Messages send without body (should fail)", False,
                           f"Expected 400, got {response.status_code}")
    except Exception as e:
        results.add_test("Messages send without body (should fail)", False, str(e))
    
    # Test 2: Messages send with various invalid bodies → should fail
    invalid_bodies = ["", None]
    for body in invalid_bodies:
        try:
            payload = {"body": body} if body is not None else {}
            response = requests.post(f"{API_BASE}/messages/send", json=payload)
            if response.status_code == 400:
                results.add_test(f"Messages send with invalid body '{body}' (should fail)", True)
            else:
                results.add_test(f"Messages send with invalid body '{body}' (should fail)", False,
                               f"Expected 400, got {response.status_code}")
        except Exception as e:
            results.add_test(f"Messages send with invalid body '{body}' (should fail)", False, str(e))
    
    # Test 3: Messages send with valid bodies → should succeed and return message object
    test_messages = [
        "مرحبا، كيف حالك؟",  # Arabic
        "Hello, how are you?",  # English
        "Bonjour, comment allez-vous?",  # French
        "¡Hola! ¿Cómo estás?",  # Spanish
        "😊 Hello with emoji! 🎉",  # With emojis
        "A" * 1000,  # Long message
        "123456789",  # Numbers
        "Test@#$%^&*()",  # Special characters
    ]
    
    for test_message in test_messages:
        try:
            response = requests.post(f"{API_BASE}/messages/send", json={
                "body": test_message,
                "conversationId": f"test-conversation-{hash(test_message) % 1000}"
            })
            
            if response.status_code == 200:
                data = response.json()
                message = data.get("message")
                
                # Validate message object structure
                required_fields = ["id", "body", "mine", "status", "createdAt"]
                if message and all(key in message for key in required_fields):
                    if message["body"] == test_message:
                        results.add_test(f"Messages send with '{test_message[:30]}...' (should succeed)", True)
                    else:
                        results.add_test(f"Messages send with '{test_message[:30]}...' (should succeed)", False,
                                       f"Message body mismatch: expected '{test_message}', got '{message['body']}'")
                else:
                    results.add_test(f"Messages send with '{test_message[:30]}...' (should succeed)", False,
                                   f"Invalid message object structure: {message}")
            else:
                results.add_test(f"Messages send with '{test_message[:30]}...' (should succeed)", False,
                               f"Expected 200, got {response.status_code}: {response.text}")
        except Exception as e:
            results.add_test(f"Messages send with '{test_message[:30]}...' (should succeed)", False, str(e))
    
    # Test 4: Messages send with optional fields
    try:
        response = requests.post(f"{API_BASE}/messages/send", json={
            "body": "Test message with conversation ID",
            "conversationId": "conv-12345"
        })
        
        if response.status_code == 200:
            data = response.json()
            message = data.get("message")
            if message and message.get("body") == "Test message with conversation ID":
                results.add_test("Messages send with conversationId (should succeed)", True)
            else:
                results.add_test("Messages send with conversationId (should succeed)", False,
                               f"Invalid response: {data}")
        else:
            results.add_test("Messages send with conversationId (should succeed)", False,
                           f"Expected 200, got {response.status_code}: {response.text}")
    except Exception as e:
        results.add_test("Messages send with conversationId (should succeed)", False, str(e))
    
    return results

def test_explore_sections_authenticated(auth_token):
    """Test Explore Sections API with authentication"""
    results = TestResults()
    
    print(f"\n🔍 AUTHENTICATED EXPLORE SECTIONS API TESTING")
    print(f"{'='*50}")
    
    if not auth_token:
        results.add_test("Explore sections authentication setup", False, "No auth token available")
        return results
    
    # Test 1: Get explore sections with valid authentication → should succeed
    try:
        headers = {"Authorization": f"Bearer {auth_token}"}
        response = requests.get(f"{API_BASE}/explore/sections", headers=headers)
        
        if response.status_code == 200:
            data = response.json()
            sections = data.get("sections", [])
            
            if isinstance(sections, list) and len(sections) > 0:
                # Validate section structure
                valid_sections = True
                for section in sections:
                    if not all(key in section for key in ["type", "title", "profiles"]):
                        valid_sections = False
                        break
                    if not isinstance(section["profiles"], list):
                        valid_sections = False
                        break
                
                if valid_sections:
                    results.add_test(f"Explore sections with auth (found {len(sections)} sections)", True)
                    
                    # Test section details
                    total_profiles = sum(len(section["profiles"]) for section in sections)
                    results.add_test(f"Explore sections profile count ({total_profiles} total profiles)", True)
                    
                    # Check for expected section types
                    section_types = [section["type"] for section in sections]
                    expected_types = ["most_active", "ready_chat", "new_faces"]
                    found_expected = any(t in section_types for t in expected_types)
                    results.add_test(f"Explore sections contain expected types", found_expected,
                                   f"Found types: {section_types}")
                else:
                    results.add_test("Explore sections with auth (should succeed)", False,
                                   "Invalid section structure")
            else:
                results.add_test("Explore sections with auth (should succeed)", False,
                               f"No sections returned: {data}")
        else:
            results.add_test("Explore sections with auth (should succeed)", False,
                           f"Expected 200, got {response.status_code}: {response.text}")
    except Exception as e:
        results.add_test("Explore sections with auth (should succeed)", False, str(e))
    
    return results

def test_personal_moments_authenticated(auth_token):
    """Test Personal Moments API with authentication"""
    results = TestResults()
    
    print(f"\n💫 AUTHENTICATED PERSONAL MOMENTS API TESTING")
    print(f"{'='*50}")
    
    if not auth_token:
        results.add_test("Personal moments authentication setup", False, "No auth token available")
        return results
    
    # Test 1: Get personal moments with valid authentication → should succeed
    try:
        headers = {"Authorization": f"Bearer {auth_token}"}
        response = requests.get(f"{API_BASE}/personal/list", headers=headers)
        
        if response.status_code == 200:
            data = response.json()
            moments = data.get("moments", [])
            
            if isinstance(moments, list) and len(moments) > 0:
                # Validate moment structure
                valid_moments = True
                for moment in moments:
                    required_fields = ["id", "title", "description", "action", "ctaText"]
                    if not all(key in moment for key in required_fields):
                        valid_moments = False
                        break
                
                if valid_moments:
                    results.add_test(f"Personal moments with auth (found {len(moments)} moments)", True)
                    
                    # Test moment details
                    categories = [moment.get("category", "unknown") for moment in moments]
                    safe_categories = ["flatshare", "travel", "outing", "activity", "roommate"]
                    found_safe = any(cat in safe_categories for cat in categories)
                    results.add_test(f"Personal moments contain safe categories", found_safe,
                                   f"Found categories: {categories}")
                    
                    # Check for premium/new badges
                    premium_count = sum(1 for moment in moments if moment.get("isPremium"))
                    new_count = sum(1 for moment in moments if moment.get("isNew"))
                    results.add_test(f"Personal moments badge system ({premium_count} premium, {new_count} new)", True)
                else:
                    results.add_test("Personal moments with auth (should succeed)", False,
                                   "Invalid moment structure")
            else:
                results.add_test("Personal moments with auth (should succeed)", False,
                               f"No moments returned: {data}")
        else:
            results.add_test("Personal moments with auth (should succeed)", False,
                           f"Expected 200, got {response.status_code}: {response.text}")
    except Exception as e:
        results.add_test("Personal moments with auth (should succeed)", False, str(e))
    
    return results

def test_unauthenticated_endpoints():
    """Test that protected endpoints properly reject unauthenticated requests"""
    results = TestResults()
    
    print(f"\n🔒 AUTHENTICATION PROTECTION TESTING")
    print(f"{'='*50}")
    
    protected_endpoints = [
        ("GET", "/explore/sections", "Explore sections"),
        ("GET", "/personal/list", "Personal moments")
    ]
    
    for method, endpoint, name in protected_endpoints:
        # Test without auth
        try:
            if method == "GET":
                response = requests.get(f"{API_BASE}{endpoint}")
            elif method == "POST":
                response = requests.post(f"{API_BASE}{endpoint}", json={})
            
            if response.status_code in [401, 403]:
                results.add_test(f"{name} without auth (should fail)", True)
            else:
                results.add_test(f"{name} without auth (should fail)", False,
                               f"Expected 401/403, got {response.status_code}")
        except Exception as e:
            results.add_test(f"{name} without auth (should fail)", False, str(e))
        
        # Test with invalid token
        try:
            headers = {"Authorization": "Bearer invalid-token-12345"}
            if method == "GET":
                response = requests.get(f"{API_BASE}{endpoint}", headers=headers)
            elif method == "POST":
                response = requests.post(f"{API_BASE}{endpoint}", json={}, headers=headers)
            
            if response.status_code in [401, 403]:
                results.add_test(f"{name} with invalid token (should fail)", True)
            else:
                results.add_test(f"{name} with invalid token (should fail)", False,
                               f"Expected 401/403, got {response.status_code}")
        except Exception as e:
            results.add_test(f"{name} with invalid token (should fail)", False, str(e))
    
    return results

def main():
    """Run comprehensive Arabic review backend tests"""
    print(f"🎯 ARABIC REVIEW COMPREHENSIVE BACKEND API TESTING")
    print(f"Testing Backend URL: {BACKEND_URL}")
    print(f"Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    all_results = []
    
    # Create test user for authenticated tests
    print(f"\n👤 SETTING UP TEST USER")
    print(f"{'='*50}")
    auth_token, user_id = create_test_user()
    
    # Test OTP APIs (comprehensive)
    otp_results = test_otp_apis_comprehensive()
    all_results.append(otp_results)
    
    # Test Messages API (comprehensive)
    messages_results = test_messages_api_comprehensive()
    all_results.append(messages_results)
    
    # Test authentication protection
    auth_protection_results = test_unauthenticated_endpoints()
    all_results.append(auth_protection_results)
    
    # Test authenticated endpoints
    if auth_token:
        explore_results = test_explore_sections_authenticated(auth_token)
        all_results.append(explore_results)
        
        personal_results = test_personal_moments_authenticated(auth_token)
        all_results.append(personal_results)
    else:
        print(f"\n⚠️  Skipping authenticated tests - no auth token available")
    
    # Combined summary
    total_tests = sum(r.total_tests for r in all_results)
    total_passed = sum(r.passed_tests for r in all_results)
    total_failed = sum(len(r.failed_tests) for r in all_results)
    
    print(f"\n{'='*60}")
    print(f"🎯 ARABIC REVIEW COMPREHENSIVE TESTING SUMMARY")
    print(f"{'='*60}")
    print(f"Total Tests Executed: {total_tests}")
    print(f"✅ Passed: {total_passed}")
    print(f"❌ Failed: {total_failed}")
    print(f"📊 Success Rate: {(total_passed/total_tests)*100:.1f}%")
    
    # Detailed results by category
    print(f"\n📋 RESULTS BY CATEGORY:")
    category_names = [
        "🔐 OTP APIs (Comprehensive)",
        "💬 Messages API (Comprehensive)", 
        "🔒 Authentication Protection",
    ]
    
    if auth_token:
        category_names.extend([
            "🔍 Explore Sections (Authenticated)",
            "💫 Personal Moments (Authenticated)"
        ])
    
    for i, results in enumerate(all_results):
        if i < len(category_names):
            success_rate = (results.passed_tests/results.total_tests)*100 if results.total_tests > 0 else 0
            print(f"  {category_names[i]}: {results.passed_tests}/{results.total_tests} ({success_rate:.1f}%)")
    
    # List all failures
    all_failures = []
    for results in all_results:
        all_failures.extend(results.failed_tests)
    
    if all_failures:
        print(f"\n❌ ALL FAILED TESTS:")
        for i, failure in enumerate(all_failures, 1):
            print(f"  {i}. {failure}")
    else:
        print(f"\n🎉 ALL TESTS PASSED! No failures detected.")
    
    print(f"\n🏁 Testing completed at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Return success status
    return total_failed == 0

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)