import React from 'react';

const CustomLogo = ({ size = 'lg', className = '' }) => {
  const sizeClasses = {
    sm: 'text-2xl',
    md: 'text-3xl',
    lg: 'text-4xl',
    xl: 'text-5xl'
  };

  return (
    <div className={`flex items-center gap-1 ${className}`}>
      <span 
        className={`${sizeClasses[size]} font-black`}
        style={{ 
          fontFamily: "'Poppins', 'Cairo', sans-serif",
          background: 'linear-gradient(135deg, #ec4899 0%, #f472b6 50%, #fb7185 100%)',
          WebkitBackgroundClip: 'text',
          WebkitTextFillColor: 'transparent',
          backgroundClip: 'text',
          textShadow: '2px 2px 4px rgba(236, 72, 153, 0.2)',
          letterSpacing: '-0.02em',
          fontWeight: 900
        }}
      >
        Pizoo
      </span>
      <span className={`${sizeClasses[size]}`}>❤️‍🔥</span>
    </div>
  );
};

export default CustomLogo;
