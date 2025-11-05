import React from 'react';
import GoldenLogo from './branding/GoldenLogo';

const CustomLogo = ({ size = 'lg', className = '' }) => {
  // Map sizes to pixel widths for the Golden Logo
  const sizeMap = {
    sm: 120,
    md: 160,
    lg: 200,
    xl: 240
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
