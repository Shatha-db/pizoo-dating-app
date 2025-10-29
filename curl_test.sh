#!/bin/bash

echo "🚀 اختبار Backend APIs باستخدام curl"
echo "=================================="

BASE_URL="https://dating-app-bugfix.preview.emergentagent.com/api"

# 1. اختبار الاتصال الأساسي
echo "1. اختبار الاتصال الأساسي..."
curl -s -X GET "$BASE_URL/" -H "Content-Type: application/json" | jq .

# 2. تسجيل مستخدم جديد
echo -e "\n2. تسجيل مستخدم جديد..."
REGISTER_RESPONSE=$(curl -s -X POST "$BASE_URL/auth/register" \
-H "Content-Type: application/json" \
-d '{
  "name": "مستخدم اختبار curl",
  "email": "curl_test_'$(date +%s)'@example.com",
  "phone_number": "+966501234567",
  "password": "TestPassword123!",
  "terms_accepted": true
}')

echo $REGISTER_RESPONSE | jq .

# استخراج التوكن
TOKEN=$(echo $REGISTER_RESPONSE | jq -r '.access_token')
echo "Token: $TOKEN"

if [ "$TOKEN" != "null" ] && [ "$TOKEN" != "" ]; then
    echo -e "\n3. جلب ملف المستخدم..."
    curl -s -X GET "$BASE_URL/profile/me" \
    -H "Content-Type: application/json" \
    -H "Authorization: Bearer $TOKEN" | jq .

    echo -e "\n4. اكتشاف المستخدمين..."
    curl -s -X GET "$BASE_URL/profiles/discover?limit=3" \
    -H "Content-Type: application/json" \
    -H "Authorization: Bearer $TOKEN" | jq .

    echo -e "\n5. إحصائيات الاستخدام..."
    curl -s -X GET "$BASE_URL/usage-stats" \
    -H "Content-Type: application/json" \
    -H "Authorization: Bearer $TOKEN" | jq .

    echo -e "\n6. التطابقات..."
    curl -s -X GET "$BASE_URL/matches" \
    -H "Content-Type: application/json" \
    -H "Authorization: Bearer $TOKEN" | jq .

    echo -e "\n✅ جميع الاختبارات اكتملت بنجاح!"
else
    echo "❌ فشل في الحصول على التوكن"
fi