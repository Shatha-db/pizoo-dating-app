import React from "react";
import classicLogo from "../../assets/branding/pizoo-classic.png";
import goldenLogo from "../../assets/branding/pizoo-golden.png";

/**
 * Official Pizoo Logo Component
 * - Classic: Orange-Red gradient (Auth pages)
 * - Golden: Yellow-Orange gradient (In-app)
 * - No text labels underneath
 * - Transparent background
 */
export default function PizooLogo({ 
  variant = "classic", 
  width = 280,
  className = "",
  alt = "Pizoo"
}) {
  const src = variant === "golden" ? goldenLogo : classicLogo;
  const height = width * 2; // Maintain aspect ratio (512x1024)

  return (
    <img
      src={src}
      alt={alt}
      width={width}
      height={height}
      style={{
        width: `${width}px`,
        height: 'auto',
        display: 'block',
      }}
      loading="eager"
      fetchPriority="high"
      className={className}
    />
  );
}
