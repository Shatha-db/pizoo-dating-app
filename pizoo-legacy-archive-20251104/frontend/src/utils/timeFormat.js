/**
 * Format timestamp to relative time (e.g., "5 minutes ago")
 * Supports both Arabic and English
 */
export const formatRelativeTime = (timestamp, lang = 'ar') => {
  if (!timestamp) return '';
  
  const now = new Date();
  const messageTime = new Date(timestamp);
  const diffMs = now - messageTime;
  const diffSeconds = Math.floor(diffMs / 1000);
  const diffMinutes = Math.floor(diffSeconds / 60);
  const diffHours = Math.floor(diffMinutes / 60);
  const diffDays = Math.floor(diffHours / 24);

  if (lang === 'ar') {
    if (diffSeconds < 60) return 'الآن';
    if (diffMinutes < 60) return `منذ ${diffMinutes} ${diffMinutes === 1 ? 'دقيقة' : 'دقائق'}`;
    if (diffHours < 24) return `منذ ${diffHours} ${diffHours === 1 ? 'ساعة' : 'ساعات'}`;
    if (diffDays < 7) return `منذ ${diffDays} ${diffDays === 1 ? 'يوم' : 'أيام'}`;
    
    // Format as date if older than 7 days
    return messageTime.toLocaleDateString('ar-SA', { 
      month: 'short', 
      day: 'numeric',
      year: messageTime.getFullYear() !== now.getFullYear() ? 'numeric' : undefined
    });
  } else {
    if (diffSeconds < 60) return 'Just now';
    if (diffMinutes < 60) return `${diffMinutes}m ago`;
    if (diffHours < 24) return `${diffHours}h ago`;
    if (diffDays < 7) return `${diffDays}d ago`;
    
    // Format as date if older than 7 days
    return messageTime.toLocaleDateString('en-US', { 
      month: 'short', 
      day: 'numeric',
      year: messageTime.getFullYear() !== now.getFullYear() ? 'numeric' : undefined
    });
  }
};

/**
 * Format timestamp to time string (e.g., "2:30 PM")
 */
export const formatTimeOnly = (timestamp, lang = 'ar') => {
  if (!timestamp) return '';
  
  const messageTime = new Date(timestamp);
  return messageTime.toLocaleTimeString(lang === 'ar' ? 'ar-SA' : 'en-US', {
    hour: 'numeric',
    minute: '2-digit',
    hour12: true
  });
};
