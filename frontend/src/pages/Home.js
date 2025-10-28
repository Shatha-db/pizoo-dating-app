import React, { useEffect, useState } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import { useNotifications } from '../context/NotificationContext';
import { useTranslation } from 'react-i18next';
import { Button } from '../components/ui/button';
import { Card } from '../components/ui/card';
import BottomNav from '../components/BottomNav';
import CustomLogo from '../components/CustomLogo';
import LocationPermissionRequest from '../components/LocationPermissionRequest';
import GeoPermissionModal from '../components/GeoPermissionModal';
import { Heart, X, Star, RotateCcw, Zap, Info, Bell } from 'lucide-react';
import axios from 'axios';
import { 
  getCurrentPosition, 
  reverseGeocode, 
  getCountryFromIP, 
  getDefaultRadius,
  validateCoordinates
} from '../utils/geoUtils';
import '../styles/home-cta.css';

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

const Home = () => {
  const navigate = useNavigate();
  const { token } = useAuth();
  const { unreadCount } = useNotifications();
  const { t } = useTranslation(['home', 'common']);
  const [profiles, setProfiles] = useState([]);
  const [currentIndex, setCurrentIndex] = useState(0);
  const [loading, setLoading] = useState(true);
  const [showMatch, setShowMatch] = useState(false);
  const [showNewLikesPopup, setShowNewLikesPopup] = useState(false);
  const [newLikesCount, setNewLikesCount] = useState(0);
  const [swipeHistory, setSwipeHistory] = useState([]); // Store last 5 swipes
  const [canRewind, setCanRewind] = useState(false);
  const [boostActive, setBoostActive] = useState(false);
  const [boostTimeRemaining, setBoostTimeRemaining] = useState(0);
  const [usageStats, setUsageStats] = useState(null);
  const [showLimitWarning, setShowLimitWarning] = useState(false);
  const [showLocationRequest, setShowLocationRequest] = useState(false);
  const [showGeoModal, setShowGeoModal] = useState(false);
  const [geoLoading, setGeoLoading] = useState(false);

  useEffect(() => {
    fetchProfiles();
    checkNewLikes();
    checkBoostStatus();
    fetchUsageStats();
    checkGeoPermission();
  }, []);

  const checkGeoPermission = async () => {
    try {
      // Check if location already granted
      const hasLocation = localStorage.getItem('location_granted');
      const locationDenied = localStorage.getItem('location_denied');
      
      if (hasLocation) {
        console.log('✅ Location already granted');
        return;
      }
      
      if (locationDenied) {
        console.log('ℹ️ Location previously denied, using GeoIP fallback');
        await handleGeoIPFallback();
        return;
      }
      
      // Fetch user data first to check if location is already set
      try {
        const res = await axios.get(`${API}/me`, {
          headers: { Authorization: `Bearer ${token}` }
        });
        
        const user = res.data;
        
        // Only show modal if user doesn't have location or country
        if (user && !user.latitude && !user.longitude && !user.country) {
          // Show geo modal after 2 seconds
          setTimeout(() => {
            setShowGeoModal(true);
          }, 2000);
        }
      } catch (error) {
        console.error('Error fetching user data for geo check:', error);
      }
      
    } catch (error) {
      console.error('Error checking geo permission:', error);
    }
  };

  const handleAllowGPS = async () => {
    setGeoLoading(true);
    try {
      console.log('📍 Requesting GPS permission...');
      
      // Get GPS coordinates
      const position = await getCurrentPosition();
      console.log('✅ GPS coordinates obtained:', position);
      
      // Safe number guards
      const safeLat = Number(position.latitude);
      const safeLng = Number(position.longitude);
      
      // Validate coordinates with safe checks
      if (!Number.isFinite(safeLat) || !Number.isFinite(safeLng)) {
        throw new Error('Invalid coordinates - NaN detected');
      }
      
      if (!validateCoordinates(safeLat, safeLng)) {
        throw new Error('Invalid coordinates - out of range');
      }
      
      // Reverse geocode to get country
      const geoData = await reverseGeocode(safeLat, safeLng);
      console.log('✅ Reverse geocoding complete:', geoData);
      
      // Get default radius for country
      const defaultRadius = getDefaultRadius(geoData.countryCode);
      const safeRadius = Number(defaultRadius);
      console.log(`📍 Default radius for ${geoData.countryCode}: ${safeRadius}km`);
      
      // Save to backend with try-catch
      try {
        await axios.put(`${API}/user/location`, {
          country: geoData.countryCode,
          latitude: safeLat,
          longitude: safeLng,
          radiusKm: Number.isFinite(safeRadius) && safeRadius > 0 ? safeRadius : 25
        }, {
          headers: { Authorization: `Bearer ${token}` }
        });
      } catch (apiError) {
        console.error('API error saving location:', apiError);
        throw apiError;
      }
      
      // Save to localStorage
      localStorage.setItem('location_granted', 'true');
      localStorage.setItem('user_country', geoData.countryCode || '');
      localStorage.setItem('user_latitude', safeLat.toString());
      localStorage.setItem('user_longitude', safeLng.toString());
      
      console.log('✅ Location saved successfully');
      setShowGeoModal(false);
      
    } catch (error) {
      console.error('❌ GPS permission error:', error);
      
      // Fallback to GeoIP if GPS fails
      if (error.code === 1) {
        // User denied permission
        localStorage.setItem('location_denied', 'true');
        await handleGeoIPFallback();
      } else {
        alert(t('home:locationError'));
        await handleGeoIPFallback();
      }
      
      setShowGeoModal(false);
    } finally {
      setGeoLoading(false);
    }
  };

  const handleDenyGPS = async () => {
    console.log('ℹ️ User denied GPS, using GeoIP fallback');
    localStorage.setItem('location_denied', 'true');
    setShowGeoModal(false);
    await handleGeoIPFallback();
  };

  const handleManualEntry = () => {
    console.log('ℹ️ User chose manual entry');
    setShowGeoModal(false);
    // Navigate to discovery settings for manual city entry
    navigate('/discovery-settings');
  };

  const handleGeoIPFallback = async () => {
    try {
      console.log('🌐 Using GeoIP fallback...');
      
      const geoData = await getCountryFromIP();
      console.log('✅ GeoIP data obtained:', geoData);
      
      const defaultRadius = getDefaultRadius(geoData.countryCode);
      const safeRadius = Number(defaultRadius);
      
      // Save country only (no precise coordinates) with try-catch
      try {
        await axios.put(`${API}/user/location`, {
          country: geoData.countryCode,
          latitude: null,
          longitude: null,
          radiusKm: Number.isFinite(safeRadius) && safeRadius > 0 ? safeRadius : 25
        }, {
          headers: { Authorization: `Bearer ${token}` }
        });
      } catch (apiError) {
        console.error('API error in GeoIP fallback:', apiError);
        // Continue anyway - not critical
      }
      
      localStorage.setItem('user_country', geoData.countryCode || '');
      console.log(`✅ GeoIP fallback complete: ${geoData.countryCode}`);
      
    } catch (error) {
      console.error('❌ GeoIP fallback error:', error);
      // Silent fail - user can still use app without location
    }
  };

  const fetchUsageStats = async () => {
    try {
      const response = await axios.get(`${API}/usage-stats`, {
        headers: { Authorization: `Bearer ${token}` }
      });
      setUsageStats(response.data);
    } catch (error) {
      console.error('Error fetching usage stats:', error);
    }
  };

  const fetchProfiles = async () => {
    try {
      const response = await axios.get(`${API}/profiles/discover?limit=50`, {
        headers: { Authorization: `Bearer ${token}` }
      });
      setProfiles(response.data.profiles);
    } catch (error) {
      console.error('Error:', error);
    } finally {
      setLoading(false);
    }
  };

  const checkNewLikes = async () => {
    try {
      const response = await axios.get(`${API}/likes/received`, {
        headers: { Authorization: `Bearer ${token}` }
      });
      const likesCount = response.data.profiles?.length || 0;
      
      // Show popup if there are new likes (simulate new likes check)
      const lastSeenCount = localStorage.getItem('lastSeenLikesCount') || 0;
      if (likesCount > lastSeenCount && likesCount > 0) {
        setNewLikesCount(likesCount);
        setShowNewLikesPopup(true);
      }
    } catch (error) {
      console.error('Error checking likes:', error);
    }
  };

  const handleDismissLikesPopup = () => {
    localStorage.setItem('lastSeenLikesCount', newLikesCount.toString());
    setShowNewLikesPopup(false);
  };

  const handleSwipe = async (action) => {
    if (!currentProfile) return;
    
    // Check if user has reached limit before making the request
    if (usageStats && !usageStats.is_premium && action !== 'pass') {
      if (usageStats.likes.remaining <= 0) {
        setShowLimitWarning(true);
        return;
      }
    }
    
    // Save swipe to history (keep last 5)
    const newHistory = [...swipeHistory, {
      profile: currentProfile,
      action: action,
      index: currentIndex
    }].slice(-5);
    setSwipeHistory(newHistory);
    setCanRewind(true);
    
    try {
      const response = await axios.post(`${API}/swipe`, {
        swiped_user_id: currentProfile.user_id,
        action
      }, {
        headers: { Authorization: `Bearer ${token}` }
      });
      
      if (response.data.is_match) {
        setShowMatch(true);
        setTimeout(() => setShowMatch(false), 3000);
      }
      
      // Update usage stats if returned
      if (response.data.remaining_likes !== undefined) {
        setUsageStats(prev => ({
          ...prev,
          likes: {
            ...prev.likes,
            remaining: response.data.remaining_likes,
            sent: prev.likes.sent + 1
          }
        }));
        
        // Show warning if getting close to limit
        if (response.data.remaining_likes <= 2 && response.data.remaining_likes > 0) {
          setShowLimitWarning(true);
          setTimeout(() => setShowLimitWarning(false), 3000);
        }
      }
      
      setCurrentIndex(currentIndex + 1);
    } catch (error) {
      console.error('Error:', error);
      // Check if it's a 403 error (limit reached)
      if (error.response && error.response.status === 403) {
        setShowLimitWarning(true);
        // Refresh usage stats
        fetchUsageStats();
      }
    }
  };

  const handleRewind = () => {
    if (swipeHistory.length === 0) return;
    
    // Get last swipe
    const lastSwipe = swipeHistory[swipeHistory.length - 1];
    
    // Remove from history
    setSwipeHistory(swipeHistory.slice(0, -1));
    
    // Go back to that profile
    setCurrentIndex(lastSwipe.index);
    
    // Check if we can still rewind
    setCanRewind(swipeHistory.length > 1);
  };

  const checkBoostStatus = async () => {
    try {
      const response = await axios.get(`${API}/boost/status`, {
        headers: { Authorization: `Bearer ${token}` }
      });

      if (response.data.is_active) {
        setBoostActive(true);
        setBoostTimeRemaining(response.data.time_remaining_seconds);
        
        // Start countdown
        const interval = setInterval(() => {
          setBoostTimeRemaining(prev => {
            if (prev <= 1) {
              clearInterval(interval);
              setBoostActive(false);
              return 0;
            }
            return prev - 1;
          });
        }, 1000);
      }
    } catch (error) {
      console.error('Error checking boost:', error);
    }
  };

  const handleBoost = async () => {
    if (boostActive) return;

    try {
      const response = await axios.post(`${API}/boost/activate`, {}, {
        headers: { Authorization: `Bearer ${token}` }
      });

      setBoostActive(true);
      setBoostTimeRemaining(30 * 60); // 30 minutes
      
      // Start countdown
      const interval = setInterval(() => {
        setBoostTimeRemaining(prev => {
          if (prev <= 1) {
            clearInterval(interval);
            setBoostActive(false);
            return 0;
          }
          return prev - 1;
        });
      }, 1000);

      alert(t('home:boostActivated'));
    } catch (error) {
      console.error('Error activating boost:', error);
      alert(t('home:boostError'));
    }
  };

  const formatTime = (seconds) => {
    const mins = Math.floor(seconds / 60);
    const secs = seconds % 60;
    return `${mins}:${secs.toString().padStart(2, '0')}`;
  };

  const currentProfile = profiles[currentIndex];

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="animate-spin rounded-full h-16 w-16 border-b-4 border-pink-500"></div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-pink-50 via-pink-25 to-rose-50 dark:from-gray-200 dark:via-gray-300 dark:to-gray-400 pb-20" dir="rtl">
      {/* Header */}
      <header className="bg-pink-50/80 dark:bg-gray-200 shadow-sm p-4 flex justify-between items-center sticky top-0 z-10 backdrop-blur-sm">
        <div className="flex gap-2">
          <Button 
            variant="ghost" 
            size="icon"
            onClick={() => navigate('/discovery')}
            title={t('home:discoveryMap')}
          >
            <svg className="w-6 h-6 text-gray-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 20l-5.447-2.724A1 1 0 013 16.382V5.618a1 1 0 011.447-.894L9 7m0 13l6-3m-6 3V7m6 10l4.553 2.276A1 1 0 0021 18.382V7.618a1 1 0 00-.553-.894L15 4m0 13V4m0 0L9 7" />
            </svg>
          </Button>
        </div>
        <div className="flex items-center flex-1 justify-center">
          <CustomLogo size="lg" />
        </div>
        <div className="flex gap-2">
          {/* Notification Bell */}
          <Button 
            variant="ghost" 
            size="icon"
            onClick={() => navigate('/notifications')}
            title={t('home:notifications')}
            className="relative"
          >
            <Bell className="w-6 h-6 text-gray-600" />
            {unreadCount > 0 && (
              <span className="absolute -top-1 -right-1 bg-red-500 text-white text-xs w-5 h-5 rounded-full flex items-center justify-center font-bold">
                {unreadCount > 9 ? '9+' : unreadCount}
              </span>
            )}
          </Button>
          
          <Button 
            variant="ghost" 
            size="icon"
            onClick={() => navigate('/double-dating')}
            title={t('home:doubleDate')}
          >
            <svg className="w-6 h-6 text-pink-500" viewBox="0 0 24 24" fill="none" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M17 20h5v-2a3 3 0 00-5.356-1.857M17 20H7m10 0v-2c0-.656-.126-1.283-.356-1.857M7 20H2v-2a3 3 0 015.356-1.857M7 20v-2c0-.656.126-1.283.356-1.857m0 0a5.002 5.002 0 019.288 0M15 7a3 3 0 11-6 0 3 3 0 016 0zm6 3a2 2 0 11-4 0 2 2 0 014 0zM7 10a2 2 0 11-4 0 2 2 0 014 0z" />
            </svg>
          </Button>
          <Button 
            variant="ghost" 
            size="icon"
            onClick={() => navigate('/top-picks')}
            title={t('home:topPicks')}
          >
            <Star className="w-6 h-6 text-yellow-500 fill-yellow-500" />
          </Button>
          <Button 
            variant="ghost" 
            size="icon"
            onClick={handleBoost}
            className="relative"
            disabled={boostActive}
          >
            <Zap className={`w-6 h-6 ${boostActive ? 'text-yellow-500 animate-pulse' : 'text-purple-500'}`} />
            {boostActive && (
              <span className="absolute -bottom-1 text-xs font-bold text-purple-600">
                {formatTime(boostTimeRemaining)}
              </span>
            )}
          </Button>
        </div>
      </header>

      {/* CTA Buttons */}
      <div className="home-ctas">
        <Link to="/explore-new" className="btn-cta explore">
          <span className="icon">✨</span>
          {t('cta.exploreNew')}
        </Link>
        <Link to="/personal" className="btn-cta personal">
          <span className="icon">🎯</span>
          {t('cta.personal')}
        </Link>
      </div>

      {/* Main Card */}
      <main className="max-w-md mx-auto px-4 pt-6">
        {currentProfile ? (
          <Card className="overflow-hidden shadow-2xl">
            <div className="relative h-96 bg-gradient-to-br from-pink-200 to-purple-200">
              {currentProfile.photos && currentProfile.photos.length > 0 ? (
                <img 
                  src={currentProfile.photos[0]} 
                  alt={currentProfile.display_name}
                  className="w-full h-full object-cover"
                />
              ) : (
                <div className="w-full h-full flex items-center justify-center">
                  <div className="text-6xl">❤️</div>
                </div>
              )}
              
              <div className="absolute bottom-0 left-0 right-0 bg-gradient-to-t from-black/70 to-transparent p-6 text-white">
                <h2 className="text-3xl font-bold">{currentProfile.display_name}</h2>
                <p className="text-lg opacity-90">{currentProfile.occupation || 'Professional'}</p>
                <div className="flex items-center gap-2 text-sm opacity-80 mt-1">
                  <span>📍 {currentProfile.location}</span>
                  {currentProfile.distance && (
                    <span className="bg-white/20 px-2 py-1 rounded-full text-xs font-semibold">
                      {currentProfile.distance} km
                    </span>
                  )}
                </div>
                {currentProfile.bio && (
                  <p className="text-sm mt-2 opacity-90">{currentProfile.bio}</p>
                )}
              </div>

              <Button 
                size="icon" 
                variant="ghost" 
                className="absolute top-4 left-4 bg-white/20 backdrop-blur"
              >
                <Info className="w-5 h-5 text-white" />
              </Button>
            </div>

            {currentProfile.interests && currentProfile.interests.length > 0 && (
              <div className="p-4">
                <div className="flex flex-wrap gap-2">
                  {currentProfile.interests.slice(0, 5).map((interest, i) => (
                    <span key={i} className="px-3 py-1 bg-pink-100 text-pink-700 rounded-full text-sm">
                      {interest}
                    </span>
                  ))}
                </div>
              </div>
            )}
          </Card>
        ) : (
          <div className="text-center py-20">
            <div className="text-6xl mb-4">😔</div>
            <p className="text-xl text-gray-600 mb-4">{t('home:noMoreProfiles')}</p>
            <Button onClick={fetchProfiles} className="bg-pink-500 hover:bg-pink-600">
              {t('home:refresh')}
            </Button>
          </div>
        )}

        {/* Action Buttons */}
        {currentProfile && (
          <div className="flex justify-center items-center gap-4 mt-6">
            <Button
              size="icon"
              className="w-14 h-14 rounded-full bg-white shadow-lg hover:shadow-xl border-2 border-yellow-400 disabled:opacity-30 disabled:cursor-not-allowed"
              onClick={handleRewind}
              disabled={!canRewind}
              title={canRewind ? t('home:undoLastAction') : t('home:cannotUndo')}
            >
              <RotateCcw className="w-6 h-6 text-yellow-500" />
            </Button>

            <Button
              size="icon"
              className="w-16 h-16 rounded-full bg-white shadow-lg hover:shadow-xl border-2 border-red-400"
              onClick={() => handleSwipe('pass')}
            >
              <X className="w-8 h-8 text-red-500" />
            </Button>

            <Button
              size="icon"
              className="w-20 h-20 rounded-full bg-gradient-to-r from-pink-500 to-red-500 shadow-lg hover:shadow-xl"
              onClick={() => handleSwipe('like')}
            >
              <Heart className="w-10 h-10 text-white" fill="white" />
            </Button>

            <Button
              size="icon"
              className="w-16 h-16 rounded-full bg-white shadow-lg hover:shadow-xl border-2 border-blue-400"
              onClick={() => handleSwipe('super_like')}
            >
              <Star className="w-8 h-8 text-blue-500" />
            </Button>

            <Button
              size="icon"
              className="w-14 h-14 rounded-full bg-white shadow-lg hover:shadow-xl border-2 border-purple-400"
            >
              <Zap className="w-6 h-6 text-purple-500" />
            </Button>
          </div>
        )}
      </main>

      {/* Match Popup */}
      {showMatch && (
        <div className="fixed inset-0 bg-gradient-to-br from-pink-500/95 to-purple-500/95 flex items-center justify-center z-50 animate-in fade-in">
          <div className="text-center text-white">
            <div className="text-8xl mb-6 animate-bounce">💕</div>
            <h2 className="text-4xl font-bold mb-2">{t('home:itsAMatch')}</h2>
            <p className="text-xl">{t('home:newMatchCreated')}</p>
          </div>
        </div>
      )}

      {/* New Likes Popup */}
      {showNewLikesPopup && (
        <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50 p-4">
          <Card className="max-w-md w-full p-6 bg-gradient-to-br from-yellow-50 to-orange-50 border-4 border-yellow-400">
            <div className="text-center">
              <div className="text-6xl mb-4">💕</div>
              <h2 className="text-2xl font-bold mb-2">
                {t('home:youHaveNewLikes', { count: newLikesCount })}
              </h2>
              <p className="text-gray-700 mb-6">
                {t('home:someoneAdmires')}
              </p>
              
              <div className="flex gap-2 mb-4">
                {[1, 2, 3, 4].slice(0, Math.min(newLikesCount, 4)).map((_, index) => (
                  <div
                    key={index}
                    className="flex-1 aspect-square rounded-lg bg-gradient-to-br from-pink-300 to-purple-300 blur-sm"
                  />
                ))}
              </div>

              <Button
                onClick={() => {
                  handleDismissLikesPopup();
                  navigate('/likes-you');
                }}
                className="w-full bg-gradient-to-r from-yellow-400 to-orange-400 hover:from-yellow-500 hover:to-orange-500 text-black font-bold text-lg py-6 mb-3"
              >
                <Zap className="w-5 h-5 ml-2" />
                {t('home:seeLikes')}
              </Button>
              
              <Button
                onClick={handleDismissLikesPopup}
                variant="ghost"
                className="w-full"
              >
                {t('home:maybeLater')}
              </Button>
            </div>
          </Card>
        </div>
      )}

      {/* Limit Warning Modal */}
      {showLimitWarning && (
        <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50 p-4">
          <Card className="max-w-md w-full p-6 bg-gradient-to-br from-purple-50 to-pink-50">
            <div className="text-center">
              <div className="text-6xl mb-4">⏰</div>
              <h2 className="text-2xl font-bold mb-2 text-gray-800">
                {t('home:weeklyLimitReached')}
              </h2>
              <p className="text-gray-600 mb-1">
                {t('home:freeUsersHave')}
              </p>
              <ul className="text-right mb-6 space-y-2">
                <li className="flex items-center justify-center gap-2">
                  <span className="font-semibold">12 إعجاب</span>
                  <Heart className="w-5 h-5 text-pink-500" />
                </li>
                <li className="flex items-center justify-center gap-2">
                  <span className="font-semibold">10 رسائل</span>
                  <span className="text-xl">💬</span>
                </li>
                <li className="text-sm text-gray-500">كل أسبوع</li>
              </ul>

              <Button
                onClick={() => {
                  setShowLimitWarning(false);
                  navigate('/premium');
                }}
                className="w-full bg-gradient-to-r from-pink-500 to-purple-500 hover:from-pink-600 hover:to-purple-600 text-white font-bold text-lg py-6 mb-3"
              >
                <Star className="w-5 h-5 ml-2 fill-white" />
                ترقية إلى Premium
              </Button>
              
              <Button
                onClick={() => setShowLimitWarning(false)}
                variant="ghost"
                className="w-full"
              >
                إغلاق
              </Button>
            </div>
          </Card>
        </div>
      )}

      {/* Location Permission Request */}
      {showLocationRequest && (
        <LocationPermissionRequest
          onClose={() => setShowLocationRequest(false)}
          token={token}
        />
      )}

      {/* Geo Permission Modal (Phase 5) */}
      {showGeoModal && (
        <GeoPermissionModal
          onAllow={handleAllowGPS}
          onDeny={handleDenyGPS}
          onManual={handleManualEntry}
          onClose={() => setShowGeoModal(false)}
        />
      )}

      <BottomNav />
    </div>
  );
};

export default Home;
