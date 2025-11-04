import { useEffect } from 'react';
import { useTranslation } from 'react-i18next';

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;

export default function LanguageBootstrap() {
  const { i18n } = useTranslation();
  
  useEffect(() => {
    let aborted = false;
    
    (async () => {
      try {
        const token = localStorage.getItem('token');
        if (!token) return;
        
        const r = await fetch(`${BACKEND_URL}/api/me`, {
          credentials: 'include',
          headers: { Authorization: `Bearer ${token}` }
        });
        
        if (!r.ok) return;
        
        const me = await r.json();
        const lng = me?.language || localStorage.getItem('i18nextLng') || 'en';
        
        if (!aborted && lng && i18n.language !== lng) {
          await i18n.changeLanguage(lng);
          console.log('✅ Language bootstrapped from backend:', lng);
        }
      } catch (e) {
        console.warn('Language bootstrap failed:', e);
      }
    })();
    
    return () => {
      aborted = true;
    };
  // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);
  
  return null;
}
