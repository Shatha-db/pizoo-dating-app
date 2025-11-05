import React from 'react';
import GoldenLogo from './branding/GoldenLogo';

const CustomLogo = ({ size = 'lg', className = '' }) => {
  // Map sizes to pixel widths for the Golden Logo
  // Adjusted for better navbar proportions
  const sizeMap = {
    xs: 80,   // Extra small - compact navbar (smaller)
    sm: 120,  // Small - standard navbar  
    md: 160,  // Medium - larger headers
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
