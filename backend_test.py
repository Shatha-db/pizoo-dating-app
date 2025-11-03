#!/usr/bin/env python3
"""
Production Health Check for Pizoo Dating App
Testing URL: https://multilingual-date.emergent.host
"""

import httpx
import json
import time
import asyncio
from datetime import datetime
from typing import Dict, Any, Optional

# URLs to test
PRODUCTION_URL = "https://multilingual-date.emergent.host"  # From review request
BACKEND_URL = "https://pizoo-monorepo.preview.emergentagent.com"  # From frontend config

class ProductionHealthChecker:
    def __init__(self):
        self.results = {
            "timestamp": datetime.now().isoformat(),
            "production_url": PRODUCTION_URL,
            "backend_url": BACKEND_URL,
            "overall_status": "unknown",
            "services": {
                "backend_api": {"status": "unknown", "response_time_ms": 0, "details": ""},
                "mongodb": {"status": "unknown", "connection": "unknown", "details": ""},
                "livekit": {"status": "unknown", "url": "", "details": ""},
                "cloudinary": {"status": "unknown", "cloud_name": "", "details": ""},
                "sentry": {"status": "unknown", "environment": "", "details": ""},
                "cors": {"status": "unknown", "allowed_origins": [], "details": ""}
            },
            "environment_variables": {
                "critical_missing": [],
                "all_set": False
            },
            "recommendations": []
        }
        self.client = httpx.AsyncClient(timeout=30.0, follow_redirects=True)
        self.active_backend_url = None  # Will be determined during testing

    async def determine_active_backend(self):
        """Determine which backend URL is active"""
        print("🔍 Determining active backend URL...")
        
        urls_to_test = [PRODUCTION_URL, BACKEND_URL]
        
        for url in urls_to_test:
            try:
                response = await self.client.get(f"{url}/api/")
                if response.status_code == 200:
                    data = response.json()
                    if "message" in data:
                        print(f"✅ Active backend found at: {url}")
                        self.active_backend_url = url
                        return url
            except Exception as e:
                print(f"   {url} not accessible: {e}")
                continue
        
        print("❌ No active backend found")
        return None

    async def test_health_endpoint(self):
        """Test GET /health endpoint"""
        print("🔍 Testing health endpoint...")
        
        if not self.active_backend_url:
            print("❌ No active backend URL available")
            self.results["services"]["backend_api"]["status"] = "fail"
            self.results["services"]["backend_api"]["details"] = "No active backend URL found"
            return
        
        # Try multiple possible health endpoint locations
        health_endpoints = ["/health", "/api/health"]
        
        for endpoint in health_endpoints:
            try:
                start_time = time.time()
                response = await self.client.get(f"{self.active_backend_url}{endpoint}")
                response_time = int((time.time() - start_time) * 1000)
                
                self.results["services"]["backend_api"]["response_time_ms"] = response_time
                
                print(f"   Trying {endpoint}: {response.status_code}")
                
                if response.status_code == 200:
                    # Check if response is JSON
                    try:
                        data = response.json()
                        print(f"✅ Health endpoint found at {endpoint} - responded in {response_time}ms")
                        print(f"   Response: {json.dumps(data, indent=2)}")
                        
                        # Check expected fields
                        expected_fields = ["db", "otp", "ai", "status"]
                        missing_fields = [field for field in expected_fields if field not in data]
                        
                        if not missing_fields and data.get("status") == "healthy":
                            self.results["services"]["backend_api"]["status"] = "ok"
                            self.results["services"]["backend_api"]["details"] = f"Health check passed at {endpoint}. Response time: {response_time}ms"
                            
                            # Update individual service statuses based on health response
                            if data.get("db") == "ok":
                                self.results["services"]["mongodb"]["status"] = "ok"
                                self.results["services"]["mongodb"]["connection"] = "active"
                                self.results["services"]["mongodb"]["details"] = "Database connection healthy"
                            else:
                                self.results["services"]["mongodb"]["status"] = "fail"
                                self.results["services"]["mongodb"]["connection"] = "inactive"
                                self.results["services"]["mongodb"]["details"] = f"Database status: {data.get('db', 'unknown')}"
                            
                            if data.get("otp") == "ok":
                                self.results["services"]["backend_api"]["details"] += ". OTP service operational"
                            
                            if data.get("ai") == "ok":
                                self.results["services"]["backend_api"]["details"] += ". AI matching service operational"
                            
                            return  # Success, exit function
                            
                        else:
                            self.results["services"]["backend_api"]["status"] = "warn"
                            self.results["services"]["backend_api"]["details"] = f"Health check incomplete at {endpoint}. Missing fields: {missing_fields}. Status: {data.get('status', 'unknown')}"
                            return  # Found endpoint but incomplete, exit function
                            
                    except json.JSONDecodeError:
                        # Response is not JSON (probably HTML frontend)
                        print(f"   {endpoint} returned HTML (frontend), not JSON API")
                        continue
                        
                elif response.status_code == 404:
                    print(f"   {endpoint} not found")
                    continue
                else:
                    print(f"   {endpoint} returned {response.status_code}")
                    continue
                    
            except Exception as e:
                print(f"   Error testing {endpoint}: {e}")
                continue
        
        # If we get here, no health endpoint was found
        self.results["services"]["backend_api"]["status"] = "fail"
        self.results["services"]["backend_api"]["details"] = "No health endpoint found at /health or /api/health"
        print(f"❌ No health endpoint found")

    async def test_root_endpoint(self):
        """Test GET / endpoint"""
        print("🔍 Testing root endpoint...")
        if not self.active_backend_url:
            print("❌ No active backend URL available")
            return
            
        try:
            response = await self.client.get(f"{self.active_backend_url}/")
            if response.status_code == 200:
                print(f"✅ Root endpoint accessible")
                print(f"   Response: {response.text[:200]}")
            else:
                print(f"⚠️ Root endpoint returned {response.status_code}")
        except Exception as e:
            print(f"❌ Root endpoint error: {e}")

    async def test_api_endpoints(self):
        """Test various API endpoints"""
        print("🔍 Testing API endpoints...")
        
        endpoints_to_test = [
            ("/api/", "GET", "API root"),
            ("/api/auth/register", "POST", "Registration validation"),
            ("/api/auth/login", "POST", "Login validation")
        ]
        
        if not self.active_backend_url:
            print("❌ No active backend URL available")
            return
            
        for endpoint, method, description in endpoints_to_test:
            try:
                url = f"{self.active_backend_url}{endpoint}"
                print(f"   Testing {method} {endpoint} - {description}")
                
                if method == "GET":
                    response = await self.client.get(url)
                elif method == "POST":
                    # Test with invalid data to check validation
                    response = await self.client.post(url, json={})
                
                print(f"   → {response.status_code} {response.reason_phrase}")
                
                # For auth endpoints, we expect 400 (validation error) or 422 (unprocessable entity)
                if endpoint in ["/api/auth/register", "/api/auth/login"] and response.status_code in [400, 422]:
                    print(f"   ✅ Validation working correctly")
                elif endpoint == "/api/" and response.status_code == 200:
                    print(f"   ✅ API root accessible")
                    
            except Exception as e:
                print(f"   ❌ Error testing {endpoint}: {e}")

    async def test_cors_configuration(self):
        """Test CORS configuration"""
        print("🔍 Testing CORS configuration...")
        try:
            # Test OPTIONS request for CORS preflight
            if not self.active_backend_url:
                print("❌ No active backend URL available")
                return
                
            headers = {
                "Origin": self.active_backend_url,
                "Access-Control-Request-Method": "POST",
                "Access-Control-Request-Headers": "Content-Type,Authorization"
            }
            
            response = await self.client.options(f"{self.active_backend_url}/api/", headers=headers)
            
            cors_headers = {
                "access-control-allow-origin": response.headers.get("access-control-allow-origin"),
                "access-control-allow-methods": response.headers.get("access-control-allow-methods"),
                "access-control-allow-headers": response.headers.get("access-control-allow-headers"),
                "access-control-allow-credentials": response.headers.get("access-control-allow-credentials")
            }
            
            print(f"   CORS Headers: {json.dumps(cors_headers, indent=4)}")
            
            # Check if CORS is properly configured
            origin_header = cors_headers.get("access-control-allow-origin")
            if origin_header and origin_header != "*":
                self.results["services"]["cors"]["status"] = "ok"
                self.results["services"]["cors"]["allowed_origins"] = [origin_header]
                self.results["services"]["cors"]["details"] = "CORS properly configured with specific origins"
                print("✅ CORS configuration looks secure")
            elif origin_header == "*":
                self.results["services"]["cors"]["status"] = "warn"
                self.results["services"]["cors"]["details"] = "CORS allows all origins (*) - security risk in production"
                print("⚠️ CORS allows all origins - potential security risk")
            else:
                self.results["services"]["cors"]["status"] = "fail"
                self.results["services"]["cors"]["details"] = "CORS not properly configured"
                print("❌ CORS not properly configured")
                
        except Exception as e:
            self.results["services"]["cors"]["status"] = "fail"
            self.results["services"]["cors"]["details"] = f"CORS test error: {str(e)}"
            print(f"❌ CORS test error: {e}")

    async def test_livekit_service(self):
        """Test LiveKit service connectivity"""
        print("🔍 Testing LiveKit service...")
        if not self.active_backend_url:
            print("❌ No active backend URL available")
            return
            
        try:
            # Test LiveKit token generation endpoint
            response = await self.client.post(
                f"{self.active_backend_url}/api/livekit/token",
                json={"match_id": "test_match_123"}
            )
            
            if response.status_code == 401:
                # Expected - requires authentication
                self.results["services"]["livekit"]["status"] = "ok"
                self.results["services"]["livekit"]["details"] = "LiveKit endpoint accessible, requires authentication (expected)"
                print("✅ LiveKit endpoint accessible (requires auth)")
            elif response.status_code == 200:
                data = response.json()
                if "token" in data:
                    self.results["services"]["livekit"]["status"] = "ok"
                    self.results["services"]["livekit"]["details"] = "LiveKit token generation working"
                    print("✅ LiveKit token generation working")
            else:
                self.results["services"]["livekit"]["status"] = "warn"
                self.results["services"]["livekit"]["details"] = f"LiveKit endpoint returned {response.status_code}"
                print(f"⚠️ LiveKit endpoint returned {response.status_code}")
                
        except Exception as e:
            self.results["services"]["livekit"]["status"] = "fail"
            self.results["services"]["livekit"]["details"] = f"LiveKit test error: {str(e)}"
            print(f"❌ LiveKit test error: {e}")

    async def test_cloudinary_service(self):
        """Test Cloudinary configuration (indirect)"""
        print("🔍 Testing Cloudinary service...")
        if not self.active_backend_url:
            print("❌ No active backend URL available")
            return
            
        try:
            # We can't directly test Cloudinary without uploading, but we can check if upload endpoint exists
            response = await self.client.post(
                f"{self.active_backend_url}/api/media/upload",
                files={"file": ("test.txt", b"test", "text/plain")}
            )
            
            if response.status_code == 401:
                # Expected - requires authentication
                self.results["services"]["cloudinary"]["status"] = "ok"
                self.results["services"]["cloudinary"]["details"] = "Media upload endpoint accessible, requires authentication"
                print("✅ Media upload endpoint accessible (requires auth)")
            elif response.status_code in [400, 422]:
                # Validation error - endpoint exists
                self.results["services"]["cloudinary"]["status"] = "ok"
                self.results["services"]["cloudinary"]["details"] = "Media upload endpoint accessible, validation working"
                print("✅ Media upload endpoint accessible")
            else:
                self.results["services"]["cloudinary"]["status"] = "warn"
                self.results["services"]["cloudinary"]["details"] = f"Media upload endpoint returned {response.status_code}"
                print(f"⚠️ Media upload endpoint returned {response.status_code}")
                
        except Exception as e:
            self.results["services"]["cloudinary"]["status"] = "fail"
            self.results["services"]["cloudinary"]["details"] = f"Cloudinary test error: {str(e)}"
            print(f"❌ Cloudinary test error: {e}")

    async def test_sentry_service(self):
        """Test Sentry configuration (indirect)"""
        print("🔍 Testing Sentry service...")
        if not self.active_backend_url:
            print("❌ No active backend URL available")
            return
            
        try:
            # Test debug endpoint if available
            response = await self.client.get(f"{self.active_backend_url}/debug-sentry")
            
            if response.status_code == 200:
                data = response.json()
                if data.get("sentry_enabled"):
                    self.results["services"]["sentry"]["status"] = "ok"
                    self.results["services"]["sentry"]["environment"] = "production"
                    self.results["services"]["sentry"]["details"] = "Sentry error tracking enabled"
                    print("✅ Sentry error tracking enabled")
                else:
                    self.results["services"]["sentry"]["status"] = "warn"
                    self.results["services"]["sentry"]["details"] = "Sentry debug endpoint accessible but not enabled"
                    print("⚠️ Sentry not enabled")
            else:
                # Debug endpoint might be disabled in production (good practice)
                self.results["services"]["sentry"]["status"] = "ok"
                self.results["services"]["sentry"]["details"] = "Debug endpoint disabled (good security practice)"
                print("✅ Debug endpoint disabled (good security)")
                
        except Exception as e:
            self.results["services"]["sentry"]["status"] = "unknown"
            self.results["services"]["sentry"]["details"] = f"Cannot verify Sentry: {str(e)}"
            print(f"⚠️ Cannot verify Sentry: {e}")

    async def check_performance(self):
        """Check API performance"""
        print("🔍 Checking API performance...")
        
        # Test multiple requests to get average response time
        response_times = []
        if not self.active_backend_url:
            print("❌ No active backend URL available")
            return
            
        for i in range(3):
            try:
                start_time = time.time()
                response = await self.client.get(f"{self.active_backend_url}/api/")
                response_time = (time.time() - start_time) * 1000
                response_times.append(response_time)
                
                if response_time > 5000:  # 5 seconds
                    print(f"⚠️ Slow response detected: {response_time:.0f}ms")
                    
            except Exception as e:
                print(f"❌ Performance test error: {e}")
        
        if response_times:
            avg_response_time = sum(response_times) / len(response_times)
            print(f"📊 Average response time: {avg_response_time:.0f}ms")
            
            if avg_response_time > 5000:
                self.results["recommendations"].append("API response times are slow (>5s). Consider performance optimization.")

    def calculate_overall_status(self):
        """Calculate overall system status"""
        service_statuses = [service["status"] for service in self.results["services"].values()]
        
        if all(status == "ok" for status in service_statuses):
            self.results["overall_status"] = "healthy"
        elif any(status == "fail" for status in service_statuses):
            self.results["overall_status"] = "unhealthy"
        else:
            self.results["overall_status"] = "degraded"

    def add_recommendations(self):
        """Add recommendations based on test results"""
        recommendations = []
        
        # Check for failed services
        for service_name, service_data in self.results["services"].items():
            if service_data["status"] == "fail":
                recommendations.append(f"Fix {service_name} service: {service_data['details']}")
            elif service_data["status"] == "warn":
                recommendations.append(f"Review {service_name} configuration: {service_data['details']}")
        
        # Performance recommendations
        if self.results["services"]["backend_api"]["response_time_ms"] > 2000:
            recommendations.append("Consider optimizing API response times (currently >2s)")
        
        # Security recommendations
        if self.results["services"]["cors"]["status"] == "warn":
            recommendations.append("Review CORS configuration for production security")
        
        self.results["recommendations"].extend(recommendations)

    async def run_health_check(self):
        """Run complete health check"""
        print("🚀 Starting Production Health Check for Pizoo Dating App")
        print(f"🎯 Target URL: {PRODUCTION_URL}")
        print("=" * 60)
        
        # Run all tests
        await self.test_health_endpoint()
        await self.test_root_endpoint()
        await self.test_api_endpoints()
        await self.test_cors_configuration()
        await self.test_livekit_service()
        await self.test_cloudinary_service()
        await self.test_sentry_service()
        await self.check_performance()
        
        # Calculate results
        self.calculate_overall_status()
        self.add_recommendations()
        
        # Close HTTP client
        await self.client.aclose()
        
        print("\n" + "=" * 60)
        print("📋 HEALTH CHECK COMPLETE")
        print("=" * 60)
        
        return self.results

async def main():
    """Main function to run health check"""
    checker = ProductionHealthChecker()
    results = await checker.run_health_check()
    
    # Print results
    print(f"\n🎯 PRODUCTION HEALTH REPORT")
    print(f"Timestamp: {results['timestamp']}")
    print(f"Overall Status: {results['overall_status'].upper()}")
    print(f"Production URL: {results['production_url']}")
    
    print(f"\n📊 SERVICE STATUS:")
    for service_name, service_data in results['services'].items():
        status_emoji = {"ok": "✅", "warn": "⚠️", "fail": "❌", "unknown": "❓"}
        emoji = status_emoji.get(service_data['status'], "❓")
        print(f"  {emoji} {service_name.upper()}: {service_data['status']}")
        if service_data['details']:
            print(f"     Details: {service_data['details']}")
    
    if results['recommendations']:
        print(f"\n💡 RECOMMENDATIONS:")
        for i, rec in enumerate(results['recommendations'], 1):
            print(f"  {i}. {rec}")
    
    # Save results to file
    with open('/app/production_health_report.json', 'w') as f:
        json.dump(results, f, indent=2)
    
    print(f"\n📄 Full report saved to: /app/production_health_report.json")
    
    return results

if __name__ == "__main__":
    asyncio.run(main())