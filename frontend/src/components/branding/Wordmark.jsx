import React from "react";
import styles from "./Wordmark.module.css";

/**
 * Official Pizoo Classic Logo
 * - Uses the exact original logo image
 * - No modifications to design or quality
 * - Maintains original 3D effect and texture
 */
export default function Wordmark({
  width = 220,
  className = "",
  title = "Pizoo",
}) {
  return (
    <div
      className={`${styles.wrap} ${className}`}
      style={{ width, height: "auto" }}
      aria-label={title}
      role="img"
    >
      <img
        src="/logo/pizoo-classic-transparent.png"
        alt="Pizoo"
        style={{ width: '100%', height: 'auto', display: 'block' }}
        loading="eager"
        fetchPriority="high"
      />
    </div>
  );
}
