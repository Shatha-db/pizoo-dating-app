/**
 * Daily Usage Quotas System
 * Manages profile views and likes limits for free users
 */

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL || '';
const API = `${BACKEND_URL}/api`;

/**
 * Fetch user's current usage context
 * @returns {Promise<Object>} Usage context with limits and remaining counts
 */
export async function fetchUsage() {
  try {
    const response = await fetch(`${API}/usage/context`, {
      credentials: 'include',
      headers: {
        'Authorization': `Bearer ${localStorage.getItem('token')}`
      }
    });
    
    if (!response.ok) {
      throw new Error('USAGE_CTX_FAIL');
    }
    
    return await response.json();
  } catch (error) {
    console.error('Failed to fetch usage context:', error);
    throw error;
  }
}

/**
 * Increment usage counter
 * @param {string} kind - 'view' or 'like'
 * @returns {Promise<Object>} Success response
 */
export async function incUsage(kind) {
  try {
    const response = await fetch(`${API}/usage/increment`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${localStorage.getItem('token')}`
      },
      credentials: 'include',
      body: JSON.stringify({ kind })
    });
    
    if (!response.ok) {
      const errorText = await response.text();
      throw new Error(errorText || 'USAGE_INC_FAIL');
    }
    
    return await response.json();
  } catch (error) {
    console.error(`Failed to increment ${kind} usage:`, error);
    throw error;
  }
}

/**
 * Check if user can perform an action (view or like)
 * @param {string} kind - 'view' or 'like'
 * @returns {Promise<boolean>} True if allowed, false if limit reached
 */
export async function canPerformAction(kind) {
  try {
    const usage = await fetchUsage();
    
    // Premium users have unlimited access
    if (usage.isPremium) {
      return true;
    }
    
    // Check remaining quota
    if (kind === 'view') {
      return usage.remainingViews > 0;
    } else if (kind === 'like') {
      return usage.remainingLikes > 0;
    }
    
    return false;
  } catch (error) {
    console.error('Failed to check action permission:', error);
    return false;
  }
}
