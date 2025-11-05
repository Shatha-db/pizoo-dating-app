import React from 'react';
import GoldenLogo from './branding/GoldenLogo';

const CustomLogo = ({ size = 'lg', className = '' }) => {
  // Map sizes to pixel widths for the Golden Logo
  // Using original large sizes as requested
  const sizeMap = {
    xs: 120,  // Extra small - compact navbar
    sm: 160,  // Small - standard navbar  
    md: 180,  // Medium - larger headers
    lg: 200,  // Large - splash/hero (original size)
    xl: 240   // Extra large - auth pages
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
