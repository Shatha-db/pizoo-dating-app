import React from "react";
import PizooLogo from "./PizooLogo";

/**
 * Wordmark wrapper for backward compatibility
 * Uses the new PizooLogo component
 */
export default function Wordmark({
  width = 280,
  variant = "classic",
  className = "",
  title = "Pizoo",
}) {
  return (
    <div aria-label={title} role="img" className={className}>
      <PizooLogo variant={variant} width={width} />
    </div>
  );
}
