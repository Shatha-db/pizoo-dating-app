import React, { useEffect, useState } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import { Button } from '../components/ui/button';
import { Card } from '../components/ui/card';
import { ArrowRight, MapPin, Briefcase, Heart, X, MessageCircle, Star, MoreVertical, Flag, Ban } from 'lucide-react';
import axios from 'axios';

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

const ProfileView = () => {
  const { userId } = useParams();
  const navigate = useNavigate();
  const { token } = useAuth();
  const [profile, setProfile] = useState(null);
  const [loading, setLoading] = useState(true);
  const [currentPhotoIndex, setCurrentPhotoIndex] = useState(0);
  const [toast, setToast] = useState(null);
  const [showOptionsMenu, setShowOptionsMenu] = useState(false);
  const [showReportModal, setShowReportModal] = useState(false);
  const [reportReason, setReportReason] = useState('');
  const [reportDetails, setReportDetails] = useState('');

  useEffect(() => {
    fetchProfile();
  }, [userId]);

  const fetchProfile = async () => {
    try {
      // Fetch all profiles and find the one with matching user_id
      const response = await axios.get(`${API}/profiles/discover?limit=100`, {
        headers: { Authorization: `Bearer ${token}` }
      });
      
      const userProfile = response.data.profiles.find(p => p.user_id === userId);
      
      if (userProfile) {
        setProfile(userProfile);
      } else {
        showToast('البروفايل غير موجود');
        navigate(-1);
      }
    } catch (error) {
      console.error('Error fetching profile:', error);
      showToast('حدث خطأ في تحميل البروفايل');
      navigate(-1);
    } finally {
      setLoading(false);
    }
  };

  const handleSwipe = async (action) => {
    try {
      const response = await axios.post(`${API}/swipe`, {
        swiped_user_id: userId,
        action: action
      }, {
        headers: { Authorization: `Bearer ${token}` }
      });

      if (response.data.is_match) {
        showToast('🎉 تهانينا! لديك تطابق جديد!');
        setTimeout(() => {
          navigate('/matches');
        }, 2000);
      } else if (action === 'like' || action === 'super_like') {
        showToast('تم الإعجاب! 💕');
        setTimeout(() => navigate(-1), 1500);
      } else {
        navigate(-1);
      }
    } catch (error) {
      console.error('Error swiping:', error);
      showToast('حدث خطأ، حاول مرة أخرى');
    }
  };

  const handleMessage = async () => {
    try {
      // Check if match exists
      const matchesRes = await axios.get(`${API}/matches`, {
        headers: { Authorization: `Bearer ${token}` }
      });
      
      const match = matchesRes.data.matches.find(m => 
        m.profile.user_id === userId
      );

      if (match) {
        // Match exists, go to chat
        navigate(`/chat/${match.match_id}`);
      } else {
        // No match, send like first
        showToast('قم بالإعجاب أولاً لفتح المحادثة!');
      }
    } catch (error) {
      console.error('Error:', error);
      showToast('حدث خطأ، حاول مرة أخرى');
    }
  };

  const showToast = (message) => {
    setToast(message);
    setTimeout(() => setToast(null), 3000);
  };

  const nextPhoto = () => {
    if (profile?.photos && currentPhotoIndex < profile.photos.length - 1) {
      setCurrentPhotoIndex(currentPhotoIndex + 1);
    }
  };

  const prevPhoto = () => {
    if (currentPhotoIndex > 0) {
      setCurrentPhotoIndex(currentPhotoIndex - 1);
    }
  };

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-gray-50">
        <div className="animate-spin rounded-full h-16 w-16 border-b-4 border-pink-500"></div>
      </div>
    );
  }

  if (!profile) {
    return null;
  }

  return (
    <div className="min-h-screen bg-gray-50" dir="rtl">
      {/* Toast Notification */}
      {toast && (
        <div className="fixed top-4 left-1/2 transform -translate-x-1/2 bg-black/90 text-white px-6 py-3 rounded-full z-50 shadow-lg">
          {toast}
        </div>
      )}

      {/* Header */}
      <header className="bg-white shadow-sm p-4 sticky top-0 z-10 flex items-center gap-3">
        <button
          onClick={() => navigate(-1)}
          className="p-2 hover:bg-gray-100 rounded-full"
        >
          <ArrowRight className="w-6 h-6" />
        </button>
        <h1 className="text-xl font-bold">البروفايل</h1>
      </header>

      <main className="max-w-2xl mx-auto">
        {/* Photo Gallery */}
        <div className="relative">
          <div className="aspect-[3/4] relative bg-gray-200">
            {profile.photos && profile.photos.length > 0 ? (
              <>
                <img
                  src={profile.photos[currentPhotoIndex]}
                  alt={profile.display_name}
                  className="w-full h-full object-cover"
                />
                
                {/* Photo Navigation */}
                {profile.photos.length > 1 && (
                  <>
                    {/* Click areas for navigation */}
                    <div 
                      className="absolute left-0 top-0 w-1/3 h-full cursor-pointer"
                      onClick={nextPhoto}
                    />
                    <div 
                      className="absolute right-0 top-0 w-1/3 h-full cursor-pointer"
                      onClick={prevPhoto}
                    />
                    
                    {/* Dots indicator */}
                    <div className="absolute top-4 left-1/2 transform -translate-x-1/2 flex gap-1">
                      {profile.photos.map((_, index) => (
                        <div
                          key={index}
                          className={`h-1 rounded-full transition-all ${
                            index === currentPhotoIndex
                              ? 'bg-white w-8'
                              : 'bg-white/50 w-1'
                          }`}
                        />
                      ))}
                    </div>
                  </>
                )}
              </>
            ) : (
              <div className="w-full h-full bg-gradient-to-br from-pink-300 to-purple-300 flex items-center justify-center text-8xl">
                ❤️
              </div>
            )}
          </div>
        </div>

        {/* Profile Info */}
        <div className="p-6 space-y-6">
          {/* Name and Age */}
          <div>
            <h1 className="text-3xl font-bold flex items-center gap-2">
              {profile.display_name}
              {profile.age && <span className="text-2xl font-normal text-gray-600">{profile.age}</span>}
            </h1>
          </div>

          {/* Location */}
          {profile.location && (
            <div className="flex items-center gap-2 text-gray-600">
              <MapPin className="w-5 h-5" />
              <span>{profile.location}</span>
            </div>
          )}

          {/* Occupation */}
          {profile.occupation && (
            <div className="flex items-center gap-2 text-gray-600">
              <Briefcase className="w-5 h-5" />
              <span>{profile.occupation}</span>
            </div>
          )}

          {/* Bio */}
          {profile.bio && (
            <Card className="p-4 bg-gray-50">
              <p className="text-gray-700 leading-relaxed">{profile.bio}</p>
            </Card>
          )}

          {/* Stats */}
          <div className="grid grid-cols-3 gap-4">
            {profile.height && (
              <Card className="p-4 text-center">
                <div className="text-2xl font-bold text-pink-500">{profile.height}</div>
                <div className="text-sm text-gray-600">الطول (سم)</div>
              </Card>
            )}
            {profile.gender && (
              <Card className="p-4 text-center">
                <div className="text-2xl font-bold text-pink-500">
                  {profile.gender === 'male' ? '👨' : profile.gender === 'female' ? '👩' : '🧑'}
                </div>
                <div className="text-sm text-gray-600">
                  {profile.gender === 'male' ? 'ذكر' : profile.gender === 'female' ? 'أنثى' : 'آخر'}
                </div>
              </Card>
            )}
            {profile.languages && profile.languages.length > 0 && (
              <Card className="p-4 text-center">
                <div className="text-2xl font-bold text-pink-500">{profile.languages.length}</div>
                <div className="text-sm text-gray-600">لغات</div>
              </Card>
            )}
          </div>

          {/* Interests */}
          {profile.interests && profile.interests.length > 0 && (
            <div>
              <h3 className="font-bold text-lg mb-3">الاهتمامات</h3>
              <div className="flex flex-wrap gap-2">
                {profile.interests.map((interest, index) => (
                  <span
                    key={index}
                    className="bg-gradient-to-r from-pink-100 to-purple-100 text-gray-800 px-4 py-2 rounded-full text-sm font-medium"
                  >
                    {interest}
                  </span>
                ))}
              </div>
            </div>
          )}

          {/* Languages */}
          {profile.languages && profile.languages.length > 0 && (
            <div>
              <h3 className="font-bold text-lg mb-3">اللغات</h3>
              <div className="flex flex-wrap gap-2">
                {profile.languages.map((language, index) => (
                  <span
                    key={index}
                    className="bg-blue-100 text-blue-800 px-4 py-2 rounded-full text-sm font-medium"
                  >
                    {language}
                  </span>
                ))}
              </div>
            </div>
          )}
        </div>

        {/* Action Buttons */}
        <div className="fixed bottom-0 left-0 right-0 bg-white border-t border-gray-200 p-4">
          <div className="max-w-2xl mx-auto flex items-center justify-center gap-4">
            <button
              onClick={() => handleSwipe('pass')}
              className="w-16 h-16 rounded-full bg-white shadow-lg flex items-center justify-center hover:scale-110 transition-transform border-2 border-gray-200"
            >
              <X className="w-8 h-8 text-gray-500" />
            </button>
            
            <button
              onClick={handleMessage}
              className="w-14 h-14 rounded-full bg-blue-500 text-white shadow-lg flex items-center justify-center hover:scale-110 transition-transform"
            >
              <MessageCircle className="w-6 h-6" />
            </button>
            
            <button
              onClick={() => handleSwipe('like')}
              className="w-20 h-20 rounded-full bg-gradient-to-r from-pink-500 to-red-500 text-white shadow-lg flex items-center justify-center hover:scale-110 transition-transform"
            >
              <Heart className="w-10 h-10 fill-current" />
            </button>
            
            <button
              onClick={() => handleSwipe('super_like')}
              className="w-14 h-14 rounded-full bg-blue-400 text-white shadow-lg flex items-center justify-center hover:scale-110 transition-transform"
            >
              <Star className="w-6 h-6 fill-current" />
            </button>
          </div>
        </div>

        {/* Bottom padding for action buttons */}
        <div className="h-24"></div>
      </main>
    </div>
  );
};

export default ProfileView;
