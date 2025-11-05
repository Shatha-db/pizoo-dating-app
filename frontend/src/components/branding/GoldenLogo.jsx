import React from "react";
import PizooLogo from "./PizooLogo";

/**
 * Golden Logo variant for in-app usage
 * - Bright golden-yellow gradient
 * - Perfect for headers, navbars, in-app pages
 * - Width: 140px (optimized for navbar)
 */
export default function GoldenLogo({
  width = 140,
  className = "",
}) {
  return (
    <PizooLogo 
      variant="golden" 
      width={width} 
      className={className}
    />
  );
}
