import React from 'react';

interface Props {
  size?: number;
  className?: string;
}

const AppLogo: React.FC<Props> = ({ size = 120, className = '' }) => {
  return (
    <img
      src="/logo/logo_classic.svg"
      alt="Pizoo"
      width={size}
      height="auto"
      loading="eager"
      fetchPriority="high"
      decoding="async"
      className={className}
      style={{ display: 'inline-block' }}
    />
  );
};

export default AppLogo;