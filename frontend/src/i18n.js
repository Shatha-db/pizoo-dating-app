import i18n from 'i18next';
import { initReactI18next } from 'react-i18next';
import LanguageDetector from 'i18next-browser-languagedetector';
import Backend from 'i18next-http-backend';

const SUPPORTED = ['ar','en','fr','es','de','tr','it','pt-BR','ru'];

function setHtmlDirLang(lng) {
  const lang = lng || 'en';
  const dir = ['ar','fa','ur','he'].includes(lang.split('-')[0]) ? 'rtl' : 'ltr';
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
    ns: ['common','auth','profile','chat','map','notifications','settings','swipe'],
    defaultNS: 'common',
    fallbackNS: 'common',
    keySeparator: false,
    detection: {
      order: ['localStorage','querystring','cookie','navigator','htmlTag'],
      lookupLocalStorage: 'i18nextLng',
      caches: ['localStorage'],
    },
    backend: {
      loadPath: '/locales/{{lng}}/{{ns}}.json',
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
