// Animation utility functions for Pizoo UI
// Uses CSS classes defined in theme.css + framer-motion

/**
 * Trigger heart burst animation on an element
 */
export const heartBurst = (element) => {
  if (!element) return;
  element.classList.add('animate-heartBurst');
  setTimeout(() => element.classList.remove('animate-heartBurst'), 300);
};

/**
 * Trigger shake animation on an element
 */
export const shake = (element) => {
  if (!element) return;
  element.classList.add('animate-shake');
  setTimeout(() => element.classList.remove('animate-shake'), 400);
};

/**
 * Trigger pulse animation on an element
 */
export const pulse = (element) => {
  if (!element) return;
  element.classList.add('animate-pulse');
  setTimeout(() => element.classList.remove('animate-pulse'), 600);
};

/**
 * Framer Motion variants for common animations
 */
export const motionVariants = {
  // Fade in from bottom
  slideUp: {
    initial: { y: 20, opacity: 0 },
    animate: { y: 0, opacity: 1 },
    exit: { y: -20, opacity: 0 },
    transition: { duration: 0.3 }
  },
  
  // Fade in
  fadeIn: {
    initial: { opacity: 0 },
    animate: { opacity: 1 },
    exit: { opacity: 0 },
    transition: { duration: 0.2 }
  },
  
  // Scale up
  scaleUp: {
    initial: { scale: 0.9, opacity: 0 },
    animate: { scale: 1, opacity: 1 },
    exit: { scale: 0.9, opacity: 0 },
    transition: { duration: 0.2 }
  },
  
  // Swipe card
  swipeCard: {
    enter: (direction) => ({
      x: direction > 0 ? 1000 : -1000,
      opacity: 0
    }),
    center: {
      zIndex: 1,
      x: 0,
      opacity: 1
    },
    exit: (direction) => ({
      zIndex: 0,
      x: direction < 0 ? 1000 : -1000,
      opacity: 0
    })
  },
  
  // Button press
  buttonPress: {
    whileTap: { scale: 0.95 },
    whileHover: { scale: 1.05 }
  },
  
  // Badge bounce
  badgeBounce: {
    initial: { scale: 0 },
    animate: { scale: 1 },
    transition: {
      type: "spring",
      stiffness: 500,
      damping: 15
    }
  }
};

/**
 * Get swipe direction indicator styles
 */
export const getSwipeIndicator = (direction, distance) => {
  const opacity = Math.min(Math.abs(distance) / 100, 1);
  
  if (direction === 'right') {
    return {
      type: 'like',
      icon: '❤️',
      color: 'var(--color-green)',
      opacity
    };
  } else if (direction === 'left') {
    return {
      type: 'nope',
      icon: '✕',
      color: 'var(--color-red)',
      opacity
    };
  } else if (direction === 'up') {
    return {
      type: 'superlike',
      icon: '⭐',
      color: 'var(--color-blue)',
      opacity
    };
  }
  
  return null;
};

/**
 * Haptic feedback (for mobile)
 */
export const hapticFeedback = (type = 'light') => {
  if (typeof window !== 'undefined' && window.navigator && window.navigator.vibrate) {
    const patterns = {
      light: [10],
      medium: [20],
      heavy: [30],
      success: [10, 50, 10],
      error: [20, 100, 20]
    };
    window.navigator.vibrate(patterns[type] || patterns.light);
  }
};
