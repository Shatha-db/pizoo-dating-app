import React from 'react';

// Custom Logo: Infinity in "oo" + Flame
export const PizooCustomLogo = ({ size = 'md', animated = true }) => {
  const sizes = {
    sm: { height: 32, textSize: 'text-2xl' },
    md: { height: 48, textSize: 'text-3xl' },
    lg: { height: 64, textSize: 'text-5xl' }
  };

  const currentSize = sizes[size];

  return (
    <div className="flex items-center gap-1" style={{ direction: 'ltr' }}>
      {/* Text "Piz" */}
      <span 
        className={`${currentSize.textSize} font-bold text-gray-900`}
        style={{ 
          fontFamily: "'Poppins', sans-serif",
          letterSpacing: '-0.02em',
          fontWeight: 700
        }}
      >
        Piz
      </span>
      
      {/* Infinity Symbol as "oo" with Flame on top */}
      <div className="relative" style={{ width: currentSize.height * 1.5, height: currentSize.height }}>
        <svg 
          width={currentSize.height * 1.5} 
          height={currentSize.height} 
          viewBox="0 0 72 48" 
          fill="none" 
          xmlns="http://www.w3.org/2000/svg"
        >
          {/* Infinity symbol representing "oo" */}
          <path 
            d="M 12 24 C 12 18 16 14 20 14 C 24 14 26 18 28 22 L 36 22 C 38 18 40 14 44 14 C 48 14 52 18 52 24 C 52 30 48 34 44 34 C 40 34 38 30 36 26 L 28 26 C 26 30 24 34 20 34 C 16 34 12 30 12 24 Z" 
            fill="url(#infinityGradient)"
            stroke="#EC4899"
            strokeWidth="2"
          />
          
          {/* Flame on top of infinity */}
          <g transform="translate(32, -4)">
            {/* Main flame */}
            <path 
              d="M 0 10 C -3 16 -4 20 -4 24 C -4 28 -2 32 0 34 C 2 32 4 28 4 24 C 4 20 3 16 0 10 Z" 
              fill="url(#flameGradient)"
            >
              {animated && (
                <animate 
                  attributeName="d" 
                  values="M 0 10 C -3 16 -4 20 -4 24 C -4 28 -2 32 0 34 C 2 32 4 28 4 24 C 4 20 3 16 0 10 Z;
                          M 0 8 C -4 14 -5 19 -5 23 C -5 28 -2 33 0 35 C 2 33 5 28 5 23 C 5 19 4 14 0 8 Z;
                          M 0 10 C -3 16 -4 20 -4 24 C -4 28 -2 32 0 34 C 2 32 4 28 4 24 C 4 20 3 16 0 10 Z" 
                  dur="1.5s" 
                  repeatCount="indefinite"
                />
              )}
            </path>
            
            {/* Inner flame (yellow/orange) */}
            <path 
              d="M 0 16 C -1.5 20 -2 22 -2 24 C -2 26.5 -1 29 0 30 C 1 29 2 26.5 2 24 C 2 22 1.5 20 0 16 Z" 
              fill="#FBBF24"
              opacity="0.9"
            >
              {animated && (
                <animate 
                  attributeName="opacity" 
                  values="0.9;0.6;0.9" 
                  dur="1s" 
                  repeatCount="indefinite"
                />
              )}
            </path>
          </g>
          
          {/* Gradients */}
          <defs>
            <linearGradient id="infinityGradient" x1="12" y1="24" x2="52" y2="24">
              <stop offset="0%" stopColor="#EC4899"/>
              <stop offset="50%" stopColor="#EF4444"/>
              <stop offset="100%" stopColor="#F97316"/>
            </linearGradient>
            
            <linearGradient id="flameGradient" x1="0" y1="10" x2="0" y2="34">
              <stop offset="0%" stopColor="#F97316"/>
              <stop offset="50%" stopColor="#EF4444"/>
              <stop offset="100%" stopColor="#DC2626"/>
            </linearGradient>
          </defs>
        </svg>
      </div>
    </div>
  );
};

// Icon version (just the infinity with flame)
export const PizooCustomIcon = ({ size = 48, animated = true }) => {
  return (
    <svg 
      width={size} 
      height={size} 
      viewBox="0 0 72 48" 
      fill="none" 
      xmlns="http://www.w3.org/2000/svg"
    >
      {/* Infinity symbol */}
      <path 
        d="M 12 24 C 12 18 16 14 20 14 C 24 14 26 18 28 22 L 36 22 C 38 18 40 14 44 14 C 48 14 52 18 52 24 C 52 30 48 34 44 34 C 40 34 38 30 36 26 L 28 26 C 26 30 24 34 20 34 C 16 34 12 30 12 24 Z" 
        fill="url(#infinityGradient)"
        stroke="#EC4899"
        strokeWidth="2"
      />
      
      {/* Flame on top */}
      <g transform="translate(32, -4)">
        <path 
          d="M 0 10 C -3 16 -4 20 -4 24 C -4 28 -2 32 0 34 C 2 32 4 28 4 24 C 4 20 3 16 0 10 Z" 
          fill="url(#flameGradient)"
        >
          {animated && (
            <animate 
              attributeName="d" 
              values="M 0 10 C -3 16 -4 20 -4 24 C -4 28 -2 32 0 34 C 2 32 4 28 4 24 C 4 20 3 16 0 10 Z;
                      M 0 8 C -4 14 -5 19 -5 23 C -5 28 -2 33 0 35 C 2 33 5 28 5 23 C 5 19 4 14 0 8 Z;
                      M 0 10 C -3 16 -4 20 -4 24 C -4 28 -2 32 0 34 C 2 32 4 28 4 24 C 4 20 3 16 0 10 Z" 
              dur="1.5s" 
              repeatCount="indefinite"
            />
          )}
        </path>
        
        <path 
          d="M 0 16 C -1.5 20 -2 22 -2 24 C -2 26.5 -1 29 0 30 C 1 29 2 26.5 2 24 C 2 22 1.5 20 0 16 Z" 
          fill="#FBBF24"
          opacity="0.9"
        >
          {animated && (
            <animate 
              attributeName="opacity" 
              values="0.9;0.6;0.9" 
              dur="1s" 
              repeatCount="indefinite"
            />
          )}
        </path>
      </g>
      
      <defs>
        <linearGradient id="infinityGradient" x1="12" y1="24" x2="52" y2="24">
          <stop offset="0%" stopColor="#EC4899"/>
          <stop offset="50%" stopColor="#EF4444"/>
          <stop offset="100%" stopColor="#F97316"/>
        </linearGradient>
        
        <linearGradient id="flameGradient" x1="0" y1="10" x2="0" y2="34">
          <stop offset="0%" stopColor="#F97316"/>
          <stop offset="50%" stopColor="#EF4444"/>
          <stop offset="100%" stopColor="#DC2626"/>
        </linearGradient>
      </defs>
    </svg>
  );
};

// Preview Component
export const CustomLogoPreview = () => {
  return (
    <div className="p-8 bg-gray-50 min-h-screen" dir="rtl">
      <div className="max-w-4xl mx-auto">
        <h2 className="text-3xl font-bold text-center mb-8">اللوجو المخصص - Pizoo</h2>
        
        {/* Main Preview */}
        <div className="bg-white p-12 rounded-2xl shadow-lg mb-8">
          <div className="flex flex-col items-center gap-8">
            <div className="text-center">
              <p className="text-sm text-gray-600 mb-4">الحجم الكبير (Large)</p>
              <PizooCustomLogo size="lg" animated={true} />
            </div>
            
            <div className="text-center">
              <p className="text-sm text-gray-600 mb-4">الحجم المتوسط (Medium)</p>
              <PizooCustomLogo size="md" animated={true} />
            </div>
            
            <div className="text-center">
              <p className="text-sm text-gray-600 mb-4">الحجم الصغير (Small)</p>
              <PizooCustomLogo size="sm" animated={true} />
            </div>
          </div>
        </div>

        {/* Icon Preview */}
        <div className="bg-white p-8 rounded-2xl shadow-lg mb-8">
          <h3 className="text-xl font-bold mb-4 text-center">أيقونة فقط</h3>
          <div className="flex justify-center gap-8">
            <div className="text-center">
              <PizooCustomIcon size={64} animated={true} />
              <p className="text-sm text-gray-600 mt-2">64px</p>
            </div>
            <div className="text-center">
              <PizooCustomIcon size={48} animated={true} />
              <p className="text-sm text-gray-600 mt-2">48px</p>
            </div>
            <div className="text-center">
              <PizooCustomIcon size={32} animated={true} />
              <p className="text-sm text-gray-600 mt-2">32px</p>
            </div>
          </div>
        </div>

        {/* Features */}
        <div className="bg-gradient-to-br from-pink-50 to-orange-50 p-8 rounded-2xl">
          <h3 className="text-xl font-bold mb-4 text-center">مميزات اللوجو المخصص</h3>
          <div className="grid md:grid-cols-2 gap-4">
            <div className="flex items-start gap-3">
              <span className="text-2xl">∞</span>
              <div>
                <h4 className="font-bold">رمز اللانهاية في "oo"</h4>
                <p className="text-sm text-gray-600">يرمز للاتصالات اللانهائية</p>
              </div>
            </div>
            
            <div className="flex items-start gap-3">
              <span className="text-2xl">🔥</span>
              <div>
                <h4 className="font-bold">لهب عصري متحرك</h4>
                <p className="text-sm text-gray-600">يعبر عن الطاقة والشغف</p>
              </div>
            </div>
            
            <div className="flex items-start gap-3">
              <span className="text-2xl">🎨</span>
              <div>
                <h4 className="font-bold">تدرج لوني جذاب</h4>
                <p className="text-sm text-gray-600">وردي → أحمر → برتقالي</p>
              </div>
            </div>
            
            <div className="flex items-start gap-3">
              <span className="text-2xl">✨</span>
              <div>
                <h4 className="font-bold">تصميم فريد ومميز</h4>
                <p className="text-sm text-gray-600">غير مسبوق في تطبيقات المواعدة</p>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default PizooCustomLogo;
