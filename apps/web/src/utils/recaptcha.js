/**
 * reCAPTCHA Configuration Utility
 * 
 * This utility determines when reCAPTCHA should be enforced based on:
 * - Environment (production vs preview/development)
 * - Domain (pizoo.ch / www.pizoo.ch)
 * - Site key availability
 * 
 * Usage:
 * - getRecaptchaMode() returns "required" or "disabled"
 * - isRecaptchaRequired() returns boolean
 */

const PRODUCTION_DOMAINS = ['pizoo.ch', 'www.pizoo.ch'];

/**
 * Get the current reCAPTCHA enforcement mode
 * @returns {string} "required" | "disabled"
 */
export const getRecaptchaMode = () => {
  // Check if we have a site key configured
  const siteKey = process.env.REACT_APP_RECAPTCHA_SITE_KEY;
  if (!siteKey) {
    return 'disabled';
  }

  // Check if we're in production environment
  const isProduction = process.env.NODE_ENV === 'production';
  if (!isProduction) {
    return 'disabled';
  }

  // Check if current hostname is a production domain
  const currentHostname = window.location.hostname;
  const isProductionDomain = PRODUCTION_DOMAINS.includes(currentHostname);
  
  if (!isProductionDomain) {
    return 'disabled';
  }

  // All checks passed - require reCAPTCHA
  return 'required';
};

/**
 * Check if reCAPTCHA is required for the current environment
 * @returns {boolean}
 */
export const isRecaptchaRequired = () => {
  return getRecaptchaMode() === 'required';
};

/**
 * Get the reCAPTCHA site key
 * @returns {string|null}
 */
export const getRecaptchaSiteKey = () => {
  return process.env.REACT_APP_RECAPTCHA_SITE_KEY || null;
};

/**
 * Get user-friendly message about reCAPTCHA status
 * @returns {string|null}
 */
export const getRecaptchaStatusMessage = () => {
  const mode = getRecaptchaMode();
  
  if (mode === 'disabled') {
    const isPreview = window.location.hostname.includes('preview') || 
                      window.location.hostname.includes('emergentagent') ||
                      window.location.hostname.includes('vercel');
    
    if (isPreview) {
      return 'reCAPTCHA disabled in preview environment. Will be enforced on pizoo.ch';
    }
    
    if (process.env.NODE_ENV === 'development') {
      return 'reCAPTCHA disabled in development mode';
    }
    
    return 'reCAPTCHA not configured';
  }
  
  return null; // No message needed when required
};

/**
 * Log reCAPTCHA configuration (for debugging)
 */
export const logRecaptchaConfig = () => {
  console.log('🔐 reCAPTCHA Configuration:', {
    mode: getRecaptchaMode(),
    required: isRecaptchaRequired(),
    siteKey: getRecaptchaSiteKey() ? '***' + getRecaptchaSiteKey().slice(-10) : 'not set',
    hostname: window.location.hostname,
    nodeEnv: process.env.NODE_ENV,
    message: getRecaptchaStatusMessage()
  });
};
