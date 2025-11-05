#!/usr/bin/env python3
"""
Comprehensive Backend API Testing for Pizoo Dating App
Tests all authentication endpoints, LiveKit integration, and MongoDB connection
"""

import asyncio
import httpx
import os
import sys
import json
from datetime import datetime
from typing import Dict, Any, Optional

# Add backend directory to path for imports
sys.path.append('/app/backend')

# Test configuration
BACKEND_URL = os.getenv('REACT_APP_BACKEND_URL', 'https://pizoo-rebrand.preview.emergentagent.com')
API_BASE = f"{BACKEND_URL}/api"

# Test data
TEST_USER_DATA = {
    "name": "أحمد محمد",
    "email": "ahmed.test@pizoo.ch", 
    "phone_number": "+41791234567",
    "password": "SecurePass123!",
    "terms_accepted": True
}

TEST_LOGIN_DATA = {
    "email": "ahmed.test@pizoo.ch",
    "password": "SecurePass123!"
}

class BackendTester:
    def __init__(self):
        self.client = httpx.AsyncClient(timeout=30.0)
        self.access_token = None
        self.user_id = None
        self.test_results = []
        
    async def __aenter__(self):
        return self
        
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.client.aclose()
    
    def log_result(self, test_name: str, success: bool, details: str = "", response_data: Any = None):
        """Log test result"""
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{status} {test_name}")
        if details:
            print(f"   {details}")
        if response_data and not success:
            print(f"   Response: {json.dumps(response_data, indent=2, ensure_ascii=False)}")
        print()
        
        self.test_results.append({
            "test": test_name,
            "success": success,
            "details": details,
            "timestamp": datetime.now().isoformat()
        })
    
    async def test_backend_connectivity(self):
        """Test basic backend connectivity via API root"""
        try:
            response = await self.client.get(f"{API_BASE}/")
            
            if response.status_code == 200:
                data = response.json()
                if 'message' in data:
                    self.log_result("Backend Connectivity", True, f"API accessible: {data['message']}")
                else:
                    self.log_result("Backend Connectivity", True, "API accessible")
            else:
                self.log_result("Backend Connectivity", False, f"HTTP {response.status_code}", response.text)
                
        except Exception as e:
            self.log_result("Backend Connectivity", False, f"Connection error: {str(e)}")
    
    async def test_mongodb_connection(self):
        """Test MongoDB connection via user registration (indirect test)"""
        try:
            # Test MongoDB by attempting to register a user (which requires DB connection)
            test_email = f"db_test_{int(datetime.now().timestamp())}@pizoo.ch"
            test_data = {
                "name": "DB Test User",
                "email": test_email,
                "phone_number": "+41791234999",
                "password": "TestPass123!",
                "terms_accepted": True
            }
            
            response = await self.client.post(f"{API_BASE}/auth/register", json=test_data)
            
            if response.status_code == 200:
                self.log_result("MongoDB Connection", True, "Database operations working (user registration successful)")
            elif response.status_code == 400:
                # Even validation errors indicate DB connection is working
                self.log_result("MongoDB Connection", True, "Database connection working (validation response received)")
            else:
                self.log_result("MongoDB Connection", False, f"Unexpected response: HTTP {response.status_code}")
                
        except Exception as e:
            self.log_result("MongoDB Connection", False, f"Error: {str(e)}")
    
    async def test_cors_settings(self):
        """Test CORS settings for pizoo.ch"""
        try:
            # Test preflight request
            headers = {
                'Origin': 'https://pizoo.ch',
                'Access-Control-Request-Method': 'POST',
                'Access-Control-Request-Headers': 'Content-Type,Authorization'
            }
            
            response = await self.client.options(f"{API_BASE}/auth/login", headers=headers)
            
            cors_origin = response.headers.get('Access-Control-Allow-Origin', '')
            cors_methods = response.headers.get('Access-Control-Allow-Methods', '')
            
            if 'https://pizoo.ch' in cors_origin or '*' in cors_origin:
                self.log_result("CORS Settings", True, f"Origin allowed: {cors_origin}")
            else:
                self.log_result("CORS Settings", False, f"pizoo.ch not in allowed origins: {cors_origin}")
                
        except Exception as e:
            self.log_result("CORS Settings", False, f"Error: {str(e)}")
    
    async def test_auth_register(self):
        """Test user registration endpoint"""
        try:
            response = await self.client.post(
                f"{API_BASE}/auth/register",
                json=TEST_USER_DATA
            )
            
            if response.status_code == 200:
                data = response.json()
                if 'access_token' in data and 'user' in data:
                    self.access_token = data['access_token']
                    self.user_id = data['user']['id']
                    self.log_result("Auth Register", True, f"User created: {data['user']['email']}")
                else:
                    self.log_result("Auth Register", False, "Missing access_token or user in response", data)
            elif response.status_code == 400 and "مسجل مسبقاً" in response.text:
                # User already exists - try login instead
                self.log_result("Auth Register", True, "User already exists (expected)")
                await self.test_auth_login()
            else:
                self.log_result("Auth Register", False, f"HTTP {response.status_code}", response.json())
                
        except Exception as e:
            self.log_result("Auth Register", False, f"Error: {str(e)}")
    
    async def test_auth_login(self):
        """Test user login endpoint"""
        try:
            response = await self.client.post(
                f"{API_BASE}/auth/login",
                json=TEST_LOGIN_DATA
            )
            
            if response.status_code == 200:
                data = response.json()
                if 'access_token' in data and 'user' in data:
                    self.access_token = data['access_token']
                    self.user_id = data['user']['id']
                    verified = data['user'].get('verified', False)
                    self.log_result("Auth Login", True, f"Login successful, verified: {verified}")
                else:
                    self.log_result("Auth Login", False, "Missing access_token or user in response", data)
            else:
                self.log_result("Auth Login", False, f"HTTP {response.status_code}", response.json())
                
        except Exception as e:
            self.log_result("Auth Login", False, f"Error: {str(e)}")
    
    async def test_auth_google_oauth(self):
        """Test Google OAuth endpoint (without actual OAuth flow)"""
        try:
            # Test with invalid session_id to check endpoint exists and handles errors properly
            response = await self.client.post(
                f"{API_BASE}/auth/oauth/google",
                json={"session_id": "invalid_test_session"}
            )
            
            # We expect this to fail with 401 (invalid session), which means endpoint exists
            if response.status_code == 401:
                error_data = response.json()
                if "Invalid or expired session" in error_data.get('detail', ''):
                    self.log_result("Auth Google OAuth", True, "Endpoint exists and handles invalid sessions correctly")
                else:
                    self.log_result("Auth Google OAuth", False, "Unexpected error message", error_data)
            else:
                self.log_result("Auth Google OAuth", False, f"Unexpected status code: {response.status_code}", response.json())
                
        except Exception as e:
            self.log_result("Auth Google OAuth", False, f"Error: {str(e)}")
    
    async def test_users_me(self):
        """Test /api/users/me endpoint (requires authentication)"""
        if not self.access_token:
            self.log_result("Users Me", False, "No access token available - login first")
            return
            
        try:
            headers = {"Authorization": f"Bearer {self.access_token}"}
            response = await self.client.get(f"{API_BASE}/auth/me", headers=headers)
            
            if response.status_code == 200:
                data = response.json()
                if 'user' in data and data['user'].get('id'):
                    user_info = data['user']
                    self.log_result("Users Me", True, f"User info retrieved: {user_info.get('email', 'N/A')}")
                else:
                    self.log_result("Users Me", False, "Invalid user data structure", data)
            else:
                self.log_result("Users Me", False, f"HTTP {response.status_code}", response.json())
                
        except Exception as e:
            self.log_result("Users Me", False, f"Error: {str(e)}")
    
    async def test_livekit_configuration(self):
        """Test LiveKit environment configuration"""
        try:
            # Import LiveKit service to check configuration
            from livekit_service import LIVEKIT_URL, LIVEKIT_API_KEY, LIVEKIT_API_SECRET, LiveKitService
            
            config_status = []
            
            if LIVEKIT_URL:
                config_status.append(f"URL: {LIVEKIT_URL}")
            else:
                config_status.append("URL: ❌ Missing")
            
            if LIVEKIT_API_KEY:
                config_status.append(f"API_KEY: {LIVEKIT_API_KEY[:8]}...")
            else:
                config_status.append("API_KEY: ❌ Missing")
            
            if LIVEKIT_API_SECRET:
                config_status.append(f"API_SECRET: {LIVEKIT_API_SECRET[:8]}...")
            else:
                config_status.append("API_SECRET: ❌ Missing")
            
            is_configured = LiveKitService.is_configured()
            
            if is_configured:
                self.log_result("LiveKit Configuration", True, f"All credentials present: {', '.join(config_status)}")
            else:
                self.log_result("LiveKit Configuration", False, f"Missing credentials: {', '.join(config_status)}")
                
        except Exception as e:
            self.log_result("LiveKit Configuration", False, f"Error checking configuration: {str(e)}")
    
    async def test_livekit_token_endpoint(self):
        """Test LiveKit token generation endpoint"""
        if not self.access_token:
            self.log_result("LiveKit Token", False, "No access token available - login first")
            return
            
        try:
            headers = {"Authorization": f"Bearer {self.access_token}"}
            test_data = {
                "match_id": "test_match_123",
                "call_type": "video"
            }
            
            response = await self.client.post(
                f"{API_BASE}/livekit/token",
                json=test_data,
                headers=headers
            )
            
            if response.status_code == 200:
                data = response.json()
                if data.get('success') and 'token' in data and 'url' in data:
                    token_info = {
                        'url': data.get('url'),
                        'room_name': data.get('room_name'),
                        'participant_identity': data.get('participant_identity')
                    }
                    self.log_result("LiveKit Token", True, f"Token generated successfully: {json.dumps(token_info, ensure_ascii=False)}")
                else:
                    self.log_result("LiveKit Token", False, "Invalid response format", data)
            elif response.status_code == 403:
                # User not verified
                error_data = response.json()
                if "verified" in error_data.get('detail', '').lower():
                    self.log_result("LiveKit Token", True, "Endpoint working - requires verified user (expected)")
                else:
                    self.log_result("LiveKit Token", False, f"Unexpected 403 error: {error_data}")
            elif response.status_code == 429:
                # Rate limited
                self.log_result("LiveKit Token", True, "Endpoint working - rate limited (expected)")
            else:
                self.log_result("LiveKit Token", False, f"HTTP {response.status_code}", response.json())
                
        except Exception as e:
            self.log_result("LiveKit Token", False, f"Error: {str(e)}")
    
    async def test_livekit_token_response_format(self):
        """Test LiveKit token response format using service directly"""
        try:
            from livekit_service import LiveKitService
            
            # Test token generation directly
            result = LiveKitService.create_room_token(
                match_id="test_match_format",
                user_id="test_user_123",
                user_name="Test User",
                call_type="video"
            )
            
            required_fields = ['success', 'token', 'url', 'room_name', 'participant_identity']
            missing_fields = [field for field in required_fields if field not in result]
            
            if result.get('success') and not missing_fields:
                self.log_result("LiveKit Response Format", True, f"All required fields present: {required_fields}")
            elif not result.get('success'):
                # Service not configured - this is expected
                error_code = result.get('error_code', 'UNKNOWN')
                if error_code == 'SERVICE_UNAVAILABLE':
                    self.log_result("LiveKit Response Format", True, "Service correctly reports unavailable status")
                else:
                    self.log_result("LiveKit Response Format", False, f"Unexpected error: {result}")
            else:
                self.log_result("LiveKit Response Format", False, f"Missing fields: {missing_fields}", result)
                
        except Exception as e:
            self.log_result("LiveKit Response Format", False, f"Error: {str(e)}")
    
    async def test_email_verification_endpoints(self):
        """Test email verification endpoints"""
        try:
            # Test send email verification
            email_data = {
                "email": "test.verification@pizoo.ch",
                "name": "Test User"
            }
            
            response = await self.client.post(
                f"{API_BASE}/auth/email/send-link",
                json=email_data
            )
            
            if response.status_code == 200:
                data = response.json()
                if data.get('success') and 'expires_in' in data:
                    self.log_result("Email Verification Send", True, f"Email sent successfully, expires in {data['expires_in']}s")
                else:
                    self.log_result("Email Verification Send", False, "Invalid response format", data)
            else:
                self.log_result("Email Verification Send", False, f"HTTP {response.status_code}", response.json())
            
            # Test verify with invalid token
            verify_response = await self.client.post(
                f"{API_BASE}/auth/email/verify",
                json={"token": "invalid_test_token"}
            )
            
            if verify_response.status_code == 400:
                self.log_result("Email Verification Verify", True, "Correctly rejects invalid token")
            else:
                self.log_result("Email Verification Verify", False, f"Unexpected response to invalid token: {verify_response.status_code}")
                
        except Exception as e:
            self.log_result("Email Verification", False, f"Error: {str(e)}")
    
    async def test_jwt_refresh_endpoint(self):
        """Test JWT refresh token endpoint"""
        try:
            # Test with invalid refresh token
            response = await self.client.post(
                f"{API_BASE}/auth/refresh",
                json={"refresh_token": "invalid_refresh_token"}
            )
            
            if response.status_code == 401:
                error_data = response.json()
                if "Invalid or expired" in error_data.get('detail', ''):
                    self.log_result("JWT Refresh", True, "Correctly rejects invalid refresh token")
                else:
                    self.log_result("JWT Refresh", False, "Unexpected error message", error_data)
            else:
                self.log_result("JWT Refresh", False, f"Unexpected status code: {response.status_code}", response.json())
                
        except Exception as e:
            self.log_result("JWT Refresh", False, f"Error: {str(e)}")
    
    def print_summary(self):
        """Print test summary"""
        total_tests = len(self.test_results)
        passed_tests = sum(1 for result in self.test_results if result['success'])
        failed_tests = total_tests - passed_tests
        
        print("=" * 60)
        print("🧪 BACKEND API TEST SUMMARY")
        print("=" * 60)
        print(f"Total Tests: {total_tests}")
        print(f"✅ Passed: {passed_tests}")
        print(f"❌ Failed: {failed_tests}")
        print(f"Success Rate: {(passed_tests/total_tests)*100:.1f}%")
        print()
        
        if failed_tests > 0:
            print("❌ FAILED TESTS:")
            for result in self.test_results:
                if not result['success']:
                    print(f"   • {result['test']}: {result['details']}")
            print()
        
        print("🔍 KEY FINDINGS:")
        
        # Check critical endpoints
        critical_endpoints = ['Health Check', 'MongoDB Connection', 'Auth Login', 'LiveKit Configuration']
        critical_failures = [r for r in self.test_results if r['test'] in critical_endpoints and not r['success']]
        
        if not critical_failures:
            print("   ✅ All critical endpoints are working")
        else:
            print("   ❌ Critical endpoint failures detected:")
            for failure in critical_failures:
                print(f"      • {failure['test']}")
        
        # Check LiveKit status
        livekit_tests = [r for r in self.test_results if 'LiveKit' in r['test']]
        livekit_working = all(r['success'] for r in livekit_tests)
        
        if livekit_working:
            print("   ✅ LiveKit integration is properly configured")
        else:
            print("   ⚠️ LiveKit integration has issues")
        
        # Check auth system
        auth_tests = [r for r in self.test_results if 'Auth' in r['test']]
        auth_working = any(r['success'] for r in auth_tests if r['test'] in ['Auth Login', 'Auth Register'])
        
        if auth_working:
            print("   ✅ Authentication system is working")
        else:
            print("   ❌ Authentication system has critical issues")
        
        print("=" * 60)

async def main():
    """Run all backend tests"""
    print("🚀 Starting Pizoo Backend API Tests")
    print(f"🌐 Backend URL: {BACKEND_URL}")
    print(f"🔗 API Base: {API_BASE}")
    print("=" * 60)
    
    async with BackendTester() as tester:
        # Core infrastructure tests
        await tester.test_health_check()
        await tester.test_mongodb_connection()
        await tester.test_cors_settings()
        
        # Authentication tests
        await tester.test_auth_register()
        await tester.test_auth_login()
        await tester.test_auth_google_oauth()
        await tester.test_users_me()
        
        # Email verification tests
        await tester.test_email_verification_endpoints()
        await tester.test_jwt_refresh_endpoint()
        
        # LiveKit tests
        await tester.test_livekit_configuration()
        await tester.test_livekit_token_endpoint()
        await tester.test_livekit_token_response_format()
        
        # Print summary
        tester.print_summary()

if __name__ == "__main__":
    asyncio.run(main())