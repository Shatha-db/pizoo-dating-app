import React from "react";
import styles from "./Wordmark.module.css";

/**
 * Official Pizoo Logo (Classic or Golden variant)
 * - Uses the exact original logo image
 * - No text labels underneath
 * - Maintains original 3D effect and texture
 */
export default function Wordmark({
  width = 220,
  variant = "classic",
  className = "",
  title = "Pizoo",
}) {
  const logoSrc = variant === "golden" 
    ? "/logo/pizoo-golden-clean.png"
    : "/logo/pizoo-classic-clean.png";

  return (
    <div
      className={`${styles.wrap} ${className}`}
      style={{ width, height: "auto" }}
      aria-label={title}
      role="img"
    >
      <img
        src={logoSrc}
        alt="Pizoo"
        style={{ width: '100%', height: 'auto', display: 'block' }}
        loading="eager"
        fetchPriority="high"
      />
    </div>
  );
}
