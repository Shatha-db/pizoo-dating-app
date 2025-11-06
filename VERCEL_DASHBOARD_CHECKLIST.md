# ✅ Vercel Dashboard Checklist - للمراجعة اليدوية

**للمستخدم: راجع هذه الإعدادات في Vercel Dashboard**

---

## 🎯 الهدف:
التأكد من أن Vercel متصل بالمصدر الصحيح وينشر آخر نسخة من `main`

---

## 📋 Checklist (للمراجعة في Dashboard):

### 1️⃣ Project Settings → General

**Connected Git Repository:**
- [ ] Repository: `Shatha-db/pizoo-dating-app` ✅
- [ ] Branch: `main` ✅
- [ ] إذا كان مختلف، اضغط "Disconnect" ثم "Reconnect"

---

### 2️⃣ Project Settings → Git

**Production Branch:**
- [ ] Production Branch: `main` ✅
- [ ] ليس `master` أو أي branch آخر

**Connected Repository:**
- [ ] يظهر: `Shatha-db/pizoo-dating-app`
- [ ] Status: Connected ✅

**إذا وجدت repo قديم:**
1. اضغط "Disconnect"
2. اضغط "Connect Git Repository"
3. اختر `Shatha-db/pizoo-dating-app`
4. اختر branch `main`

---

### 3️⃣ Project Settings → Deploy Hooks

**Deploy Hooks الموجودة:**
- [ ] Hook واحد فقط باسم "Production Main"
- [ ] Branch: `main`
- [ ] URL ينتهي بـ: `2im8oZHyQW`

**إذا وجدت hooks قديمة:**
1. احذف جميع الـ hooks القديمة (اضغط Delete)
2. أضف Hook جديد:
   - Name: `Production Main`
   - Branch: `main`
   - (URL سيتم توليده تلقائياً)

---

### 4️⃣ Project Settings → Domains

**Domains المربوطة:**
- [ ] `pizoo.ch` → Status: Valid Configuration ✅
- [ ] `www.pizoo.ch` → Status: Valid Configuration ✅
- [ ] `pizoo.vercel.app` → Default (automatic)

**DNS Records (للمرجعية):**
```
pizoo.ch → A → 216.198.79.1
www.pizoo.ch → CNAME → 44589a4b7c4c7957.vercel-dns-017.com
```

**إذا وجدت "Invalid Configuration":**
1. اضغط على Domain
2. اتبع التعليمات لتصحيح DNS
3. انتظر 5-60 دقيقة للتحديث

---

### 5️⃣ Project Settings → Environment Variables

**Production Environment Variables:**
- [ ] `REACT_APP_BACKEND_URL` = `https://datemaps.emergent.host`
- [ ] أي متغيرات أخرى مطلوبة

**إذا كانت مفقودة:**
1. اضغط "Add Variable"
2. Name: `REACT_APP_BACKEND_URL`
3. Value: `https://datemaps.emergent.host`
4. Environment: Production ✅
5. اضغط "Save"
6. **مهم:** Redeploy بعد إضافة متغيرات!

---

### 6️⃣ Project Settings → Build & Development Settings

**Root Directory:**
- [ ] Root Directory: (فارغ أو `.`) ✅

**Framework Preset:**
- [ ] Framework: `Create React App` ✅

**Build Command:**
- [ ] فارغ (override in vercel.json) ✅
- أو: `cd frontend && yarn build`

**Output Directory:**
- [ ] فارغ (override in vercel.json) ✅
- أو: `frontend/build`

**Install Command:**
- [ ] فارغ (override in vercel.json) ✅
- أو: `cd frontend && yarn install`

---

### 7️⃣ Project Settings → Ignored Build Step

**Setting:**
- [ ] `Automatic (Recommended)` ✅

**أو Custom Script:**
```bash
#!/bin/bash
if [ "$VERCEL_GIT_COMMIT_REF" != "main" ]; then
  exit 0
fi
exit 1
```

---

### 8️⃣ Deployments Tab

**آخر Deployment:**
- [ ] Status: `Ready` ✅
- [ ] Branch: `main` ✅
- [ ] Commit: يظهر آخر commit hash
- [ ] Duration: 1-3 minutes
- [ ] Timestamp: حديث (آخر deploy)

**إذا Status = "Failed":**
1. اضغط على Deployment
2. افحص Build Logs
3. ابحث عن الخطأ
4. أصلح المشكلة
5. اضغط "Redeploy"

---

### 9️⃣ تحذيرات يجب حذفها:

**ابحث عن:**
- [ ] ❌ أي مشروع Vercel آخر ينشر نفس Domain
- [ ] ❌ Deploy Hooks قديمة متعددة
- [ ] ❌ Connected Git Repository قديم
- [ ] ❌ Environment Variables مكررة أو قديمة

**احذف:**
1. مشاريع Vercel قديمة (إن وجدت)
2. Deploy Hooks قديمة
3. Disconnect أي repo قديم

---

## 🔄 إعادة Deploy (إذا لزم):

### من Deployments Tab:
1. افتح آخر deployment
2. اضغط زر **"Redeploy"** (ثلاث نقاط)
3. اختر "Use existing Build Cache" (أسرع)
   أو "Redeploy without Cache" (أنظف)
4. اضغط "Redeploy"
5. انتظر 2-4 دقائق

---

## ✅ التحقق النهائي:

### بعد أي تغيير:

**افتح في المتصفح:**
1. https://pizoo.ch
2. https://www.pizoo.ch
3. https://pizoo.ch/login
4. https://pizoo.ch/register

**تأكد من:**
- [ ] الصفحة تفتح بدون 404
- [ ] اللوجوهات تظهر (Classic Orange خارجي، Golden داخلي)
- [ ] التصميم محدث
- [ ] لا يوجد أخطاء في Console

---

## 📸 Screenshot للتوثيق:

**من Vercel Dashboard:**

### Deployments → Production:
اضغط على آخر deployment واحفظ screenshot يظهر:
- ✅ Status: Ready
- ✅ Branch: main
- ✅ Commit SHA (آخر commit)
- ✅ Timestamp
- ✅ Duration

### Project Settings → Overview:
احفظ screenshot يظهر:
- ✅ Connected Git Repository
- ✅ Production Branch
- ✅ Framework Preset
- ✅ Domains

---

## 🆘 إذا واجهت مشاكل:

### 1. Domain لا يعمل (404):
- راجع DNS records
- تأكد من Valid Configuration
- انتظر 5-60 دقيقة

### 2. Build يفشل:
- افحص Build Logs
- تأكد من vercel.json صحيح
- تأكد من Environment Variables

### 3. النسخة القديمة لا تزال تظهر:
- Clear browser cache (Ctrl+Shift+R)
- تأكد من آخر deployment = Ready
- Redeploy مرة أخرى

### 4. React Routes تعطي 404:
- تأكد من frontend/vercel.json موجود
- تأكد من rewrites صحيح
- Redeploy

---

## ✅ بعد المراجعة:

**إذا كل شيء صحيح:**
- [x] Connected to correct repo ✅
- [x] Branch = main ✅
- [x] Deploy Hook صحيح ✅
- [x] Domains working ✅
- [x] Latest deployment = Ready ✅

**يمكنك الآن:**
- Push أي تحديث لـ main
- سيتم النشر تلقائياً في 2-4 دقائق
- لا حاجة لتدخل يدوي

---

**🎉 Vercel Dashboard الآن معد بشكل صحيح!**

**راجع هذه القائمة كل فترة للتأكد من عدم وجود تغييرات غير مرغوبة.**
