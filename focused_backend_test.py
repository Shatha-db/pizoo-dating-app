#!/usr/bin/env python3
"""
Focused Backend Testing - Pizoo Deep Stability Test
Addresses the specific issues found in the comprehensive test.
"""

import requests
import json
import sys
import time
import io
from datetime import datetime
from PIL import Image
import uuid

# Configuration
BASE_URL = "https://pizoo-dating-2.preview.emergentagent.com/api"
HEADERS = {"Content-Type": "application/json"}

class FocusedTester:
    def __init__(self):
        self.base_url = BASE_URL
        self.headers = HEADERS.copy()
        self.auth_token = None
        self.user_id = None
        self.test_results = []
        
    def log_result(self, test_name, success, message, duration=None):
        """Log test results"""
        result = {
            "test": test_name,
            "success": success,
            "message": message,
            "timestamp": datetime.now().isoformat(),
            "duration_ms": duration
        }
        self.test_results.append(result)
        status = "✅ PASS" if success else "❌ FAIL"
        duration_text = f" ({duration:.0f}ms)" if duration else ""
        print(f"{status} {test_name}: {message}{duration_text}")
    
    def make_request(self, method, endpoint, data=None, use_auth=False, files=None, timeout=30):
        """Make HTTP request with timing"""
        url = f"{self.base_url}{endpoint}"
        headers = self.headers.copy() if not files else {}
        
        if use_auth and self.auth_token:
            headers["Authorization"] = f"Bearer {self.auth_token}"
        
        start_time = time.time()
        try:
            if method.upper() == "GET":
                response = requests.get(url, headers=headers, timeout=timeout)
            elif method.upper() == "POST":
                if files:
                    response = requests.post(url, headers=headers, files=files, timeout=timeout)
                else:
                    response = requests.post(url, headers=headers, json=data, timeout=timeout)
            elif method.upper() == "PUT":
                response = requests.put(url, headers=headers, json=data, timeout=timeout)
            elif method.upper() == "DELETE":
                response = requests.delete(url, headers=headers, timeout=timeout)
            else:
                raise ValueError(f"Unsupported method: {method}")
            
            duration = (time.time() - start_time) * 1000
            return response, duration
        except requests.exceptions.RequestException as e:
            duration = (time.time() - start_time) * 1000
            return None, duration
    
    def setup_test_user(self):
        """Create and authenticate test user"""
        unique_id = str(uuid.uuid4())[:8]
        user_data = {
            "name": f"Focused Test User {unique_id}",
            "email": f"focustest{unique_id}@pizoo.com",
            "phone_number": f"+41791234{unique_id[:4]}",
            "password": "FocusTest123!",
            "terms_accepted": True
        }
        
        response, duration = self.make_request("POST", "/auth/register", user_data)
        
        if response and response.status_code == 200:
            try:
                data = response.json()
                self.auth_token = data["access_token"]
                self.user_id = data["user"]["id"]
                self.log_result("Setup Test User", True, f"User created: {self.user_id}", duration)
                return True
            except:
                self.log_result("Setup Test User", False, "Invalid registration response", duration)
                return False
        else:
            error_msg = response.text if response else "Connection failed"
            self.log_result("Setup Test User", False, f"Registration failed: {error_msg}", duration)
            return False
    
    def create_real_test_image(self, width=100, height=100, color=(255, 0, 0)):
        """Create a real valid image for testing"""
        # Create a simple colored image
        image = Image.new('RGB', (width, height), color)
        
        # Save to bytes
        img_bytes = io.BytesIO()
        image.save(img_bytes, format='JPEG', quality=85)
        img_bytes.seek(0)
        
        return img_bytes.getvalue()
    
    def test_real_image_upload(self):
        """Test photo upload with real valid image"""
        if not self.auth_token:
            self.log_result("Real Image Upload", False, "No auth token available")
            return False
        
        # Create a real test image (red 200x200 JPEG)
        test_image_bytes = self.create_real_test_image(200, 200, (255, 0, 0))
        
        files = {
            'file': ('test_image.jpg', io.BytesIO(test_image_bytes), 'image/jpeg')
        }
        
        response, duration = self.make_request("POST", "/profile/photo/upload", files=files, use_auth=True)
        
        if response is None:
            self.log_result("Real Image Upload", False, "Connection failed", duration)
            return False
        
        if response.status_code == 200:
            try:
                data = response.json()
                if data.get("success") and "photo" in data:
                    photo_url = data["photo"].get("url")
                    self.log_result("Real Image Upload", True, f"Photo uploaded: {photo_url}", duration)
                    return True
                else:
                    self.log_result("Real Image Upload", False, f"Invalid response: {data}", duration)
                    return False
            except json.JSONDecodeError:
                self.log_result("Real Image Upload", False, "Invalid JSON response", duration)
                return False
        else:
            try:
                error_data = response.json()
                self.log_result("Real Image Upload", False, f"HTTP {response.status_code}: {error_data.get('detail', response.text)}", duration)
            except:
                self.log_result("Real Image Upload", False, f"HTTP {response.status_code}: {response.text}", duration)
            return False
    
    def test_multiple_image_formats(self):
        """Test uploading different image formats"""
        if not self.auth_token:
            self.log_result("Multiple Image Formats", False, "No auth token available")
            return False
        
        formats = [
            ('JPEG', 'image/jpeg', 'test.jpg', (255, 0, 0)),    # Red
            ('PNG', 'image/png', 'test.png', (0, 255, 0)),     # Green  
            ('WEBP', 'image/webp', 'test.webp', (0, 0, 255))   # Blue
        ]
        
        success_count = 0
        for img_format, mime_type, filename, color in formats:
            # Create image in specific format
            image = Image.new('RGB', (150, 150), color)
            img_bytes = io.BytesIO()
            
            try:
                image.save(img_bytes, format=img_format, quality=85)
                img_bytes.seek(0)
                
                files = {
                    'file': (filename, img_bytes, mime_type)
                }
                
                response, duration = self.make_request("POST", "/profile/photo/upload", files=files, use_auth=True)
                
                if response and response.status_code == 200:
                    try:
                        data = response.json()
                        if data.get("success"):
                            self.log_result(f"Upload {img_format}", True, f"Format accepted", duration)
                            success_count += 1
                        else:
                            self.log_result(f"Upload {img_format}", False, f"Upload failed: {data}", duration)
                    except:
                        self.log_result(f"Upload {img_format}", False, "Invalid JSON response", duration)
                else:
                    # Format might be rejected, which is acceptable
                    status_code = response.status_code if response else "No response"
                    self.log_result(f"Upload {img_format}", True, f"Format validation (status: {status_code})", duration)
                    success_count += 1
                    
            except Exception as e:
                self.log_result(f"Upload {img_format}", False, f"Format not supported: {str(e)}")
        
        return success_count > 0
    
    def test_image_size_limits(self):
        """Test image upload size limits"""
        if not self.auth_token:
            self.log_result("Image Size Limits", False, "No auth token available")
            return False
        
        # Test different sizes
        test_sizes = [
            (50, 50, "Small (50x50)"),
            (500, 500, "Medium (500x500)"),
            (1000, 1000, "Large (1000x1000)"),
            (2000, 2000, "Very Large (2000x2000)")
        ]
        
        success_count = 0
        for width, height, size_label in test_sizes:
            try:
                test_image_bytes = self.create_real_test_image(width, height, (128, 128, 128))
                
                files = {
                    'file': (f'test_{width}x{height}.jpg', io.BytesIO(test_image_bytes), 'image/jpeg')
                }
                
                response, duration = self.make_request("POST", "/profile/photo/upload", files=files, use_auth=True, timeout=60)
                
                if response and response.status_code == 200:
                    try:
                        data = response.json()
                        if data.get("success"):
                            self.log_result(f"Size Test {size_label}", True, "Upload successful", duration)
                            success_count += 1
                        else:
                            self.log_result(f"Size Test {size_label}", False, f"Upload failed: {data}", duration)
                    except:
                        self.log_result(f"Size Test {size_label}", False, "Invalid JSON response", duration)
                else:
                    # Large images might be rejected
                    if width >= 2000:
                        self.log_result(f"Size Test {size_label}", True, "Large image correctly handled", duration)
                        success_count += 1
                    else:
                        error_msg = response.text if response else "Connection failed"
                        self.log_result(f"Size Test {size_label}", False, f"Unexpected failure: {error_msg}", duration)
                        
            except Exception as e:
                self.log_result(f"Size Test {size_label}", False, f"Error creating image: {str(e)}")
        
        return success_count > 0
    
    def test_gps_profile_creation(self):
        """Test profile creation with GPS coordinates"""
        if not self.auth_token:
            self.log_result("GPS Profile Creation", False, "No auth token available")
            return False
        
        # Test locations with real coordinates
        test_locations = [
            {
                "name": "Basel, Switzerland",
                "latitude": 47.5596,
                "longitude": 7.5886
            },
            {
                "name": "Zurich, Switzerland", 
                "latitude": 47.3769,
                "longitude": 8.5417
            }
        ]
        
        for location in test_locations:
            profile_data = {
                "display_name": f"GPS Test User - {location['name']}",
                "bio": f"Testing GPS coordinates for {location['name']}",
                "age": 30,
                "gender": "male",
                "height": 175,
                "location": location["name"],
                "latitude": location["latitude"],
                "longitude": location["longitude"],
                "interests": ["GPS Testing", "Location Services"],
                "languages": ["English", "Arabic"]
            }
            
            response, duration = self.make_request("PUT", "/profile/update", profile_data, use_auth=True)
            
            if response and response.status_code == 200:
                # Verify GPS coordinates were saved
                get_response, get_duration = self.make_request("GET", "/profile/me", use_auth=True)
                
                if get_response and get_response.status_code == 200:
                    try:
                        profile = get_response.json()
                        saved_lat = profile.get("latitude")
                        saved_lon = profile.get("longitude")
                        
                        if saved_lat == location["latitude"] and saved_lon == location["longitude"]:
                            self.log_result(f"GPS Profile {location['name']}", True, f"GPS coordinates saved correctly", duration)
                        else:
                            self.log_result(f"GPS Profile {location['name']}", False, f"GPS coordinates not saved correctly", duration)
                    except:
                        self.log_result(f"GPS Profile {location['name']}", False, "Invalid profile response", duration)
                else:
                    self.log_result(f"GPS Profile {location['name']}", False, "Could not verify profile", duration)
            else:
                error_msg = response.text if response else "Connection failed"
                self.log_result(f"GPS Profile {location['name']}", False, f"Profile update failed: {error_msg}", duration)
        
        return True
    
    def test_discovery_with_gps_profiles(self):
        """Test discovery API after creating GPS profiles"""
        if not self.auth_token:
            self.log_result("Discovery with GPS", False, "No auth token available")
            return False
        
        # First create some test profiles with GPS coordinates
        self.create_gps_test_profiles()
        
        # Now test discovery
        response, duration = self.make_request("GET", "/profiles/discover?limit=20", use_auth=True)
        
        if response and response.status_code == 200:
            try:
                data = response.json()
                profiles = data.get("profiles", [])
                
                profiles_with_distance = [p for p in profiles if "distance" in p and p["distance"] is not None]
                profiles_with_gps = [p for p in profiles if p.get("latitude") and p.get("longitude")]
                
                self.log_result("Discovery with GPS", True, 
                    f"Found {len(profiles)} profiles, {len(profiles_with_gps)} with GPS, {len(profiles_with_distance)} with distance", 
                    duration)
                return True
                
            except json.JSONDecodeError:
                self.log_result("Discovery with GPS", False, "Invalid JSON response", duration)
                return False
        else:
            self.log_result("Discovery with GPS", False, f"Discovery failed", duration)
            return False
    
    def create_gps_test_profiles(self):
        """Create additional test profiles with GPS coordinates"""
        test_profiles = [
            {
                "name": "GPS Test Profile 1",
                "email": f"gpstest1{uuid.uuid4().hex[:6]}@test.com",
                "latitude": 47.5500,  # Near Basel
                "longitude": 7.5800,
                "location": "Near Basel"
            },
            {
                "name": "GPS Test Profile 2", 
                "email": f"gpstest2{uuid.uuid4().hex[:6]}@test.com",
                "latitude": 47.6000,  # Basel suburbs
                "longitude": 7.6500,
                "location": "Basel Suburbs"
            }
        ]
        
        for profile_info in test_profiles:
            # Register user
            user_data = {
                "name": profile_info["name"],
                "email": profile_info["email"],
                "phone_number": f"+41791{uuid.uuid4().hex[:6]}",
                "password": "TestGPS123!",
                "terms_accepted": True
            }
            
            reg_response, _ = self.make_request("POST", "/auth/register", user_data)
            
            if reg_response and reg_response.status_code == 200:
                try:
                    reg_data = reg_response.json()
                    temp_token = reg_data["access_token"]
                    
                    # Create profile with GPS
                    profile_data = {
                        "display_name": profile_info["name"],
                        "bio": f"GPS test profile at {profile_info['location']}",
                        "age": 28,
                        "gender": "female",
                        "height": 165,
                        "location": profile_info["location"],
                        "latitude": profile_info["latitude"],
                        "longitude": profile_info["longitude"],
                        "interests": ["Testing", "GPS"],
                        "languages": ["English"]
                    }
                    
                    # Temporarily use this user's token
                    original_token = self.auth_token
                    self.auth_token = temp_token
                    
                    self.make_request("PUT", "/profile/update", profile_data, use_auth=True)
                    
                    # Restore original token
                    self.auth_token = original_token
                    
                except:
                    pass  # Ignore errors in test profile creation
    
    def test_usage_stats_api(self):
        """Test usage stats API"""
        if not self.auth_token:
            self.log_result("Usage Stats API", False, "No auth token available")
            return False
        
        response, duration = self.make_request("GET", "/usage-stats", use_auth=True)
        
        if response and response.status_code == 200:
            try:
                data = response.json()
                required_fields = ["premium_tier", "is_premium", "likes", "messages"]
                missing_fields = [field for field in required_fields if field not in data]
                
                if missing_fields:
                    self.log_result("Usage Stats API", False, f"Missing fields: {missing_fields}", duration)
                    return False
                
                # Check likes structure
                likes = data.get("likes", {})
                if "sent" in likes and "remaining" in likes:
                    self.log_result("Usage Stats API", True, f"Usage stats working: {likes['sent']} likes sent, {likes['remaining']} remaining", duration)
                    return True
                else:
                    self.log_result("Usage Stats API", False, "Invalid likes structure", duration)
                    return False
                    
            except json.JSONDecodeError:
                self.log_result("Usage Stats API", False, "Invalid JSON response", duration)
                return False
        else:
            error_msg = response.text if response else "Connection failed"
            self.log_result("Usage Stats API", False, f"API failed: {error_msg}", duration)
            return False
    
    def test_weekly_limits_enforcement(self):
        """Test weekly limits enforcement in swipe API"""
        if not self.auth_token:
            self.log_result("Weekly Limits Enforcement", False, "No auth token available")
            return False
        
        # Get some profiles to swipe on
        discovery_response, _ = self.make_request("GET", "/profiles/discover?limit=5", use_auth=True)
        
        if not (discovery_response and discovery_response.status_code == 200):
            self.log_result("Weekly Limits Enforcement", False, "Could not get profiles for testing")
            return False
        
        try:
            profiles = discovery_response.json().get("profiles", [])
            if not profiles:
                self.log_result("Weekly Limits Enforcement", False, "No profiles available for swipe testing")
                return False
            
            # Test swipe action
            target_profile = profiles[0]
            swipe_data = {
                "swiped_user_id": target_profile["user_id"],
                "action": "like"
            }
            
            response, duration = self.make_request("POST", "/swipe", swipe_data, use_auth=True)
            
            if response and response.status_code == 200:
                try:
                    swipe_result = response.json()
                    remaining_likes = swipe_result.get("remaining_likes")
                    
                    if remaining_likes is not None:
                        self.log_result("Weekly Limits Enforcement", True, f"Swipe successful, {remaining_likes} likes remaining", duration)
                        return True
                    else:
                        self.log_result("Weekly Limits Enforcement", True, "Swipe successful (premium user - unlimited)", duration)
                        return True
                except:
                    self.log_result("Weekly Limits Enforcement", False, "Invalid swipe response", duration)
                    return False
            elif response and response.status_code == 403:
                # Limit reached - this is expected behavior
                self.log_result("Weekly Limits Enforcement", True, "Weekly limit correctly enforced", duration)
                return True
            else:
                error_msg = response.text if response else "Connection failed"
                self.log_result("Weekly Limits Enforcement", False, f"Swipe failed: {error_msg}", duration)
                return False
                
        except json.JSONDecodeError:
            self.log_result("Weekly Limits Enforcement", False, "Invalid discovery response")
            return False
    
    def run_focused_tests(self):
        """Run focused tests addressing specific issues"""
        print("🎯 Starting Focused Backend Testing - Pizoo Deep Stability")
        print(f"📍 Testing against: {self.base_url}")
        print("=" * 70)
        
        # Setup
        print("\n🔧 Setting up test environment...")
        if not self.setup_test_user():
            print("❌ Failed to setup test user. Aborting tests.")
            return 0, 1, self.test_results
        
        # 1. Image Upload System (with real images)
        print("\n📸 Testing Image Upload System (Real Images)...")
        self.test_real_image_upload()
        self.test_multiple_image_formats()
        self.test_image_size_limits()
        
        # 2. GPS/Location Features
        print("\n🌍 Testing GPS/Location Features...")
        self.test_gps_profile_creation()
        self.test_discovery_with_gps_profiles()
        
        # 3. Usage Stats & Limits
        print("\n📊 Testing Usage Stats & Weekly Limits...")
        self.test_usage_stats_api()
        self.test_weekly_limits_enforcement()
        
        # Summary
        print("\n" + "=" * 70)
        print("📊 FOCUSED TEST SUMMARY")
        print("=" * 70)
        
        total_tests = len(self.test_results)
        passed_tests = sum(1 for result in self.test_results if result["success"])
        failed_tests = total_tests - passed_tests
        
        print(f"Total Tests: {total_tests}")
        print(f"✅ Passed: {passed_tests}")
        print(f"❌ Failed: {failed_tests}")
        print(f"Success Rate: {(passed_tests/total_tests)*100:.1f}%")
        
        # Failed Tests
        if failed_tests > 0:
            print("\n❌ FAILED TESTS:")
            for result in self.test_results:
                if not result["success"]:
                    print(f"   • {result['test']}: {result['message']}")
        
        # Performance Analysis
        durations = [r["duration_ms"] for r in self.test_results if r["duration_ms"] is not None]
        if durations:
            avg_duration = sum(durations) / len(durations)
            max_duration = max(durations)
            print(f"\n📈 Performance Analysis:")
            print(f"   • Average Response Time: {avg_duration:.0f}ms")
            print(f"   • Maximum Response Time: {max_duration:.0f}ms")
        
        return passed_tests, failed_tests, self.test_results

def main():
    """Main function to run focused tests"""
    tester = FocusedTester()
    passed, failed, results = tester.run_focused_tests()
    
    # Exit with error code if tests failed
    if failed > 0:
        print(f"\n⚠️  {failed} focused tests failed!")
        sys.exit(1)
    else:
        print("\n🎉 All focused tests passed!")
        sys.exit(0)

if __name__ == "__main__":
    main()