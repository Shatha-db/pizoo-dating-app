import React from 'react';
import { useTranslation } from 'react-i18next';

const LANGUAGE_OPTIONS = [
  { code: 'en', label: 'English', flag: '🇬🇧' },
  { code: 'ar', label: 'العربية', flag: '🇸🇦' },
  { code: 'fr', label: 'Français', flag: '🇫🇷' },
  { code: 'es', label: 'Español', flag: '🇪🇸' },
  { code: 'de', label: 'Deutsch', flag: '🇩🇪' },
  { code: 'tr', label: 'Türkçe', flag: '🇹🇷' },
  { code: 'it', label: 'Italiano', flag: '🇮🇹' },
  { code: 'pt-BR', label: 'Português', flag: '🇧🇷' },
  { code: 'ru', label: 'Русский', flag: '🇷🇺' },
];

/**
 * Language Selector Component
 * Changes app language and syncs with backend
 */
export default function LanguageSelector({ variant = 'default' }) {
  const { i18n } = useTranslation();

  const changeLanguage = async (lng) => {
    try {
      // Change i18n language
      await i18n.changeLanguage(lng);
      
      // Save to localStorage
      localStorage.setItem('i18nextLng', lng);
      
      // Sync with backend
      const token = localStorage.getItem('token');
      if (token) {
        await fetch(`${process.env.REACT_APP_BACKEND_URL || ''}/api/user/language`, {
          method: 'PUT',
          credentials: 'include',
          headers: {
            'Content-Type': 'application/json',
            'Authorization': `Bearer ${token}`
          },
          body: JSON.stringify({ language: lng })
        });
      }
    } catch (error) {
      console.error('Failed to change language:', error);
    }
  };

  if (variant === 'compact') {
    // Compact dropdown for headers
    return (
      <select
        value={i18n.language}
        onChange={(e) => changeLanguage(e.target.value)}
        className="bg-white/10 backdrop-blur-sm text-white border border-white/20 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-white/50 cursor-pointer"
      >
        {LANGUAGE_OPTIONS.map((opt) => (
          <option key={opt.code} value={opt.code} className="bg-gray-800 text-white">
            {opt.flag} {opt.label}
          </option>
        ))}
      </select>
    );
  }

  // Default variant with more styling
  return (
    <div className="relative">
      <select
        value={i18n.language}
        onChange={(e) => changeLanguage(e.target.value)}
        className="appearance-none bg-white border border-gray-300 rounded-md px-4 py-2 pr-10 text-sm font-medium text-gray-700 hover:border-gray-400 focus:outline-none focus:ring-2 focus:ring-pink-500 focus:border-transparent cursor-pointer transition-all"
      >
        {LANGUAGE_OPTIONS.map((opt) => (
          <option key={opt.code} value={opt.code}>
            {opt.flag} {opt.label}
          </option>
        ))}
      </select>
      <div className="pointer-events-none absolute inset-y-0 right-0 flex items-center px-2 text-gray-700">
        <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" />
        </svg>
      </div>
    </div>
  );
}
