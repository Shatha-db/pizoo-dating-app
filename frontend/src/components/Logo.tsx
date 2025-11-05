import React from 'react';
import logoWordmark from '../assets/branding/logo-wordmark.svg';
import logoMark from '../assets/branding/logo-mark.svg';

type Variant = 'wordmark' | 'mark' | 'gold';
interface Props {
  variant?: Variant;
  width?: number | string;
  height?: number | string;
  className?: string;
  title?: string;
}

const Logo: React.FC<Props> = ({
  variant = 'wordmark',
  width = 220,
  height = 'auto',
  className,
  title = 'PiZOO'
}) => {
  // Use new SVG files from assets/branding
  let src = logoWordmark;
  
  if (variant === 'mark') {
    src = logoMark;
  } else if (variant === 'gold') {
    // Fallback to old gold variant if needed
    src = '/brand/pizoo-logo-gold.svg';
  }

  return (
    <img
      src={src}
      width={typeof width === 'number' ? width : undefined}
      style={typeof width === 'string' ? { width, height } : { height }}
      loading="eager"
      fetchPriority="high"
      decoding="async"
      alt="PiZOO logo"
      aria-label={title}
      className={className}
    />
  );
};

export default Logo;