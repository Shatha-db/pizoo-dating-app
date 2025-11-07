/**
 * Format API error responses for display
 * Handles FastAPI validation errors and other error formats
 */
export const formatErrorMessage = (error, defaultMessage = 'حدث خطأ') => {
  // If error is already a string
  if (typeof error === 'string') {
    return error;
  }

  // Handle axios error
  if (error.response?.data?.detail) {
    const detail = error.response.data.detail;
    
    // If detail is an array (FastAPI validation errors)
    if (Array.isArray(detail)) {
      return detail.map(err => {
        const field = err.loc?.[1] || err.loc?.[0] || 'field';
        const message = err.msg || 'invalid value';
        return `${field}: ${message}`;
      }).join(', ');
    }
    
    // If detail is a string
    if (typeof detail === 'string') {
      return detail;
    }
    
    // If detail is an object with msg
    if (detail.msg) {
      return detail.msg;
    }
  }

  // Handle error.message
  if (error.message) {
    return error.message;
  }

  // Fallback to default
  return defaultMessage;
};

/**
 * Safe error display component helper
 * Ensures error is always a string before rendering
 */
export const safeErrorDisplay = (error) => {
  if (!error) return null;
  
  if (typeof error === 'string') {
    return error;
  }
  
  // Try to extract meaningful message
  if (error.message) {
    return error.message;
  }
  
  // Last resort: stringify
  try {
    return JSON.stringify(error);
  } catch (e) {
    return 'حدث خطأ غير متوقع';
  }
};
