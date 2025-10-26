import i18n from 'i18next';
import { initReactI18next } from 'react-i18next';
import LanguageDetector from 'i18next-browser-languagedetector';
import Backend from 'i18next-http-backend';

// Supported languages - 9 languages total
const SUPPORTED = ['ar', 'en', 'fr', 'es', 'de', 'tr', 'it', 'pt-BR', 'ru'];

/**
 * Sets HTML dir and lang attributes based on language
 * RTL for: Arabic, Farsi, Urdu, Hebrew
 * LTR for: all others
 */
function setHtmlDirLang(lng) {
  const lang = lng || 'en';
  const dir = ['ar', 'fa', 'ur', 'he'].includes(lang.split('-')[0]) ? 'rtl' : 'ltr';
  document.documentElement.dir = dir;
  document.documentElement.lang = lang;
}

i18n
  .use(Backend)
  .use(LanguageDetector)
  .use(initReactI18next)
  .init({
    supportedLngs: SUPPORTED,
    fallbackLng: 'en',
    
    // All namespaces (10 total)
    ns: ['common', 'auth', 'profile', 'chat', 'map', 'notifications', 'settings', 'swipe', 'likes', 'premium'],
    defaultNS: 'common',
    fallbackNS: 'common',
    
    // Prevent dot notation interpretation - use explicit namespace:key
    keySeparator: false,
    
    // Detection configuration
    detection: {
      // Priority: localStorage > querystring > cookie > navigator > htmlTag
      order: ['localStorage', 'querystring', 'cookie', 'navigator', 'htmlTag'],
      lookupLocalStorage: 'i18nextLng',
      caches: ['localStorage'],
    },
    
    // Backend configuration for lazy loading
    backend: {
      loadPath: '/locales/{{lng}}/{{ns}}.json',
    },
    
    // React configuration
    interpolation: { escapeValue: false },
    react: { useSuspense: true }
  });

// Set HTML attributes on initialization
i18n.on('initialized', () => setHtmlDirLang(i18n.language));

// Update HTML attributes and localStorage on language change
i18n.on('languageChanged', (lng) => {
  setHtmlDirLang(lng);
  try {
    localStorage.setItem('i18nextLng', lng);
  } catch (e) {
    console.warn('Failed to save language to localStorage:', e);
  }
});

export default i18n;
