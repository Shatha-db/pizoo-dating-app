#!/usr/bin/env python3
"""
Arabic Review Backend API Testing
اختبار شامل للـAPIs الجديدة والمحدثة

Testing the following APIs as requested:
1. OTP APIs (new) - POST /api/auth/otp/send, POST /api/auth/otp/verify  
2. Messages API (new) - POST /api/messages/send
3. Explore Sections - GET /api/explore/sections
4. Personal Moments - GET /api/personal/list

Test scenarios:
- Test OTP send without phone → should fail
- Test OTP send with phone → should succeed  
- Test OTP verify without code → should fail
- Test messages send without body → should fail
- Test messages send with body → should succeed and return message object
"""

import requests
import json
import sys
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
        print(f"ARABIC REVIEW BACKEND TESTING SUMMARY")
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

def test_otp_apis():
    """Test OTP APIs - POST /api/auth/otp/send and POST /api/auth/otp/verify"""
    results = TestResults()
    
    print(f"\n🔐 TESTING OTP APIs")
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
    
    # Test 2: OTP send with empty phone → should fail  
    try:
        response = requests.post(f"{API_BASE}/auth/otp/send", json={"phone": ""})
        if response.status_code == 400:
            results.add_test("OTP send with empty phone (should fail)", True)
        else:
            results.add_test("OTP send with empty phone (should fail)", False,
                           f"Expected 400, got {response.status_code}")
    except Exception as e:
        results.add_test("OTP send with empty phone (should fail)", False, str(e))
    
    # Test 3: OTP send with valid phone → should succeed
    try:
        response = requests.post(f"{API_BASE}/auth/otp/send", json={"phone": "+41791234567"})
        if response.status_code == 200:
            data = response.json()
            if data.get("ok") and "message" in data:
                results.add_test("OTP send with valid phone (should succeed)", True)
            else:
                results.add_test("OTP send with valid phone (should succeed)", False,
                               f"Invalid response structure: {data}")
        else:
            results.add_test("OTP send with valid phone (should succeed)", False,
                           f"Expected 200, got {response.status_code}: {response.text}")
    except Exception as e:
        results.add_test("OTP send with valid phone (should succeed)", False, str(e))
    
    # Test 4: OTP verify without code → should fail
    try:
        response = requests.post(f"{API_BASE}/auth/otp/verify", json={"phone": "+41791234567"})
        if response.status_code == 400:
            results.add_test("OTP verify without code (should fail)", True)
        else:
            results.add_test("OTP verify without code (should fail)", False,
                           f"Expected 400, got {response.status_code}")
    except Exception as e:
        results.add_test("OTP verify without code (should fail)", False, str(e))
    
    # Test 5: OTP verify with empty code → should fail
    try:
        response = requests.post(f"{API_BASE}/auth/otp/verify", json={"phone": "+41791234567", "code": ""})
        if response.status_code == 400:
            results.add_test("OTP verify with empty code (should fail)", True)
        else:
            results.add_test("OTP verify with empty code (should fail)", False,
                           f"Expected 400, got {response.status_code}")
    except Exception as e:
        results.add_test("OTP verify with empty code (should fail)", False, str(e))
    
    # Test 6: OTP verify with valid data → should succeed (mock implementation)
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

def test_messages_api():
    """Test Messages API - POST /api/messages/send"""
    results = TestResults()
    
    print(f"\n💬 TESTING MESSAGES API")
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
    
    # Test 2: Messages send with empty body → should fail
    try:
        response = requests.post(f"{API_BASE}/messages/send", json={"body": ""})
        if response.status_code == 400:
            results.add_test("Messages send with empty body (should fail)", True)
        else:
            results.add_test("Messages send with empty body (should fail)", False,
                           f"Expected 400, got {response.status_code}")
    except Exception as e:
        results.add_test("Messages send with empty body (should fail)", False, str(e))
    
    # Test 3: Messages send with valid body → should succeed and return message object
    try:
        test_message = "مرحبا، كيف حالك؟"  # Arabic test message
        response = requests.post(f"{API_BASE}/messages/send", json={
            "body": test_message,
            "conversationId": "test-conversation-123"
        })
        
        if response.status_code == 200:
            data = response.json()
            message = data.get("message")
            
            if message and all(key in message for key in ["id", "body", "mine", "status", "createdAt"]):
                if message["body"] == test_message:
                    results.add_test("Messages send with valid body (should succeed)", True)
                else:
                    results.add_test("Messages send with valid body (should succeed)", False,
                                   f"Message body mismatch: expected '{test_message}', got '{message['body']}'")
            else:
                results.add_test("Messages send with valid body (should succeed)", False,
                               f"Invalid message object structure: {message}")
        else:
            results.add_test("Messages send with valid body (should succeed)", False,
                           f"Expected 200, got {response.status_code}: {response.text}")
    except Exception as e:
        results.add_test("Messages send with valid body (should succeed)", False, str(e))
    
    # Test 4: Messages send with English text → should succeed
    try:
        test_message = "Hello, how are you?"
        response = requests.post(f"{API_BASE}/messages/send", json={
            "body": test_message
        })
        
        if response.status_code == 200:
            data = response.json()
            message = data.get("message")
            
            if message and message.get("body") == test_message:
                results.add_test("Messages send with English text (should succeed)", True)
            else:
                results.add_test("Messages send with English text (should succeed)", False,
                               f"Message body mismatch or invalid structure: {message}")
        else:
            results.add_test("Messages send with English text (should succeed)", False,
                           f"Expected 200, got {response.status_code}: {response.text}")
    except Exception as e:
        results.add_test("Messages send with English text (should succeed)", False, str(e))
    
    return results

def test_explore_sections():
    """Test Explore Sections API - GET /api/explore/sections"""
    results = TestResults()
    
    print(f"\n🔍 TESTING EXPLORE SECTIONS API")
    print(f"{'='*50}")
    
    # Test 1: Get explore sections without authentication → should fail
    try:
        response = requests.get(f"{API_BASE}/explore/sections")
        if response.status_code in [401, 403]:
            results.add_test("Explore sections without auth (should fail)", True)
        else:
            results.add_test("Explore sections without auth (should fail)", False,
                           f"Expected 401/403, got {response.status_code}")
    except Exception as e:
        results.add_test("Explore sections without auth (should fail)", False, str(e))
    
    # Test 2: Get explore sections with invalid token → should fail
    try:
        headers = {"Authorization": "Bearer invalid-token"}
        response = requests.get(f"{API_BASE}/explore/sections", headers=headers)
        if response.status_code in [401, 403]:
            results.add_test("Explore sections with invalid token (should fail)", True)
        else:
            results.add_test("Explore sections with invalid token (should fail)", False,
                           f"Expected 401/403, got {response.status_code}")
    except Exception as e:
        results.add_test("Explore sections with invalid token (should fail)", False, str(e))
    
    return results

def test_personal_moments():
    """Test Personal Moments API - GET /api/personal/list"""
    results = TestResults()
    
    print(f"\n💫 TESTING PERSONAL MOMENTS API")
    print(f"{'='*50}")
    
    # Test 1: Get personal moments without authentication → should fail
    try:
        response = requests.get(f"{API_BASE}/personal/list")
        if response.status_code in [401, 403]:
            results.add_test("Personal moments without auth (should fail)", True)
        else:
            results.add_test("Personal moments without auth (should fail)", False,
                           f"Expected 401/403, got {response.status_code}")
    except Exception as e:
        results.add_test("Personal moments without auth (should fail)", False, str(e))
    
    # Test 2: Get personal moments with invalid token → should fail
    try:
        headers = {"Authorization": "Bearer invalid-token"}
        response = requests.get(f"{API_BASE}/personal/list", headers=headers)
        if response.status_code in [401, 403]:
            results.add_test("Personal moments with invalid token (should fail)", True)
        else:
            results.add_test("Personal moments with invalid token (should fail)", False,
                           f"Expected 401/403, got {response.status_code}")
    except Exception as e:
        results.add_test("Personal moments with invalid token (should fail)", False, str(e))
    
    return results

def main():
    """Run all Arabic review backend tests"""
    print(f"🎯 ARABIC REVIEW BACKEND API TESTING")
    print(f"Testing Backend URL: {BACKEND_URL}")
    print(f"Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    all_results = []
    
    # Test OTP APIs
    otp_results = test_otp_apis()
    all_results.append(otp_results)
    
    # Test Messages API
    messages_results = test_messages_api()
    all_results.append(messages_results)
    
    # Test Explore Sections API
    explore_results = test_explore_sections()
    all_results.append(explore_results)
    
    # Test Personal Moments API
    personal_results = test_personal_moments()
    all_results.append(personal_results)
    
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
    categories = [
        ("🔐 OTP APIs", otp_results),
        ("💬 Messages API", messages_results), 
        ("🔍 Explore Sections", explore_results),
        ("💫 Personal Moments", personal_results)
    ]
    
    for category_name, results in categories:
        success_rate = (results.passed_tests/results.total_tests)*100 if results.total_tests > 0 else 0
        print(f"  {category_name}: {results.passed_tests}/{results.total_tests} ({success_rate:.1f}%)")
    
    # List all failures
    all_failures = []
    for results in all_results:
        all_failures.extend(results.failed_tests)
    
    if all_failures:
        print(f"\n❌ ALL FAILED TESTS:")
        for i, failure in enumerate(all_failures, 1):
            print(f"  {i}. {failure}")
    
    print(f"\n🏁 Testing completed at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Return success status
    return total_failed == 0

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)