import React from 'react';
import GoldenLogo from './branding/GoldenLogo';

const CustomLogo = ({ size = 'lg', className = '' }) => {
  // Map sizes to pixel widths for the Golden Logo
  // Optimized for navbar use - proportionate to icons (24-28px)
  const sizeMap = {
    xs: 60,   // Extra small - compact navbar
    sm: 80,   // Small - standard navbar
    md: 120,  // Medium - larger headers
    lg: 160,  // Large - splash/hero
    xl: 200   // Extra large - auth pages
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
