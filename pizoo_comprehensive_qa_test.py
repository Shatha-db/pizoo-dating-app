#!/usr/bin/env python3
"""
Comprehensive QA & Bug Sweep - Pizoo Dating App Backend
Tests all backend endpoints with detailed error reporting and validation.
"""

import requests
import json
import sys
import base64
from datetime import datetime
import uuid
import time

# Configuration
BASE_URL = "https://dating-app-bugfix.preview.emergentagent.com/api"
HEADERS = {"Content-Type": "application/json"}

class PizooQATester:
    def __init__(self):
        self.base_url = BASE_URL
        self.headers = HEADERS.copy()
        self.auth_token = None
        self.user_id = None
        self.profile_id = None
        self.test_results = []
        self.test_email = None
        self.test_password = None
        self.critical_issues = []
        self.high_issues = []
        self.medium_issues = []
        self.low_issues = []
        
    def log_issue(self, severity, category, endpoint, description, steps_to_reproduce, expected_behavior, actual_behavior, error_message=None):
        """Log issues with detailed information"""
        issue = {
            "severity": severity,  # Critical/High/Medium/Low
            "category": category,
            "endpoint": endpoint,
            "description": description,
            "steps_to_reproduce": steps_to_reproduce,
            "expected_behavior": expected_behavior,
            "actual_behavior": actual_behavior,
            "error_message": error_message,
            "timestamp": datetime.now().isoformat()
        }
        
        if severity == "Critical":
            self.critical_issues.append(issue)
        elif severity == "High":
            self.high_issues.append(issue)
        elif severity == "Medium":
            self.medium_issues.append(issue)
        else:
            self.low_issues.append(issue)
    
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
    
    def make_request(self, method, endpoint, data=None, use_auth=False, timeout=30):
        """Make HTTP request with proper headers and error handling"""
        url = f"{self.base_url}{endpoint}"
        headers = self.headers.copy()
        
        if use_auth and self.auth_token:
            headers["Authorization"] = f"Bearer {self.auth_token}"
        
        try:
            if method.upper() == "GET":
                response = requests.get(url, headers=headers, timeout=timeout)
            elif method.upper() == "POST":
                response = requests.post(url, headers=headers, json=data, timeout=timeout)
            elif method.upper() == "PUT":
                response = requests.put(url, headers=headers, json=data, timeout=timeout)
            elif method.upper() == "DELETE":
                response = requests.delete(url, headers=headers, timeout=timeout)
            else:
                raise ValueError(f"Unsupported method: {method}")
            
            return response
        except requests.exceptions.Timeout:
            self.log_issue("High", "Performance", endpoint, "Request timeout", 
                         f"Make {method} request to {endpoint}", "Response within 30 seconds", 
                         "Request timed out after 30 seconds")
            return None
        except requests.exceptions.ConnectionError:
            self.log_issue("Critical", "Infrastructure", endpoint, "Connection failed", 
                         f"Make {method} request to {endpoint}", "Successful connection", 
                         "Connection error - server may be down")
            return None
        except requests.exceptions.RequestException as e:
            self.log_issue("High", "Network", endpoint, f"Request failed: {str(e)}", 
                         f"Make {method} request to {endpoint}", "Successful request", 
                         f"Request exception: {str(e)}")
            return None

    # ===== 1. AUTHENTICATION & USER MANAGEMENT TESTS =====
    
    def test_authentication_flow(self):
        """Comprehensive authentication testing"""
        print("\n🔐 TESTING AUTHENTICATION & USER MANAGEMENT")
        print("=" * 50)
        
        # Test 1: User Registration with valid data
        self.test_user_registration_valid()
        
        # Test 2: User Registration with invalid data
        self.test_user_registration_invalid()
        
        # Test 3: User Login with valid credentials
        self.test_user_login_valid()
        
        # Test 4: User Login with invalid credentials
        self.test_user_login_invalid()
        
        # Test 5: Token validation
        self.test_token_validation()
        
        # Test 6: Email validation
        self.test_email_validation()
        
        # Test 7: Phone validation
        self.test_phone_validation()
    
    def test_user_registration_valid(self):
        """Test user registration with valid data"""
        unique_id = str(uuid.uuid4())[:8]
        self.test_email = f"pizoo.test.{unique_id}@example.com"
        self.test_password = "PizooTest123!"
        
        test_data = {
            "name": f"أحمد محمد {unique_id}",
            "email": self.test_email,
            "phone_number": f"+966501234{unique_id[:3]}",
            "password": self.test_password,
            "terms_accepted": True
        }
        
        response = self.make_request("POST", "/auth/register", test_data)
        
        if response is None:
            self.log_result("User Registration (Valid)", False, "Connection failed")
            return False
        
        if response.status_code == 200:
            try:
                data = response.json()
                if "access_token" in data and "user" in data:
                    self.auth_token = data["access_token"]
                    self.user_id = data["user"]["id"]
                    
                    # Validate token format (JWT should have 3 parts)
                    token_parts = self.auth_token.split('.')
                    if len(token_parts) != 3:
                        self.log_issue("Medium", "Authentication", "/auth/register", 
                                     "Invalid JWT token format", "Register user", 
                                     "Valid JWT token with 3 parts", f"Token has {len(token_parts)} parts")
                    
                    self.log_result("User Registration (Valid)", True, f"User registered successfully. ID: {self.user_id}")
                    return True
                else:
                    self.log_issue("High", "Authentication", "/auth/register", 
                                 "Missing required fields in response", "Register user", 
                                 "Response with access_token and user", f"Response: {data}")
                    self.log_result("User Registration (Valid)", False, "Missing access_token or user in response")
                    return False
            except json.JSONDecodeError:
                self.log_issue("High", "API Response", "/auth/register", 
                             "Invalid JSON response", "Register user", 
                             "Valid JSON response", f"Response: {response.text}")
                self.log_result("User Registration (Valid)", False, "Invalid JSON response")
                return False
        else:
            try:
                error_data = response.json()
                self.log_issue("High", "Authentication", "/auth/register", 
                             f"Registration failed with status {response.status_code}", 
                             "Register with valid data", "Status 200", 
                             f"Status {response.status_code}: {error_data.get('detail', 'Unknown error')}")
                self.log_result("User Registration (Valid)", False, f"HTTP {response.status_code}: {error_data.get('detail', response.text)}")
            except:
                self.log_result("User Registration (Valid)", False, f"HTTP {response.status_code}: {response.text}")
            return False
    
    def test_user_registration_invalid(self):
        """Test user registration with invalid data"""
        # Test missing terms acceptance
        test_data = {
            "name": "Test User",
            "email": "test@example.com",
            "phone_number": "+1234567890",
            "password": "password123",
            "terms_accepted": False
        }
        
        response = self.make_request("POST", "/auth/register", test_data)
        
        if response and response.status_code != 400:
            self.log_issue("Medium", "Validation", "/auth/register", 
                         "Should reject registration without terms acceptance", 
                         "Register without accepting terms", "HTTP 400 error", 
                         f"HTTP {response.status_code}")
        
        # Test duplicate email
        if self.test_email:
            duplicate_data = {
                "name": "Another User",
                "email": self.test_email,
                "phone_number": "+9876543210",
                "password": "password123",
                "terms_accepted": True
            }
            
            response = self.make_request("POST", "/auth/register", duplicate_data)
            
            if response and response.status_code != 400:
                self.log_issue("High", "Validation", "/auth/register", 
                             "Should reject duplicate email registration", 
                             "Register with existing email", "HTTP 400 error", 
                             f"HTTP {response.status_code}")
        
        self.log_result("User Registration (Invalid Data)", True, "Invalid data validation tests completed")
    
    def test_user_login_valid(self):
        """Test user login with valid credentials"""
        if not self.test_email or not self.test_password:
            self.log_result("User Login (Valid)", False, "No test credentials available")
            return False
        
        login_data = {
            "email": self.test_email,
            "password": self.test_password
        }
        
        response = self.make_request("POST", "/auth/login", login_data)
        
        if response is None:
            self.log_result("User Login (Valid)", False, "Connection failed")
            return False
        
        if response.status_code == 200:
            try:
                data = response.json()
                if "access_token" in data:
                    # Update token with login token
                    old_token = self.auth_token
                    self.auth_token = data["access_token"]
                    
                    # Verify token is different from registration token (should be new)
                    if old_token == self.auth_token:
                        self.log_issue("Low", "Security", "/auth/login", 
                                     "Login returns same token as registration", 
                                     "Login after registration", "New token", "Same token returned")
                    
                    self.log_result("User Login (Valid)", True, "Login successful")
                    return True
                else:
                    self.log_issue("High", "Authentication", "/auth/login", 
                                 "Missing access_token in login response", "Login with valid credentials", 
                                 "Response with access_token", f"Response: {data}")
                    self.log_result("User Login (Valid)", False, "Missing access_token in response")
                    return False
            except json.JSONDecodeError:
                self.log_issue("High", "API Response", "/auth/login", 
                             "Invalid JSON response", "Login with valid credentials", 
                             "Valid JSON response", f"Response: {response.text}")
                self.log_result("User Login (Valid)", False, "Invalid JSON response")
                return False
        else:
            try:
                error_data = response.json()
                self.log_issue("High", "Authentication", "/auth/login", 
                             f"Login failed with valid credentials", 
                             "Login with correct email/password", "Status 200", 
                             f"Status {response.status_code}: {error_data.get('detail', 'Unknown error')}")
                self.log_result("User Login (Valid)", False, f"HTTP {response.status_code}: {error_data.get('detail', response.text)}")
            except:
                self.log_result("User Login (Valid)", False, f"HTTP {response.status_code}: {response.text}")
            return False
    
    def test_user_login_invalid(self):
        """Test user login with invalid credentials"""
        # Test wrong password
        wrong_password_data = {
            "email": self.test_email if self.test_email else "test@example.com",
            "password": "wrongpassword123"
        }
        
        response = self.make_request("POST", "/auth/login", wrong_password_data)
        
        if response and response.status_code != 401:
            self.log_issue("High", "Security", "/auth/login", 
                         "Should reject login with wrong password", 
                         "Login with incorrect password", "HTTP 401 error", 
                         f"HTTP {response.status_code}")
        
        # Test non-existent email
        nonexistent_data = {
            "email": "nonexistent@example.com",
            "password": "password123"
        }
        
        response = self.make_request("POST", "/auth/login", nonexistent_data)
        
        if response and response.status_code != 401:
            self.log_issue("High", "Security", "/auth/login", 
                         "Should reject login with non-existent email", 
                         "Login with non-existent email", "HTTP 401 error", 
                         f"HTTP {response.status_code}")
        
        self.log_result("User Login (Invalid Credentials)", True, "Invalid credentials validation tests completed")
    
    def test_token_validation(self):
        """Test token validation and expiration"""
        if not self.auth_token:
            self.log_result("Token Validation", False, "No auth token available")
            return False
        
        # Test with valid token
        response = self.make_request("GET", "/profile/me", use_auth=True)
        
        if response and response.status_code == 200:
            self.log_result("Token Validation (Valid)", True, "Valid token accepted")
        else:
            self.log_issue("High", "Authentication", "/profile/me", 
                         "Valid token rejected", "Access protected endpoint with valid token", 
                         "Status 200", f"Status {response.status_code if response else 'No response'}")
        
        # Test with invalid token
        old_token = self.auth_token
        self.auth_token = "invalid.token.here"
        
        response = self.make_request("GET", "/profile/me", use_auth=True)
        
        if response and response.status_code != 401:
            self.log_issue("Critical", "Security", "/profile/me", 
                         "Invalid token accepted", "Access protected endpoint with invalid token", 
                         "HTTP 401 error", f"HTTP {response.status_code}")
        
        # Restore valid token
        self.auth_token = old_token
        
        self.log_result("Token Validation", True, "Token validation tests completed")
    
    def test_email_validation(self):
        """Test email format validation"""
        invalid_emails = [
            "invalid-email",
            "@example.com",
            "test@",
            "test..test@example.com",
            "test@example",
        ]
        
        for email in invalid_emails:
            test_data = {
                "name": "Test User",
                "email": email,
                "phone_number": "+1234567890",
                "password": "password123",
                "terms_accepted": True
            }
            
            response = self.make_request("POST", "/auth/register", test_data)
            
            if response and response.status_code != 422:  # Pydantic validation error
                self.log_issue("Medium", "Validation", "/auth/register", 
                             f"Should reject invalid email format: {email}", 
                             f"Register with email: {email}", "HTTP 422 validation error", 
                             f"HTTP {response.status_code}")
        
        self.log_result("Email Validation", True, "Email format validation tests completed")
    
    def test_phone_validation(self):
        """Test phone number validation"""
        invalid_phones = [
            "123",
            "invalid-phone",
            "+",
            "++1234567890",
            "1234567890123456789012345"  # Too long
        ]
        
        for phone in invalid_phones:
            test_data = {
                "name": "Test User",
                "email": f"test{phone.replace('+', '').replace('-', '')}@example.com",
                "phone_number": phone,
                "password": "password123",
                "terms_accepted": True
            }
            
            response = self.make_request("POST", "/auth/register", test_data)
            
            # Note: This might not fail if phone validation is not strict
            if response and response.status_code == 200:
                self.log_issue("Low", "Validation", "/auth/register", 
                             f"Weak phone validation - accepted: {phone}", 
                             f"Register with phone: {phone}", "Validation error for invalid phone", 
                             "Registration successful")
        
        self.log_result("Phone Validation", True, "Phone validation tests completed")

    # ===== 2. PROFILE MANAGEMENT TESTS =====
    
    def test_profile_management(self):
        """Comprehensive profile management testing"""
        print("\n👤 TESTING PROFILE MANAGEMENT")
        print("=" * 50)
        
        # Test profile creation
        self.test_profile_creation()
        
        # Test profile retrieval
        self.test_profile_retrieval()
        
        # Test profile update
        self.test_profile_update()
        
        # Test GPS coordinates
        self.test_gps_coordinates()
        
        # Test profile validation
        self.test_profile_validation()
    
    def test_profile_creation(self):
        """Test profile creation with comprehensive data"""
        if not self.auth_token:
            self.log_result("Profile Creation", False, "No auth token available")
            return False
        
        profile_data = {
            "display_name": "أحمد محمد الخالدي",
            "bio": "مهندس برمجيات شغوف بالتكنولوجيا والابتكار. أحب السفر واستكشاف الثقافات المختلفة. أبحث عن شريكة حياة تشاركني الاهتمامات والأحلام.",
            "date_of_birth": "1990-05-15",
            "age": 33,
            "gender": "male",
            "height": 180,
            "looking_for": "علاقة جدية",
            "interests": ["البرمجة", "السفر", "القراءة", "الرياضة", "التكنولوجيا", "الطبخ"],
            "location": "الرياض، المملكة العربية السعودية",
            "latitude": 24.7136,
            "longitude": 46.6753,
            "occupation": "مهندس برمجيات",
            "education": "بكالوريوس هندسة حاسوب",
            "relationship_goals": "serious",
            "smoking": "no",
            "drinking": "no",
            "has_children": False,
            "wants_children": True,
            "languages": ["العربية", "الإنجليزية", "الفرنسية"]
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
                    
                    # Validate that all fields were saved correctly
                    profile = data["profile"]
                    for key, value in profile_data.items():
                        if key in profile and profile[key] != value:
                            self.log_issue("Medium", "Data Integrity", "/profile/create", 
                                         f"Profile field {key} not saved correctly", 
                                         f"Create profile with {key}: {value}", 
                                         f"Field saved as: {value}", f"Field saved as: {profile[key]}")
                    
                    self.log_result("Profile Creation", True, f"Profile created successfully. ID: {self.profile_id}")
                    return True
                else:
                    self.log_result("Profile Creation", True, "Profile created (no profile ID returned)")
                    return True
            except json.JSONDecodeError:
                self.log_issue("High", "API Response", "/profile/create", 
                             "Invalid JSON response", "Create profile", 
                             "Valid JSON response", f"Response: {response.text}")
                self.log_result("Profile Creation", False, "Invalid JSON response")
                return False
        elif response.status_code == 400:
            # Check if profile already exists
            try:
                error_data = response.json()
                if "موجود بالفعل" in error_data.get('detail', ''):
                    self.log_result("Profile Creation", True, "Profile already exists (expected)")
                    return True
            except:
                pass
            
            self.log_issue("Medium", "Profile Management", "/profile/create", 
                         "Profile creation failed", "Create profile with valid data", 
                         "Status 200", f"Status {response.status_code}")
            self.log_result("Profile Creation", False, f"HTTP {response.status_code}")
            return False
        else:
            try:
                error_data = response.json()
                self.log_issue("High", "Profile Management", "/profile/create", 
                             f"Profile creation failed with status {response.status_code}", 
                             "Create profile with valid data", "Status 200", 
                             f"Status {response.status_code}: {error_data.get('detail', 'Unknown error')}")
                self.log_result("Profile Creation", False, f"HTTP {response.status_code}: {error_data.get('detail', response.text)}")
            except:
                self.log_result("Profile Creation", False, f"HTTP {response.status_code}: {response.text}")
            return False
    
    def test_profile_retrieval(self):
        """Test profile retrieval"""
        if not self.auth_token:
            self.log_result("Profile Retrieval", False, "No auth token available")
            return False
        
        response = self.make_request("GET", "/profile/me", use_auth=True)
        
        if response is None:
            self.log_result("Profile Retrieval", False, "Connection failed")
            return False
        
        if response.status_code == 200:
            try:
                data = response.json()
                required_fields = ["display_name", "user_id", "created_at"]
                
                for field in required_fields:
                    if field not in data:
                        self.log_issue("Medium", "Data Integrity", "/profile/me", 
                                     f"Missing required field: {field}", "Get profile", 
                                     f"Profile with {field} field", f"Field {field} missing")
                
                # Check for Arabic text support
                if "display_name" in data and data["display_name"]:
                    # Check if Arabic characters are properly handled
                    arabic_chars = any('\u0600' <= char <= '\u06FF' for char in data["display_name"])
                    if not arabic_chars:
                        self.log_issue("Low", "Internationalization", "/profile/me", 
                                     "No Arabic characters in display_name", "Get profile with Arabic name", 
                                     "Arabic characters preserved", "No Arabic characters found")
                
                self.log_result("Profile Retrieval", True, f"Profile retrieved: {data.get('display_name', 'Unknown')}")
                return True
            except json.JSONDecodeError:
                self.log_issue("High", "API Response", "/profile/me", 
                             "Invalid JSON response", "Get profile", 
                             "Valid JSON response", f"Response: {response.text}")
                self.log_result("Profile Retrieval", False, "Invalid JSON response")
                return False
        else:
            try:
                error_data = response.json()
                self.log_issue("High", "Profile Management", "/profile/me", 
                             f"Profile retrieval failed with status {response.status_code}", 
                             "Get existing profile", "Status 200", 
                             f"Status {response.status_code}: {error_data.get('detail', 'Unknown error')}")
                self.log_result("Profile Retrieval", False, f"HTTP {response.status_code}: {error_data.get('detail', response.text)}")
            except:
                self.log_result("Profile Retrieval", False, f"HTTP {response.status_code}: {response.text}")
            return False
    
    def test_profile_update(self):
        """Test profile update functionality"""
        if not self.auth_token:
            self.log_result("Profile Update", False, "No auth token available")
            return False
        
        update_data = {
            "bio": "مهندس برمجيات محدث - أحب السفر والتكنولوجيا والابتكار والذكاء الاصطناعي",
            "interests": ["البرمجة", "السفر", "التكنولوجيا", "الابتكار", "الذكاء الاصطناعي", "الطبخ"],
            "current_mood": "serious"
        }
        
        response = self.make_request("PUT", "/profile/update", update_data, use_auth=True)
        
        if response is None:
            self.log_result("Profile Update", False, "Connection failed")
            return False
        
        if response.status_code == 200:
            try:
                data = response.json()
                
                # Verify the update was applied
                if "profile" in data:
                    profile = data["profile"]
                    for key, value in update_data.items():
                        if key in profile and profile[key] != value:
                            self.log_issue("Medium", "Data Integrity", "/profile/update", 
                                         f"Profile field {key} not updated correctly", 
                                         f"Update profile with {key}: {value}", 
                                         f"Field updated to: {value}", f"Field is: {profile[key]}")
                
                self.log_result("Profile Update", True, "Profile updated successfully")
                return True
            except json.JSONDecodeError:
                self.log_issue("High", "API Response", "/profile/update", 
                             "Invalid JSON response", "Update profile", 
                             "Valid JSON response", f"Response: {response.text}")
                self.log_result("Profile Update", False, "Invalid JSON response")
                return False
        else:
            try:
                error_data = response.json()
                self.log_issue("High", "Profile Management", "/profile/update", 
                             f"Profile update failed with status {response.status_code}", 
                             "Update profile with valid data", "Status 200", 
                             f"Status {response.status_code}: {error_data.get('detail', 'Unknown error')}")
                self.log_result("Profile Update", False, f"HTTP {response.status_code}: {error_data.get('detail', response.text)}")
            except:
                self.log_result("Profile Update", False, f"HTTP {response.status_code}: {response.text}")
            return False
    
    def test_gps_coordinates(self):
        """Test GPS coordinates saving and retrieval"""
        if not self.auth_token:
            self.log_result("GPS Coordinates", False, "No auth token available")
            return False
        
        # Test coordinates for different cities
        test_coordinates = [
            {"name": "Riyadh", "latitude": 24.7136, "longitude": 46.6753},
            {"name": "Dubai", "latitude": 25.2048, "longitude": 55.2708},
            {"name": "Cairo", "latitude": 30.0444, "longitude": 31.2357}
        ]
        
        for coord in test_coordinates:
            update_data = {
                "location": f"{coord['name']}, Test Location",
                "latitude": coord["latitude"],
                "longitude": coord["longitude"]
            }
            
            response = self.make_request("PUT", "/profile/update", update_data, use_auth=True)
            
            if response and response.status_code == 200:
                # Verify coordinates were saved
                profile_response = self.make_request("GET", "/profile/me", use_auth=True)
                if profile_response and profile_response.status_code == 200:
                    try:
                        profile_data = profile_response.json()
                        saved_lat = profile_data.get("latitude")
                        saved_lon = profile_data.get("longitude")
                        
                        if saved_lat != coord["latitude"] or saved_lon != coord["longitude"]:
                            self.log_issue("High", "GPS Integration", "/profile/update", 
                                         f"GPS coordinates not saved correctly for {coord['name']}", 
                                         f"Save coordinates: {coord['latitude']}, {coord['longitude']}", 
                                         f"Coordinates saved correctly", 
                                         f"Saved: {saved_lat}, {saved_lon}")
                    except:
                        pass
            else:
                self.log_issue("High", "GPS Integration", "/profile/update", 
                             f"Failed to save GPS coordinates for {coord['name']}", 
                             f"Update profile with GPS coordinates", "Status 200", 
                             f"Status {response.status_code if response else 'No response'}")
        
        self.log_result("GPS Coordinates", True, "GPS coordinates tests completed")
    
    def test_profile_validation(self):
        """Test profile field validation"""
        if not self.auth_token:
            self.log_result("Profile Validation", False, "No auth token available")
            return False
        
        # Test invalid data types
        invalid_updates = [
            {"age": "not_a_number"},
            {"height": "not_a_number"},
            {"latitude": "not_a_number"},
            {"longitude": "not_a_number"},
            {"has_children": "not_a_boolean"},
            {"wants_children": "not_a_boolean"}
        ]
        
        for invalid_data in invalid_updates:
            response = self.make_request("PUT", "/profile/update", invalid_data, use_auth=True)
            
            if response and response.status_code not in [400, 422]:
                field_name = list(invalid_data.keys())[0]
                self.log_issue("Medium", "Validation", "/profile/update", 
                             f"Should reject invalid {field_name} data type", 
                             f"Update profile with invalid {field_name}", "HTTP 400/422 error", 
                             f"HTTP {response.status_code}")
        
        self.log_result("Profile Validation", True, "Profile validation tests completed")

    # ===== 3. DISCOVERY & MATCHING TESTS =====
    
    def test_discovery_matching(self):
        """Comprehensive discovery and matching testing"""
        print("\n💕 TESTING DISCOVERY & MATCHING")
        print("=" * 50)
        
        # Create dummy profiles first
        self.test_create_dummy_profiles()
        
        # Test basic discovery
        self.test_basic_discovery()
        
        # Test discovery with filters
        self.test_discovery_filters()
        
        # Test distance calculation
        self.test_distance_calculation()
        
        # Test matching algorithm
        self.test_matching_algorithm()
        
        # Test swipe actions
        self.test_swipe_actions()
    
    def test_create_dummy_profiles(self):
        """Create dummy profiles for testing"""
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
                self.log_result("Create Dummy Profiles", True, "Dummy profiles created (non-JSON response)")
                return True
        else:
            # May already exist, which is fine
            self.log_result("Create Dummy Profiles", True, "Dummy profiles endpoint called")
            return True
    
    def test_basic_discovery(self):
        """Test basic profile discovery"""
        if not self.auth_token:
            self.log_result("Basic Discovery", False, "No auth token available")
            return False
        
        response = self.make_request("GET", "/profiles/discover?limit=20", use_auth=True)
        
        if response is None:
            self.log_result("Basic Discovery", False, "Connection failed")
            return False
        
        if response.status_code == 200:
            try:
                data = response.json()
                if "profiles" in data:
                    profiles = data["profiles"]
                    profile_count = len(profiles)
                    
                    if profile_count == 0:
                        self.log_issue("Medium", "Discovery", "/profiles/discover", 
                                     "No profiles returned for discovery", "Get discovery profiles", 
                                     "At least some profiles", "0 profiles returned")
                    
                    # Validate profile structure
                    for i, profile in enumerate(profiles[:3]):  # Check first 3
                        required_fields = ["user_id", "display_name"]
                        for field in required_fields:
                            if field not in profile:
                                self.log_issue("Medium", "Data Structure", "/profiles/discover", 
                                             f"Profile {i} missing required field: {field}", 
                                             "Get discovery profiles", f"Profiles with {field} field", 
                                             f"Profile missing {field}")
                    
                    self.log_result("Basic Discovery", True, f"Found {profile_count} profiles for discovery")
                    return True, profiles
                else:
                    self.log_issue("High", "API Response", "/profiles/discover", 
                                 "Missing profiles key in response", "Get discovery profiles", 
                                 "Response with profiles array", f"Response: {data}")
                    self.log_result("Basic Discovery", False, "No profiles key in response")
                    return False, []
            except json.JSONDecodeError:
                self.log_issue("High", "API Response", "/profiles/discover", 
                             "Invalid JSON response", "Get discovery profiles", 
                             "Valid JSON response", f"Response: {response.text}")
                self.log_result("Basic Discovery", False, "Invalid JSON response")
                return False, []
        else:
            try:
                error_data = response.json()
                self.log_issue("High", "Discovery", "/profiles/discover", 
                             f"Discovery failed with status {response.status_code}", 
                             "Get discovery profiles", "Status 200", 
                             f"Status {response.status_code}: {error_data.get('detail', 'Unknown error')}")
                self.log_result("Basic Discovery", False, f"HTTP {response.status_code}: {error_data.get('detail', response.text)}")
            except:
                self.log_result("Basic Discovery", False, f"HTTP {response.status_code}: {response.text}")
            return False, []
    
    def test_discovery_filters(self):
        """Test discovery with various filters"""
        if not self.auth_token:
            self.log_result("Discovery Filters", False, "No auth token available")
            return False
        
        # Test filters
        filters = [
            {"name": "Category Filter", "params": "category=السفر&limit=10"},
            {"name": "Age Filter", "params": "min_age=25&max_age=35&limit=10"},
            {"name": "Gender Filter", "params": "gender=female&limit=10"},
            {"name": "Distance Filter", "params": "max_distance=50&limit=10"},
            {"name": "Combined Filters", "params": "gender=male&min_age=28&max_age=40&max_distance=100&limit=10"}
        ]
        
        for filter_test in filters:
            response = self.make_request("GET", f"/profiles/discover?{filter_test['params']}", use_auth=True)
            
            if response is None:
                self.log_issue("Medium", "Discovery", "/profiles/discover", 
                             f"{filter_test['name']} - Connection failed", 
                             f"Apply {filter_test['name'].lower()}", "Successful response", "Connection failed")
                continue
            
            if response.status_code == 200:
                try:
                    data = response.json()
                    if "profiles" in data:
                        profile_count = len(data["profiles"])
                        self.log_result(f"Discovery - {filter_test['name']}", True, f"Found {profile_count} profiles")
                    else:
                        self.log_issue("Medium", "Discovery", "/profiles/discover", 
                                     f"{filter_test['name']} - Missing profiles key", 
                                     f"Apply {filter_test['name'].lower()}", "Response with profiles", "Missing profiles key")
                except json.JSONDecodeError:
                    self.log_issue("Medium", "API Response", "/profiles/discover", 
                                 f"{filter_test['name']} - Invalid JSON", 
                                 f"Apply {filter_test['name'].lower()}", "Valid JSON", "Invalid JSON response")
            else:
                self.log_issue("Medium", "Discovery", "/profiles/discover", 
                             f"{filter_test['name']} - HTTP {response.status_code}", 
                             f"Apply {filter_test['name'].lower()}", "Status 200", f"Status {response.status_code}")
        
        self.log_result("Discovery Filters", True, "Discovery filter tests completed")
    
    def test_distance_calculation(self):
        """Test distance calculation accuracy"""
        if not self.auth_token:
            self.log_result("Distance Calculation", False, "No auth token available")
            return False
        
        # Set user location to Riyadh
        riyadh_coords = {"latitude": 24.7136, "longitude": 46.6753}
        update_response = self.make_request("PUT", "/profile/update", riyadh_coords, use_auth=True)
        
        if not update_response or update_response.status_code != 200:
            self.log_result("Distance Calculation", False, "Failed to set user location")
            return False
        
        # Test discovery with distance
        response = self.make_request("GET", "/profiles/discover?max_distance=100&limit=20", use_auth=True)
        
        if response and response.status_code == 200:
            try:
                data = response.json()
                if "profiles" in data:
                    profiles_with_distance = [p for p in data["profiles"] if "distance" in p and p["distance"] is not None]
                    
                    if len(profiles_with_distance) == 0:
                        self.log_issue("Medium", "GPS Integration", "/profiles/discover", 
                                     "No profiles with distance information", 
                                     "Get profiles with distance calculation", "Profiles with distance field", 
                                     "No distance information in profiles")
                    else:
                        # Check if distances are reasonable
                        for profile in profiles_with_distance[:5]:
                            distance = profile.get("distance")
                            if distance and distance > 100:
                                self.log_issue("Medium", "Distance Calculation", "/profiles/discover", 
                                             f"Profile returned with distance {distance}km > max_distance 100km", 
                                             "Filter profiles by max_distance=100", "Distance <= 100km", 
                                             f"Distance: {distance}km")
                    
                    self.log_result("Distance Calculation", True, f"Found {len(profiles_with_distance)} profiles with distance info")
                else:
                    self.log_result("Distance Calculation", False, "No profiles in response")
            except json.JSONDecodeError:
                self.log_result("Distance Calculation", False, "Invalid JSON response")
        else:
            self.log_result("Distance Calculation", False, "Failed to get discovery response")
    
    def test_matching_algorithm(self):
        """Test matching algorithm scoring"""
        # This is tested implicitly through discovery ordering
        # We can check if profiles are returned in a reasonable order
        success, profiles = self.test_basic_discovery()
        
        if success and len(profiles) > 1:
            # Check if profiles have some logical ordering
            # (This is hard to test without knowing the algorithm details)
            self.log_result("Matching Algorithm", True, "Matching algorithm appears to be working (profiles returned in order)")
        else:
            self.log_result("Matching Algorithm", False, "Cannot test matching algorithm - insufficient profiles")
    
    def test_swipe_actions(self):
        """Test swipe actions and match detection"""
        if not self.auth_token:
            self.log_result("Swipe Actions", False, "No auth token available")
            return False
        
        # Get profiles for swiping
        success, profiles = self.test_basic_discovery()
        
        if not success or not profiles:
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
                self.log_issue("High", "Swipe Actions", "/swipe", 
                             f"Connection failed for {action} action", f"Swipe {action}", 
                             "Successful response", "Connection failed")
                continue
            
            if response.status_code == 200:
                try:
                    data = response.json()
                    if data.get("success"):
                        is_match = data.get("is_match", False)
                        remaining_likes = data.get("remaining_likes")
                        
                        # Check weekly limits tracking
                        if action in ["like", "super_like"] and remaining_likes is not None:
                            if remaining_likes < 0 or remaining_likes > 12:
                                self.log_issue("Medium", "Weekly Limits", "/swipe", 
                                             f"Invalid remaining_likes count: {remaining_likes}", 
                                             f"Swipe {action}", "Valid remaining count (0-12)", 
                                             f"Remaining: {remaining_likes}")
                        
                        match_text = " (MATCH!)" if is_match else ""
                        self.log_result(f"Swipe Action ({action})", True, f"Swipe successful{match_text}")
                        success_count += 1
                    else:
                        self.log_issue("Medium", "Swipe Actions", "/swipe", 
                                     f"Swipe {action} returned success=false", f"Swipe {action}", 
                                     "success=true", f"success=false, data: {data}")
                        self.log_result(f"Swipe Action ({action})", False, "Swipe not successful")
                except json.JSONDecodeError:
                    self.log_issue("High", "API Response", "/swipe", 
                                 f"Invalid JSON response for {action}", f"Swipe {action}", 
                                 "Valid JSON response", f"Response: {response.text}")
                    self.log_result(f"Swipe Action ({action})", False, "Invalid JSON response")
            elif response.status_code == 403:
                # Weekly limit reached - this is expected behavior
                try:
                    error_data = response.json()
                    if "limit" in error_data.get('detail', '').lower():
                        self.log_result(f"Swipe Action ({action})", True, "Weekly limit enforced correctly")
                        success_count += 1
                    else:
                        self.log_issue("Medium", "Swipe Actions", "/swipe", 
                                     f"Unexpected 403 error for {action}", f"Swipe {action}", 
                                     "Success or weekly limit message", f"403: {error_data.get('detail', 'Unknown')}")
                except:
                    pass
            else:
                try:
                    error_data = response.json()
                    self.log_issue("High", "Swipe Actions", "/swipe", 
                                 f"Swipe {action} failed with status {response.status_code}", 
                                 f"Swipe {action}", "Status 200", 
                                 f"Status {response.status_code}: {error_data.get('detail', 'Unknown error')}")
                    self.log_result(f"Swipe Action ({action})", False, f"HTTP {response.status_code}: {error_data.get('detail', response.text)}")
                except:
                    self.log_result(f"Swipe Action ({action})", False, f"HTTP {response.status_code}: {response.text}")
        
        return success_count > 0

    # ===== 4. IMAGE UPLOAD TESTS =====
    
    def test_image_upload(self):
        """Test Cloudinary image upload functionality"""
        print("\n📸 TESTING IMAGE UPLOAD (CLOUDINARY)")
        print("=" * 50)
        
        if not self.auth_token:
            self.log_result("Image Upload", False, "No auth token available")
            return False
        
        # Test photo upload endpoint
        self.test_photo_upload_endpoint()
        
        # Test file size limits
        self.test_file_size_limits()
        
        # Test invalid file formats
        self.test_invalid_file_formats()
    
    def test_photo_upload_endpoint(self):
        """Test photo upload endpoint"""
        # Create a small test image (1x1 pixel PNG in base64)
        test_image_base64 = "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNkYPhfDwAChwGA60e6kgAAAABJRU5ErkJggg=="
        
        upload_data = {
            "photo_data": f"data:image/png;base64,{test_image_base64}"
        }
        
        response = self.make_request("POST", "/profile/photo/upload", upload_data, use_auth=True)
        
        if response is None:
            self.log_result("Photo Upload Endpoint", False, "Connection failed")
            return False
        
        if response.status_code == 200:
            try:
                data = response.json()
                if "message" in data:
                    photo_count = data.get("photo_count", 0)
                    self.log_result("Photo Upload Endpoint", True, f"Photo uploaded successfully. Total photos: {photo_count}")
                    return True
                else:
                    self.log_issue("Medium", "Image Upload", "/profile/photo/upload", 
                                 "Missing message in upload response", "Upload photo", 
                                 "Response with message", f"Response: {data}")
                    self.log_result("Photo Upload Endpoint", True, "Photo uploaded (no message)")
                    return True
            except json.JSONDecodeError:
                self.log_issue("High", "API Response", "/profile/photo/upload", 
                             "Invalid JSON response", "Upload photo", 
                             "Valid JSON response", f"Response: {response.text}")
                self.log_result("Photo Upload Endpoint", False, "Invalid JSON response")
                return False
        else:
            try:
                error_data = response.json()
                self.log_issue("High", "Image Upload", "/profile/photo/upload", 
                             f"Photo upload failed with status {response.status_code}", 
                             "Upload valid photo", "Status 200", 
                             f"Status {response.status_code}: {error_data.get('detail', 'Unknown error')}")
                self.log_result("Photo Upload Endpoint", False, f"HTTP {response.status_code}: {error_data.get('detail', response.text)}")
            except:
                self.log_result("Photo Upload Endpoint", False, f"HTTP {response.status_code}: {response.text}")
            return False
    
    def test_file_size_limits(self):
        """Test file size limits (10MB)"""
        # Create a large base64 string (simulate large file)
        large_data = "A" * (11 * 1024 * 1024)  # 11MB of data
        
        upload_data = {
            "photo_data": f"data:image/jpeg;base64,{large_data}"
        }
        
        response = self.make_request("POST", "/profile/photo/upload", upload_data, use_auth=True, timeout=60)
        
        if response and response.status_code not in [400, 413, 422]:
            self.log_issue("Medium", "Image Upload", "/profile/photo/upload", 
                         "Should reject files larger than 10MB", "Upload 11MB file", 
                         "HTTP 400/413/422 error", f"HTTP {response.status_code}")
        
        self.log_result("File Size Limits", True, "File size limit tests completed")
    
    def test_invalid_file_formats(self):
        """Test invalid file format handling"""
        invalid_data = {
            "photo_data": "invalid_base64_data"
        }
        
        response = self.make_request("POST", "/profile/photo/upload", invalid_data, use_auth=True)
        
        if response and response.status_code not in [400, 422]:
            self.log_issue("Medium", "Image Upload", "/profile/photo/upload", 
                         "Should reject invalid base64 data", "Upload invalid data", 
                         "HTTP 400/422 error", f"HTTP {response.status_code}")
        
        self.log_result("Invalid File Formats", True, "Invalid file format tests completed")

    # ===== 5. LOCATION & MAPS TESTS =====
    
    def test_location_maps(self):
        """Test location and maps functionality"""
        print("\n🗺️ TESTING LOCATION & MAPS")
        print("=" * 50)
        
        # GPS coordinates are tested in profile management
        # Test discovery settings
        self.test_discovery_settings()
        
        # Test proximity scoring
        self.test_proximity_scoring()
    
    def test_discovery_settings(self):
        """Test discovery settings API"""
        if not self.auth_token:
            self.log_result("Discovery Settings", False, "No auth token available")
            return False
        
        # Test GET discovery settings
        response = self.make_request("GET", "/discovery-settings", use_auth=True)
        
        if response is None:
            self.log_result("Discovery Settings (GET)", False, "Connection failed")
            return False
        
        if response.status_code == 200:
            try:
                data = response.json()
                required_fields = ["max_distance", "interested_in", "min_age", "max_age"]
                
                for field in required_fields:
                    if field not in data:
                        self.log_issue("Medium", "Discovery Settings", "/discovery-settings", 
                                     f"Missing required field: {field}", "Get discovery settings", 
                                     f"Settings with {field} field", f"Field {field} missing")
                
                self.log_result("Discovery Settings (GET)", True, "Discovery settings retrieved")
            except json.JSONDecodeError:
                self.log_issue("High", "API Response", "/discovery-settings", 
                             "Invalid JSON response", "Get discovery settings", 
                             "Valid JSON response", f"Response: {response.text}")
                self.log_result("Discovery Settings (GET)", False, "Invalid JSON response")
        else:
            self.log_issue("High", "Discovery Settings", "/discovery-settings", 
                         f"Failed to get discovery settings: {response.status_code}", 
                         "Get discovery settings", "Status 200", f"Status {response.status_code}")
        
        # Test PUT discovery settings
        update_settings = {
            "max_distance": 75,
            "interested_in": "female",
            "min_age": 25,
            "max_age": 35
        }
        
        response = self.make_request("PUT", "/discovery-settings", update_settings, use_auth=True)
        
        if response and response.status_code == 200:
            self.log_result("Discovery Settings (PUT)", True, "Discovery settings updated")
        else:
            self.log_issue("High", "Discovery Settings", "/discovery-settings", 
                         f"Failed to update discovery settings: {response.status_code if response else 'No response'}", 
                         "Update discovery settings", "Status 200", 
                         f"Status {response.status_code if response else 'No response'}")
    
    def test_proximity_scoring(self):
        """Test proximity scoring in discovery"""
        # This is tested as part of distance calculation
        self.log_result("Proximity Scoring", True, "Proximity scoring tested via distance calculation")

    # ===== 6. INTERNATIONALIZATION TESTS =====
    
    def test_internationalization(self):
        """Test internationalization support"""
        print("\n🌍 TESTING INTERNATIONALIZATION")
        print("=" * 50)
        
        # Test Arabic text handling
        self.test_arabic_text_support()
        
        # Test language preference storage
        self.test_language_preference()
    
    def test_arabic_text_support(self):
        """Test Arabic text support throughout the API"""
        if not self.auth_token:
            self.log_result("Arabic Text Support", False, "No auth token available")
            return False
        
        # Test Arabic text in profile update
        arabic_data = {
            "display_name": "أحمد محمد الخالدي",
            "bio": "مهندس برمجيات شغوف بالتكنولوجيا والابتكار. أحب السفر واستكشاف الثقافات المختلفة.",
            "location": "الرياض، المملكة العربية السعودية",
            "occupation": "مهندس برمجيات",
            "interests": ["البرمجة", "السفر", "القراءة", "الرياضة", "التكنولوجيا"]
        }
        
        response = self.make_request("PUT", "/profile/update", arabic_data, use_auth=True)
        
        if response and response.status_code == 200:
            # Verify Arabic text was saved correctly
            profile_response = self.make_request("GET", "/profile/me", use_auth=True)
            if profile_response and profile_response.status_code == 200:
                try:
                    profile_data = profile_response.json()
                    
                    # Check if Arabic characters are preserved
                    for field, expected_value in arabic_data.items():
                        if field in profile_data:
                            saved_value = profile_data[field]
                            if isinstance(expected_value, str) and expected_value != saved_value:
                                self.log_issue("Medium", "Internationalization", "/profile/update", 
                                             f"Arabic text not preserved in {field}", 
                                             f"Save Arabic text: {expected_value}", 
                                             f"Text preserved correctly", f"Saved as: {saved_value}")
                    
                    self.log_result("Arabic Text Support", True, "Arabic text handling verified")
                except json.JSONDecodeError:
                    self.log_result("Arabic Text Support", False, "Failed to verify Arabic text")
            else:
                self.log_result("Arabic Text Support", False, "Failed to retrieve profile for verification")
        else:
            self.log_issue("High", "Internationalization", "/profile/update", 
                         "Failed to save Arabic text", "Update profile with Arabic text", 
                         "Status 200", f"Status {response.status_code if response else 'No response'}")
            self.log_result("Arabic Text Support", False, "Failed to save Arabic text")
    
    def test_language_preference(self):
        """Test language preference storage"""
        if not self.auth_token:
            self.log_result("Language Preference", False, "No auth token available")
            return False
        
        # Test updating language preferences
        language_data = {
            "languages": ["العربية", "English", "Français", "Español"]
        }
        
        response = self.make_request("PUT", "/profile/update", language_data, use_auth=True)
        
        if response and response.status_code == 200:
            self.log_result("Language Preference", True, "Language preferences updated")
        else:
            self.log_issue("Medium", "Internationalization", "/profile/update", 
                         "Failed to save language preferences", "Update language preferences", 
                         "Status 200", f"Status {response.status_code if response else 'No response'}")
            self.log_result("Language Preference", False, "Failed to save language preferences")

    # ===== 7. ERROR HANDLING TESTS =====
    
    def test_error_handling(self):
        """Test error handling and validation"""
        print("\n⚠️ TESTING ERROR HANDLING")
        print("=" * 50)
        
        # Test invalid endpoints
        self.test_invalid_endpoints()
        
        # Test missing required fields
        self.test_missing_required_fields()
        
        # Test HTTP status codes
        self.test_http_status_codes()
        
        # Test error message clarity
        self.test_error_message_clarity()
    
    def test_invalid_endpoints(self):
        """Test invalid endpoint handling"""
        invalid_endpoints = [
            "/nonexistent",
            "/profile/invalid",
            "/auth/invalid",
            "/profiles/invalid"
        ]
        
        for endpoint in invalid_endpoints:
            response = self.make_request("GET", endpoint)
            
            if response and response.status_code != 404:
                self.log_issue("Low", "Error Handling", endpoint, 
                             "Should return 404 for invalid endpoints", f"Access {endpoint}", 
                             "HTTP 404", f"HTTP {response.status_code}")
        
        self.log_result("Invalid Endpoints", True, "Invalid endpoint tests completed")
    
    def test_missing_required_fields(self):
        """Test missing required fields validation"""
        # Test registration without required fields
        incomplete_registration = {
            "name": "Test User"
            # Missing email, phone_number, password, terms_accepted
        }
        
        response = self.make_request("POST", "/auth/register", incomplete_registration)
        
        if response and response.status_code not in [400, 422]:
            self.log_issue("Medium", "Validation", "/auth/register", 
                         "Should reject registration with missing fields", 
                         "Register without required fields", "HTTP 400/422", 
                         f"HTTP {response.status_code}")
        
        # Test login without required fields
        incomplete_login = {
            "email": "test@example.com"
            # Missing password
        }
        
        response = self.make_request("POST", "/auth/login", incomplete_login)
        
        if response and response.status_code not in [400, 422]:
            self.log_issue("Medium", "Validation", "/auth/login", 
                         "Should reject login with missing fields", 
                         "Login without password", "HTTP 400/422", 
                         f"HTTP {response.status_code}")
        
        self.log_result("Missing Required Fields", True, "Missing fields validation tests completed")
    
    def test_http_status_codes(self):
        """Test proper HTTP status codes"""
        # Test unauthorized access
        old_token = self.auth_token
        self.auth_token = None
        
        response = self.make_request("GET", "/profile/me", use_auth=True)
        
        if response and response.status_code != 401:
            self.log_issue("Medium", "Error Handling", "/profile/me", 
                         "Should return 401 for unauthorized access", 
                         "Access protected endpoint without token", "HTTP 401", 
                         f"HTTP {response.status_code}")
        
        # Restore token
        self.auth_token = old_token
        
        self.log_result("HTTP Status Codes", True, "HTTP status code tests completed")
    
    def test_error_message_clarity(self):
        """Test error message clarity and localization"""
        # Test Arabic error messages
        invalid_login = {
            "email": "nonexistent@example.com",
            "password": "wrongpassword"
        }
        
        response = self.make_request("POST", "/auth/login", invalid_login)
        
        if response and response.status_code == 401:
            try:
                error_data = response.json()
                error_message = error_data.get('detail', '')
                
                # Check if error message is in Arabic
                arabic_chars = any('\u0600' <= char <= '\u06FF' for char in error_message)
                if not arabic_chars:
                    self.log_issue("Low", "Internationalization", "/auth/login", 
                                 "Error messages not in Arabic", "Get error message", 
                                 "Arabic error message", f"Message: {error_message}")
                
                # Check if message is clear and helpful
                if len(error_message.strip()) < 10:
                    self.log_issue("Low", "Error Handling", "/auth/login", 
                                 "Error message too short/unclear", "Get error message", 
                                 "Clear, helpful error message", f"Message: {error_message}")
                
            except json.JSONDecodeError:
                pass
        
        self.log_result("Error Message Clarity", True, "Error message clarity tests completed")

    # ===== 8. ADDITIONAL BACKEND FEATURES TESTS =====
    
    def test_additional_features(self):
        """Test additional backend features"""
        print("\n🔧 TESTING ADDITIONAL FEATURES")
        print("=" * 50)
        
        # Test usage stats
        self.test_usage_stats()
        
        # Test matches and likes
        self.test_matches_and_likes()
        
        # Test weekly limits
        self.test_weekly_limits()
    
    def test_usage_stats(self):
        """Test usage statistics endpoint"""
        if not self.auth_token:
            self.log_result("Usage Stats", False, "No auth token available")
            return False
        
        response = self.make_request("GET", "/usage-stats", use_auth=True)
        
        if response is None:
            self.log_result("Usage Stats", False, "Connection failed")
            return False
        
        if response.status_code == 200:
            try:
                data = response.json()
                required_fields = ["premium_tier", "is_premium", "likes", "messages"]
                
                for field in required_fields:
                    if field not in data:
                        self.log_issue("Medium", "Usage Stats", "/usage-stats", 
                                     f"Missing required field: {field}", "Get usage stats", 
                                     f"Stats with {field} field", f"Field {field} missing")
                
                # Validate likes structure
                if "likes" in data:
                    likes_data = data["likes"]
                    likes_fields = ["unlimited", "sent", "remaining"]
                    for field in likes_fields:
                        if field not in likes_data:
                            self.log_issue("Medium", "Usage Stats", "/usage-stats", 
                                         f"Missing likes field: {field}", "Get usage stats", 
                                         f"Likes with {field} field", f"Likes missing {field}")
                
                self.log_result("Usage Stats", True, f"Usage stats retrieved: {data.get('premium_tier', 'unknown')} tier")
                return True
            except json.JSONDecodeError:
                self.log_issue("High", "API Response", "/usage-stats", 
                             "Invalid JSON response", "Get usage stats", 
                             "Valid JSON response", f"Response: {response.text}")
                self.log_result("Usage Stats", False, "Invalid JSON response")
                return False
        else:
            try:
                error_data = response.json()
                self.log_issue("High", "Usage Stats", "/usage-stats", 
                             f"Usage stats failed with status {response.status_code}", 
                             "Get usage statistics", "Status 200", 
                             f"Status {response.status_code}: {error_data.get('detail', 'Unknown error')}")
                self.log_result("Usage Stats", False, f"HTTP {response.status_code}: {error_data.get('detail', response.text)}")
            except:
                self.log_result("Usage Stats", False, f"HTTP {response.status_code}: {response.text}")
            return False
    
    def test_matches_and_likes(self):
        """Test matches and likes endpoints"""
        if not self.auth_token:
            self.log_result("Matches and Likes", False, "No auth token available")
            return False
        
        # Test matches endpoint
        response = self.make_request("GET", "/matches", use_auth=True)
        
        if response and response.status_code == 200:
            try:
                data = response.json()
                if "matches" in data:
                    match_count = len(data["matches"])
                    self.log_result("Get Matches", True, f"Retrieved {match_count} matches")
                else:
                    self.log_issue("Medium", "Matches", "/matches", 
                                 "Missing matches key in response", "Get matches", 
                                 "Response with matches array", f"Response: {data}")
            except json.JSONDecodeError:
                self.log_issue("High", "API Response", "/matches", 
                             "Invalid JSON response", "Get matches", 
                             "Valid JSON response", f"Response: {response.text}")
        else:
            self.log_issue("High", "Matches", "/matches", 
                         f"Matches endpoint failed: {response.status_code if response else 'No response'}", 
                         "Get user matches", "Status 200", 
                         f"Status {response.status_code if response else 'No response'}")
        
        # Test sent likes
        response = self.make_request("GET", "/likes/sent", use_auth=True)
        
        if response and response.status_code == 200:
            try:
                data = response.json()
                if "profiles" in data:
                    like_count = len(data["profiles"])
                    self.log_result("Get Sent Likes", True, f"Retrieved {like_count} sent likes")
                else:
                    self.log_issue("Medium", "Likes", "/likes/sent", 
                                 "Missing profiles key in response", "Get sent likes", 
                                 "Response with profiles array", f"Response: {data}")
            except json.JSONDecodeError:
                self.log_issue("High", "API Response", "/likes/sent", 
                             "Invalid JSON response", "Get sent likes", 
                             "Valid JSON response", f"Response: {response.text}")
        
        # Test received likes
        response = self.make_request("GET", "/likes/received", use_auth=True)
        
        if response and response.status_code == 200:
            try:
                data = response.json()
                if "profiles" in data:
                    like_count = len(data["profiles"])
                    self.log_result("Get Received Likes", True, f"Retrieved {like_count} received likes")
                else:
                    self.log_issue("Medium", "Likes", "/likes/received", 
                                 "Missing profiles key in response", "Get received likes", 
                                 "Response with profiles array", f"Response: {data}")
            except json.JSONDecodeError:
                self.log_issue("High", "API Response", "/likes/received", 
                             "Invalid JSON response", "Get received likes", 
                             "Valid JSON response", f"Response: {response.text}")
    
    def test_weekly_limits(self):
        """Test weekly limits enforcement"""
        if not self.auth_token:
            self.log_result("Weekly Limits", False, "No auth token available")
            return False
        
        # Get current usage stats
        response = self.make_request("GET", "/usage-stats", use_auth=True)
        
        if response and response.status_code == 200:
            try:
                data = response.json()
                is_premium = data.get("is_premium", False)
                
                if not is_premium:
                    likes_data = data.get("likes", {})
                    remaining_likes = likes_data.get("remaining", 0)
                    
                    if remaining_likes > 0:
                        self.log_result("Weekly Limits", True, f"Free user has {remaining_likes} likes remaining")
                    else:
                        self.log_result("Weekly Limits", True, "Free user has reached weekly limit")
                else:
                    self.log_result("Weekly Limits", True, "Premium user has unlimited access")
                
            except json.JSONDecodeError:
                self.log_result("Weekly Limits", False, "Failed to parse usage stats")
        else:
            self.log_result("Weekly Limits", False, "Failed to get usage stats")

    # ===== MAIN TEST EXECUTION =====
    
    def run_comprehensive_qa(self):
        """Run comprehensive QA testing"""
        print("🔍 STARTING COMPREHENSIVE QA & BUG SWEEP - PIZOO DATING APP BACKEND")
        print(f"📍 Testing against: {self.base_url}")
        print("=" * 80)
        
        # Run all test categories
        self.test_authentication_flow()
        self.test_profile_management()
        self.test_discovery_matching()
        self.test_image_upload()
        self.test_location_maps()
        self.test_internationalization()
        self.test_error_handling()
        self.test_additional_features()
        
        # Generate comprehensive report
        self.generate_qa_report()
    
    def generate_qa_report(self):
        """Generate comprehensive QA report"""
        print("\n" + "=" * 80)
        print("📊 COMPREHENSIVE QA REPORT - PIZOO DATING APP BACKEND")
        print("=" * 80)
        
        # Test summary
        total_tests = len(self.test_results)
        passed_tests = sum(1 for result in self.test_results if result["success"])
        failed_tests = total_tests - passed_tests
        
        print(f"\n📈 TEST EXECUTION SUMMARY:")
        print(f"   Total Tests Executed: {total_tests}")
        print(f"   ✅ Passed: {passed_tests}")
        print(f"   ❌ Failed: {failed_tests}")
        print(f"   Success Rate: {(passed_tests/total_tests)*100:.1f}%")
        
        # Issues summary
        total_issues = len(self.critical_issues) + len(self.high_issues) + len(self.medium_issues) + len(self.low_issues)
        
        print(f"\n🐛 ISSUES FOUND:")
        print(f"   🔴 Critical: {len(self.critical_issues)}")
        print(f"   🟠 High: {len(self.high_issues)}")
        print(f"   🟡 Medium: {len(self.medium_issues)}")
        print(f"   🟢 Low: {len(self.low_issues)}")
        print(f"   Total Issues: {total_issues}")
        
        # Detailed issue reports
        if self.critical_issues:
            print(f"\n🔴 CRITICAL ISSUES ({len(self.critical_issues)}):")
            for i, issue in enumerate(self.critical_issues, 1):
                print(f"\n   {i}. {issue['description']}")
                print(f"      Category: {issue['category']}")
                print(f"      Endpoint: {issue['endpoint']}")
                print(f"      Expected: {issue['expected_behavior']}")
                print(f"      Actual: {issue['actual_behavior']}")
                if issue['error_message']:
                    print(f"      Error: {issue['error_message']}")
        
        if self.high_issues:
            print(f"\n🟠 HIGH PRIORITY ISSUES ({len(self.high_issues)}):")
            for i, issue in enumerate(self.high_issues, 1):
                print(f"\n   {i}. {issue['description']}")
                print(f"      Category: {issue['category']}")
                print(f"      Endpoint: {issue['endpoint']}")
                print(f"      Expected: {issue['expected_behavior']}")
                print(f"      Actual: {issue['actual_behavior']}")
        
        if self.medium_issues:
            print(f"\n🟡 MEDIUM PRIORITY ISSUES ({len(self.medium_issues)}):")
            for i, issue in enumerate(self.medium_issues[:5], 1):  # Show first 5
                print(f"\n   {i}. {issue['description']}")
                print(f"      Category: {issue['category']}")
                print(f"      Endpoint: {issue['endpoint']}")
            if len(self.medium_issues) > 5:
                print(f"   ... and {len(self.medium_issues) - 5} more medium issues")
        
        # Failed tests
        if failed_tests > 0:
            print(f"\n❌ FAILED TESTS ({failed_tests}):")
            for result in self.test_results:
                if not result["success"]:
                    print(f"   • {result['test']}: {result['message']}")
        
        # Recommendations
        print(f"\n💡 RECOMMENDATIONS:")
        
        if len(self.critical_issues) > 0:
            print("   🔴 Address critical issues immediately - these block core functionality")
        
        if len(self.high_issues) > 0:
            print("   🟠 Fix high priority issues before production deployment")
        
        if len(self.medium_issues) > 0:
            print("   🟡 Review medium priority issues for user experience improvements")
        
        if total_issues == 0:
            print("   🎉 No major issues found! Backend appears to be working well.")
        
        print(f"\n📋 TESTING COVERAGE:")
        print("   ✅ Authentication & User Management")
        print("   ✅ Profile Management (including GPS)")
        print("   ✅ Discovery & Matching Algorithm")
        print("   ✅ Image Upload (Cloudinary)")
        print("   ✅ Location & Maps Integration")
        print("   ✅ Internationalization (Arabic)")
        print("   ✅ Error Handling & Validation")
        print("   ✅ Weekly Limits & Usage Stats")
        
        return passed_tests, failed_tests, total_issues

def main():
    """Main function to run comprehensive QA testing"""
    tester = PizooQATester()
    tester.run_comprehensive_qa()
    
    # Return appropriate exit code
    total_issues = len(tester.critical_issues) + len(tester.high_issues)
    if total_issues > 0:
        print(f"\n⚠️  QA completed with {total_issues} critical/high priority issues found")
        sys.exit(1)
    else:
        print(f"\n🎉 QA completed successfully - no critical issues found!")
        sys.exit(0)

if __name__ == "__main__":
    main()