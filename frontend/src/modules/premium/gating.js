/**
 * Pizoo Premium Gating System
 * Tracks daily profile views and enforces limits for free users
 */

const STORAGE_KEY = 'pizoo_viewed_today';
const DEFAULT_LIMIT = 10;

/**
 * Get current gating state
 * @returns {Object} { day, viewedToday, limit, gated, remaining }
 */
export function getGatingState() {
  const raw = localStorage.getItem(STORAGE_KEY);
  const today = new Date().toISOString().slice(0, 10);
  let viewedToday = 0;
  let day = today;

  if (raw) {
    try {
      const data = JSON.parse(raw);
      if (data.day === today) {
        viewedToday = data.viewedToday || 0;
      }
    } catch (e) {
      console.warn('Failed to parse gating state:', e);
    }
  }

  const limit = DEFAULT_LIMIT;
  const gated = viewedToday >= limit;
  const remaining = Math.max(0, limit - viewedToday);

  return { day, viewedToday, limit, gated, remaining };
}

/**
 * Increment view counter
 */
export function incView() {
  const { day, viewedToday } = getGatingState();
  const next = { day, viewedToday: viewedToday + 1 };
  localStorage.setItem(STORAGE_KEY, JSON.stringify(next));
}

/**
 * Reset counter if new day
 * Call this on app mount
 */
export function resetDayIfNeeded() {
  const today = new Date().toISOString().slice(0, 10);
  const raw = localStorage.getItem(STORAGE_KEY);
  
  if (!raw) {
    localStorage.setItem(STORAGE_KEY, JSON.stringify({ day: today, viewedToday: 0 }));
    return;
  }

  try {
    const data = JSON.parse(raw);
    if (data.day !== today) {
      localStorage.setItem(STORAGE_KEY, JSON.stringify({ day: today, viewedToday: 0 }));
    }
  } catch (e) {
    console.warn('Failed to reset day:', e);
  }
}

/**
 * Check if user is premium (stub - will be replaced with API call)
 * @returns {boolean}
 */
export async function checkPremiumStatus() {
  try {
    const response = await fetch(`${process.env.REACT_APP_BACKEND_URL}/api/upsell/context`, {
      credentials: 'include',
      headers: {
        'Authorization': `Bearer ${localStorage.getItem('token')}`
      }
    });
    if (response.ok) {
      const data = await response.json();
      return data.isPremium || false;
    }
  } catch (e) {
    console.warn('Failed to check premium status:', e);
  }
  return false;
}

/**
 * Get super like quota
 * @returns {number}
 */
export async function getSuperLikeQuota() {
  try {
    const response = await fetch(`${process.env.REACT_APP_BACKEND_URL}/api/upsell/context`, {
      credentials: 'include',
      headers: {
        'Authorization': `Bearer ${localStorage.getItem('token')}`
      }
    });
    if (response.ok) {
      const data = await response.json();
      return data.superLikeLeft || 0;
    }
  } catch (e) {
    console.warn('Failed to get super like quota:', e);
  }
  return 0;
}

/**
 * Record a swipe action
 * @param {string} profileId
 * @param {string} direction - 'left', 'right', 'up'
 */
export async function recordSwipe(profileId, direction) {
  try {
    await fetch(`${process.env.REACT_APP_BACKEND_URL}/api/swipe`, {
      method: 'POST',
      credentials: 'include',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${localStorage.getItem('token')}`
      },
      body: JSON.stringify({ profileId, direction })
    });
  } catch (e) {
    console.warn('Failed to record swipe:', e);
  }
}
