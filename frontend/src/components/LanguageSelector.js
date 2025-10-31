import React from 'react';
import { useTranslation } from 'react-i18next';
import axios from 'axios';

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;

const LANGUAGES = [
  { code: 'ar', name: 'العربية', flag: '🇸🇦', rtl: true },
  { code: 'en', name: 'English', flag: '🇬🇧', rtl: false },
  { code: 'fr', name: 'Français', flag: '🇫🇷', rtl: false },
  { code: 'es', name: 'Español', flag: '🇪🇸', rtl: false },
  { code: 'de', name: 'Deutsch', flag: '🇩🇪', rtl: false },
  { code: 'tr', name: 'Türkçe', flag: '🇹🇷', rtl: false },
  { code: 'it', name: 'Italiano', flag: '🇮🇹', rtl: false },
  { code: 'pt-BR', name: 'Português (BR)', flag: '🇧🇷', rtl: false },
  { code: 'ru', name: 'Русский', flag: '🇷🇺', rtl: false }
];

const LanguageSelector = ({ token, compact = false }) => {
  const { i18n } = useTranslation();

  const changeLanguage = async (lng) => {
    try {
      // Change language in i18next
      await i18n.changeLanguage(lng);
      
      // Save to localStorage
      localStorage.setItem('preferred_language', lng);
      
      // Update document direction for RTL/LTR
      const langConfig = LANGUAGES.find(l => l.code === lng);
      document.documentElement.dir = langConfig?.rtl ? 'rtl' : 'ltr';
      document.documentElement.lang = lng;
      
      // Update in backend if token available
      if (token) {
        try {
          await axios.put(
            `${BACKEND_URL}/api/user/language`,
            { language: lng },
            { headers: { Authorization: `Bearer ${token}` } }
          );
        } catch (error) {
          console.log('Could not sync language to backend:', error.message);
        }
      }
      
      console.log(`✅ Language changed to: ${lng}`);
    } catch (error) {
      console.error('Error changing language:', error);
    }
  };

  if (compact) {
    return (
      <select
        value={i18n.language}
        onChange={(e) => changeLanguage(e.target.value)}
        className="p-2 border rounded-lg bg-white dark:bg-gray-800"
      >
        {LANGUAGES.map((lang) => (
          <option key={lang.code} value={lang.code}>
            {lang.flag} {lang.name}
          </option>
        ))}
      </select>
    );
  }

  return (
    <div className="space-y-2">
      {LANGUAGES.map((lang) => (
        <button
          key={lang.code}
          onClick={() => changeLanguage(lang.code)}
          className={`w-full p-4 rounded-lg flex items-center justify-between transition-all ${
            lang.rtl ? 'text-right' : 'text-left'
          } ${
            i18n.language === lang.code || i18n.language.startsWith(lang.code)
              ? 'bg-gradient-to-r from-pink-500 to-red-500 text-white shadow-lg' 
              : 'bg-gray-100 hover:bg-gray-200 dark:bg-gray-700 dark:hover:bg-gray-600'
          }`}
        >
          <span className="font-medium">
            {lang.flag} {lang.name}
          </span>
          {(i18n.language === lang.code || i18n.language.startsWith(lang.code)) && (
            <div className="w-6 h-6 bg-white rounded-full flex items-center justify-center">
              <span className="text-pink-500 text-xl">✓</span>
            </div>
          )}
        </button>
      ))}
    </div>
  );
};

export default LanguageSelector;
export { LANGUAGES };
