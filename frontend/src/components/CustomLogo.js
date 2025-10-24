import React from 'react';

const CustomLogo = ({ size = 'lg', className = '' }) => {
  const sizeClasses = {
    sm: 'h-12',
    md: 'h-16',
    lg: 'h-24',
    xl: 'h-32'
  };

  return (
    <div className={`flex items-center justify-center ${className}`}>
      <img 
        src="/pizoo-logo-transparent.png" 
        alt="Pizoo" 
        className={`${sizeClasses[size]} w-auto object-contain`}
        style={{ imageRendering: '-webkit-optimize-contrast' }}
      />
    </div>
  );
};

export default CustomLogo;
