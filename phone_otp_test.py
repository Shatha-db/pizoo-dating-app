#!/usr/bin/env python3
"""
Phone OTP Authentication Backend Testing Script
Tests all OTP authentication scenarios as requested in the review.
"""

import requests
import json
import sys
import time
import re
from datetime import datetime
import uuid

# Configuration
BASE_URL = "https://phone-auth-2.preview.emergentagent.com/api"
HEADERS = {"Content-Type": "application/json"}

class PhoneOTPTester:
    def __init__(self):
        self.base_url = BASE_URL
        self.headers = HEADERS.copy()
        self.test_results = []
        self.test_phone = None
        self.otp_id = None
        self.generated_otp = None
        
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
    
    def make_request(self, method, endpoint, data=None):
        """Make HTTP request"""
        url = f"{self.base_url}{endpoint}"
        
        try:
            if method.upper() == "GET":
                response = requests.get(url, headers=self.headers, timeout=30)
            elif method.upper() == "POST":
                response = requests.post(url, headers=self.headers, json=data, timeout=30)
            else:
                raise ValueError(f"Unsupported method: {method}")
            
            return response
        except requests.exceptions.RequestException as e:
            return None, str(e)
    
    def extract_otp_from_logs(self):
        """Extract OTP from backend logs (mock mode)"""
        try:
            import subprocess
            result = subprocess.run(
                ["tail", "-n", "20", "/var/log/supervisor/backend.out.log"],
                capture_output=True, text=True, timeout=10
            )
            
            # Look for mock SMS pattern
            lines = result.stdout.split('\n')
            for line in reversed(lines):  # Check most recent first
                if "[MOCK SMS]" in line and self.test_phone in line:
                    # Extract OTP from message like "Pizoo verification code: 123456"
                    match = re.search(r'verification code: (\d{6})', line)
                    if match:
                        return match.group(1)
            
            # Also check stderr
            lines = result.stderr.split('\n')
            for line in reversed(lines):
                if "[MOCK SMS]" in line and self.test_phone in line:
                    match = re.search(r'verification code: (\d{6})', line)
                    if match:
                        return match.group(1)
                        
            return None
        except Exception as e:
            print(f"Error extracting OTP from logs: {e}")
            return None
    
    def test_send_otp_valid_phone(self):
        """Test sending OTP to valid phone number"""
        # Generate unique test phone (must be 8-15 digits after country code)
        import random
        unique_digits = ''.join([str(random.randint(0, 9)) for _ in range(3)])
        self.test_phone = f"+12345678901{unique_digits}"
        
        print(f"   📱 Testing with phone: {self.test_phone}")
        
        data = {"phone": self.test_phone}
        response = self.make_request("POST", "/auth/phone/send-otp", data)
        
        if response is None:
            self.log_result("Send OTP (Valid Phone)", False, "Connection failed")
            return False
        
        if response.status_code == 200:
            try:
                data = response.json()
                if data.get("ok") and "otpId" in data:
                    self.otp_id = data["otpId"]
                    ttl = data.get("ttl", 0)
                    self.log_result("Send OTP (Valid Phone)", True, f"OTP sent successfully. ID: {self.otp_id}, TTL: {ttl}s")
                    
                    # Wait a moment for logs to be written
                    time.sleep(2)
                    
                    # Extract OTP from logs (mock mode)
                    self.generated_otp = self.extract_otp_from_logs()
                    if self.generated_otp:
                        print(f"   📱 Generated OTP: {self.generated_otp}")
                    else:
                        print("   ⚠️  Could not extract OTP from logs")
                    
                    return True
                else:
                    self.log_result("Send OTP (Valid Phone)", False, "Missing ok or otpId in response", data)
                    return False
            except json.JSONDecodeError:
                self.log_result("Send OTP (Valid Phone)", False, "Invalid JSON response", response.text)
                return False
        else:
            try:
                error_data = response.json()
                self.log_result("Send OTP (Valid Phone)", False, f"HTTP {response.status_code}: {error_data.get('detail', response.text)}")
            except:
                self.log_result("Send OTP (Valid Phone)", False, f"HTTP {response.status_code}: {response.text}")
            return False
    
    def test_send_otp_invalid_phone(self):
        """Test sending OTP to invalid phone numbers"""
        invalid_phones = [
            "",  # Empty
            "123456789",  # No country code
            "+1234",  # Too short
            "invalid",  # Non-numeric
            "+",  # Just plus sign
        ]
        
        success_count = 0
        for phone in invalid_phones:
            data = {"phone": phone}
            response = self.make_request("POST", "/auth/phone/send-otp", data)
            
            if response is None:
                self.log_result(f"Send OTP (Invalid: {phone})", False, "Connection failed")
                continue
            
            if response.status_code == 400:
                try:
                    error_data = response.json()
                    if error_data.get("detail") == "INVALID_PHONE":
                        self.log_result(f"Send OTP (Invalid: {phone})", True, "Correctly rejected invalid phone")
                        success_count += 1
                    else:
                        self.log_result(f"Send OTP (Invalid: {phone})", False, f"Wrong error: {error_data.get('detail')}")
                except:
                    self.log_result(f"Send OTP (Invalid: {phone})", False, f"Invalid JSON response: {response.text}")
            else:
                self.log_result(f"Send OTP (Invalid: {phone})", False, f"Expected 400, got {response.status_code}")
        
        return success_count == len(invalid_phones)
    
    def test_verify_otp_correct(self):
        """Test verifying OTP with correct code"""
        if not self.otp_id or not self.generated_otp:
            self.log_result("Verify OTP (Correct)", False, "No OTP ID or generated OTP available")
            return False
        
        data = {
            "phone": self.test_phone,
            "code": self.generated_otp,
            "otpId": self.otp_id
        }
        
        response = self.make_request("POST", "/auth/phone/verify-otp", data)
        
        if response is None:
            self.log_result("Verify OTP (Correct)", False, "Connection failed")
            return False
        
        if response.status_code == 200:
            try:
                data = response.json()
                if data.get("ok") and data.get("verified"):
                    token = data.get("token")
                    user_id = data.get("user_id")
                    self.log_result("Verify OTP (Correct)", True, f"OTP verified successfully. Token: {token[:20]}..., User ID: {user_id}")
                    return True
                else:
                    self.log_result("Verify OTP (Correct)", False, "Missing ok/verified in response", data)
                    return False
            except json.JSONDecodeError:
                self.log_result("Verify OTP (Correct)", False, "Invalid JSON response", response.text)
                return False
        else:
            try:
                error_data = response.json()
                self.log_result("Verify OTP (Correct)", False, f"HTTP {response.status_code}: {error_data.get('detail', response.text)}")
            except:
                self.log_result("Verify OTP (Correct)", False, f"HTTP {response.status_code}: {response.text}")
            return False
    
    def test_verify_otp_wrong_code(self):
        """Test verifying OTP with wrong code (test attempts limiting)"""
        # First, send a new OTP for this test
        unique_id = str(uuid.uuid4())[:8]
        test_phone = f"+19876543210{unique_id[:3]}"
        
        # Send OTP
        data = {"phone": test_phone}
        response = self.make_request("POST", "/auth/phone/send-otp", data)
        
        if response is None or response.status_code != 200:
            self.log_result("Verify OTP (Wrong Code)", False, "Failed to send OTP for wrong code test")
            return False
        
        otp_data = response.json()
        otp_id = otp_data.get("otpId")
        
        if not otp_id:
            self.log_result("Verify OTP (Wrong Code)", False, "No OTP ID received")
            return False
        
        # Try wrong codes multiple times
        wrong_codes = ["000000", "111111", "999999"]
        success_count = 0
        
        for i, wrong_code in enumerate(wrong_codes):
            data = {
                "phone": test_phone,
                "code": wrong_code,
                "otpId": otp_id
            }
            
            response = self.make_request("POST", "/auth/phone/verify-otp", data)
            
            if response is None:
                self.log_result(f"Wrong Code Attempt {i+1}", False, "Connection failed")
                continue
            
            if response.status_code == 400:
                try:
                    error_data = response.json()
                    if error_data.get("detail") == "OTP_INVALID":
                        self.log_result(f"Wrong Code Attempt {i+1}", True, "Correctly rejected wrong OTP")
                        success_count += 1
                    else:
                        self.log_result(f"Wrong Code Attempt {i+1}", False, f"Wrong error: {error_data.get('detail')}")
                except:
                    self.log_result(f"Wrong Code Attempt {i+1}", False, f"Invalid JSON response: {response.text}")
            else:
                self.log_result(f"Wrong Code Attempt {i+1}", False, f"Expected 400, got {response.status_code}")
        
        # Test 4th attempt (should be blocked)
        data = {
            "phone": test_phone,
            "code": "123456",
            "otpId": otp_id
        }
        
        response = self.make_request("POST", "/auth/phone/verify-otp", data)
        
        if response is None:
            self.log_result("4th Attempt (Should be blocked)", False, "Connection failed")
            return success_count == len(wrong_codes)
        
        if response.status_code == 429:
            try:
                error_data = response.json()
                if error_data.get("detail") == "OTP_LOCKED":
                    self.log_result("4th Attempt (Should be blocked)", True, "Correctly blocked after max attempts")
                    success_count += 1
                else:
                    self.log_result("4th Attempt (Should be blocked)", False, f"Wrong error: {error_data.get('detail')}")
            except:
                self.log_result("4th Attempt (Should be blocked)", False, f"Invalid JSON response: {response.text}")
        else:
            self.log_result("4th Attempt (Should be blocked)", False, f"Expected 429, got {response.status_code}")
        
        return success_count == len(wrong_codes) + 1
    
    def test_verify_otp_expired(self):
        """Test verifying expired OTP (simulated by waiting)"""
        # Note: Since OTP TTL is 5 minutes, we can't wait that long in testing
        # Instead, we'll test with an invalid otpId to simulate expiry
        
        data = {
            "phone": self.test_phone or "+1234567890",
            "code": "123456",
            "otpId": "507f1f77bcf86cd799439011"  # Invalid ObjectId
        }
        
        response = self.make_request("POST", "/auth/phone/verify-otp", data)
        
        if response is None:
            self.log_result("Verify OTP (Expired/Invalid)", False, "Connection failed")
            return False
        
        if response.status_code == 400:
            try:
                error_data = response.json()
                if error_data.get("detail") == "OTP_NOT_FOUND":
                    self.log_result("Verify OTP (Expired/Invalid)", True, "Correctly rejected invalid/expired OTP")
                    return True
                else:
                    self.log_result("Verify OTP (Expired/Invalid)", False, f"Wrong error: {error_data.get('detail')}")
                    return False
            except:
                self.log_result("Verify OTP (Expired/Invalid)", False, f"Invalid JSON response: {response.text}")
                return False
        else:
            self.log_result("Verify OTP (Expired/Invalid)", False, f"Expected 400, got {response.status_code}")
            return False
    
    def test_existing_user_flow(self):
        """Test OTP flow for existing user (register via email first)"""
        # First register a user via email
        unique_id = str(uuid.uuid4())[:8]
        email = f"testuser{unique_id}@example.com"
        phone = f"+15551234567{unique_id[:3]}"
        
        register_data = {
            "name": f"Test User {unique_id}",
            "email": email,
            "phone_number": phone,
            "password": "TestPassword123!",
            "terms_accepted": True
        }
        
        response = self.make_request("POST", "/auth/register", register_data)
        
        if response is None or response.status_code != 200:
            self.log_result("Existing User Flow (Register)", False, "Failed to register user via email")
            return False
        
        # Now test OTP flow with the same phone
        otp_data = {"phone": phone}
        response = self.make_request("POST", "/auth/phone/send-otp", otp_data)
        
        if response is None or response.status_code != 200:
            self.log_result("Existing User Flow (Send OTP)", False, "Failed to send OTP to existing user")
            return False
        
        otp_response = response.json()
        otp_id = otp_response.get("otpId")
        
        if not otp_id:
            self.log_result("Existing User Flow (Send OTP)", False, "No OTP ID received")
            return False
        
        # Wait for logs and extract OTP
        time.sleep(2)
        generated_otp = self.extract_otp_from_logs()
        
        if not generated_otp:
            self.log_result("Existing User Flow (Extract OTP)", False, "Could not extract OTP from logs")
            return False
        
        # Verify OTP
        verify_data = {
            "phone": phone,
            "code": generated_otp,
            "otpId": otp_id
        }
        
        response = self.make_request("POST", "/auth/phone/verify-otp", verify_data)
        
        if response is None:
            self.log_result("Existing User Flow (Verify)", False, "Connection failed")
            return False
        
        if response.status_code == 200:
            try:
                data = response.json()
                if data.get("ok") and data.get("verified") and data.get("token"):
                    self.log_result("Existing User Flow (Verify)", True, "Existing user OTP flow successful")
                    return True
                else:
                    self.log_result("Existing User Flow (Verify)", False, "Missing verification data", data)
                    return False
            except json.JSONDecodeError:
                self.log_result("Existing User Flow (Verify)", False, "Invalid JSON response", response.text)
                return False
        else:
            try:
                error_data = response.json()
                self.log_result("Existing User Flow (Verify)", False, f"HTTP {response.status_code}: {error_data.get('detail', response.text)}")
            except:
                self.log_result("Existing User Flow (Verify)", False, f"HTTP {response.status_code}: {response.text}")
            return False
    
    def test_sms_service_functions(self):
        """Test SMS service functions directly"""
        try:
            # Import the SMS service
            import sys
            sys.path.append('/app/backend')
            from sms_service import generate_and_send, verify as verify_otp
            
            # Test OTP generation
            test_phone = "+1234567890"
            result = generate_and_send(test_phone)
            
            if result and "hash" in result and "expires_at" in result and "attempts_left" in result:
                self.log_result("SMS Service (Generate)", True, f"OTP generation successful. Hash length: {len(result['hash'])}")
                
                # Test verification with a dummy code
                test_code = "123456"
                is_valid = verify_otp(test_phone, test_code, result["hash"])
                
                # This should be False since we're using a dummy code
                if not is_valid:
                    self.log_result("SMS Service (Verify)", True, "OTP verification function working (correctly rejected dummy code)")
                    return True
                else:
                    self.log_result("SMS Service (Verify)", False, "OTP verification incorrectly accepted dummy code")
                    return False
            else:
                self.log_result("SMS Service (Generate)", False, f"Invalid result structure: {result}")
                return False
                
        except Exception as e:
            self.log_result("SMS Service (Functions)", False, f"Error testing SMS service: {str(e)}")
            return False
    
    def run_all_tests(self):
        """Run all Phone OTP tests"""
        print("🔐 Starting Phone OTP Authentication Backend Tests")
        print(f"📍 Testing against: {self.base_url}")
        print("=" * 70)
        
        # Test SMS service functions
        print("\n📱 Testing SMS Service Functions...")
        self.test_sms_service_functions()
        
        # Test invalid phone validation
        print("\n❌ Testing Invalid Phone Validation...")
        self.test_send_otp_invalid_phone()
        
        # Test valid phone OTP flow
        print("\n✅ Testing Valid Phone OTP Flow...")
        if self.test_send_otp_valid_phone():
            self.test_verify_otp_correct()
        
        # Test wrong OTP attempts
        print("\n🚫 Testing Wrong OTP & Attempts Limiting...")
        self.test_verify_otp_wrong_code()
        
        # Test expired/invalid OTP
        print("\n⏰ Testing Expired/Invalid OTP...")
        self.test_verify_otp_expired()
        
        # Test existing user flow
        print("\n👤 Testing Existing User OTP Flow...")
        self.test_existing_user_flow()
        
        # Summary
        print("\n" + "=" * 70)
        print("📊 PHONE OTP TEST SUMMARY")
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
    """Main function to run tests"""
    tester = PhoneOTPTester()
    passed, failed, results = tester.run_all_tests()
    
    # Exit with error code if tests failed
    if failed > 0:
        sys.exit(1)
    else:
        print("\n🎉 All Phone OTP tests passed!")
        sys.exit(0)

if __name__ == "__main__":
    main()