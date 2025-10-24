import React from 'react';

const CustomLogo = ({ size = 'md', className = '' }) => {
  const sizeClasses = {
    sm: 'h-8',
    md: 'h-12',
    lg: 'h-16',
    xl: 'h-20'
  };

  return (
    <div className={`flex items-center justify-center ${className}`}>
      <img 
        src="/pizoo-logo-transparent.png" 
        alt="Pizoo" 
        className={`${sizeClasses[size]} w-auto object-contain`}
      />
    </div>
  );
};

export default CustomLogo;
