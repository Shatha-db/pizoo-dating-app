// ✅ إعداد اتجاه الصفحة ولغة <html> قبل تحميل i18n
const savedLang = (
  typeof localStorage !== 'undefined' && localStorage.getItem('i18nextLng')
) || null;

if (savedLang) {
  const baseLang = savedLang.split('-')[0];
  const isRTL = ['ar', 'fa', 'ur', 'he'].includes(baseLang);
  document.documentElement.dir = isRTL ? 'rtl' : 'ltr';
  document.documentElement.lang = savedLang;
} else {
  document.documentElement.dir = 'ltr';
  document.documentElement.lang = 'en';
}

// --------------------------------------
// 🔧 إعداد i18n configuration
// --------------------------------------
import i18n from 'i18next';
import { initReactI18next } from 'react-i18next';
import LanguageDetector from 'i18next-browser-languagedetector';
import Backend from 'i18next-http-backend';

i18n
  .use(Backend)              // تحميل JSON من /public/locales/{{lng}}/{{ns}}.json
  .use(LanguageDetector)     // يقرأ i18nextLng من localStorage أولاً
  .use(initReactI18next)
  .init({
    fallbackLng: 'en',
    supportedLngs: ['ar', 'en', 'fr', 'es', 'de', 'tr', 'it', 'pt-BR', 'ru'],
    ns: ['common', 'auth', 'profile', 'chat', 'map', 'notifications', 'settings', 'swipe', 'likes', 'premium'],
    defaultNS: 'common',
    fallbackNS: 'common',
    keySeparator: false,
    backend: {
      loadPath: '/locales/{{lng}}/{{ns}}.json'
    },
    detection: {
      order: ['localStorage', 'navigator'],
      lookupLocalStorage: 'i18nextLng',
      caches: ['localStorage']
    },
    interpolation: {
      escapeValue: false
    },
    react: {
      useSuspense: true
    }
  });

export default i18n;
