import React from 'react';
import GoldenLogo from './branding/GoldenLogo';

const CustomLogo = ({ size = 'lg', className = '' }) => {
  // Map sizes to pixel widths for the Golden Logo
  // Optimized for navbar use - proportionate to icons (24-28px)
  const sizeMap = {
    xs: 40,   // Extra small - compact navbar (proportionate to 24px icons)
    sm: 50,   // Small - standard navbar
    md: 80,   // Medium - larger headers
    lg: 120,  // Large - splash/hero
    xl: 160   // Extra large - auth pages
  };

  return (
    <div className={`flex items-center justify-center ${className}`}>
      <GoldenLogo 
        width={sizeMap[size]} 
        className="mx-auto"
      />
    </div>
  );
};

export default CustomLogo;
