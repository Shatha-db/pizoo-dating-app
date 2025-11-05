import React from 'react';
import GoldenLogo from './branding/GoldenLogo';

const CustomLogo = ({ size = 'lg', className = '' }) => {
  // Map sizes to pixel widths for the Golden Logo
  // Large logo with minimal spacing around it
  const sizeMap = {
    xs: 100,  // Extra small - compact navbar
    sm: 120,  // Small - standard navbar
    md: 140,  // Medium - larger headers
    lg: 160,  // Large - splash/hero
    xl: 180   // Extra large - auth pages
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
