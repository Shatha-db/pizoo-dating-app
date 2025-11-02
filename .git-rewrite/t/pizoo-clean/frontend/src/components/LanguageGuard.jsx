import { useEffect } from 'react';
import { useTranslation } from 'react-i18next';
import axios from 'axios';

const API = process.env.REACT_APP_BACKEND_URL || '';

/**
 * LanguageGuard: Ensures user's preferred language is loaded and applied
 * This component runs on every page load to sync language from backend
 */
export default function LanguageGuard({ children }) {
  const { i18n } = useTranslation();

  useEffect(() => {
    const syncLanguage = async () => {
      try {
        // 1. Check localStorage first (fastest)
        const localLang = localStorage.getItem('i18nextLng');
        
        // 2. Check if user is logged in and fetch from backend
        const token = localStorage.getItem('token');
        if (token) {
          try {
            const response = await axios.get(`${API}/api/me`, {
              headers: { Authorization: `Bearer ${token}` }
            });
            
            const backendLang = response.data?.language || response.data?.user?.language;
            
            if (backendLang && backendLang !== i18n.language) {
              // Backend language takes precedence
              await i18n.changeLanguage(backendLang);
              localStorage.setItem('i18nextLng', backendLang);
              console.log('✅ Language synced from backend:', backendLang);
            } else if (localLang && localLang !== i18n.language) {
              // Use localStorage if backend doesn't have it
              await i18n.changeLanguage(localLang);
              console.log('✅ Language loaded from localStorage:', localLang);
            }
          } catch (err) {
            // If backend call fails, use localStorage
            if (localLang && localLang !== i18n.language) {
              await i18n.changeLanguage(localLang);
              console.log('✅ Language loaded from localStorage (backend failed):', localLang);
            }
          }
        } else {
          // Not logged in - use localStorage or default
          if (localLang && localLang !== i18n.language) {
            await i18n.changeLanguage(localLang);
            console.log('✅ Language loaded from localStorage (not logged in):', localLang);
          }
        }
      } catch (error) {
        console.error('Language sync error:', error);
      }
    };

    syncLanguage();
  }, []); // Run once on mount

  // Also listen to language changes
  useEffect(() => {
    const handleLanguageChange = (lng) => {
      // Update HTML attributes for RTL/LTR
      const rtlLanguages = ['ar', 'he', 'fa', 'ur'];
      document.documentElement.dir = rtlLanguages.includes(lng) ? 'rtl' : 'ltr';
      document.documentElement.lang = lng;
      console.log('✅ Language changed to:', lng, 'Dir:', document.documentElement.dir);
    };

    i18n.on('languageChanged', handleLanguageChange);

    // Set initial HTML attributes
    handleLanguageChange(i18n.language);

    return () => {
      i18n.off('languageChanged', handleLanguageChange);
    };
  }, [i18n]);

  return children;
}
