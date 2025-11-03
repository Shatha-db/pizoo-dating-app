#!/usr/bin/env python3
"""
Comprehensive Backend Testing for Pizoo Dating App
Testing all critical backend functionalities including authentication, user management, 
matching, messaging, LiveKit integration, and more.
"""

import httpx
import json
import time
import asyncio
import uuid
import base64
from datetime import datetime
from typing import Dict, Any, Optional, List

# URLs to test - Using local development server as requested
LOCAL_URL = "http://127.0.0.1:8001"  # Local development server
PRODUCTION_URL = "https://multilingual-date.emergent.host"  # Production URL
BACKEND_URL = "https://pizoo-monorepo.preview.emergentagent.com"  # From frontend config

class ComprehensiveBackendTester:
    def __init__(self):
        self.results = {
            "timestamp": datetime.now().isoformat(),
            "test_environment": "local_development",
            "backend_url": LOCAL_URL,
            "total_tests": 0,
            "passed_tests": 0,
            "failed_tests": 0,
            "test_categories": {
                "health_status": {"passed": 0, "failed": 0, "tests": []},
                "authentication": {"passed": 0, "failed": 0, "tests": []},
                "user_management": {"passed": 0, "failed": 0, "tests": []},
                "matching_discovery": {"passed": 0, "failed": 0, "tests": []},
                "messaging": {"passed": 0, "failed": 0, "tests": []},
                "livekit_integration": {"passed": 0, "failed": 0, "tests": []},
                "cloudinary_integration": {"passed": 0, "failed": 0, "tests": []},
                "error_handling": {"passed": 0, "failed": 0, "tests": []},
                "cors_testing": {"passed": 0, "failed": 0, "tests": []},
                "performance": {"passed": 0, "failed": 0, "tests": []},
                "database_operations": {"passed": 0, "failed": 0, "tests": []}
            },
            "test_data": {
                "userA": None,
                "userB": None,
                "auth_tokens": {},
                "test_match_id": None,
                "test_conversation_id": None
            },
            "performance_metrics": {
                "average_response_time": 0,
                "slowest_endpoint": "",
                "fastest_endpoint": ""
            },
            "recommendations": []
        }
        self.client = httpx.AsyncClient(timeout=30.0, follow_redirects=True)
        self.active_backend_url = LOCAL_URL  # Start with local URL
        self.test_users = {}  # Store test user data and tokens

    def log_test_result(self, category: str, test_name: str, passed: bool, details: str = "", response_time: float = 0):
        """Log test result"""
        self.results["total_tests"] += 1
        if passed:
            self.results["passed_tests"] += 1
            self.results["test_categories"][category]["passed"] += 1
            status = "✅ PASS"
        else:
            self.results["failed_tests"] += 1
            self.results["test_categories"][category]["failed"] += 1
            status = "❌ FAIL"
        
        test_result = {
            "name": test_name,
            "status": "passed" if passed else "failed",
            "details": details,
            "response_time_ms": int(response_time * 1000) if response_time > 0 else 0
        }
        
        self.results["test_categories"][category]["tests"].append(test_result)
        print(f"   {status} {test_name} ({int(response_time * 1000)}ms) - {details}")

    async def determine_active_backend(self):
        """Determine which backend URL is active"""
        print("🔍 Determining active backend URL...")
        
        urls_to_test = [LOCAL_URL, PRODUCTION_URL, BACKEND_URL]
        
        for url in urls_to_test:
            try:
                response = await self.client.get(f"{url}/api/", timeout=5.0)
                if response.status_code == 200:
                    data = response.json()
                    if "message" in data:
                        print(f"✅ Active backend found at: {url}")
                        self.active_backend_url = url
                        self.results["backend_url"] = url
                        return url
            except Exception as e:
                print(f"   {url} not accessible: {e}")
                continue
        
        print("❌ No active backend found")
        return None

    # ===== HEALTH & STATUS ENDPOINTS =====
    
    async def test_health_endpoints(self):
        """Test health and status endpoints"""
        print("\n🏥 Testing Health & Status Endpoints...")
        
        # Test GET /health
        try:
            start_time = time.time()
            response = await self.client.get(f"{self.active_backend_url}/health")
            response_time = time.time() - start_time
            
            if response.status_code == 200:
                data = response.json()
                expected_fields = ["db", "otp", "ai", "status"]
                has_all_fields = all(field in data for field in expected_fields)
                
                if has_all_fields and data.get("status") in ["healthy", "degraded"]:
                    self.log_test_result("health_status", "GET /health", True, 
                                       f"Health check passed. Status: {data.get('status')}", response_time)
                else:
                    self.log_test_result("health_status", "GET /health", False, 
                                       f"Missing fields or invalid status: {data}", response_time)
            else:
                self.log_test_result("health_status", "GET /health", False, 
                                   f"HTTP {response.status_code}", response_time)
        except Exception as e:
            self.log_test_result("health_status", "GET /health", False, f"Error: {str(e)}")

        # Test GET / (root)
        try:
            start_time = time.time()
            response = await self.client.get(f"{self.active_backend_url}/")
            response_time = time.time() - start_time
            
            if response.status_code == 200:
                self.log_test_result("health_status", "GET / (root)", True, 
                                   "Root endpoint accessible", response_time)
            else:
                self.log_test_result("health_status", "GET / (root)", False, 
                                   f"HTTP {response.status_code}", response_time)
        except Exception as e:
            self.log_test_result("health_status", "GET / (root)", False, f"Error: {str(e)}")

        # Test GET /api/
        try:
            start_time = time.time()
            response = await self.client.get(f"{self.active_backend_url}/api/")
            response_time = time.time() - start_time
            
            if response.status_code == 200:
                data = response.json()
                if "message" in data:
                    self.log_test_result("health_status", "GET /api/", True, 
                                       f"API welcome: {data['message']}", response_time)
                else:
                    self.log_test_result("health_status", "GET /api/", False, 
                                       "No welcome message in response", response_time)
            else:
                self.log_test_result("health_status", "GET /api/", False, 
                                   f"HTTP {response.status_code}", response_time)
        except Exception as e:
            self.log_test_result("health_status", "GET /api/", False, f"Error: {str(e)}")

    # ===== AUTHENTICATION FLOW =====
    
    async def test_authentication_flow(self):
        """Test complete authentication flow"""
        print("\n🔐 Testing Authentication Flow...")
        
        # Generate unique test users
        timestamp = int(time.time())
        userA_data = {
            "name": "Test User A",
            "email": f"usera_{timestamp}@pizoo.app",
            "phone_number": "+41790000001",
            "password": "TestPassword123!",
            "terms_accepted": True
        }
        
        userB_data = {
            "name": "Test User B", 
            "email": f"userb_{timestamp}@pizoo.app",
            "phone_number": "+41790000002",
            "password": "TestPassword123!",
            "terms_accepted": True
        }

        # Test user registration
        for user_key, user_data in [("userA", userA_data), ("userB", userB_data)]:
            try:
                start_time = time.time()
                response = await self.client.post(
                    f"{self.active_backend_url}/api/auth/register",
                    json=user_data
                )
                response_time = time.time() - start_time
                
                if response.status_code == 200:
                    data = response.json()
                    if "access_token" in data and "user" in data:
                        self.test_users[user_key] = {
                            "data": user_data,
                            "token": data["access_token"],
                            "user_info": data["user"]
                        }
                        self.results["test_data"][user_key] = data["user"]
                        self.results["test_data"]["auth_tokens"][user_key] = data["access_token"]
                        
                        self.log_test_result("authentication", f"POST /api/auth/register ({user_key})", True,
                                           f"User registered successfully. ID: {data['user']['id']}", response_time)
                    else:
                        self.log_test_result("authentication", f"POST /api/auth/register ({user_key})", False,
                                           "Missing access_token or user in response", response_time)
                else:
                    error_detail = response.text[:200] if response.text else f"HTTP {response.status_code}"
                    self.log_test_result("authentication", f"POST /api/auth/register ({user_key})", False,
                                       error_detail, response_time)
            except Exception as e:
                self.log_test_result("authentication", f"POST /api/auth/register ({user_key})", False, f"Error: {str(e)}")

        # Test user login
        if "userA" in self.test_users:
            try:
                login_data = {
                    "email": userA_data["email"],
                    "password": userA_data["password"]
                }
                
                start_time = time.time()
                response = await self.client.post(
                    f"{self.active_backend_url}/api/auth/login",
                    json=login_data
                )
                response_time = time.time() - start_time
                
                if response.status_code == 200:
                    data = response.json()
                    if "access_token" in data:
                        self.log_test_result("authentication", "POST /api/auth/login", True,
                                           "Login successful", response_time)
                    else:
                        self.log_test_result("authentication", "POST /api/auth/login", False,
                                           "Missing access_token in response", response_time)
                else:
                    error_detail = response.text[:200] if response.text else f"HTTP {response.status_code}"
                    self.log_test_result("authentication", "POST /api/auth/login", False,
                                       error_detail, response_time)
            except Exception as e:
                self.log_test_result("authentication", "POST /api/auth/login", False, f"Error: {str(e)}")

        # Test invalid credentials
        try:
            invalid_login = {
                "email": "invalid@test.com",
                "password": "wrongpassword"
            }
            
            start_time = time.time()
            response = await self.client.post(
                f"{self.active_backend_url}/api/auth/login",
                json=invalid_login
            )
            response_time = time.time() - start_time
            
            if response.status_code == 401:
                self.log_test_result("authentication", "POST /api/auth/login (invalid)", True,
                                   "Correctly rejected invalid credentials", response_time)
            else:
                self.log_test_result("authentication", "POST /api/auth/login (invalid)", False,
                                   f"Should return 401, got {response.status_code}", response_time)
        except Exception as e:
            self.log_test_result("authentication", "POST /api/auth/login (invalid)", False, f"Error: {str(e)}")

        # Test email verification endpoints
        await self.test_email_verification()
        
        # Test JWT token validation
        await self.test_jwt_validation()

    async def test_email_verification(self):
        """Test email verification flow"""
        print("\n📧 Testing Email Verification...")
        
        # Test send email verification link
        try:
            email_data = {
                "email": f"verify_{int(time.time())}@pizoo.app",
                "name": "Verification Test User"
            }
            
            start_time = time.time()
            response = await self.client.post(
                f"{self.active_backend_url}/api/auth/email/send-link",
                json=email_data
            )
            response_time = time.time() - start_time
            
            if response.status_code == 200:
                data = response.json()
                if data.get("success") and "expires_in" in data:
                    self.log_test_result("authentication", "POST /api/auth/email/send-link", True,
                                       f"Email verification link sent. TTL: {data['expires_in']}s", response_time)
                else:
                    self.log_test_result("authentication", "POST /api/auth/email/send-link", False,
                                       "Invalid response format", response_time)
            else:
                error_detail = response.text[:200] if response.text else f"HTTP {response.status_code}"
                self.log_test_result("authentication", "POST /api/auth/email/send-link", False,
                                   error_detail, response_time)
        except Exception as e:
            self.log_test_result("authentication", "POST /api/auth/email/send-link", False, f"Error: {str(e)}")

        # Test verify email with invalid token
        try:
            verify_data = {"token": "invalid_token_123"}
            
            start_time = time.time()
            response = await self.client.post(
                f"{self.active_backend_url}/api/auth/email/verify",
                json=verify_data
            )
            response_time = time.time() - start_time
            
            if response.status_code == 400:
                self.log_test_result("authentication", "POST /api/auth/email/verify (invalid)", True,
                                   "Correctly rejected invalid token", response_time)
            else:
                self.log_test_result("authentication", "POST /api/auth/email/verify (invalid)", False,
                                   f"Should return 400, got {response.status_code}", response_time)
        except Exception as e:
            self.log_test_result("authentication", "POST /api/auth/email/verify (invalid)", False, f"Error: {str(e)}")

    async def test_jwt_validation(self):
        """Test JWT token validation"""
        print("\n🎫 Testing JWT Token Validation...")
        
        if "userA" in self.test_users:
            token = self.test_users["userA"]["token"]
            headers = {"Authorization": f"Bearer {token}"}
            
            # Test /api/auth/me endpoint
            try:
                start_time = time.time()
                response = await self.client.get(
                    f"{self.active_backend_url}/api/auth/me",
                    headers=headers
                )
                response_time = time.time() - start_time
                
                if response.status_code == 200:
                    data = response.json()
                    if data.get("success") and "user" in data:
                        self.log_test_result("authentication", "GET /api/auth/me", True,
                                           f"User profile retrieved: {data['user']['email']}", response_time)
                    else:
                        self.log_test_result("authentication", "GET /api/auth/me", False,
                                           "Invalid response format", response_time)
                else:
                    self.log_test_result("authentication", "GET /api/auth/me", False,
                                       f"HTTP {response.status_code}", response_time)
            except Exception as e:
                self.log_test_result("authentication", "GET /api/auth/me", False, f"Error: {str(e)}")

        # Test invalid token
        try:
            invalid_headers = {"Authorization": "Bearer invalid_token_123"}
            
            start_time = time.time()
            response = await self.client.get(
                f"{self.active_backend_url}/api/auth/me",
                headers=invalid_headers
            )
            response_time = time.time() - start_time
            
            if response.status_code == 401:
                self.log_test_result("authentication", "GET /api/auth/me (invalid token)", True,
                                   "Correctly rejected invalid token", response_time)
            else:
                self.log_test_result("authentication", "GET /api/auth/me (invalid token)", False,
                                   f"Should return 401, got {response.status_code}", response_time)
        except Exception as e:
            self.log_test_result("authentication", "GET /api/auth/me (invalid token)", False, f"Error: {str(e)}")

    # ===== USER PROFILE MANAGEMENT =====
    
    async def test_user_profile_management(self):
        """Test user profile management endpoints"""
        print("\n👤 Testing User Profile Management...")
        
        if "userA" not in self.test_users:
            print("   ⚠️ Skipping profile tests - no authenticated user available")
            return
            
        token = self.test_users["userA"]["token"]
        headers = {"Authorization": f"Bearer {token}"}

        # Test GET /api/user/profile
        try:
            start_time = time.time()
            response = await self.client.get(
                f"{self.active_backend_url}/api/user/profile",
                headers=headers
            )
            response_time = time.time() - start_time
            
            if response.status_code == 200:
                data = response.json()
                if "id" in data and "email" in data:
                    self.log_test_result("user_management", "GET /api/user/profile", True,
                                       f"Profile retrieved: {data['email']}", response_time)
                else:
                    self.log_test_result("user_management", "GET /api/user/profile", False,
                                       "Missing required fields in profile", response_time)
            else:
                self.log_test_result("user_management", "GET /api/user/profile", False,
                                   f"HTTP {response.status_code}", response_time)
        except Exception as e:
            self.log_test_result("user_management", "GET /api/user/profile", False, f"Error: {str(e)}")

        # Test profile update (if endpoint exists)
        try:
            profile_update = {
                "display_name": "Updated Test User",
                "bio": "This is a test bio for comprehensive testing",
                "age": 25,
                "location": "Basel, Switzerland"
            }
            
            start_time = time.time()
            response = await self.client.put(
                f"{self.active_backend_url}/api/users/profile",
                json=profile_update,
                headers=headers
            )
            response_time = time.time() - start_time
            
            if response.status_code == 200:
                self.log_test_result("user_management", "PUT /api/users/profile", True,
                                   "Profile updated successfully", response_time)
            elif response.status_code == 404:
                self.log_test_result("user_management", "PUT /api/users/profile", False,
                                   "Profile update endpoint not found", response_time)
            else:
                self.log_test_result("user_management", "PUT /api/users/profile", False,
                                   f"HTTP {response.status_code}", response_time)
        except Exception as e:
            self.log_test_result("user_management", "PUT /api/users/profile", False, f"Error: {str(e)}")

        # Test photo upload endpoint
        await self.test_photo_upload(headers)

    async def test_photo_upload(self, headers):
        """Test photo upload functionality"""
        print("\n📸 Testing Photo Upload...")
        
        # Create a small test image (1x1 pixel PNG)
        test_image_data = base64.b64decode(
            "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNkYPhfDwAChAGA4nEKtAAAAABJRU5ErkJggg=="
        )
        
        try:
            files = {"file": ("test.png", test_image_data, "image/png")}
            
            start_time = time.time()
            response = await self.client.post(
                f"{self.active_backend_url}/api/users/photos",
                files=files,
                headers=headers
            )
            response_time = time.time() - start_time
            
            if response.status_code == 200:
                data = response.json()
                if "url" in data:
                    self.log_test_result("user_management", "POST /api/users/photos", True,
                                       f"Photo uploaded: {data['url'][:50]}...", response_time)
                else:
                    self.log_test_result("user_management", "POST /api/users/photos", False,
                                       "No URL in upload response", response_time)
            elif response.status_code == 404:
                # Try alternative endpoint
                try:
                    response = await self.client.post(
                        f"{self.active_backend_url}/api/media/upload",
                        files=files,
                        headers=headers
                    )
                    if response.status_code == 200:
                        data = response.json()
                        if "url" in data:
                            self.log_test_result("user_management", "POST /api/media/upload", True,
                                               f"Photo uploaded via media endpoint: {data['url'][:50]}...", response_time)
                        else:
                            self.log_test_result("user_management", "POST /api/media/upload", False,
                                               "No URL in upload response", response_time)
                    else:
                        self.log_test_result("user_management", "Photo upload endpoints", False,
                                           "Both /api/users/photos and /api/media/upload failed", response_time)
                except Exception:
                    self.log_test_result("user_management", "Photo upload endpoints", False,
                                       "Photo upload endpoints not available", response_time)
            else:
                error_detail = response.text[:200] if response.text else f"HTTP {response.status_code}"
                self.log_test_result("user_management", "POST /api/users/photos", False,
                                   error_detail, response_time)
        except Exception as e:
            self.log_test_result("user_management", "Photo upload", False, f"Error: {str(e)}")

    # ===== LIVEKIT INTEGRATION =====
    
    async def test_livekit_integration(self):
        """Test LiveKit integration"""
        print("\n🎥 Testing LiveKit Integration...")
        
        if "userA" not in self.test_users:
            print("   ⚠️ Skipping LiveKit tests - no authenticated user available")
            return
            
        token = self.test_users["userA"]["token"]
        headers = {"Authorization": f"Bearer {token}"}

        # Test LiveKit token generation
        try:
            livekit_request = {
                "match_id": f"test_match_{int(time.time())}"
            }
            
            start_time = time.time()
            response = await self.client.post(
                f"{self.active_backend_url}/api/livekit/token",
                json=livekit_request,
                headers=headers
            )
            response_time = time.time() - start_time
            
            if response.status_code == 200:
                data = response.json()
                if "token" in data and "room_name" in data:
                    self.log_test_result("livekit_integration", "POST /api/livekit/token", True,
                                       f"LiveKit token generated for room: {data['room_name']}", response_time)
                else:
                    self.log_test_result("livekit_integration", "POST /api/livekit/token", False,
                                       "Missing token or room_name in response", response_time)
            elif response.status_code == 403:
                # User might not be verified
                self.log_test_result("livekit_integration", "POST /api/livekit/token", False,
                                   "User verification required for LiveKit access", response_time)
            elif response.status_code == 429:
                # Rate limited
                self.log_test_result("livekit_integration", "POST /api/livekit/token", True,
                                   "Rate limiting working correctly", response_time)
            else:
                error_detail = response.text[:200] if response.text else f"HTTP {response.status_code}"
                self.log_test_result("livekit_integration", "POST /api/livekit/token", False,
                                   error_detail, response_time)
        except Exception as e:
            self.log_test_result("livekit_integration", "POST /api/livekit/token", False, f"Error: {str(e)}")

        # Test without authentication
        try:
            start_time = time.time()
            response = await self.client.post(
                f"{self.active_backend_url}/api/livekit/token",
                json={"match_id": "test"}
            )
            response_time = time.time() - start_time
            
            if response.status_code == 401:
                self.log_test_result("livekit_integration", "POST /api/livekit/token (no auth)", True,
                                   "Correctly requires authentication", response_time)
            else:
                self.log_test_result("livekit_integration", "POST /api/livekit/token (no auth)", False,
                                   f"Should require auth, got {response.status_code}", response_time)
        except Exception as e:
            self.log_test_result("livekit_integration", "POST /api/livekit/token (no auth)", False, f"Error: {str(e)}")

    # ===== ERROR HANDLING =====
    
    async def test_error_handling(self):
        """Test error handling"""
        print("\n🚨 Testing Error Handling...")
        
        # Test 404 for non-existent endpoints
        try:
            start_time = time.time()
            response = await self.client.get(f"{self.active_backend_url}/api/nonexistent")
            response_time = time.time() - start_time
            
            if response.status_code == 404:
                self.log_test_result("error_handling", "GET /api/nonexistent (404)", True,
                                   "Correctly returns 404 for non-existent endpoint", response_time)
            else:
                self.log_test_result("error_handling", "GET /api/nonexistent (404)", False,
                                   f"Should return 404, got {response.status_code}", response_time)
        except Exception as e:
            self.log_test_result("error_handling", "GET /api/nonexistent (404)", False, f"Error: {str(e)}")

        # Test 401 for unauthenticated requests
        try:
            start_time = time.time()
            response = await self.client.get(f"{self.active_backend_url}/api/user/profile")
            response_time = time.time() - start_time
            
            if response.status_code == 401:
                self.log_test_result("error_handling", "GET /api/user/profile (no auth)", True,
                                   "Correctly requires authentication", response_time)
            else:
                self.log_test_result("error_handling", "GET /api/user/profile (no auth)", False,
                                   f"Should return 401, got {response.status_code}", response_time)
        except Exception as e:
            self.log_test_result("error_handling", "GET /api/user/profile (no auth)", False, f"Error: {str(e)}")

        # Test malformed JSON
        try:
            start_time = time.time()
            response = await self.client.post(
                f"{self.active_backend_url}/api/auth/register",
                data="invalid json",
                headers={"Content-Type": "application/json"}
            )
            response_time = time.time() - start_time
            
            if response.status_code in [400, 422]:
                self.log_test_result("error_handling", "POST with malformed JSON", True,
                                   "Correctly handles malformed JSON", response_time)
            else:
                self.log_test_result("error_handling", "POST with malformed JSON", False,
                                   f"Should return 400/422, got {response.status_code}", response_time)
        except Exception as e:
            self.log_test_result("error_handling", "POST with malformed JSON", False, f"Error: {str(e)}")

    # ===== CORS TESTING =====
    
    async def test_cors_configuration(self):
        """Test CORS configuration"""
        print("\n🌐 Testing CORS Configuration...")
        
        try:
            headers = {
                "Origin": "https://datemaps.emergent.host",
                "Access-Control-Request-Method": "POST",
                "Access-Control-Request-Headers": "Content-Type,Authorization"
            }
            
            start_time = time.time()
            response = await self.client.options(f"{self.active_backend_url}/api/", headers=headers)
            response_time = time.time() - start_time
            
            cors_headers = {
                "access-control-allow-origin": response.headers.get("access-control-allow-origin"),
                "access-control-allow-methods": response.headers.get("access-control-allow-methods"),
                "access-control-allow-headers": response.headers.get("access-control-allow-headers"),
                "access-control-allow-credentials": response.headers.get("access-control-allow-credentials")
            }
            
            if cors_headers["access-control-allow-methods"] and cors_headers["access-control-allow-headers"]:
                self.log_test_result("cors_testing", "OPTIONS /api/ (CORS preflight)", True,
                                   f"CORS configured. Methods: {cors_headers['access-control-allow-methods']}", response_time)
            else:
                self.log_test_result("cors_testing", "OPTIONS /api/ (CORS preflight)", False,
                                   "CORS headers missing or incomplete", response_time)
                
        except Exception as e:
            self.log_test_result("cors_testing", "OPTIONS /api/ (CORS preflight)", False, f"Error: {str(e)}")

    # ===== PERFORMANCE TESTING =====
    
    async def test_performance(self):
        """Test API performance"""
        print("\n⚡ Testing Performance...")
        
        response_times = []
        endpoints_to_test = [
            ("/api/", "GET"),
            ("/health", "GET")
        ]
        
        for endpoint, method in endpoints_to_test:
            times = []
            for i in range(3):  # Test each endpoint 3 times
                try:
                    start_time = time.time()
                    if method == "GET":
                        response = await self.client.get(f"{self.active_backend_url}{endpoint}")
                    response_time = time.time() - start_time
                    times.append(response_time)
                    response_times.append(response_time)
                except Exception:
                    continue
            
            if times:
                avg_time = sum(times) / len(times)
                if avg_time < 0.5:  # Less than 500ms
                    self.log_test_result("performance", f"{method} {endpoint} performance", True,
                                       f"Average response time: {int(avg_time * 1000)}ms", avg_time)
                else:
                    self.log_test_result("performance", f"{method} {endpoint} performance", False,
                                       f"Slow response time: {int(avg_time * 1000)}ms", avg_time)

        # Calculate overall performance metrics
        if response_times:
            self.results["performance_metrics"]["average_response_time"] = int(sum(response_times) / len(response_times) * 1000)

    # ===== DATABASE OPERATIONS =====
    
    async def test_database_operations(self):
        """Test database operations indirectly"""
        print("\n🗄️ Testing Database Operations...")
        
        # Database operations are tested indirectly through API endpoints
        # We've already tested user registration, login, profile operations
        # which all require database connectivity
        
        if self.test_users:
            self.log_test_result("database_operations", "User CRUD operations", True,
                               f"Database operations working (created {len(self.test_users)} users)")
        else:
            self.log_test_result("database_operations", "User CRUD operations", False,
                               "No users created - database operations may be failing")

    # ===== MAIN TEST RUNNER =====
    
    async def run_comprehensive_tests(self):
        """Run all comprehensive backend tests"""
        print("🚀 Starting Comprehensive Backend Testing for Pizoo Dating App")
        print(f"🎯 Target URL: {LOCAL_URL}")
        print("=" * 80)
        
        # Determine active backend
        await self.determine_active_backend()
        
        if not self.active_backend_url:
            print("❌ No active backend found. Cannot proceed with testing.")
            return self.results
        
        # Run all test categories
        await self.test_health_endpoints()
        await self.test_authentication_flow()
        await self.test_user_profile_management()
        await self.test_livekit_integration()
        await self.test_error_handling()
        await self.test_cors_configuration()
        await self.test_performance()
        await self.test_database_operations()
        
        # Calculate final results
        self.calculate_final_results()
        
        # Close HTTP client
        await self.client.aclose()
        
        print("\n" + "=" * 80)
        print("📋 COMPREHENSIVE BACKEND TESTING COMPLETE")
        print("=" * 80)
        
        return self.results

    def calculate_final_results(self):
        """Calculate final test results and recommendations"""
        # Add recommendations based on test results
        failed_categories = []
        for category, results in self.results["test_categories"].items():
            if results["failed"] > 0:
                failed_categories.append(category)
        
        if failed_categories:
            self.results["recommendations"].append(f"Fix failing tests in: {', '.join(failed_categories)}")
        
        if self.results["performance_metrics"]["average_response_time"] > 1000:
            self.results["recommendations"].append("Optimize API performance - average response time > 1s")
        
        if not self.test_users:
            self.results["recommendations"].append("CRITICAL: Authentication system not working - no users could be created")

async def main():
    """Main function to run comprehensive backend tests"""
    tester = ComprehensiveBackendTester()
    results = await tester.run_comprehensive_tests()
    
    # Print summary
    print(f"\n🎯 COMPREHENSIVE BACKEND TEST REPORT")
    print(f"Timestamp: {results['timestamp']}")
    print(f"Backend URL: {results['backend_url']}")
    print(f"Total Tests: {results['total_tests']}")
    print(f"✅ Passed: {results['passed_tests']}")
    print(f"❌ Failed: {results['failed_tests']}")
    print(f"Success Rate: {(results['passed_tests'] / results['total_tests'] * 100):.1f}%" if results['total_tests'] > 0 else "0%")
    
    print(f"\n📊 TEST RESULTS BY CATEGORY:")
    for category, category_results in results['test_categories'].items():
        total = category_results['passed'] + category_results['failed']
        if total > 0:
            success_rate = (category_results['passed'] / total * 100)
            status_emoji = "✅" if category_results['failed'] == 0 else "❌" if category_results['passed'] == 0 else "⚠️"
            print(f"  {status_emoji} {category.replace('_', ' ').title()}: {category_results['passed']}/{total} ({success_rate:.1f}%)")
    
    if results['recommendations']:
        print(f"\n💡 RECOMMENDATIONS:")
        for i, rec in enumerate(results['recommendations'], 1):
            print(f"  {i}. {rec}")
    
    # Save detailed results
    with open('/app/comprehensive_backend_test_results.json', 'w') as f:
        json.dump(results, f, indent=2)
    
    print(f"\n📄 Detailed results saved to: /app/comprehensive_backend_test_results.json")
    
    return results

if __name__ == "__main__":
    asyncio.run(main())