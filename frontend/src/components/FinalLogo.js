import React from 'react';

// Final Logo: "PIZ" + Interlocking Wedding Rings
export const PizooFinalLogo = ({ size = 'md', animated = false }) => {
  const sizes = {
    sm: { height: 40, textSize: 'text-3xl', ringSize: 40 },
    md: { height: 56, textSize: 'text-5xl', ringSize: 56 },
    lg: { height: 72, textSize: 'text-6xl', ringSize: 72 }
  };

  const currentSize = sizes[size];

  return (
    <div className="flex items-center gap-0" style={{ direction: 'ltr' }}>
      {/* Text "PIZ" - Serif font, Orange color */}
      <span 
        className={`${currentSize.textSize} font-bold`}
        style={{ 
          fontFamily: "'Playfair Display', 'Georgia', serif",
          color: '#E87722',
          letterSpacing: '0.02em',
          fontWeight: 700
        }}
      >
        PIZ
      </span>
      
      {/* Interlocking Wedding Rings as "OO" */}
      <div className="relative" style={{ width: currentSize.ringSize, height: currentSize.height }}>
        <svg 
          width={currentSize.ringSize} 
          height={currentSize.height} 
          viewBox="0 0 80 56" 
          fill="none" 
          xmlns="http://www.w3.org/2000/svg"
        >
          {/* Left Ring */}
          <g>
            {/* Outer circle */}
            <circle cx="25" cy="28" r="14" fill="none" stroke="#E87722" strokeWidth="3"/>
            
            {/* Inner circle (hole) */}
            <circle cx="25" cy="28" r="10" fill="none" stroke="#E87722" strokeWidth="1.5"/>
            
            {/* Hatching/texture lines for depth - Left Ring */}
            <path d="M 17 20 Q 20 18 23 18" stroke="#E87722" strokeWidth="0.5" opacity="0.6" fill="none"/>
            <path d="M 15 24 Q 18 22 21 22" stroke="#E87722" strokeWidth="0.5" opacity="0.6" fill="none"/>
            <path d="M 14 28 Q 17 26 20 26" stroke="#E87722" strokeWidth="0.5" opacity="0.6" fill="none"/>
            <path d="M 15 32 Q 18 30 21 30" stroke="#E87722" strokeWidth="0.5" opacity="0.6" fill="none"/>
            <path d="M 17 36 Q 20 34 23 34" stroke="#E87722" strokeWidth="0.5" opacity="0.6" fill="none"/>
            
            {/* Right side highlights */}
            <path d="M 33 20 Q 30 18 27 18" stroke="#E87722" strokeWidth="0.5" opacity="0.4" fill="none"/>
            <path d="M 35 24 Q 32 22 29 22" stroke="#E87722" strokeWidth="0.5" opacity="0.4" fill="none"/>
            <path d="M 36 28 Q 33 26 30 26" stroke="#E87722" strokeWidth="0.5" opacity="0.4" fill="none"/>
            <path d="M 35 32 Q 32 30 29 30" stroke="#E87722" strokeWidth="0.5" opacity="0.4" fill="none"/>
            <path d="M 33 36 Q 30 34 27 34" stroke="#E87722" strokeWidth="0.5" opacity="0.4" fill="none"/>
          </g>

          {/* Right Ring - Interlocking behind */}
          <g>
            {/* Outer circle */}
            <circle cx="45" cy="28" r="14" fill="none" stroke="#E87722" strokeWidth="3"/>
            
            {/* Inner circle (hole) */}
            <circle cx="45" cy="28" r="10" fill="none" stroke="#E87722" strokeWidth="1.5"/>
            
            {/* Hatching/texture lines for depth - Right Ring */}
            <path d="M 37 20 Q 40 18 43 18" stroke="#E87722" strokeWidth="0.5" opacity="0.6" fill="none"/>
            <path d="M 35 24 Q 38 22 41 22" stroke="#E87722" strokeWidth="0.5" opacity="0.6" fill="none"/>
            <path d="M 34 28 Q 37 26 40 26" stroke="#E87722" strokeWidth="0.5" opacity="0.6" fill="none"/>
            <path d="M 35 32 Q 38 30 41 30" stroke="#E87722" strokeWidth="0.5" opacity="0.6" fill="none"/>
            <path d="M 37 36 Q 40 34 43 34" stroke="#E87722" strokeWidth="0.5" opacity="0.6" fill="none"/>
            
            {/* Right side highlights */}
            <path d="M 53 20 Q 50 18 47 18" stroke="#E87722" strokeWidth="0.5" opacity="0.4" fill="none"/>
            <path d="M 55 24 Q 52 22 49 22" stroke="#E87722" strokeWidth="0.5" opacity="0.4" fill="none"/>
            <path d="M 56 28 Q 53 26 50 26" stroke="#E87722" strokeWidth="0.5" opacity="0.4" fill="none"/>
            <path d="M 55 32 Q 52 30 49 30" stroke="#E87722" strokeWidth="0.5" opacity="0.4" fill="none"/>
            <path d="M 53 36 Q 50 34 47 34" stroke="#E87722" strokeWidth="0.5" opacity="0.4" fill="none"/>
          </g>

          {/* Interlocking effect - overlap shadow */}
          <ellipse cx="35" cy="28" rx="3" ry="12" fill="#E87722" opacity="0.1"/>
          
          {animated && (
            <g>
              <circle cx="20" cy="22" r="2" fill="#FFD700" opacity="0.8">
                <animate attributeName="opacity" values="0.8;0.3;0.8" dur="2s" repeatCount="indefinite"/>
              </circle>
              <circle cx="50" cy="22" r="2" fill="#FFD700" opacity="0.8">
                <animate attributeName="opacity" values="0.3;0.8;0.3" dur="2s" repeatCount="indefinite"/>
              </circle>
            </g>
          )}
        </svg>
      </div>
    </div>
  );
};

// Icon only version
export const PizooRingsIcon = ({ size = 56 }) => {
  return (
    <svg 
      width={size} 
      height={size} 
      viewBox="0 0 80 56" 
      fill="none" 
      xmlns="http://www.w3.org/2000/svg"
    >
      {/* Left Ring */}
      <g>
        <circle cx="25" cy="28" r="14" fill="none" stroke="#E87722" strokeWidth="3"/>
        <circle cx="25" cy="28" r="10" fill="none" stroke="#E87722" strokeWidth="1.5"/>
        
        {/* Hatching lines */}
        <path d="M 17 20 Q 20 18 23 18" stroke="#E87722" strokeWidth="0.5" opacity="0.6" fill="none"/>
        <path d="M 15 24 Q 18 22 21 22" stroke="#E87722" strokeWidth="0.5" opacity="0.6" fill="none"/>
        <path d="M 14 28 Q 17 26 20 26" stroke="#E87722" strokeWidth="0.5" opacity="0.6" fill="none"/>
        <path d="M 15 32 Q 18 30 21 30" stroke="#E87722" strokeWidth="0.5" opacity="0.6" fill="none"/>
        <path d="M 17 36 Q 20 34 23 34" stroke="#E87722" strokeWidth="0.5" opacity="0.6" fill="none"/>
      </g>

      {/* Right Ring */}
      <g>
        <circle cx="45" cy="28" r="14" fill="none" stroke="#E87722" strokeWidth="3"/>
        <circle cx="45" cy="28" r="10" fill="none" stroke="#E87722" strokeWidth="1.5"/>
        
        {/* Hatching lines */}
        <path d="M 37 20 Q 40 18 43 18" stroke="#E87722" strokeWidth="0.5" opacity="0.6" fill="none"/>
        <path d="M 35 24 Q 38 22 41 22" stroke="#E87722" strokeWidth="0.5" opacity="0.6" fill="none"/>
        <path d="M 34 28 Q 37 26 40 26" stroke="#E87722" strokeWidth="0.5" opacity="0.6" fill="none"/>
        <path d="M 35 32 Q 38 30 41 30" stroke="#E87722" strokeWidth="0.5" opacity="0.6" fill="none"/>
        <path d="M 37 36 Q 40 34 43 34" stroke="#E87722" strokeWidth="0.5" opacity="0.6" fill="none"/>
      </g>

      {/* Interlocking shadow */}
      <ellipse cx="35" cy="28" rx="3" ry="12" fill="#E87722" opacity="0.1"/>
    </svg>
  );
};

// White version for dark backgrounds
export const PizooFinalLogoWhite = ({ size = 'md' }) => {
  const sizes = {
    sm: { height: 40, textSize: 'text-3xl', ringSize: 40 },
    md: { height: 56, textSize: 'text-5xl', ringSize: 56 },
    lg: { height: 72, textSize: 'text-6xl', ringSize: 72 }
  };

  const currentSize = sizes[size];

  return (
    <div className="flex items-center gap-0" style={{ direction: 'ltr' }}>
      <span 
        className={`${currentSize.textSize} font-bold text-white`}
        style={{ 
          fontFamily: "'Playfair Display', 'Georgia', serif",
          letterSpacing: '0.02em',
          fontWeight: 700
        }}
      >
        PIZ
      </span>
      
      <div className="relative" style={{ width: currentSize.ringSize, height: currentSize.height }}>
        <svg 
          width={currentSize.ringSize} 
          height={currentSize.height} 
          viewBox="0 0 80 56" 
          fill="none" 
          xmlns="http://www.w3.org/2000/svg"
        >
          {/* Same rings but in white */}
          <g>
            <circle cx="25" cy="28" r="14" fill="none" stroke="white" strokeWidth="3"/>
            <circle cx="25" cy="28" r="10" fill="none" stroke="white" strokeWidth="1.5"/>
            <path d="M 17 20 Q 20 18 23 18" stroke="white" strokeWidth="0.5" opacity="0.6" fill="none"/>
            <path d="M 15 24 Q 18 22 21 22" stroke="white" strokeWidth="0.5" opacity="0.6" fill="none"/>
            <path d="M 14 28 Q 17 26 20 26" stroke="white" strokeWidth="0.5" opacity="0.6" fill="none"/>
          </g>
          <g>
            <circle cx="45" cy="28" r="14" fill="none" stroke="white" strokeWidth="3"/>
            <circle cx="45" cy="28" r="10" fill="none" stroke="white" strokeWidth="1.5"/>
            <path d="M 37 20 Q 40 18 43 18" stroke="white" strokeWidth="0.5" opacity="0.6" fill="none"/>
            <path d="M 35 24 Q 38 22 41 22" stroke="white" strokeWidth="0.5" opacity="0.6" fill="none"/>
            <path d="M 34 28 Q 37 26 40 26" stroke="white" strokeWidth="0.5" opacity="0.6" fill="none"/>
          </g>
          <ellipse cx="35" cy="28" rx="3" ry="12" fill="white" opacity="0.1"/>
        </svg>
      </div>
    </div>
  );
};

export default PizooFinalLogo;
