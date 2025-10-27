import i18n from 'i18next';
import { initReactI18next } from 'react-i18next';
import LanguageDetector from 'i18next-browser-languagedetector';
import Backend from 'i18next-http-backend';

const SUPPORTED = ['en', 'ar', 'fr', 'es', 'de', 'tr', 'it', 'pt-BR', 'ru'];

function updateDir(lng = 'en') {
  const base = (lng || 'en').split('-')[0];
  const isRTL = ['ar', 'fa', 'ur', 'he'].includes(base);
  
  // Update HTML attributes
  document.documentElement.dir = isRTL ? 'rtl' : 'ltr';
  document.documentElement.lang = lng || 'en';
  
  // Update body class for Tailwind RTL support
  if (isRTL) {
    document.documentElement.classList.add('rtl');
    document.body.classList.add('rtl');
  } else {
    document.documentElement.classList.remove('rtl');
    document.body.classList.remove('rtl');
  }
  
  console.log(`✅ Language updated: ${lng}, Direction: ${isRTL ? 'RTL' : 'LTR'}`);
}

// First visit → save EN
try {
  if (typeof localStorage !== 'undefined' && !localStorage.getItem('i18nextLng')) {
    localStorage.setItem('i18nextLng', 'en');
  }
} catch {}

const saved = (typeof localStorage !== 'undefined' && localStorage.getItem('i18nextLng')) || 'en';
updateDir(saved);

i18n
  .use(Backend)
  .use(LanguageDetector)
  .use(initReactI18next)
  .init({
    supportedLngs: SUPPORTED,
    fallbackLng: 'en',
    ns: ['common', 'auth', 'profile', 'chat', 'map', 'notifications', 'settings', 'premium', 'likes', 'swipe'],
    defaultNS: 'common',
    keySeparator: false,
    load: 'languageOnly',
    detection: {
      order: ['localStorage', 'querystring', 'cookie', 'htmlTag', 'navigator'],
      lookupLocalStorage: 'i18nextLng',
      caches: ['localStorage']
    },
    backend: {
      loadPath: '/locales/{{lng}}/{{ns}}.json'
    },
    interpolation: { escapeValue: false },
    react: { useSuspense: false }
  });

// Update direction on language change
i18n.on('initialized', () => updateDir(i18n.language));
i18n.on('languageChanged', (lng) => {
  updateDir(lng);
  try {
    localStorage.setItem('i18nextLng', lng);
  } catch {}
});

export default i18n;
