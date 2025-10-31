import React, { useState } from 'react';
import { useTranslation } from 'react-i18next';
import { Globe, Check } from 'lucide-react';
import { Card } from './ui/card';
import { Button } from './ui/button';

// Enhanced Language List with more languages
const LANGUAGES = [
  { code: 'ar', name: 'العربية', nativeName: 'Arabic', flag: '🇸🇦', rtl: true },
  { code: 'en', name: 'English', nativeName: 'English', flag: '🇬🇧', rtl: false },
  { code: 'fr', name: 'Français', nativeName: 'French', flag: '🇫🇷', rtl: false },
  { code: 'es', name: 'Español', nativeName: 'Spanish', flag: '🇪🇸', rtl: false },
  { code: 'de', name: 'Deutsch', nativeName: 'German', flag: '🇩🇪', rtl: false },
  { code: 'tr', name: 'Türkçe', nativeName: 'Turkish', flag: '🇹🇷', rtl: false },
  { code: 'it', name: 'Italiano', nativeName: 'Italian', flag: '🇮🇹', rtl: false },
  { code: 'pt-BR', name: 'Português', nativeName: 'Portuguese (BR)', flag: '🇧🇷', rtl: false },
  { code: 'ru', name: 'Русский', nativeName: 'Russian', flag: '🇷🇺', rtl: false },
  { code: 'zh', name: '中文', nativeName: 'Chinese', flag: '🇨🇳', rtl: false },
  { code: 'ja', name: '日本語', nativeName: 'Japanese', flag: '🇯🇵', rtl: false },
  { code: 'ko', name: '한국어', nativeName: 'Korean', flag: '🇰🇷', rtl: false },
  { code: 'hi', name: 'हिन्दी', nativeName: 'Hindi', flag: '🇮🇳', rtl: false },
  { code: 'ur', name: 'اردو', nativeName: 'Urdu', flag: '🇵🇰', rtl: true },
];

const ImprovedLanguageSelector = ({ onLanguageChange, currentLanguage }) => {
  const { t, i18n } = useTranslation(['settings', 'common']);
  const [isOpen, setIsOpen] = useState(false);
  const [selectedLang, setSelectedLang] = useState(currentLanguage || i18n.language);

  const handleLanguageSelect = async (langCode) => {
    try {
      // Change language
      await i18n.changeLanguage(langCode);
      setSelectedLang(langCode);
      
      // Update backend
      if (onLanguageChange) {
        await onLanguageChange(langCode);
      }
      
      // Update HTML attributes
      const rtlLanguages = ['ar', 'he', 'fa', 'ur'];
      document.documentElement.dir = rtlLanguages.includes(langCode) ? 'rtl' : 'ltr';
      document.documentElement.lang = langCode;
      
      setIsOpen(false);
    } catch (error) {
      console.error('Language change error:', error);
    }
  };

  const currentLangData = LANGUAGES.find(l => l.code === selectedLang) || LANGUAGES[0];

  return (
    <div className="space-y-4">
      {/* Current Language Display */}
      <div 
        onClick={() => setIsOpen(!isOpen)}
        className="flex items-center justify-between p-4 bg-white dark:bg-gray-800 rounded-xl border border-gray-200 dark:border-gray-700 cursor-pointer hover:shadow-md transition-all"
      >
        <div className="flex items-center gap-3">
          <div className="w-10 h-10 bg-gradient-to-br from-pink-500 to-purple-500 rounded-full flex items-center justify-center">
            <Globe className="w-5 h-5 text-white" />
          </div>
          <div>
            <p className="text-xs text-gray-500 dark:text-gray-400">
              {t('app_language', { ns: 'settings' })}
            </p>
            <p className="font-semibold text-gray-900 dark:text-white">
              {currentLangData.flag} {currentLangData.name}
            </p>
          </div>
        </div>
        <div className={`transform transition-transform ${isOpen ? 'rotate-180' : ''}`}>
          <svg className="w-5 h-5 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" />
          </svg>
        </div>
      </div>

      {/* Language List */}
      {isOpen && (
        <Card className="border border-gray-200 dark:border-gray-700 overflow-hidden animate-slide-down">
          <div className="p-2 max-h-96 overflow-y-auto">
            {LANGUAGES.map((lang) => (
              <button
                key={lang.code}
                onClick={() => handleLanguageSelect(lang.code)}
                className={`w-full flex items-center justify-between p-3 rounded-lg transition-colors ${
                  selectedLang === lang.code
                    ? 'bg-pink-50 dark:bg-pink-900/20 border border-pink-200 dark:border-pink-800'
                    : 'hover:bg-gray-50 dark:hover:bg-gray-800'
                }`}
              >
                <div className="flex items-center gap-3">
                  <span className="text-2xl">{lang.flag}</span>
                  <div className="text-left">
                    <p className={`font-medium ${
                      selectedLang === lang.code 
                        ? 'text-pink-600 dark:text-pink-400' 
                        : 'text-gray-900 dark:text-white'
                    }`}>
                      {lang.name}
                    </p>
                    <p className="text-xs text-gray-500 dark:text-gray-400">
                      {lang.nativeName}
                    </p>
                  </div>
                </div>
                {selectedLang === lang.code && (
                  <Check className="w-5 h-5 text-pink-600 dark:text-pink-400" />
                )}
              </button>
            ))}
          </div>
        </Card>
      )}
    </div>
  );
};

export default ImprovedLanguageSelector;
