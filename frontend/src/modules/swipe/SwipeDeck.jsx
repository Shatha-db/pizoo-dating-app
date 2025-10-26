import React, { useState, useRef, useMemo, useEffect } from 'react';
import TinderCard from 'react-tinder-card';
import { motion, AnimatePresence } from 'framer-motion';
import { useTranslation } from 'react-i18next';
import { heartBurst, shake, hapticFeedback } from '../../utils/animations';
import { getGatingState, incView, recordSwipe } from '../premium/gating';

const ActionButton = ({ color, icon, onClick, size = 'md', label }) => {
  const sizes = {
    sm: 'w-12 h-12 text-2xl',
    md: 'w-16 h-16 text-3xl',
    lg: 'w-20 h-20 text-4xl'
  };
  
  return (
    <motion.button
      whileTap={{ scale: 0.9 }}
      whileHover={{ scale: 1.1 }}
      onClick={onClick}
      className={`${sizes[size]} rounded-full grid place-items-center shadow-xl transition-all hover:shadow-2xl active:shadow-lg`}
      style={{ background: color }}
      aria-label={label}
    >
      {icon}
    </motion.button>
  );
};

const SwipeIndicator = ({ direction, opacity }) => {
  const indicators = {
    right: { icon: '❤️', text: 'LIKE', color: 'text-green-500', rotate: -25 },
    left: { icon: '✕', text: 'NOPE', color: 'text-red-500', rotate: 25 },
    up: { icon: '⭐', text: 'SUPER', color: 'text-blue-500', rotate: 0 }
  };
  
  const config = indicators[direction];
  if (!config) return null;
  
  return (
    <motion.div
      initial={{ opacity: 0, scale: 0.8 }}
      animate={{ opacity, scale: 1 }}
      className={`absolute top-20 ${direction === 'left' ? 'right-8' : 'left-8'} z-20 pointer-events-none`}
      style={{ transform: `rotate(${config.rotate}deg)` }}
    >
      <div className={`${config.color} text-6xl font-black drop-shadow-2xl border-4 border-current px-6 py-3 rounded-2xl bg-white/90`}>
        {config.text}
      </div>
    </motion.div>
  );
};

export default function SwipeDeck({ users = [], onSwipe, onCardLeftScreen, className, gating, onGate }) {
  const { t } = useTranslation(['swipe', 'common']);
  const [currentIndex, setCurrentIndex] = useState(users.length - 1);
  const [swipeDirection, setSwipeDirection] = useState(null);
  const [swipeOpacity, setSwipeOpacity] = useState(0);
  const [localGating, setLocalGating] = useState(null);
  const currentIndexRef = useRef(currentIndex);
  
  // Use prop gating or local state
  const gatingState = gating || localGating || getGatingState();
  const canSwipe = currentIndex >= 0 && !gatingState.gated;
  
  const childRefs = useMemo(
    () =>
      Array(users.length)
        .fill(0)
        .map((i) => React.createRef()),
    [users.length]
  );
  
  // Update local gating state
  useEffect(() => {
    if (!gating) {
      setLocalGating(getGatingState());
    }
  }, [gating, currentIndex]);
  
  const updateCurrentIndex = (val) => {
    setCurrentIndex(val);
    currentIndexRef.current = val;
  };
  
  const swiped = (direction, userId, index) => {
    // Check if gated before allowing swipe
    if (gatingState.gated) {
      onGate?.('daily_limit');
      return;
    }
    
    // Increment view counter
    incView();
    setLocalGating(getGatingState());
    
    // Record swipe to backend
    recordSwipe(userId, direction);
    
    updateCurrentIndex(index - 1);
    setSwipeDirection(null);
    setSwipeOpacity(0);
    onSwipe?.(userId, direction);
    hapticFeedback(direction === 'up' ? 'heavy' : 'medium');
  };
  
  const outOfFrame = (userId, index) => {
    currentIndexRef.current >= index && childRefs[index].current?.restoreCard();
    onCardLeftScreen?.(userId);
  };
  
  const swipe = async (dir) => {
    // Check if gated
    if (gatingState.gated) {
      onGate?.('daily_limit');
      return;
    }
    
    if (canSwipe && currentIndex < users.length) {
      await childRefs[currentIndex].current.swipe(dir);
    }
  };
  
  const handleSwipeMove = (direction) => {
    setSwipeDirection(direction);
  };
  
  const handleSwipeRequirementFulfilled = (direction) => {
    setSwipeOpacity(1);
  };
  
  const handleSwipeRequirementUnfulfilled = () => {
    setSwipeOpacity(0);
  };
  
  if (users.length === 0) {
    return (
      <div className={`flex flex-col items-center justify-center h-full ${className}`}>
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          className="text-center p-8"
        >
          <div className="text-6xl mb-4">😔</div>
          <h3 className="text-xl font-bold text-gray-800 mb-2">
            {t('swipe:noMoreCards')}
          </h3>
          <p className="text-gray-600">
            {t('swipe:checkBackLater')}
          </p>
        </motion.div>
      </div>
    );
  }
  
  const currentUser = users[currentIndex];
  
  return (
    <div className={`w-full h-full flex flex-col items-center justify-between ${className}`}>
      {/* Card Stack */}
      <div className="relative w-full flex-1 flex items-center justify-center px-4 py-4">
        <div className="relative w-full max-w-md" style={{ height: 'min(70vh, 600px)' }}>
          <AnimatePresence>
            {users.map((user, index) => {
              if (index > currentIndex) return null;
              
              return (
                <TinderCard
                  ref={childRefs[index]}
                  key={user.id || user.user_id}
                  onSwipe={(dir) => swiped(dir, user.id || user.user_id, index)}
                  onCardLeftScreen={() => outOfFrame(user.id || user.user_id, index)}
                  onSwipeRequirementFulfilled={handleSwipeRequirementFulfilled}
                  onSwipeRequirementUnfulfilled={handleSwipeRequirementUnfulfilled}
                  swipeRequirementType="position"
                  swipeThreshold={100}
                  preventSwipe={['down']}
                  className="absolute inset-0"
                >
                  <motion.div
                    initial={{ scale: index === currentIndex ? 1 : 0.95 }}
                    animate={{ scale: index === currentIndex ? 1 : 0.95 }}
                    className="relative w-full h-full rounded-3xl overflow-hidden shadow-2xl"
                    style={{
                      zIndex: users.length - index,
                      transform: `translateY(${(currentIndex - index) * 8}px)`
                    }}
                  >
                    {/* Swipe Direction Indicator */}
                    {index === currentIndex && swipeDirection && (
                      <SwipeIndicator direction={swipeDirection} opacity={swipeOpacity} />
                    )}
                    
                    {/* Profile Image */}
                    <img
                      src={user.photos?.[0]?.url || user.photos?.[0] || user.primary_photo || '/placeholder-profile.jpg'}
                      alt={user.display_name || user.name}
                      className={`w-full h-full object-cover ${gatingState.gated ? 'blur-xl scale-105' : ''}`}
                      draggable={false}
                    />
                    
                    {/* Gating Overlay */}
                    {gatingState.gated && index === currentIndex && (
                      <motion.div
                        initial={{ opacity: 0 }}
                        animate={{ opacity: 1 }}
                        className="absolute inset-0 bg-black/60 backdrop-blur-md flex flex-col items-center justify-center p-6 text-center pointer-events-none"
                      >
                        <div className="pointer-events-auto">
                          <div className="text-6xl mb-4">🔒</div>
                          <h3 className="text-2xl font-bold text-white mb-2">
                            {t('swipe:daily_limit_reached')}
                          </h3>
                          <p className="text-white/80 mb-4 text-sm">
                            {t('swipe:upgrade_to_continue', { remaining: gatingState.remaining })}
                          </p>
                          <motion.button
                            whileTap={{ scale: 0.95 }}
                            onClick={() => onGate?.('daily_limit')}
                            className="px-8 py-3 rounded-full bg-gradient-to-r from-[#F59E0B] to-[#EA580C] text-white font-semibold shadow-xl hover:brightness-110 transition-all"
                          >
                            {t('swipe:upgrade_now')}
                          </motion.button>
                        </div>
                      </motion.div>
                    )}
                    
                    {/* Gradient Overlay */}
                    <div className="absolute inset-0 bg-gradient-to-t from-black/80 via-black/20 to-transparent" />
                    
                    {/* Profile Info */}
                    <div className="absolute bottom-0 inset-x-0 p-6 text-white">
                      <motion.div
                        initial={{ opacity: 0, y: 20 }}
                        animate={{ opacity: 1, y: 0 }}
                        transition={{ delay: 0.1 }}
                      >
                        <div className="flex items-baseline gap-2 mb-2">
                          <h2 className="text-3xl font-bold">
                            {user.display_name || user.name}
                          </h2>
                          {user.age && (
                            <span className="text-2xl font-light opacity-90">
                              {user.age}
                            </span>
                          )}
                        </div>
                        
                        <div className="flex items-center gap-2 text-sm opacity-90 mb-3">
                          {user.location && (
                            <span className="flex items-center gap-1">
                              <svg className="w-4 h-4" viewBox="0 0 24 24" fill="currentColor">
                                <path d="M12 2C8.13 2 5 5.13 5 9c0 5.25 7 13 7 13s7-7.75 7-13c0-3.87-3.13-7-7-7zm0 9.5c-1.38 0-2.5-1.12-2.5-2.5s1.12-2.5 2.5-2.5 2.5 1.12 2.5 2.5-1.12 2.5-2.5 2.5z"/>
                              </svg>
                              {user.location}
                            </span>
                          )}
                          {user.distance && (
                            <span>• {user.distance < 1 ? '<1' : Math.round(user.distance)} km</span>
                          )}
                        </div>
                        
                        {/* Quick Info Tags */}
                        {user.interests && user.interests.length > 0 && (
                          <div className="flex flex-wrap gap-2">
                            {user.interests.slice(0, 3).map((interest, i) => (
                              <span
                                key={i}
                                className="px-3 py-1 rounded-full bg-white/20 backdrop-blur-sm text-xs font-medium"
                              >
                                {interest}
                              </span>
                            ))}
                            {user.interests.length > 3 && (
                              <span className="px-3 py-1 rounded-full bg-white/20 backdrop-blur-sm text-xs font-medium">
                                +{user.interests.length - 3}
                              </span>
                            )}
                          </div>
                        )}
                      </motion.div>
                    </div>
                  </motion.div>
                </TinderCard>
              );
            })}
          </AnimatePresence>
        </div>
      </div>
      
      {/* Action Buttons */}
      <motion.div
        initial={{ opacity: 0, y: 50 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.2 }}
        className="flex items-center justify-center gap-4 pb-24 px-4"
      >
        <ActionButton
          color="linear-gradient(135deg, #f87171 0%, #ef4444 100%)"
          label={t('swipe:reject')}
          icon={
            <svg className="w-8 h-8 text-white" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="3">
              <line x1="18" y1="6" x2="6" y2="18"/>
              <line x1="6" y1="6" x2="18" y2="18"/>
            </svg>
          }
          onClick={() => swipe('left')}
        />
        
        <ActionButton
          color="linear-gradient(135deg, #60a5fa 0%, #3b82f6 100%)"
          size="md"
          label={t('swipe:superLike')}
          icon={<span className="text-white text-2xl">⭐</span>}
          onClick={() => swipe('up')}
        />
        
        <ActionButton
          color="linear-gradient(135deg, #34d399 0%, #10b981 100%)"
          size="lg"
          label={t('swipe:like')}
          icon={
            <svg className="w-10 h-10 text-white" viewBox="0 0 24 24" fill="currentColor">
              <path d="M20.84 4.61a5.5 5.5 0 0 0-7.78 0L12 5.67l-1.06-1.06a5.5 5.5 0 0 0-7.78 7.78l1.06 1.06L12 21.23l7.78-7.78 1.06-1.06a5.5 5.5 0 0 0 0-7.78z"/>
            </svg>
          }
          onClick={() => swipe('right')}
        />
      </motion.div>
    </div>
  );
}
