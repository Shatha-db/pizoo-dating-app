import React from 'react';

export default function SafetyConsentModal({ open, onAccept, onClose }) {
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
        <div className="text-2xl font-bold mb-2" dir="rtl">السلامة أولاً</div>
        <p className="text-gray-600 mb-4 text-sm leading-relaxed" dir="rtl">
          نستخدم أنظمة آلية ويدوية لمراقبة الدردشات ومقاطع الفيديو للكشف عن النشاط غير القانوني.
          بالموافقة، أنت تلتزم بقواعد السلامة والاحترام.
        </p>
        <div className="flex gap-2">
          <button 
            className="flex-1 h-11 rounded-full bg-gray-200 text-gray-700 hover:bg-gray-300 transition-colors"
            onClick={onClose}
          >
            لا ترسل الرسالة
          </button>
          <button 
            className="flex-1 h-11 rounded-full text-white bg-gradient-to-r from-pink-500 to-orange-500 hover:brightness-110 transition-all"
            onClick={accept}
          >
            أوافق
          </button>
        </div>
      </div>
    </div>
  );
}
