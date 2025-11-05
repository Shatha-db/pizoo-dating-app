import React from "react";
import Wordmark from "./Wordmark";

/**
 * Golden Logo variant for in-app usage
 * - Bright yellow-orange gradient
 * - Perfect for headers, navbars, success states
 */
export default function GoldenLogo({
  width = 180,
  className = "",
}) {
  return (
    <Wordmark 
      variant="golden" 
      width={width} 
      className={className}
      title="Pizoo"
    />
  );
}
