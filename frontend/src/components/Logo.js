import React from 'react';

// Main Logo Component for Headers and Navigation
export const PizooLogo = ({ size = 'md', showText = true, animated = false }) => {
  const sizes = {
    sm: { icon: 32, text: 'text-xl' },
    md: { icon: 48, text: 'text-3xl' },
    lg: { icon: 64, text: 'text-5xl' }
  };

  const currentSize = sizes[size];

  return (
    <div className="flex items-center gap-2">
      {/* Logo Icon */}
      <div className="relative">
        <svg 
          width={currentSize.icon} 
          height={currentSize.icon} 
          viewBox="0 0 48 48" 
          fill="none" 
          xmlns="http://www.w3.org/2000/svg"
        >
          {/* Heart Shape */}
          <path 
            d="M24 42C24 42 6 30 6 18C6 12.4772 10.4772 8 16 8C19.3137 8 22.2353 9.72549 24 12.2353C25.7647 9.72549 28.6863 8 32 8C37.5228 8 42 12.4772 42 18C42 30 24 42 24 42Z" 
            fill="url(#heartGradient)" 
            stroke="white" 
            strokeWidth="2"
          />
          {animated && (
            <>
              {/* Sparkle/Fire elements with animation */}
              <circle cx="32" cy="10" r="3" fill="#FFD700">
                <animate attributeName="opacity" values="1;0.5;1" dur="1.5s" repeatCount="indefinite"/>
              </circle>
              <circle cx="38" cy="14" r="2" fill="#FFD700">
                <animate attributeName="opacity" values="0.5;1;0.5" dur="1.5s" repeatCount="indefinite"/>
              </circle>
            </>
          )}
          
          {/* Gradient Definition */}
          <defs>
            <linearGradient id="heartGradient" x1="6" y1="8" x2="42" y2="42">
              <stop offset="0%" stopColor="#EC4899" />
              <stop offset="50%" stopColor="#EF4444" />
              <stop offset="100%" stopColor="#F97316" />
            </linearGradient>
          </defs>
        </svg>
      </div>
      
      {/* Logo Text */}
      {showText && (
        <h1 
          className={`${currentSize.text} font-bold bg-gradient-to-r from-pink-600 to-orange-600 bg-clip-text text-transparent tracking-tight`}
          style={{ fontFamily: "'Poppins', sans-serif" }}
        >
          Pizoo
        </h1>
      )}
    </div>
  );
};

// Simple Icon-only Logo for compact spaces
export const PizooIcon = ({ size = 32 }) => {
  return (
    <svg 
      width={size} 
      height={size} 
      viewBox="0 0 48 48" 
      fill="none" 
      xmlns="http://www.w3.org/2000/svg"
    >
      <path 
        d="M24 42C24 42 6 30 6 18C6 12.4772 10.4772 8 16 8C19.3137 8 22.2353 9.72549 24 12.2353C25.7647 9.72549 28.6863 8 32 8C37.5228 8 42 12.4772 42 18C42 30 24 42 24 42Z" 
        fill="url(#heartGradient)" 
        stroke="white" 
        strokeWidth="2"
      />
      <defs>
        <linearGradient id="heartGradient" x1="6" y1="8" x2="42" y2="42">
          <stop offset="0%" stopColor="#EC4899" />
          <stop offset="50%" stopColor="#EF4444" />
          <stop offset="100%" stopColor="#F97316" />
        </linearGradient>
      </defs>
    </svg>
  );
};

// Text-only Logo for minimalist designs
export const PizooText = ({ size = 'md', gradient = true }) => {
  const textSizes = {
    sm: 'text-xl',
    md: 'text-3xl',
    lg: 'text-5xl',
    xl: 'text-6xl'
  };

  const className = gradient 
    ? `${textSizes[size]} font-bold bg-gradient-to-r from-pink-600 to-orange-600 bg-clip-text text-transparent tracking-tight`
    : `${textSizes[size]} font-bold text-gray-900 tracking-tight`;

  return (
    <h1 
      className={className}
      style={{ fontFamily: "'Poppins', sans-serif" }}
    >
      Pizoo
    </h1>
  );
};

export default PizooLogo;
