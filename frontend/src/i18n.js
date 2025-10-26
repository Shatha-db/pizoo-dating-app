import i18n from 'i18next';
import { initReactI18next } from 'react-i18next';
import LanguageDetector from 'i18next-browser-languagedetector';
import Backend from 'i18next-http-backend';

i18n
  // Load translation using http backend
  .use(Backend)
  // Detect user language
  .use(LanguageDetector)
  // Pass the i18n instance to react-i18next
  .use(initReactI18next)
  // Init i18next
  .init({
    fallbackLng: 'en', // Default language is English
    debug: false,
    
    // Detection options
    detection: {
      order: ['localStorage', 'navigator', 'htmlTag', 'path', 'subdomain'],
      caches: ['localStorage'],
      lookupLocalStorage: 'preferred_language', // Match with Settings.js
    },
    
    interpolation: {
      escapeValue: false, // React already escapes values
    },
    
    backend: {
      loadPath: '/locales/{{lng}}/translation.json',
    },
    
    // Available languages (BCP-47 compliant)
    supportedLngs: ['en', 'ar', 'fr', 'es', 'de', 'tr', 'it', 'pt-BR', 'ru'],
    
    react: {
      useSuspense: true,
    },
  });

// Listen for language changes to update document direction
i18n.on('languageChanged', (lng) => {
  const rtlLanguages = ['ar', 'he', 'fa', 'ur'];
  document.documentElement.dir = rtlLanguages.includes(lng) ? 'rtl' : 'ltr';
  document.documentElement.lang = lng;
  
  // Also save to localStorage when changed
  localStorage.setItem('preferred_language', lng);
  
  console.log(`🌐 Language changed to: ${lng}, Direction: ${document.documentElement.dir}`);
});

export default i18n;
