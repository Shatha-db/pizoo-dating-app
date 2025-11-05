import React from 'react';
import Logo from './Logo.tsx';

const CustomLogo = ({ size = 'lg', className = '' }) => {
  // Map sizes to pixel widths for the new Logo component
  const sizeMap = {
    sm: 120,
    md: 160,
    lg: 200,
    xl: 240
  };

  return (
    <div className={`flex items-center justify-center ${className}`}>
      <Logo 
        variant="wordmark" 
        width={sizeMap[size]} 
        className="mx-auto"
      />
    </div>
  );
};

export default CustomLogo;
