import React from 'react';
import logo from '../assets/logo/pizoo.svg';

interface Props {
  size?: number;
  width?: number | string;
  height?: number | string;
  className?: string;
  title?: string;
}

const Logo: React.FC<Props> = ({
  size = 164,
  width,
  height,
  className,
  title = 'Pizoo'
}) => {
  // Use size if provided, otherwise use width/height
  const finalWidth = width || size;
  const finalHeight = height || size;

  return (
    <img
      src={logo}
      width={typeof finalWidth === 'number' ? finalWidth : undefined}
      height={typeof finalHeight === 'number' ? finalHeight : undefined}
      style={
        typeof finalWidth === 'string' || typeof finalHeight === 'string'
          ? { width: finalWidth, height: finalHeight }
          : undefined
      }
      loading="eager"
      fetchPriority="high"
      decoding="async"
      alt="Pizoo logo"
      aria-label={title}
      className={className ?? 'select-none'}
    />
  );
};

export default Logo;