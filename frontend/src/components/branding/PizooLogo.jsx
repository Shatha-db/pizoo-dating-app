import React from "react";
import classicLogo from "../../assets/branding/pizoo-classic.png";
import goldenLogo from "../../assets/branding/pizoo-golden.png";

/**
 * Official Pizoo Logo Component
 * - Classic (Orange): For Auth pages, Splash, Landing
 * - Golden: For In-app pages, Navbar, Header
 * - Clean design with minimal padding
 * - Transparent background
 * - Optimized aspect ratio (712x950 ≈ 3:4)
 */
export default function PizooLogo({ 
  variant = "classic", 
  width = 200,
  className = "",
  alt = "Pizoo"
}) {
  const src = variant === "golden" ? goldenLogo : classicLogo;
  // Aspect ratio: 712x950 ≈ 0.75 (3:4)
  const height = Math.round(width * 1.33);

  return (
    <img
      src={src}
      alt={alt}
      style={{
        width: `${width}px`,
        height: 'auto',
        maxWidth: '100%',
        display: 'block',
      }}
      loading="eager"
      fetchPriority="high"
      className={className}
    />
  );
}
