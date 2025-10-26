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

// ---------------------------
// 🧠 تهيئة i18next الفعلية
import i18n from 'i18next';
import { initReactI18next } from 'react-i18next';
import LanguageDetector from 'i18next-browser-languagedetector';
import Backend from 'i18next-http-backend';

const SUPPORTED = ['ar','en','fr','es','de','tr','it','pt-BR','ru'];

function setHtmlDirLang(lng) {
  const lang = lng || 'en';
  const base = lang.split('-')[0];
  const dir = ['ar','fa','ur','he'].includes(base) ? 'rtl' : 'ltr';
  document.documentElement.dir = dir;
  document.documentElement.lang = lang;
}

i18n
  .use(Backend)              // تحميل JSON من /public/locales/{{lng}}/{{ns}}.json
  .use(LanguageDetector)     // يقرأ i18nextLng من localStorage أولاً
  .use(initReactI18next)
  .init({
    supportedLngs: SUPPORTED,
    fallbackLng: 'en',
    ns: ['common','auth','profile','chat','map','notifications','settings','premium','swipe','likes'],
    defaultNS: 'common',
    fallbackNS: 'common',
    keySeparator: false,     // استعمل ns:key بدل ns.key
    detection: {
      order: ['localStorage','querystring','cookie','navigator','htmlTag'],
      lookupLocalStorage: 'i18nextLng',
      caches: ['localStorage'],
    },
    backend: {
      loadPath: '/locales/{{lng}}/{{ns}}.json'
    },
    interpolation: { escapeValue: false },
    react: { useSuspense: true }
  });

i18n.on('initialized', () => setHtmlDirLang(i18n.language));
i18n.on('languageChanged', (lng) => {
  setHtmlDirLang(lng);
  try { localStorage.setItem('i18nextLng', lng); } catch(e){}
});

export default i18n;
