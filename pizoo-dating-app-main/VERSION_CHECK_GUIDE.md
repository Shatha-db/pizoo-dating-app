# ✅ كيف تتأكد أنك على آخر نسخة من Pizoo

## للمستخدمين / For Users

### 🔍 التحقق من النسخة الحالية / Check Current Version

**الطريقة 1: من المتصفح**
1. افتح Pizoo في المتصفح
2. اضغط F12 (أو انقر بالزر الأيمن واختر "فحص")
3. اذهب إلى تبويب "Console"
4. اكتب: `localStorage.getItem('app_version')`
5. يجب أن ترى: **"2.3.0"**

**Method 1: From Browser**
1. Open Pizoo in browser
2. Press F12 (or right-click and select "Inspect")
3. Go to "Console" tab
4. Type: `localStorage.getItem('app_version')`
5. You should see: **"2.3.0"**

---

### 🔄 إذا كنت على نسخة قديمة / If You're on Old Version

#### الخيار الأول: صفحة التحديث التلقائي
**اضغط على هذا الرابط:**
```
https://multilingual-date.preview.emergentagent.com/force-update.html
```

**ماذا سيحدث؟**
- ستفتح صفحة جميلة بعنوان "نسخة جديدة متوفرة!"
- اضغط على زر "تحديث الآن"
- سيتم مسح الذاكرة المؤقتة تلقائياً
- سيعيد فتح التطبيق بآخر نسخة

#### Option 1: Auto-Update Page
**Click this link:**
```
https://multilingual-date.preview.emergentagent.com/force-update.html
```

**What will happen?**
- A beautiful page will open saying "New Version Available!"
- Click "Update Now" button
- Cache will be cleared automatically
- App will reopen with latest version

---

#### الخيار الثاني: مسح الذاكرة المؤقتة يدوياً

**لمتصفح Chrome / Edge:**
1. اضغط Ctrl + Shift + Delete (Windows) أو Cmd + Shift + Delete (Mac)
2. اختر "الصور والملفات المخزنة مؤقتًا"
3. اضغط "مسح البيانات"
4. أعد فتح Pizoo

**لمتصفح Safari (Mac):**
1. اضغط Cmd + Option + E
2. سيتم مسح الذاكرة المؤقتة فوراً
3. أعد فتح Pizoo

**لمتصفح Firefox:**
1. اضغط Ctrl + Shift + Delete
2. اختر "ذاكرة التخزين المؤقت"
3. اضغط "مسح الآن"
4. أعد فتح Pizoo

#### Option 2: Clear Cache Manually

**For Chrome / Edge:**
1. Press Ctrl + Shift + Delete (Windows) or Cmd + Shift + Delete (Mac)
2. Select "Cached images and files"
3. Click "Clear data"
4. Reopen Pizoo

**For Safari (Mac):**
1. Press Cmd + Option + E
2. Cache will be cleared immediately
3. Reopen Pizoo

**For Firefox:**
1. Press Ctrl + Shift + Delete
2. Select "Cache"
3. Click "Clear Now"
4. Reopen Pizoo

---

#### الخيار الثالث: إعادة التحميل الكامل
**طريقة سريعة:**
1. افتح Pizoo
2. اضغط Ctrl + F5 (Windows) أو Cmd + Shift + R (Mac)
3. سيتم تجاوز الذاكرة المؤقتة وتحميل آخر نسخة

#### Option 3: Hard Reload
**Quick method:**
1. Open Pizoo
2. Press Ctrl + F5 (Windows) or Cmd + Shift + R (Mac)
3. Cache will be bypassed and latest version will load

---

### ✨ مميزات النسخة الحالية 2.3.0 / Features in Version 2.3.0

✅ **نظام Premium Cards**
- بطاقات اشتراك Gold / Platinum / Plus
- تصميم gradient جميل
- أسعار واضحة

✅ **نظام Gating**
- 10 بطاقات مجانية يومياً
- تعتيم تلقائي بعد الحد
- رسالة ترقية واضحة

✅ **تحسينات i18n**
- دعم كامل لـ RTL/LTR
- 9 لغات
- ترجمات محدّثة

✅ **إصلاح مشكلة الشاشة البيضاء**
- React 18.3.1
- Lazy loading محسّن
- استقرار كامل

---

### 🆘 المساعدة / Help

**إذا واجهت مشاكل:**
- جرّب صفحة التحديث: `force-update.html`
- امسح الذاكرة المؤقتة يدوياً
- أعد تشغيل المتصفح
- جرّب متصفح آخر

**If you face issues:**
- Try update page: `force-update.html`
- Clear cache manually
- Restart browser
- Try another browser

---

### 📱 للأجهزة المحمولة / For Mobile Devices

**Android Chrome:**
1. الإعدادات → الخصوصية → مسح بيانات التصفح
2. اختر "الصور والملفات المخزنة"
3. امسح البيانات

**iOS Safari:**
1. الإعدادات → Safari → مسح السجل وبيانات المواقع
2. أكّد المسح

**Android Chrome:**
1. Settings → Privacy → Clear browsing data
2. Select "Cached images and files"
3. Clear data

**iOS Safari:**
1. Settings → Safari → Clear History and Website Data
2. Confirm clear

---

## 📊 للمطورين / For Developers

### How to Update Version

**Step 1: Edit version in index.html**
```javascript
// File: /app/frontend/public/index.html
const APP_VERSION = '2.4.0'; // Update this
```

**Step 2: Restart frontend**
```bash
sudo supervisorctl restart frontend
```

**Step 3: Verify**
```bash
# Check if frontend compiled
tail -n 10 /var/log/supervisor/frontend.out.log
```

**Step 4: Test**
- Open in incognito mode
- Check console for version message
- Verify localStorage has new version

### Version History

| Version | Date | Features |
|---------|------|----------|
| 2.3.0 | Oct 26, 2025 | Premium UI + Gating System |
| 2.2.0 | Oct 26, 2025 | React 18 downgrade + white screen fix |
| 2.1.0 | Oct 26, 2025 | i18n finalization + map fixes |
| 2.0.0 | Oct 25, 2025 | Initial stable release |

---

## ✅ Checklist

**قبل استخدام التطبيق / Before Using App:**
- [ ] تحقق من رقم النسخة (يجب أن تكون 2.3.0)
- [ ] جرّب تسجيل الدخول
- [ ] تأكد من ظهور بطاقات الاشتراك
- [ ] جرّب تغيير اللغة

**Before Using App:**
- [ ] Check version number (should be 2.3.0)
- [ ] Try logging in
- [ ] Verify subscription cards appear
- [ ] Try changing language

---

**آخر تحديث / Last Updated:** October 26, 2025  
**النسخة الحالية / Current Version:** 2.3.0  
**الحالة / Status:** ✅ مستقر / Stable
