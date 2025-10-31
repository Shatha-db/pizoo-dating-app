import React, { useEffect, useState } from 'react';
import { useAuth } from '../context/AuthContext';
import { Button } from '../components/ui/button';
import { Card } from '../components/ui/card';
import { Heart, X, User, MapPin, Briefcase, Sparkles, Star } from 'lucide-react';
import { useTranslation } from 'react-i18next';
import axios from 'axios';

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

const Discover = () => {
  const { token, logout } = useAuth();
  const { t, i18n } = useTranslation(['discover', 'common']);
  const [profiles, setProfiles] = useState([]);
  const [currentIndex, setCurrentIndex] = useState(0);
  const [loading, setLoading] = useState(true);
  const [useAI, setUseAI] = useState(true);  // Toggle for AI matching

  useEffect(() => {
    fetchProfiles();
  }, [useAI]);

  const fetchProfiles = async () => {
    setLoading(true);
    try {
      const endpoint = useAI ? '/ai/match' : '/profiles/discover';
      const response = await axios.get(`${API}${endpoint}`, {
        headers: { Authorization: `Bearer ${token}` }
      });
      
      if (useAI) {
        // AI matching response format
        setProfiles(response.data.matches || []);
      } else {
        // Regular discover response format
        setProfiles(response.data.profiles || []);
      }
    } catch (error) {
      console.error('Error fetching profiles:', error);
      // Fallback to regular discover if AI fails
      if (useAI) {
        setUseAI(false);
      }
    } finally {
      setLoading(false);
    }
  };

  const handleLike = async () => {
    try {
      const profile = profiles[currentIndex];
      const profileId = useAI ? profile.profile?.id : profile.user_id;
      
      await axios.post(
        `${API}/likes/send`,
        { liked_user_id: profileId },
        { headers: { Authorization: `Bearer ${token}` } }
      );
      
      // Track analytics
      if (window.analytics) {
        window.analytics.track('like_sent', { profile_id: profileId });
      }
    } catch (error) {
      console.error('Error sending like:', error);
    }
    
    if (currentIndex < profiles.length - 1) {
      setCurrentIndex(currentIndex + 1);
    }
  };

  const handlePass = () => {
    if (currentIndex < profiles.length - 1) {
      setCurrentIndex(currentIndex + 1);
    }
  };

  const getCompatibilityBadge = (score) => {
    if (score >= 70) return { text: t('high_compatibility', 'High'), color: 'bg-green-500' };
    if (score >= 50) return { text: t('medium_compatibility', 'Medium'), color: 'bg-yellow-500' };
    return { text: t('good_compatibility', 'Good'), color: 'bg-blue-500' };
  };

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-gray-50" dir={i18n.language === 'ar' ? 'rtl' : 'ltr'}>
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-pink-600 mx-auto"></div>
          <p className="mt-4 text-gray-600">{t('loading_matches', 'Finding your matches...')}</p>
        </div>
      </div>
    );
  }

  const currentProfile = profiles[currentIndex];
  
  // Extract profile data based on source (AI vs regular)
  const profileData = useAI ? currentProfile?.profile : currentProfile;
  const matchScore = currentProfile?.matchScore;
  const matchReasons = currentProfile?.matchReasons || [];
  const compatibility = currentProfile?.compatibility;

  if (!profileData) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-pink-50 via-white to-purple-50 flex items-center justify-center" dir={i18n.language === 'ar' ? 'rtl' : 'ltr'}>
        <div className="text-center p-8">
          <Heart className="w-16 h-16 text-gray-300 mx-auto mb-4" />
          <h2 className="text-xl font-bold text-gray-700 mb-2">{t('no_more_profiles', 'No more profiles')}</h2>
          <p className="text-gray-500 mb-4">{t('check_back_later', 'Check back later for new matches!')}</p>
          <Button onClick={() => window.location.reload()} className="bg-pink-500 hover:bg-pink-600">
            {t('refresh', 'Refresh')}
          </Button>
        </div>
      </div>
    );
  }

  const compatBadge = matchScore ? getCompatibilityBadge(matchScore) : null;

  return (
    <div className="min-h-screen bg-gradient-to-br from-pink-50 via-white to-purple-50" dir={i18n.language === 'ar' ? 'rtl' : 'ltr'}>
      <header className="bg-white shadow-sm border-b p-4">
        <div className="max-w-7xl mx-auto flex justify-between items-center">
          <div className="flex items-center gap-3">
            <h1 className="text-2xl font-bold text-pink-600">💕 {t('discover', 'Discover')}</h1>
            {useAI && (
              <span className="flex items-center gap-1 text-xs bg-purple-100 text-purple-700 px-2 py-1 rounded-full">
                <Sparkles className="w-3 h-3" />
                {t('ai_powered', 'AI Powered')}
              </span>
            )}
          </div>
          <div className="flex items-center gap-2">
            <Button 
              variant="outline" 
              size="sm"
              onClick={() => setUseAI(!useAI)}
              className="text-xs"
            >
              {useAI ? t('regular_mode', 'Regular') : t('ai_mode', 'AI Match')}
            </Button>
            <Button variant="ghost" onClick={logout}>{t('logout', 'Logout')}</Button>
          </div>
        </div>
      </header>

      <main className="max-w-md mx-auto p-4 pt-8">
        <Card className="overflow-hidden shadow-2xl">
          {/* Match Score Badge - Only for AI matches */}
          {useAI && matchScore && compatBadge && (
            <div className="absolute top-4 right-4 z-10 flex items-center gap-2">
              <div className={`${compatBadge.color} text-white px-3 py-1 rounded-full text-sm font-bold flex items-center gap-1`}>
                <Star className="w-4 h-4" />
                {matchScore}% {compatBadge.text}
              </div>
            </div>
          )}
          
          {/* Profile Image */}
          <div className="relative h-96 bg-gradient-to-br from-pink-200 to-purple-200 flex items-center justify-center">
            {profileData.photos && profileData.photos[0] ? (
              <img 
                src={profileData.photos[0]} 
                alt={profileData.name}
                className="w-full h-full object-cover"
              />
            ) : (
              <User className="w-32 h-32 text-white" />
            )}
            
            {/* Profile overlay info */}
            <div className="absolute bottom-0 left-0 right-0 bg-gradient-to-t from-black/70 to-transparent p-4 text-white">
              <h2 className="text-2xl font-bold">
                {profileData.name}, {profileData.age || '?'}
              </h2>
              {profileData.location?.city && (
                <div className="flex items-center gap-1 text-sm">
                  <MapPin className="w-4 h-4" />
                  {profileData.location.city}
                </div>
              )}
            </div>
          </div>
          
          {/* Profile Details */}
          <div className="p-6 space-y-4">
            {/* Match Reasons - AI only */}
            {useAI && matchReasons.length > 0 && (
              <div className="bg-purple-50 border border-purple-200 rounded-lg p-3">
                <h3 className="font-bold text-purple-900 mb-2 flex items-center gap-2">
                  <Sparkles className="w-4 h-4" />
                  {t('why_match', 'Why you match:')}
                </h3>
                <ul className="space-y-1">
                  {matchReasons.map((reason, idx) => (
                    <li key={idx} className="text-sm text-purple-700 flex items-center gap-2">
                      <span className="w-1.5 h-1.5 bg-purple-500 rounded-full"></span>
                      {reason}
                    </li>
                  ))}
                </ul>
              </div>
            )}
            
            {/* Bio */}
            {profileData.bio && (
              <div>
                <h3 className="font-bold text-gray-700 mb-1">{t('about', 'About')}</h3>
                <p className="text-gray-600 text-sm">{profileData.bio}</p>
              </div>
            )}
            
            {/* Occupation */}
            {profileData.occupation && (
              <div className="flex items-center gap-2 text-gray-600">
                <Briefcase className="w-4 h-4" />
                <span className="text-sm">{profileData.occupation}</span>
              </div>
            )}
            
            {/* Interests */}
            {profileData.interests && profileData.interests.length > 0 && (
              <div>
                <h3 className="font-bold text-gray-700 mb-2">{t('interests', 'Interests')}</h3>
                <div className="flex flex-wrap gap-2">
                  {profileData.interests.map((interest, idx) => (
                    <span 
                      key={idx}
                      className="bg-pink-100 text-pink-700 text-xs px-3 py-1 rounded-full"
                    >
                      {interest}
                    </span>
                  ))}
                </div>
              </div>
            )}
            
            {/* Action Buttons */}
            <div className="flex gap-4 pt-4">
              <Button
                onClick={handlePass}
                variant="outline"
                className="flex-1 h-14 border-2 border-gray-300 hover:border-gray-400"
              >
                <X className="w-6 h-6 text-gray-500" />
              </Button>
              <Button
                onClick={handleLike}
                className="flex-1 h-14 bg-gradient-to-r from-pink-500 to-red-500 hover:from-pink-600 hover:to-red-600"
              >
                <Heart className="w-6 h-6" />
              </Button>
            </div>
            
            {/* Profile counter */}
            <div className="text-center text-sm text-gray-500">
              {currentIndex + 1} / {profiles.length}
            </div>
          </div>
        </Card>
      </main>
    </div>
  );
};

export default Discover;
              <div className="space-y-2 text-sm text-gray-600">
                {currentProfile.location && (
                  <div className="flex items-center gap-2">
                    <MapPin className="w-4 h-4" />
                    {currentProfile.location}
                  </div>
                )}
                {currentProfile.occupation && (
                  <div className="flex items-center gap-2">
                    <Briefcase className="w-4 h-4" />
                    {currentProfile.occupation}
                  </div>
                )}
                {currentProfile.interests && currentProfile.interests.length > 0 && (
                  <div className="flex flex-wrap gap-2 mt-2">
                    {currentProfile.interests.map((interest, i) => (
                      <span key={i} className="px-2 py-1 bg-pink-100 text-pink-700 rounded-full text-xs">
                        {interest}
                      </span>
                    ))}
                  </div>
                )}
              </div>
            </div>
          </Card>
        ) : (
          <div className="text-center py-12">
            <p className="text-gray-600">لا توجد مزيد من الملفات الشخصية الآن</p>
            <Button onClick={fetchProfiles} className="mt-4">تحديث</Button>
          </div>
        )}

        {currentProfile && (
          <div className="flex justify-center gap-6 mt-6">
            <Button
              size="lg"
              variant="outline"
              className="rounded-full w-16 h-16 border-2 border-red-500 hover:bg-red-50"
              onClick={handlePass}
            >
              <X className="w-8 h-8 text-red-500" />
            </Button>
            <Button
              size="lg"
              className="rounded-full w-16 h-16 bg-pink-500 hover:bg-pink-600"
              onClick={handleLike}
            >
              <Heart className="w-8 h-8 text-white" />
            </Button>
          </div>
        )}
      </main>
    </div>
  );
};

export default Discover;
