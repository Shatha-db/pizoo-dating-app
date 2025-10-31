import React from 'react';
import { useTranslation } from 'react-i18next';

export default function SafetyConsentModal({ open, onAccept, onClose }) {
  const { t } = useTranslation(['chat']);
  if (!open) return null;
  
  const accept = async () => {
    try {
      localStorage.setItem('pizoo_safety_accepted', '1');
      await fetch(`${process.env.REACT_APP_BACKEND_URL}/api/user/settings`, {
        method: 'PUT',
        headers: { 'Content-Type': 'application/json' },
        credentials: 'include',
        body: JSON.stringify({ safetyAccepted: true })
      }).catch(() => {});
      onAccept?.();
    } finally {
      onClose?.();
    }
  };
  
  return (
    <div className="fixed inset-0 z-50 bg-black/50 grid place-items-center" onClick={onClose}>
      <div 
        className="bg-white rounded-2xl p-5 w-[92%] max-w-md text-center"
        onClick={(e) => e.stopPropagation()}
      >
        <div className="text-2xl font-bold mb-2">{t('safety_first')}</div>
        <p className="text-gray-600 mb-4 text-sm leading-relaxed">
          {t('safety_message_1')}
          {' '}
          {t('safety_message_2')}
        </p>
        <div className="flex gap-2">
          <button 
            className="flex-1 h-11 rounded-full bg-gray-200 text-gray-700 hover:bg-gray-300 transition-colors"
            onClick={onClose}
          >
            {t('dont_send')}
          </button>
          <button 
            className="flex-1 h-11 rounded-full text-white bg-gradient-to-r from-pink-500 to-orange-500 hover:brightness-110 transition-all"
            onClick={accept}
          >
            {t('agree')}
          </button>
        </div>
      </div>
    </div>
  );
}
