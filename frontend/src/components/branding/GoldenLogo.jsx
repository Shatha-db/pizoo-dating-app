import React from "react";
import PizooLogo from "./PizooLogo";

/**
 * Golden Logo variant for in-app usage
 * - Bright yellow-orange gradient
 * - Perfect for headers, navbars, success states
 * - Width: 160px (recommended for navbar)
 */
export default function GoldenLogo({
  width = 160,
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
