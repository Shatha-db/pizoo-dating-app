import React from 'react';

// ==================== OPTION 1: Minimalist Geometric Heart ====================
export const Logo1_MinimalistHeart = ({ size = 48 }) => (
  <div className="flex items-center gap-3">
    <svg width={size} height={size} viewBox="0 0 48 48" fill="none">
      {/* Modern geometric heart - clean lines */}
      <path 
        d="M24 40L8 24C4 20 4 12 10 8C13 6 17 6 20 8C21 9 23 11 24 13C25 11 27 9 28 8C31 6 35 6 38 8C44 12 44 20 40 24L24 40Z" 
        fill="#EC4899"
        stroke="#EC4899" 
        strokeWidth="2"
        strokeLinejoin="round"
      />
    </svg>
    <span className="text-3xl font-bold" style={{ fontFamily: 'system-ui, sans-serif', letterSpacing: '-0.02em' }}>
      <span className="text-gray-900">Pizoo</span>
    </span>
  </div>
);

// ==================== OPTION 2: Interlocking Circles (Connection) ====================
export const Logo2_InterlockingCircles = ({ size = 48 }) => (
  <div className="flex items-center gap-3">
    <svg width={size} height={size} viewBox="0 0 48 48" fill="none">
      {/* Two circles representing connection */}
      <circle cx="18" cy="24" r="12" fill="#EC4899" opacity="0.8"/>
      <circle cx="30" cy="24" r="12" fill="#F97316" opacity="0.8"/>
      {/* Center overlap creates a heart-like shape */}
    </svg>
    <span className="text-3xl font-bold bg-gradient-to-r from-pink-500 to-orange-500 bg-clip-text text-transparent" 
          style={{ fontFamily: 'system-ui, sans-serif' }}>
      Pizoo
    </span>
  </div>
);

// ==================== OPTION 3: Letter P with Heart (Monogram) ====================
export const Logo3_PMonogram = ({ size = 48 }) => (
  <div className="flex items-center gap-3">
    <svg width={size} height={size} viewBox="0 0 48 48" fill="none">
      {/* Letter P shape with heart integrated */}
      <path 
        d="M12 8 L12 40 M12 8 L28 8 C34 8 38 12 38 18 C38 24 34 28 28 28 L12 28" 
        stroke="#EC4899" 
        strokeWidth="5" 
        strokeLinecap="round" 
        strokeLinejoin="round"
        fill="none"
      />
      {/* Small heart inside P */}
      <path 
        d="M18 18 C18 16 20 14 22 16 C23 15 24 14 25 14 C27 14 28 16 28 18 C28 22 22 24 22 24 C22 24 18 22 18 18Z" 
        fill="#F97316"
      />
    </svg>
    <span className="text-3xl font-bold text-gray-900" style={{ fontFamily: 'Inter, sans-serif', fontWeight: 700 }}>
      izoo
    </span>
  </div>
);

// ==================== OPTION 4: Flame Modern (Like Tinder but different) ====================
export const Logo4_ModernFlame = ({ size = 48 }) => (
  <div className="flex items-center gap-3">
    <svg width={size} height={size} viewBox="0 0 48 48" fill="none">
      {/* Modern stylized flame */}
      <path 
        d="M24 6 C20 14 18 20 18 26 C18 32 20 38 24 42 C28 38 30 32 30 26 C30 20 28 14 24 6 Z" 
        fill="url(#flameGradient)"
      />
      <path 
        d="M24 20 C22 24 21 27 21 30 C21 33 22 36 24 38 C26 36 27 33 27 30 C27 27 26 24 24 20 Z" 
        fill="#FBBF24"
        opacity="0.8"
      />
      <defs>
        <linearGradient id="flameGradient" x1="24" y1="6" x2="24" y2="42">
          <stop offset="0%" stopColor="#F97316"/>
          <stop offset="100%" stopColor="#EF4444"/>
        </linearGradient>
      </defs>
    </svg>
    <span className="text-3xl font-bold" style={{ fontFamily: 'Montserrat, sans-serif', fontWeight: 800 }}>
      <span className="bg-gradient-to-r from-orange-500 to-red-500 bg-clip-text text-transparent">PIZOO</span>
    </span>
  </div>
);

// ==================== OPTION 5: Hand-Drawn Doodle Style ====================
export const Logo5_DoodleStyle = ({ size = 48 }) => (
  <div className="flex items-center gap-3">
    <svg width={size} height={size} viewBox="0 0 48 48" fill="none">
      {/* Hand-drawn style heart with imperfect lines */}
      <path 
        d="M24 38 C24 38 10 28 8 20 C7 16 9 12 13 11 C16 10 19 12 21 15 L24 19 L27 15 C29 12 32 10 35 11 C39 12 41 16 40 20 C38 28 24 38 24 38 Z" 
        fill="none"
        stroke="#EC4899" 
        strokeWidth="2.5"
        strokeLinecap="round"
        strokeLinejoin="round"
        style={{ 
          strokeDasharray: '1, 1',
          strokeDashoffset: '0',
        }}
      />
      {/* Sketch-style decorative elements */}
      <circle cx="16" cy="14" r="2" fill="#F97316" opacity="0.6"/>
      <circle cx="32" cy="14" r="2" fill="#F97316" opacity="0.6"/>
      <path d="M 12 10 L 14 8" stroke="#FBBF24" strokeWidth="2" strokeLinecap="round"/>
      <path d="M 34 8 L 36 10" stroke="#FBBF24" strokeWidth="2" strokeLinecap="round"/>
    </svg>
    <span className="text-3xl font-bold text-gray-800" 
          style={{ 
            fontFamily: 'Comic Neue, cursive',
            fontWeight: 700,
            transform: 'rotate(-2deg)',
            display: 'inline-block'
          }}>
      Pizoo
    </span>
  </div>
);

// ==================== OPTION 6: 3D Cube Modern ====================
export const Logo6_3DCube = ({ size = 48 }) => (
  <div className="flex items-center gap-3">
    <svg width={size} height={size} viewBox="0 0 48 48" fill="none">
      {/* Isometric cube with heart */}
      <path d="M24 10 L36 17 L36 31 L24 38 L12 31 L12 17 Z" fill="#EC4899" opacity="0.9"/>
      <path d="M24 10 L36 17 L24 24 Z" fill="#F97316" opacity="0.7"/>
      <path d="M24 10 L12 17 L24 24 Z" fill="#EF4444" opacity="0.7"/>
      {/* Heart symbol on front face */}
      <ellipse cx="24" cy="28" rx="4" ry="5" fill="white" opacity="0.9"/>
      <path d="M22 26 C22 25 23 24 24 25 C25 24 26 25 26 26 C26 28 24 30 24 30 C24 30 22 28 22 26" fill="#EC4899"/>
    </svg>
    <span className="text-3xl font-bold text-gray-900" style={{ fontFamily: 'Roboto, sans-serif', fontWeight: 900 }}>
      PIZOO
    </span>
  </div>
);

// ==================== OPTION 7: Abstract Infinity/Connection ====================
export const Logo7_AbstractInfinity = ({ size = 48 }) => (
  <div className="flex items-center gap-3">
    <svg width={size} height={size} viewBox="0 0 48 48" fill="none">
      {/* Infinity symbol representing endless connections */}
      <path 
        d="M 12 24 C 12 18 16 14 20 14 C 24 14 26 18 28 22 C 30 18 32 14 36 14 C 40 14 44 18 44 24 C 44 30 40 34 36 34 C 32 34 30 30 28 26 C 26 30 24 34 20 34 C 16 34 12 30 12 24 Z" 
        fill="url(#infinityGradient)"
        stroke="#EC4899"
        strokeWidth="1.5"
      />
      <defs>
        <linearGradient id="infinityGradient" x1="12" y1="24" x2="44" y2="24">
          <stop offset="0%" stopColor="#EC4899"/>
          <stop offset="50%" stopColor="#EF4444"/>
          <stop offset="100%" stopColor="#F97316"/>
        </linearGradient>
      </defs>
    </svg>
    <span className="text-3xl font-bold text-gray-900" style={{ fontFamily: 'Poppins, sans-serif', fontWeight: 600 }}>
      Pizoo
    </span>
  </div>
);

// ==================== OPTION 8: Lowercase Modern ====================
export const Logo8_LowercaseModern = ({ size = 48 }) => (
  <div className="flex items-center gap-2">
    <svg width={size} height={size} viewBox="0 0 48 48" fill="none">
      {/* Simple dot with gradient */}
      <circle cx="24" cy="24" r="16" fill="url(#dotGradient)"/>
      {/* Letter 'p' integrated */}
      <path 
        d="M 20 14 L 20 34 M 20 18 C 20 18 22 14 26 14 C 30 14 32 18 32 22 C 32 26 30 30 26 30 C 22 30 20 26 20 26" 
        stroke="white" 
        strokeWidth="3" 
        strokeLinecap="round" 
        strokeLinejoin="round"
        fill="none"
      />
      <defs>
        <linearGradient id="dotGradient" x1="8" y1="8" x2="40" y2="40">
          <stop offset="0%" stopColor="#EC4899"/>
          <stop offset="100%" stopColor="#F97316"/>
        </linearGradient>
      </defs>
    </svg>
    <span className="text-3xl font-bold text-gray-900" style={{ fontFamily: 'Inter, sans-serif', fontWeight: 600, textTransform: 'lowercase' }}>
      izoo
    </span>
  </div>
);

// Component to display all options
export const LogoShowcase = () => {
  return (
    <div className="p-8 bg-gray-50 space-y-8">
      <h2 className="text-3xl font-bold text-center mb-8">اختر اللوجو المناسب لـ Pizoo</h2>
      
      <div className="grid gap-8">
        {/* Option 1 */}
        <div className="bg-white p-8 rounded-xl shadow-sm hover:shadow-md transition-shadow">
          <div className="flex items-center justify-between">
            <div>
              <Logo1_MinimalistHeart size={56} />
              <p className="text-sm text-gray-600 mt-4">خيار 1: قلب هندسي بسيط وأنيق</p>
            </div>
            <span className="text-4xl font-bold text-gray-300">01</span>
          </div>
        </div>

        {/* Option 2 */}
        <div className="bg-white p-8 rounded-xl shadow-sm hover:shadow-md transition-shadow">
          <div className="flex items-center justify-between">
            <div>
              <Logo2_InterlockingCircles size={56} />
              <p className="text-sm text-gray-600 mt-4">خيار 2: دوائر متداخلة (رمز الاتصال)</p>
            </div>
            <span className="text-4xl font-bold text-gray-300">02</span>
          </div>
        </div>

        {/* Option 3 */}
        <div className="bg-white p-8 rounded-xl shadow-sm hover:shadow-md transition-shadow">
          <div className="flex items-center justify-between">
            <div>
              <Logo3_PMonogram size={56} />
              <p className="text-sm text-gray-600 mt-4">خيار 3: حرف P مع قلب مدمج</p>
            </div>
            <span className="text-4xl font-bold text-gray-300">03</span>
          </div>
        </div>

        {/* Option 4 */}
        <div className="bg-white p-8 rounded-xl shadow-sm hover:shadow-md transition-shadow">
          <div className="flex items-center justify-between">
            <div>
              <Logo4_ModernFlame size={56} />
              <p className="text-sm text-gray-600 mt-4">خيار 4: لهب عصري (طاقة وحماس)</p>
            </div>
            <span className="text-4xl font-bold text-gray-300">04</span>
          </div>
        </div>

        {/* Option 5 */}
        <div className="bg-white p-8 rounded-xl shadow-sm hover:shadow-md transition-shadow">
          <div className="flex items-center justify-between">
            <div>
              <Logo5_DoodleStyle size={56} />
              <p className="text-sm text-gray-600 mt-4">خيار 5: نمط رسم يدوي دافئ وإنساني</p>
            </div>
            <span className="text-4xl font-bold text-gray-300">05</span>
          </div>
        </div>

        {/* Option 6 */}
        <div className="bg-white p-8 rounded-xl shadow-sm hover:shadow-md transition-shadow">
          <div className="flex items-center justify-between">
            <div>
              <Logo6_3DCube size={56} />
              <p className="text-sm text-gray-600 mt-4">خيار 6: مكعب ثلاثي الأبعاد حديث</p>
            </div>
            <span className="text-4xl font-bold text-gray-300">06</span>
          </div>
        </div>

        {/* Option 7 */}
        <div className="bg-white p-8 rounded-xl shadow-sm hover:shadow-md transition-shadow">
          <div className="flex items-center justify-between">
            <div>
              <Logo7_AbstractInfinity size={56} />
              <p className="text-sm text-gray-600 mt-4">خيار 7: رمز اللانهاية المجرد</p>
            </div>
            <span className="text-4xl font-bold text-gray-300">07</span>
          </div>
        </div>

        {/* Option 8 */}
        <div className="bg-white p-8 rounded-xl shadow-sm hover:shadow-md transition-shadow">
          <div className="flex items-center justify-between">
            <div>
              <Logo8_LowercaseModern size={56} />
              <p className="text-sm text-gray-600 mt-4">خيار 8: أحرف صغيرة عصرية</p>
            </div>
            <span className="text-4xl font-bold text-gray-300">08</span>
          </div>
        </div>
      </div>
    </div>
  );
};

export default LogoShowcase;
