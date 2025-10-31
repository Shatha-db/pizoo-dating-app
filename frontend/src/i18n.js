import i18n from "i18next";
import { initReactI18next } from "react-i18next";
import LanguageDetector from "i18next-browser-languagedetector";
import Backend from "i18next-http-backend";

const SUPPORTED = ["en","ar","fr","es","de","tr","it","pt-BR","ru"];

function setHtml(lng){
  const lang = (lng || "en").split("-")[0];
  const dir  = ["ar","fa","ur","he"].includes(lang) ? "rtl" : "ltr";
  document.documentElement.setAttribute("dir", dir);
  document.documentElement.setAttribute("lang", lng || "en");
  document.documentElement.classList.toggle("rtl", dir==="rtl");
}

try {
  if (typeof localStorage!=="undefined" && !localStorage.getItem("i18nextLng")){
    localStorage.setItem("i18nextLng","en");
  }
} catch { /* ignore */ }

i18n
 .use(Backend)
 .use(LanguageDetector)
 .use(initReactI18next)
 .init({
    supportedLngs: SUPPORTED,
    fallbackLng: "en",
    ns: ["common","auth","profile","chat","map","notifications","settings","likes","explore","personal","home","premium","editProfile","swipe","terms","privacy","cookies","doubledating","discover"],
    defaultNS: "common",
    keySeparator: false,
    interpolation: { escapeValue: false },
    detection: {
      order: ["localStorage","querystring","cookie","htmlTag","navigator"],
      lookupLocalStorage: "i18nextLng",
      caches: ["localStorage"]
    },
    backend: { loadPath: "/locales/{{lng}}/{{ns}}.json" },
    react: { useSuspense: false }
 });

setHtml(i18n.resolvedLanguage || "en");
i18n.on("languageChanged", (lng) => {
  try { localStorage.setItem("i18nextLng", lng); } catch {}
  setHtml(lng);
});

export default i18n;
