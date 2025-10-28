import i18n from "i18next";
import { initReactI18next } from "react-i18next";
import LanguageDetector from "i18next-browser-languagedetector";
import Backend from "i18next-http-backend";

const SUPPORTED = ["en","ar","fr","es","de","tr","it","pt-BR","ru"];

const setHtml = (lng) => {
  const base = (lng || 'en').split('-')[0];
  const dir = ['ar','fa','ur','he'].includes(base)?'rtl':'ltr';
  document.documentElement.dir = dir;
  document.documentElement.lang = lng || 'en';
  document.documentElement.classList.toggle("rtl", dir==='rtl');
};

try {
  if (typeof localStorage!=='undefined' && !localStorage.getItem('i18nextLng')){
    localStorage.setItem('i18nextLng','en');
  }
} catch {}

const saved = (typeof localStorage!=='undefined' && localStorage.getItem('i18nextLng')) || 'en';
setHtml(saved);

i18n
  .use(Backend)
  .use(LanguageDetector)
  .use(initReactI18next)
  .init({
    supportedLngs: SUPPORTED,
    fallbackLng: "en",
    detection: {
      order: ['localStorage','querystring','cookie','htmlTag','navigator'],
      lookupLocalStorage: 'i18nextLng',
      caches: ['localStorage']
    },
    backend: { loadPath: "/locales/{{lng}}/{{ns}}.json" },
    ns: ["common","auth","profile","chat","map","notifications","settings","premium","likes","explore","personal"],
    defaultNS: "common",
    keySeparator: false,
    interpolation: { escapeValue: false },
    react: { useSuspense: false }
  });

i18n.on('initialized',()=>setHtml(i18n.language));
i18n.on('languageChanged',(lng)=>{ setHtml(lng); try{ localStorage.setItem('i18nextLng',lng);}catch{} });

export default i18n;
