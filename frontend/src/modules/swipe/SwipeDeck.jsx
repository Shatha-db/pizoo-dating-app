import React, { useState, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { useTranslation } from 'react-i18next';
import { useNavigate } from 'react-router-dom';
import { getGatingState, incView, recordSwipe } from '../premium/gating';
import PhotoLightbox from '../media/PhotoLightbox';

export default function SwipeDeck({ users = [], onSwipe, className, gating, onGate }) {
  const { t } = useTranslation('swipe');
  const navigate = useNavigate();
  const [currentIndex, setCurrentIndex] = useState(0);
  const [localGating, setLocalGating] = useState(null);
  const [showLightbox, setShowLightbox] = useState(false);
  const [startAt, setStartAt] = useState(0);
  
  // Use prop gating or local state
  const gatingState = gating || localGating || getGatingState();
  const currentUser = users[currentIndex];
  
  // Update local gating state
  useEffect(() => {
    if (!gating) {
      setLocalGating(getGatingState());
    }
  }, [gating, currentIndex]);
  
  const openLightbox = (index = 0) => {
    setStartAt(index);
    setShowLightbox(true);
  };
  
  const visitProfile = () => {
    if (currentUser?.id) {
      navigate(`/profile/${currentUser.id}`);
    }
  };
  
  const handleSwipe = (direction) => {
    // Check if gated
    if (gatingState.gated) {
      onGate?.('daily_limit');
      return;
    }
    
    if (!currentUser) return;
    
    // Increment view counter
    incView();
    setLocalGating(getGatingState());
    
    // Record swipe to backend
    recordSwipe(currentUser.id, direction);
    
    // Move to next card
    setCurrentIndex(prev => prev + 1);
    onSwipe?.(currentUser.id, direction);
  };
  
  if (!currentUser) {
    return (
      <div className={`w-full h-full flex items-center justify-center ${className || ''}`}>
        <div className="text-center">
          <div className="text-6xl mb-4">🎉</div>
          <h3 className="text-xl font-bold text-gray-700 mb-2">
            No more profiles
          </h3>
          <p className="text-gray-500">
            Check back later for new matches!
          </p>
        </div>
      </div>
    );
  }
  
  return (
    <div className={`w-full h-full flex flex-col items-center justify-between ${className || ''}`}>
      {/* Gating Counter (top banner) */}
      {!gatingState.gated && gatingState.remaining <= 3 && gatingState.remaining > 0 && (
        <motion.div
          initial={{ y: -20, opacity: 0 }}
          animate={{ y: 0, opacity: 1 }}
          className="w-full bg-gradient-to-r from-orange-500 to-pink-500 text-white px-4 py-2 text-center text-sm font-semibold shadow-lg"
        >
          {gatingState.remaining} swipes remaining today
        </motion.div>
      )}
      
      {/* Card */}
      <div className="relative w-full flex-1 flex items-center justify-center px-4 py-4">
        <AnimatePresence mode="wait">
          <motion.div
            key={currentUser.id}
            initial={{ scale: 0.9, opacity: 0 }}
            animate={{ scale: 1, opacity: 1 }}
            exit={{ scale: 0.9, opacity: 0 }}
            transition={{ duration: 0.2 }}
            className="relative w-full max-w-sm h-[600px] rounded-3xl overflow-hidden shadow-2xl"
          >
            {/* Profile Image */}
            <img
              src={currentUser.photos?.[0]?.url || currentUser.photos?.[0] || '/placeholder-profile.jpg'}
              alt={currentUser.display_name || currentUser.name}
              className={`w-full h-full object-cover ${gatingState.gated ? 'blur-xl scale-105' : ''}`}
            />
            
            {/* Gating Overlay */}
            {gatingState.gated && (
              <motion.div
                initial={{ opacity: 0 }}
                animate={{ opacity: 1 }}
                className="absolute inset-0 bg-black/60 backdrop-blur-md flex flex-col items-center justify-center p-6 text-center"
              >
                <div className="text-6xl mb-4">🔒</div>
                <h3 className="text-2xl font-bold text-white mb-2">
                  Daily Limit Reached
                </h3>
                <p className="text-white/80 mb-4 text-sm">
                  Upgrade to keep swiping!
                </p>
                <motion.button
                  whileTap={{ scale: 0.95 }}
                  onClick={() => onGate?.('daily_limit')}
                  className="px-8 py-3 rounded-full bg-gradient-to-r from-[#F59E0B] to-[#EA580C] text-white font-semibold shadow-xl hover:brightness-110 transition-all"
                >
                  Upgrade Now
                </motion.button>
              </motion.div>
            )}
            
            {/* Gradient Overlay */}
            <div className="absolute inset-0 bg-gradient-to-t from-black/80 via-black/20 to-transparent" />
            
            {/* Profile Info */}
            <div className="absolute bottom-0 left-0 right-0 p-6 text-white">
              <h2 className="text-3xl font-bold mb-1">
                {currentUser.display_name || currentUser.name}, {currentUser.age || '??'}
              </h2>
              {currentUser.bio && (
                <p className="text-sm text-white/90 line-clamp-2">
                  {currentUser.bio}
                </p>
              )}
            </div>
          </motion.div>
        </AnimatePresence>
      </div>
      
      {/* Action Buttons */}
      <div className="flex items-center justify-center gap-6 pb-6">
        <motion.button
          whileTap={{ scale: 0.9 }}
          onClick={() => handleSwipe('left')}
          disabled={gatingState.gated}
          className="w-16 h-16 rounded-full bg-white shadow-xl flex items-center justify-center text-2xl hover:scale-110 transition-transform disabled:opacity-50"
        >
          ✕
        </motion.button>
        
        <motion.button
          whileTap={{ scale: 0.9 }}
          onClick={() => handleSwipe('up')}
          disabled={gatingState.gated}
          className="w-14 h-14 rounded-full bg-blue-500 shadow-xl flex items-center justify-center text-2xl text-white hover:scale-110 transition-transform disabled:opacity-50"
        >
          ⭐
        </motion.button>
        
        <motion.button
          whileTap={{ scale: 0.9 }}
          onClick={() => handleSwipe('right')}
          disabled={gatingState.gated}
          className="w-16 h-16 rounded-full bg-gradient-to-r from-pink-500 to-rose-500 shadow-xl flex items-center justify-center text-2xl text-white hover:scale-110 transition-transform disabled:opacity-50"
        >
          ❤️
        </motion.button>
      </div>
    </div>
  );
}
