import React from 'react';

type Variant = 'brand' | 'gold';
interface Props {
  variant?: Variant;
  width?: number | string;
  height?: number | string;
  className?: string;
  title?: string;
}

const Logo: React.FC<Props> = ({
  variant = 'brand',
  width = 220,
  height = 'auto',
  className,
  title = 'PiZOO'
}) => {
  const src =
    variant === 'gold'
      ? '/brand/pizoo-logo-gold.svg'
      : '/brand/pizoo-logo.svg';

  return (
    <img
      src={src}
      width={width}
      height={height}
      loading="eager"
      decoding="sync"
      alt="PiZOO logo"
      aria-label={title}
      className={className}
      style={{ display: 'inline-block', verticalAlign: 'middle' }}
    />
  );
};

export default Logo;