// ✅ إعداد اتجاه الصفحة ولغة <html> قبل تحميل i18n
const savedLang = (
  typeof localStorage !== 'undefined' && localStorage.getItem('i18nextLng')
) || null;

if (savedLang) {
  const baseLang = savedLang.split('-')[0]; // مثال: "ar-EG" → "ar"
  const isRTL = ['ar', 'fa', 'ur', 'he'].includes(baseLang);
  document.documentElement.dir = isRTL ? 'rtl' : 'ltr';
  document.documentElement.lang = savedLang;
} else {
  // 🔹 في حال لا يوجد لغة محفوظة، استخدم الاتجاه الافتراضي LTR
  document.documentElement.dir = 'ltr';
  document.documentElement.lang = 'en';
}
