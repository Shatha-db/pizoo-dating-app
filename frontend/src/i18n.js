import i18n from 'i18next';
import { initReactI18next } from 'react-i18next';
import LanguageDetector from 'i18next-browser-languagedetector';
import Backend from 'i18next-http-backend';

const SUPPORTED = ['en', 'ar', 'de', 'fr', 'es', 'tr', 'it', 'pt-BR', 'ru'];
const RTL_SET = ['ar', 'fa', 'ur', 'he'];

function setHtmlAttributes(lng = 'en') {
  const baseLanguage = (lng || 'en').split('-')[0];
  const dir = RTL_SET.includes(baseLanguage) ? 'rtl' : 'ltr';
  document.documentElement.dir = dir;
  document.documentElement.lang = lng;
  document.body.dir = dir;
}

// Set default language to English if not set
try {
  if (typeof localStorage !== 'undefined' && !localStorage.getItem('i18nextLng')) {
    localStorage.setItem('i18nextLng', 'en');
  }
} catch (e) {
  console.warn('localStorage not available:', e);
}

i18n
  .use(Backend)
  .use(LanguageDetector)
  .use(initReactI18next)
  .init({
    supportedLngs: SUPPORTED,
    fallbackLng: 'en',
    ns: ['common', 'auth', 'profile', 'chat', 'map', 'notifications', 'settings', 'premium', 'likes', 'swipe', 'explore', 'personal'],
    defaultNS: 'common',
    keySeparator: false,
    load: 'languageOnly',
    detection: {
      order: ['localStorage', 'querystring', 'cookie', 'navigator', 'htmlTag'],
      caches: ['localStorage'],
      lookupQuerystring: 'lng',
      lookupCookie: 'i18next',
      lookupLocalStorage: 'i18nextLng',
    },
    backend: {
      loadPath: '/locales/{{lng}}/{{ns}}.json'
    },
    interpolation: { escapeValue: false },
    react: { useSuspense: false }
  });

// Set HTML attributes on initial load
setHtmlAttributes(i18n.resolvedLanguage || 'en');

// Update HTML attributes when language changes
i18n.on('languageChanged', (lng) => {
  setHtmlAttributes(lng);
  try {
    localStorage.setItem('i18nextLng', lng);
  } catch (e) {
    console.warn('Could not save language to localStorage:', e);
  }
});

export default i18n;
