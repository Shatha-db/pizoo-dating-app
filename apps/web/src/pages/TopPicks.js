import React, { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import { Card } from '../components/ui/card';
import { Button } from '../components/ui/button';
import BottomNav from '../components/BottomNav';
import { Star, Sparkles, Heart, X, MapPin } from 'lucide-react';
import axios from 'axios';

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

const TopPicks = () => {
  const navigate = useNavigate();
  const { token } = useAuth();
  const [topPicks, setTopPicks] = useState([]);
  const [loading, setLoading] = useState(true);
  const [currentIndex, setCurrentIndex] = useState(0);

  useEffect(() => {
    fetchTopPicks();
  }, []);

  const fetchTopPicks = async () => {
    try {
      const response = await axios.get(`${API}/profiles/top-picks`, {
        headers: { Authorization: `Bearer ${token}` }
      });
      setTopPicks(response.data.profiles || []);
    } catch (error) {
      console.error('Error fetching top picks:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleSwipe = async (action) => {
    if (currentIndex >= topPicks.length) return;

    const currentProfile = topPicks[currentIndex];

    try {
      const response = await axios.post(
        `${API}/swipe`,
        {
          swiped_user_id: currentProfile.user_id,
          action: action
        },
        {
          headers: { Authorization: `Bearer ${token}` }
        }
      );

      if (response.data.is_match) {
        // Show match modal
        alert('🎉 تهانينا! لديك تطابق جديد!');
      }

      // Move to next profile
      setCurrentIndex(currentIndex + 1);
    } catch (error) {
      console.error('Error swiping:', error);
    }
  };

  const handleViewProfile = (profile) => {
    navigate(`/profile/${profile.user_id}`);
  };

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-gray-50">
        <div className="animate-spin rounded-full h-16 w-16 border-b-4 border-pink-500"></div>
      </div>
    );
  }

  const currentProfile = topPicks[currentIndex];

  return (
    <div className="min-h-screen bg-gradient-to-br from-purple-50 via-pink-50 to-white pb-20" dir="rtl">
      {/* Header */}
      <header className="bg-white shadow-sm p-4 sticky top-0 z-10">
        <div className="flex items-center justify-between">
          <h1 className="text-2xl font-bold flex items-center gap-2">
            <Sparkles className="w-6 h-6 text-purple-500" />
            اختيارات اليوم
          </h1>
          <div className="text-sm text-gray-600">
            {currentIndex + 1}/{topPicks.length}
          </div>
        </div>
      </header>

      <main className="max-w-md mx-auto p-4">
        {currentProfile ? (
          <div className="space-y-4">
            {/* Top Pick Badge */}
            <div className="flex items-center justify-center gap-2 bg-gradient-to-r from-purple-500 to-pink-500 text-white py-3 px-6 rounded-full shadow-lg">
              <Star className="w-5 h-5 fill-current" />
              <span className="font-bold">تطابق مميز لك اليوم</span>
            </div>

            {/* Profile Card */}
            <Card className="overflow-hidden shadow-xl">
              <div className="relative">
                {/* Main Photo */}
                <div className="aspect-[3/4] relative bg-gradient-to-br from-pink-300 to-purple-300">
                  {currentProfile.photos && currentProfile.photos.length > 0 ? (
                    <img
                      src={currentProfile.photos[0]}
                      alt={currentProfile.display_name}
                      className="w-full h-full object-cover cursor-pointer"
                      onClick={() => handleViewProfile(currentProfile)}
                    />
                  ) : (
                    <div className="w-full h-full flex items-center justify-center text-8xl">
                      ❤️
                    </div>
                  )}

                  {/* Gradient Overlay */}
                  <div className="absolute inset-0 bg-gradient-to-t from-black/70 via-transparent to-transparent" />

                  {/* Profile Info Overlay */}
                  <div className="absolute bottom-0 left-0 right-0 p-6 text-white">
                    <h2 className="text-3xl font-bold mb-2">
                      {currentProfile.display_name}
                      {currentProfile.age && `, ${currentProfile.age}`}
                    </h2>
                    
                    {currentProfile.location && (
                      <div className="flex items-center gap-2 text-sm mb-2">
                        <MapPin className="w-4 h-4" />
                        <span>{currentProfile.location}</span>
                      </div>
                    )}

                    {currentProfile.occupation && (
                      <p className="text-sm opacity-90 mb-3">💼 {currentProfile.occupation}</p>
                    )}

                    {currentProfile.bio && (
                      <p className="text-sm leading-relaxed line-clamp-3">
                        {currentProfile.bio}
                      </p>
                    )}
                  </div>

                  {/* Top Pick Star Badge */}
                  <div className="absolute top-4 right-4 bg-yellow-400 text-black p-2 rounded-full shadow-lg">
                    <Star className="w-6 h-6 fill-current" />
                  </div>
                </div>
              </div>

              {/* Interests */}
              {currentProfile.interests && currentProfile.interests.length > 0 && (
                <div className="p-4 border-t">
                  <div className="flex flex-wrap gap-2">
                    {currentProfile.interests.slice(0, 5).map((interest, i) => (
                      <span
                        key={i}
                        className="bg-gradient-to-r from-pink-100 to-purple-100 text-gray-800 px-3 py-1 rounded-full text-sm"
                      >
                        {interest}
                      </span>
                    ))}
                    {currentProfile.interests.length > 5 && (
                      <span className="text-gray-500 text-sm">
                        +{currentProfile.interests.length - 5} المزيد
                      </span>
                    )}
                  </div>
                </div>
              )}
            </Card>

            {/* Why This Pick? */}
            <Card className="p-4 bg-gradient-to-r from-purple-50 to-pink-50">
              <div className="flex items-start gap-3">
                <Sparkles className="w-5 h-5 text-purple-500 flex-shrink-0 mt-1" />
                <div>
                  <h3 className="font-bold text-gray-800 mb-1">لماذا هذا الاختيار؟</h3>
                  <p className="text-sm text-gray-600">
                    اخترنا هذا الملف الشخصي لك بناءً على اهتماماتك المشتركة، موقعك، وأهداف علاقتك.
                  </p>
                </div>
              </div>
            </Card>

            {/* Action Buttons */}
            <div className="flex items-center justify-center gap-4 py-4">
              <button
                onClick={() => handleSwipe('pass')}
                className="w-16 h-16 rounded-full bg-white shadow-lg flex items-center justify-center hover:scale-110 transition-transform border-2 border-gray-200"
              >
                <X className="w-8 h-8 text-gray-500" />
              </button>

              <button
                onClick={() => handleViewProfile(currentProfile)}
                className="w-14 h-14 rounded-full bg-purple-500 text-white shadow-lg flex items-center justify-center hover:scale-110 transition-transform"
              >
                <Star className="w-6 h-6" />
              </button>

              <button
                onClick={() => handleSwipe('like')}
                className="w-20 h-20 rounded-full bg-gradient-to-r from-pink-500 to-red-500 text-white shadow-lg flex items-center justify-center hover:scale-110 transition-transform"
              >
                <Heart className="w-10 h-10 fill-current" />
              </button>
            </div>
          </div>
        ) : (
          <div className="text-center py-20">
            <Sparkles className="w-20 h-20 text-purple-300 mx-auto mb-4" />
            <h2 className="text-2xl font-bold text-gray-700 mb-2">
              لا مزيد من الاختيارات اليوم
            </h2>
            <p className="text-gray-600 mb-6">
              عد غداً لاختيارات جديدة مميزة!
            </p>
            <Button
              onClick={() => navigate('/home')}
              className="bg-gradient-to-r from-purple-500 to-pink-500 text-white"
            >
              العودة إلى الرئيسية
            </Button>
          </div>
        )}
      </main>

      <BottomNav />
    </div>
  );
};

export default TopPicks;
