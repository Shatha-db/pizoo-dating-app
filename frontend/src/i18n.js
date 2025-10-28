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
    ns: ['common', 'auth', 'profile', 'chat', 'map', 'notifications', 'settings', 'premium', 'likes', 'swipe', 'explore', 'personal'],
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
