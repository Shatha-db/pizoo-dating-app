import React from 'react';

export default function Loader({ text = 'جاري التحميل…' }) {
  return (
    <div style={{
      display: 'grid',
      placeItems: 'center',
      height: '100vh',
      backgroundColor: '#fafafa'
    }}>
      <div style={{ textAlign: 'center' }}>
        <div style={{
          width: '64px',
          height: '64px',
          margin: '0 auto 1rem',
          border: '4px solid #ec4899',
          borderTopColor: 'transparent',
          borderRadius: '50%',
          animation: 'spin 1s linear infinite'
        }}></div>
        <div className="animate-pulse text-gray-500" style={{ color: '#6b7280', fontSize: '1rem' }}>
          {text}
        </div>
      </div>
    </div>
  );
}
