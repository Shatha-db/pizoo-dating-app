import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import { motion } from 'framer-motion';
import SwipeDeck from '../modules/swipe/SwipeDeck';
import axios from 'axios';

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;

export default function SwipePage() {
  const { token } = useAuth();
  const navigate = useNavigate();
  const [users, setUsers] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    fetchProfiles();
  }, []);

  const fetchProfiles = async () => {
    try {
      setLoading(true);
      const response = await axios.get(`${BACKEND_URL}/api/profiles/discover`, {
        headers: { Authorization: `Bearer ${token}` },
        params: {
          limit: 20,
          max_distance: 50
        }
      });
      
      // Format the data for SwipeDeck
      const profiles = Array.isArray(response.data) ? response.data : [];
      setUsers(profiles);
      setError(null);
    } catch (err) {
      console.error('Error fetching profiles:', err);
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  const handleSwipe = async (userId, direction) => {
    console.log(`Swiped ${direction} on user ${userId}`);
    
    try {
      // Map swipe directions to actions
      const actionMap = {
        'right': 'like',
        'left': 'pass',
        'up': 'superlike'
      };
      
      const action = actionMap[direction];
      
      // Call the swipe API (create stub if doesn't exist)
      await axios.post(
        `${BACKEND_URL}/api/swipe`,
        { 
          target_user_id: userId, 
          action: action 
        },
        { headers: { Authorization: `Bearer ${token}` } }
      );
      
      // If it's a match, you might want to show a match modal
      // For now, we'll just log it
      console.log(`Action ${action} recorded for user ${userId}`);
      
    } catch (err) {
      console.error('Error recording swipe:', err);
      // Continue anyway - optimistic UI
    }
  };

  const handleCardLeftScreen = (userId) => {
    console.log(`Card ${userId} left screen`);
    // Optional: Track analytics or update state
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center h-screen bg-gradient-to-br from-pink-50 via-orange-50 to-purple-50">
        <motion.div
          initial={{ opacity: 0, scale: 0.8 }}
          animate={{ opacity: 1, scale: 1 }}
          className="text-center"
        >
          <div className="w-16 h-16 border-4 border-pink-500 border-t-transparent rounded-full animate-spin mx-auto mb-4"></div>
          <p className="text-gray-600 font-medium">جاري التحميل...</p>
        </motion.div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="flex items-center justify-center h-screen bg-gradient-to-br from-pink-50 via-orange-50 to-purple-50 p-4">
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          className="text-center bg-white p-8 rounded-3xl shadow-xl max-w-md"
        >
          <div className="text-6xl mb-4">⚠️</div>
          <h3 className="text-xl font-bold text-gray-800 mb-2">حدث خطأ</h3>
          <p className="text-gray-600 mb-4">
            {typeof error === 'string' ? error : 'حدث خطأ'}
          </p>
          <button
            onClick={fetchProfiles}
            className="px-6 py-3 bg-gradient-to-r from-pink-500 to-orange-400 text-white rounded-full font-medium shadow-lg hover:shadow-xl transition-shadow"
          >
            إعادة المحاولة
          </button>
        </motion.div>
      </div>
    );
  }

  return (
    <div className="h-screen bg-gradient-to-br from-pink-50 via-orange-50 to-purple-50 overflow-hidden">
      {/* Header */}
      <motion.header
        initial={{ y: -50, opacity: 0 }}
        animate={{ y: 0, opacity: 1 }}
        className="flex items-center justify-between p-4 bg-white/80 backdrop-blur-lg shadow-sm"
      >
        <button
          onClick={() => navigate(-1)}
          className="w-10 h-10 rounded-full bg-gray-100 hover:bg-gray-200 transition-colors grid place-items-center"
        >
          <svg className="w-6 h-6 text-gray-600" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
            <path d="M19 12H5M12 19l-7-7 7-7"/>
          </svg>
        </button>
        
        <div className="flex items-center gap-2">
          <div className="w-8 h-8 rounded-full bg-gradient-to-br from-pink-500 to-orange-400"></div>
          <h1 className="text-xl font-bold bg-gradient-to-r from-pink-500 to-orange-400 bg-clip-text text-transparent">
            Pizoo
          </h1>
        </div>
        
        <button
          onClick={() => navigate('/settings')}
          className="w-10 h-10 rounded-full bg-gray-100 hover:bg-gray-200 transition-colors grid place-items-center"
        >
          <svg className="w-6 h-6 text-gray-600" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
            <circle cx="12" cy="12" r="3"/>
            <path d="M12 1v6m0 6v6M5.6 5.6l4.2 4.2m4.2 4.2l4.2 4.2M1 12h6m6 0h6M5.6 18.4l4.2-4.2m4.2-4.2l4.2-4.2"/>
          </svg>
        </button>
      </motion.header>

      {/* Swipe Deck */}
      <SwipeDeck
        users={users}
        onSwipe={handleSwipe}
        onCardLeftScreen={handleCardLeftScreen}
        className="h-full"
      />
    </div>
  );
}
