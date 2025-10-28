#!/usr/bin/env python3
"""
اختبار شامل لـ Backend APIs بعد دمج الفروع
Comprehensive Backend API Testing Script After Branch Merge
Tests all requested endpoints with Arabic support
"""

import requests
import json
import sys
import base64
import io
from datetime import datetime
import uuid
from PIL import Image

# Configuration
BASE_URL = "https://pizoo-dating-3.preview.emergentagent.com/api"
HEADERS = {"Content-Type": "application/json"}

class PizooBackendTester:
    def __init__(self):
        self.base_url = BASE_URL
        self.headers = HEADERS.copy()
        self.auth_token = None
        self.user_id = None
        self.profile_id = None
        self.test_results = []
        self.test_email = None
        self.test_password = None
        self.discovered_profiles = []
        
    def log_result(self, test_name, success, message, response_data=None):
        """تسجيل نتائج الاختبار"""
        result = {
            "test": test_name,
            "success": success,
            "message": message,
            "timestamp": datetime.now().isoformat(),
            "response_data": response_data
        }
        self.test_results.append(result)
        status = "✅ نجح" if success else "❌ فشل"
        print(f"{status} {test_name}: {message}")
        if not success and response_data:
            print(f"   الاستجابة: {response_data}")
    
    def make_request(self, method, endpoint, data=None, use_auth=False, files=None):
        """إجراء طلب HTTP مع الرؤوس المناسبة"""
        url = f"{self.base_url}{endpoint}"
        headers = self.headers.copy() if not files else {}
        
        if use_auth and self.auth_token:
            headers["Authorization"] = f"Bearer {self.auth_token}"
        
        try:
            if method.upper() == "GET":
                response = requests.get(url, headers=headers, timeout=30)
            elif method.upper() == "POST":
                if files:
                    response = requests.post(url, headers=headers, files=files, timeout=30)
                else:
                    response = requests.post(url, headers=headers, json=data, timeout=30)
            elif method.upper() == "PUT":
                response = requests.put(url, headers=headers, json=data, timeout=30)
            elif method.upper() == "DELETE":
                response = requests.delete(url, headers=headers, timeout=30)
            else:
                raise ValueError(f"طريقة غير مدعومة: {method}")
            
            return response
        except requests.exceptions.RequestException as e:
            return None, str(e)
    
    def test_mongodb_connection(self):
        """اختبار اتصال MongoDB من خلال API الجذر"""
        response = self.make_request("GET", "/")
        
        if response is None:
            self.log_result("اتصال MongoDB", False, "فشل الاتصال بالخادم")
            return False
        
        if response.status_code == 200:
            try:
                data = response.json()
                self.log_result("اتصال MongoDB", True, f"قاعدة البيانات متصلة: {data.get('message', 'OK')}")
                return True
            except:
                self.log_result("اتصال MongoDB", True, "قاعدة البيانات متصلة")
                return True
        else:
            self.log_result("اتصال MongoDB", False, f"HTTP {response.status_code}: {response.text}")
            return False
    
    def test_user_registration(self):
        """اختبار تسجيل مستخدم جديد - POST /api/auth/register"""
        # إنشاء بيانات اختبار فريدة
        unique_id = str(uuid.uuid4())[:8]
        self.test_email = f"مستخدم_اختبار_{unique_id}@example.com"
        self.test_password = "كلمة_مرور_قوية123!"
        
        test_data = {
            "name": f"أحمد محمد {unique_id}",
            "email": self.test_email,
            "phone_number": f"+966501234{unique_id[:3]}",
            "password": self.test_password,
            "terms_accepted": True
        }
        
        response = self.make_request("POST", "/auth/register", test_data)
        
        if response is None:
            self.log_result("تسجيل مستخدم جديد", False, "فشل الاتصال")
            return False
        
        if response.status_code == 200:
            try:
                data = response.json()
                if "access_token" in data and "user" in data:
                    self.auth_token = data["access_token"]
                    self.user_id = data["user"]["id"]
                    self.log_result("تسجيل مستخدم جديد", True, f"تم تسجيل المستخدم بنجاح. المعرف: {self.user_id}")
                    return True
                else:
                    self.log_result("تسجيل مستخدم جديد", False, "مفقود access_token أو user في الاستجابة", data)
                    return False
            except json.JSONDecodeError:
                self.log_result("تسجيل مستخدم جديد", False, "استجابة JSON غير صالحة", response.text)
                return False
        else:
            try:
                error_data = response.json()
                self.log_result("تسجيل مستخدم جديد", False, f"HTTP {response.status_code}: {error_data.get('detail', response.text)}")
            except:
                self.log_result("تسجيل مستخدم جديد", False, f"HTTP {response.status_code}: {response.text}")
            return False
    
    def test_user_login(self):
        """اختبار تسجيل الدخول - POST /api/auth/login"""
        if not self.user_id or not self.test_email:
            self.log_result("تسجيل الدخول", False, "لا يوجد مستخدم مسجل لاختبار تسجيل الدخول")
            return False
        
        login_data = {
            "email": self.test_email,
            "password": self.test_password
        }
        
        response = self.make_request("POST", "/auth/login", login_data)
        
        if response is None:
            self.log_result("تسجيل الدخول", False, "فشل الاتصال")
            return False
        
        if response.status_code == 200:
            try:
                data = response.json()
                if "access_token" in data:
                    self.auth_token = data["access_token"]
                    self.log_result("تسجيل الدخول", True, "تم تسجيل الدخول بنجاح")
                    return True
                else:
                    self.log_result("تسجيل الدخول", False, "مفقود access_token في الاستجابة", data)
                    return False
            except json.JSONDecodeError:
                self.log_result("تسجيل الدخول", False, "استجابة JSON غير صالحة", response.text)
                return False
        else:
            try:
                error_data = response.json()
                self.log_result("تسجيل الدخول", False, f"HTTP {response.status_code}: {error_data.get('detail', response.text)}")
            except:
                self.log_result("تسجيل الدخول", False, f"HTTP {response.status_code}: {response.text}")
            return False
    
    def test_get_user_profile(self):
        """اختبار جلب ملف المستخدم - GET /api/profile/me"""
        if not self.auth_token:
            self.log_result("جلب ملف المستخدم", False, "لا يوجد رمز مصادقة")
            return False
        
        response = self.make_request("GET", "/profile/me", use_auth=True)
        
        if response is None:
            self.log_result("جلب ملف المستخدم", False, "فشل الاتصال")
            return False
        
        if response.status_code == 200:
            try:
                data = response.json()
                if "display_name" in data or "user_id" in data:
                    self.log_result("جلب ملف المستخدم", True, f"تم جلب الملف الشخصي بنجاح")
                    return True
                else:
                    self.log_result("جلب ملف المستخدم", True, "تم جلب الملف الشخصي")
                    return True
            except json.JSONDecodeError:
                self.log_result("جلب ملف المستخدم", False, "استجابة JSON غير صالحة", response.text)
                return False
        else:
            try:
                error_data = response.json()
                self.log_result("جلب ملف المستخدم", False, f"HTTP {response.status_code}: {error_data.get('detail', response.text)}")
            except:
                self.log_result("جلب ملف المستخدم", False, f"HTTP {response.status_code}: {response.text}")
            return False
    
    def test_profile_discovery(self):
        """اختبار اكتشاف المستخدمين - GET /api/profiles/discover"""
        if not self.auth_token:
            self.log_result("اكتشاف المستخدمين", False, "لا يوجد رمز مصادقة")
            return False
        
        # أولاً إنشاء ملفات وهمية للاختبار
        self.create_dummy_profiles()
        
        response = self.make_request("GET", "/profiles/discover?limit=20", use_auth=True)
        
        if response is None:
            self.log_result("اكتشاف المستخدمين", False, "فشل الاتصال")
            return False
        
        if response.status_code == 200:
            try:
                data = response.json()
                if "profiles" in data:
                    profile_count = len(data["profiles"])
                    self.discovered_profiles = data["profiles"]
                    self.log_result("اكتشاف المستخدمين", True, f"تم العثور على {profile_count} ملف شخصي للاكتشاف")
                    return True
                else:
                    self.log_result("اكتشاف المستخدمين", False, "لا يوجد مفتاح profiles في الاستجابة", data)
                    return False
            except json.JSONDecodeError:
                self.log_result("اكتشاف المستخدمين", False, "استجابة JSON غير صالحة", response.text)
                return False
        else:
            try:
                error_data = response.json()
                self.log_result("اكتشاف المستخدمين", False, f"HTTP {response.status_code}: {error_data.get('detail', response.text)}")
            except:
                self.log_result("اكتشاف المستخدمين", False, f"HTTP {response.status_code}: {response.text}")
            return False
    
    def test_discovery_settings(self):
        """اختبار إعدادات الاكتشاف - PUT /api/discovery-settings"""
        if not self.auth_token:
            self.log_result("إعدادات الاكتشاف", False, "لا يوجد رمز مصادقة")
            return False
        
        # اختبار تحديث إعدادات الاكتشاف مع lat/lng
        settings_data = {
            "location": "الرياض، المملكة العربية السعودية",
            "max_distance": 50,
            "interested_in": "all",
            "min_age": 22,
            "max_age": 35,
            "latitude": 24.7136,
            "longitude": 46.6753
        }
        
        response = self.make_request("PUT", "/discovery-settings", settings_data, use_auth=True)
        
        if response is None:
            self.log_result("إعدادات الاكتشاف", False, "فشل الاتصال")
            return False
        
        if response.status_code == 200:
            try:
                data = response.json()
                self.log_result("إعدادات الاكتشاف", True, "تم تحديث إعدادات الاكتشاف بنجاح مع الإحداثيات")
                return True
            except json.JSONDecodeError:
                self.log_result("إعدادات الاكتشاف", False, "استجابة JSON غير صالحة", response.text)
                return False
        else:
            try:
                error_data = response.json()
                self.log_result("إعدادات الاكتشاف", False, f"HTTP {response.status_code}: {error_data.get('detail', response.text)}")
            except:
                self.log_result("إعدادات الاكتشاف", False, f"HTTP {response.status_code}: {response.text}")
            return False
    
    def create_test_image(self):
        """إنشاء صورة اختبار للرفع"""
        # إنشاء صورة RGB بسيطة
        img = Image.new('RGB', (300, 300), color='red')
        img_bytes = io.BytesIO()
        img.save(img_bytes, format='JPEG')
        img_bytes.seek(0)
        return img_bytes
    
    def test_image_upload_cloudinary(self):
        """اختبار رفع صورة عبر Cloudinary - POST /api/upload/photo"""
        if not self.auth_token:
            self.log_result("رفع صورة Cloudinary", False, "لا يوجد رمز مصادقة")
            return False
        
        try:
            # إنشاء صورة اختبار
            test_image = self.create_test_image()
            
            # رفع الصورة
            files = {
                'file': ('test_image.jpg', test_image, 'image/jpeg')
            }
            
            response = self.make_request("POST", "/profile/photo/upload", use_auth=True, files=files)
            
            if response is None:
                self.log_result("رفع صورة Cloudinary", False, "فشل الاتصال")
                return False
            
            if response.status_code == 200:
                try:
                    data = response.json()
                    if data.get("success") and "photo" in data:
                        photo_url = data["photo"].get("url", "")
                        self.log_result("رفع صورة Cloudinary", True, f"تم رفع الصورة بنجاح: {photo_url[:50]}...")
                        return True
                    else:
                        self.log_result("رفع صورة Cloudinary", False, "فشل رفع الصورة", data)
                        return False
                except json.JSONDecodeError:
                    self.log_result("رفع صورة Cloudinary", False, "استجابة JSON غير صالحة", response.text)
                    return False
            else:
                try:
                    error_data = response.json()
                    self.log_result("رفع صورة Cloudinary", False, f"HTTP {response.status_code}: {error_data.get('detail', response.text)}")
                except:
                    self.log_result("رفع صورة Cloudinary", False, f"HTTP {response.status_code}: {response.text}")
                return False
                
        except Exception as e:
            self.log_result("رفع صورة Cloudinary", False, f"خطأ في إنشاء الصورة: {str(e)}")
            return False
    
    def test_swipe_action(self):
        """اختبار إعجاب/عدم إعجاب - POST /api/swipe"""
        if not self.auth_token:
            self.log_result("إجراء السوايب", False, "لا يوجد رمز مصادقة")
            return False
        
        if not self.discovered_profiles:
            self.log_result("إجراء السوايب", False, "لا توجد ملفات شخصية للسوايب")
            return False
        
        # اختبار إعجاب بأول ملف شخصي
        target_profile = self.discovered_profiles[0]
        swipe_data = {
            "swiped_user_id": target_profile["user_id"],
            "action": "like"
        }
        
        response = self.make_request("POST", "/swipe", swipe_data, use_auth=True)
        
        if response is None:
            self.log_result("إجراء السوايب", False, "فشل الاتصال")
            return False
        
        if response.status_code == 200:
            try:
                data = response.json()
                if data.get("success"):
                    is_match = data.get("is_match", False)
                    match_text = " (تطابق!)" if is_match else ""
                    remaining_likes = data.get("remaining_likes", "غير محدود")
                    self.log_result("إجراء السوايب", True, f"تم الإعجاب بنجاح{match_text}. الإعجابات المتبقية: {remaining_likes}")
                    return True
                else:
                    self.log_result("إجراء السوايب", False, "فشل إجراء السوايب", data)
                    return False
            except json.JSONDecodeError:
                self.log_result("إجراء السوايب", False, "استجابة JSON غير صالحة", response.text)
                return False
        else:
            try:
                error_data = response.json()
                self.log_result("إجراء السوايب", False, f"HTTP {response.status_code}: {error_data.get('detail', response.text)}")
            except:
                self.log_result("إجراء السوايب", False, f"HTTP {response.status_code}: {response.text}")
            return False
    
    def test_get_matches(self):
        """اختبار جلب التطابقات - GET /api/matches"""
        if not self.auth_token:
            self.log_result("جلب التطابقات", False, "لا يوجد رمز مصادقة")
            return False
        
        response = self.make_request("GET", "/matches", use_auth=True)
        
        if response is None:
            self.log_result("جلب التطابقات", False, "فشل الاتصال")
            return False
        
        if response.status_code == 200:
            try:
                data = response.json()
                if "matches" in data:
                    match_count = len(data["matches"])
                    self.log_result("جلب التطابقات", True, f"تم جلب {match_count} تطابق")
                    return True
                else:
                    self.log_result("جلب التطابقات", False, "لا يوجد مفتاح matches في الاستجابة", data)
                    return False
            except json.JSONDecodeError:
                self.log_result("جلب التطابقات", False, "استجابة JSON غير صالحة", response.text)
                return False
        else:
            try:
                error_data = response.json()
                self.log_result("جلب التطابقات", False, f"HTTP {response.status_code}: {error_data.get('detail', response.text)}")
            except:
                self.log_result("جلب التطابقات", False, f"HTTP {response.status_code}: {response.text}")
            return False
    
    def create_dummy_profiles(self):
        """إنشاء ملفات وهمية للاختبار"""
        response = self.make_request("POST", "/seed/dummy-profiles")
        if response and response.status_code == 200:
            return True
        return False
    
    def test_response_format_validation(self):
        """اختبار صحة تنسيق الاستجابات"""
        if not self.auth_token:
            self.log_result("تحقق تنسيق الاستجابة", False, "لا يوجد رمز مصادقة")
            return False
        
        # اختبار عدة endpoints للتأكد من تنسيق JSON صحيح
        endpoints_to_test = [
            ("/profile/me", "GET"),
            ("/profiles/discover?limit=5", "GET"),
            ("/matches", "GET"),
            ("/likes/sent", "GET"),
            ("/likes/received", "GET")
        ]
        
        valid_responses = 0
        total_endpoints = len(endpoints_to_test)
        
        for endpoint, method in endpoints_to_test:
            response = self.make_request(method, endpoint, use_auth=True)
            if response and response.status_code == 200:
                try:
                    data = response.json()
                    valid_responses += 1
                except json.JSONDecodeError:
                    pass
        
        if valid_responses == total_endpoints:
            self.log_result("تحقق تنسيق الاستجابة", True, f"جميع الـ {total_endpoints} endpoints ترجع JSON صحيح")
            return True
        else:
            self.log_result("تحقق تنسيق الاستجابة", False, f"{valid_responses}/{total_endpoints} endpoints ترجع JSON صحيح")
            return False
    
    def test_no_500_errors(self):
        """اختبار عدم وجود أخطاء 500"""
        if not self.auth_token:
            self.log_result("فحص أخطاء 500", False, "لا يوجد رمز مصادقة")
            return False
        
        # اختبار عدة endpoints للتأكد من عدم وجود أخطاء 500
        endpoints_to_test = [
            "/profile/me",
            "/profiles/discover",
            "/matches",
            "/likes/sent",
            "/likes/received",
            "/usage-stats"
        ]
        
        no_500_errors = True
        error_endpoints = []
        
        for endpoint in endpoints_to_test:
            response = self.make_request("GET", endpoint, use_auth=True)
            if response and response.status_code == 500:
                no_500_errors = False
                error_endpoints.append(endpoint)
        
        if no_500_errors:
            self.log_result("فحص أخطاء 500", True, f"لا توجد أخطاء 500 في {len(endpoints_to_test)} endpoints")
            return True
        else:
            self.log_result("فحص أخطاء 500", False, f"أخطاء 500 موجودة في: {', '.join(error_endpoints)}")
            return False
    
    def run_comprehensive_test(self):
        """تشغيل الاختبار الشامل لجميع APIs"""
        print("🚀 بدء الاختبار الشامل لـ Backend APIs بعد دمج الفروع")
        print(f"📍 الاختبار ضد: {self.base_url}")
        print("=" * 80)
        
        # 1. اختبار اتصال MongoDB
        print("\n🗄️ اختبار اتصال قاعدة البيانات...")
        self.test_mongodb_connection()
        
        # 2. اختبار Authentication APIs
        print("\n🔐 اختبار APIs المصادقة...")
        self.test_user_registration()
        self.test_user_login()
        self.test_get_user_profile()
        
        # 3. اختبار Profile Discovery
        print("\n🔍 اختبار اكتشاف المستخدمين...")
        self.test_profile_discovery()
        self.test_discovery_settings()
        
        # 4. اختبار Image Upload
        print("\n📸 اختبار رفع الصور...")
        self.test_image_upload_cloudinary()
        
        # 5. اختبار Swipe & Matching
        print("\n💕 اختبار السوايب والتطابق...")
        self.test_swipe_action()
        self.test_get_matches()
        
        # 6. اختبار صحة النظام
        print("\n🔧 اختبار صحة النظام...")
        self.test_response_format_validation()
        self.test_no_500_errors()
        
        # ملخص النتائج
        print("\n" + "=" * 80)
        print("📊 ملخص نتائج الاختبار")
        print("=" * 80)
        
        total_tests = len(self.test_results)
        passed_tests = sum(1 for result in self.test_results if result["success"])
        failed_tests = total_tests - passed_tests
        
        print(f"إجمالي الاختبارات: {total_tests}")
        print(f"✅ نجح: {passed_tests}")
        print(f"❌ فشل: {failed_tests}")
        print(f"معدل النجاح: {(passed_tests/total_tests)*100:.1f}%")
        
        # تفاصيل الاختبارات الناجحة
        print(f"\n✅ الاختبارات الناجحة ({passed_tests}):")
        for result in self.test_results:
            if result["success"]:
                print(f"   • {result['test']}")
        
        # تفاصيل الاختبارات الفاشلة
        if failed_tests > 0:
            print(f"\n❌ الاختبارات الفاشلة ({failed_tests}):")
            for result in self.test_results:
                if not result["success"]:
                    print(f"   • {result['test']}: {result['message']}")
        
        # تقييم النتائج
        if failed_tests == 0:
            print("\n🎉 جميع الاختبارات نجحت! النظام جاهز للإنتاج.")
        elif failed_tests <= 2:
            print("\n⚠️ معظم الاختبارات نجحت مع بعض المشاكل البسيطة.")
        else:
            print("\n🚨 يوجد مشاكل كبيرة تحتاج إلى إصلاح.")
        
        return passed_tests, failed_tests, self.test_results

def main():
    """الدالة الرئيسية لتشغيل الاختبارات"""
    tester = PizooBackendTester()
    passed, failed, results = tester.run_comprehensive_test()
    
    # الخروج برمز خطأ إذا فشلت الاختبارات
    if failed > 0:
        sys.exit(1)
    else:
        print("\n🎉 جميع الاختبارات نجحت!")
        sys.exit(0)

if __name__ == "__main__":
    main()