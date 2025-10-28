import React, { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import { useTranslation } from 'react-i18next';
import { Button } from '../components/ui/button';
import { Card } from '../components/ui/card';
import BottomNav from '../components/BottomNav';
import { Settings, Edit, LogOut, Heart, Star, Users, Shield, X } from 'lucide-react';
import axios from 'axios';

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

const Profile = () => {
  const navigate = useNavigate();
  const { token, logout } = useAuth();
  const { t } = useTranslation('profile');
  const [profile, setProfile] = useState(null);
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);
  const [completionScore, setCompletionScore] = useState(0);
  const [showPhotoModal, setShowPhotoModal] = useState(false);
  const [selectedPhotoIndex, setSelectedPhotoIndex] = useState(0);

  useEffect(() => {
    fetchProfileData();
  }, []);

  const fetchProfileData = async () => {
    try {
      const [profileRes, userRes] = await Promise.all([
        axios.get(`${API}/profile/me`, {
          headers: { Authorization: `Bearer ${token}` }
        }),
        axios.get(`${API}/user/profile`, {
          headers: { Authorization: `Bearer ${token}` }
        })
      ]);
      const profileData = profileRes.data;
      setProfile(profileData);
      setUser(userRes.data);
      
      // Calculate completion score
      calculateCompletionScore(profileData);
    } catch (error) {
      console.error('Error fetching profile:', error);
    } finally {
      setLoading(false);
    }
  };

  const calculateCompletionScore = (profile) => {
    if (!profile) {
      setCompletionScore(0);
      return;
    }

    let score = 0;
    const maxScore = 100;

    // Photos (30 points - 10 per photo, max 3)
    if (profile.photos && profile.photos.length > 0) {
      score += Math.min(profile.photos.length * 10, 30);
    }

    // Basic info (20 points)
    if (profile.display_name) score += 5;
    if (profile.age) score += 5;
    if (profile.location) score += 5;
    if (profile.occupation) score += 5;

    // Bio (10 points)
    if (profile.bio && profile.bio.length > 50) score += 10;
    else if (profile.bio) score += 5;

    // Interests (10 points)
    if (profile.interests && profile.interests.length >= 3) score += 10;
    else if (profile.interests && profile.interests.length > 0) score += 5;

    // Languages (10 points)
    if (profile.languages && profile.languages.length >= 2) score += 10;
    else if (profile.languages && profile.languages.length > 0) score += 5;

    // Lifestyle info (10 points)
    if (profile.pets) score += 2;
    if (profile.drinking) score += 2;
    if (profile.smoking) score += 2;
    if (profile.exercise) score += 2;
    if (profile.dietary_preference) score += 2;

    // Relationship goals (5 points)
    if (profile.relationship_goals) score += 5;

    // Education (5 points)
    if (profile.education) score += 5;

    setCompletionScore(Math.min(score, maxScore));
  };

  const getMissingFields = () => {
    if (!profile) return [];
    
    const missing = [];
    
    if (!profile.photos || profile.photos.length < 3) {
      missing.push(t('addMorePhotos'));
    }
    if (!profile.bio || profile.bio.length < 50) {
      missing.push(t('writeLongerBio'));
    }
    if (!profile.interests || profile.interests.length < 3) {
      missing.push(t('addMoreInterests'));
    }
    if (!profile.languages || profile.languages.length < 2) {
      missing.push(t('addLanguages'));
    }
    if (!profile.occupation) {
      missing.push(t('addOccupation'));
    }
    
    return missing;
  };

  const handleLogout = () => {
    logout();
    navigate('/login');
  };

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="animate-spin rounded-full h-16 w-16 border-b-4 border-pink-500"></div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-gray-50 to-gray-100 pb-20" dir="rtl">
      {/* Header */}
      <header className="bg-white shadow-sm p-4 flex justify-between items-center">
        <h1 className="text-2xl font-bold">{t('myAccount')}</h1>
        <Button variant="ghost" size="icon" onClick={() => navigate('/settings')}>
          <Settings className="w-6 h-6" />
        </Button>
      </header>

      <main className="max-w-md mx-auto p-4 space-y-4">
        {/* Profile Completion Card */}
        <Card className="p-4 bg-gradient-to-r from-green-50 to-blue-50">
          <div className="flex items-center justify-between mb-2">
            <h3 className="font-bold text-lg">{t('profileCompletion')}</h3>
            <span className={`text-2xl font-bold ${
              completionScore >= 80 ? 'text-green-600' : 
              completionScore >= 50 ? 'text-yellow-600' : 'text-red-600'
            }`}>
              {completionScore}%
            </span>
          </div>
          
          {/* Progress Bar */}
          <div className="w-full bg-gray-200 rounded-full h-3 mb-3">
            <div 
              className={`h-full rounded-full transition-all duration-500 ${
                completionScore >= 80 ? 'bg-green-500' : 
                completionScore >= 50 ? 'bg-yellow-500' : 'bg-red-500'
              }`}
              style={{ width: `${completionScore}%` }}
            />
          </div>
          
          {completionScore < 100 && (
            <div>
              <p className="text-sm text-gray-700 mb-2 font-medium">{t('toImproveProfile')}</p>
              <ul className="space-y-1">
                {getMissingFields().slice(0, 3).map((field, index) => (
                  <li key={index} className="text-sm text-gray-600 flex items-start gap-2">
                    <span className="text-orange-500 mt-0.5">•</span>
                    <span>{field}</span>
                  </li>
                ))}
              </ul>
              {completionScore < 80 && (
                <p className="text-xs text-gray-500 mt-2">
                  💡 {t('completeProfileTip')}
                </p>
              )}
            </div>
          )}
          
          {completionScore === 100 && (
            <div className="flex items-center gap-2 text-green-600">
              <Star className="w-5 h-5 fill-current" />
              <span className="font-medium">{t('excellentComplete')}</span>
            </div>
          )}
        </Card>

        {/* Profile Card */}
        <Card className="overflow-hidden">
          <div className="relative h-48 bg-gradient-to-br from-pink-400 to-purple-500 cursor-pointer" onClick={() => {
            if (profile?.photos && profile.photos.length > 0) {
              setSelectedPhotoIndex(0);
              setShowPhotoModal(true);
            }
          }}>
            {profile?.photos && profile.photos.length > 0 ? (
              <img 
                src={profile.photos[0]} 
                alt={profile.display_name}
                className="w-full h-full object-cover hover:opacity-90 transition-opacity"
              />
            ) : (
              <div className="w-full h-full flex items-center justify-center text-white text-6xl">
                👤
              </div>
            )}
            {profile?.photos && profile.photos.length > 1 && (
              <div className="absolute bottom-2 right-2 bg-black bg-opacity-60 text-white px-3 py-1 rounded-full text-sm">
                +{profile.photos.length - 1} صور
              </div>
            )}
          </div>
          
          <div className="p-6 text-center">
            <h2 className="text-2xl font-bold mb-1">
              {profile?.display_name || user?.name || 'مستخدم'}
            </h2>
            {profile?.occupation && (
              <p className="text-gray-600 mb-2">{profile.occupation}</p>
            )}
            {profile?.location && (
              <p className="text-sm text-gray-500 mb-4">📍 {profile.location}</p>
            )}
            
            {profile?.bio && (
              <p className="text-gray-700 text-sm mb-4">{profile.bio}</p>
            )}

            <Button 
              className="w-full bg-gradient-to-r from-pink-500 to-purple-500 text-white"
              onClick={() => navigate('/profile/edit')}
            >
              <Edit className="w-4 h-4 ml-2" />
              تعديل البروفايل
            </Button>
          </div>
        </Card>

        {/* Profile Details */}
        {profile && (
          <Card className="p-4">
            <h3 className="font-bold text-lg mb-3">التفاصيل</h3>
            <div className="space-y-2 text-sm">
              {profile.gender && (
                <div className="flex justify-between">
                  <span className="text-gray-600">الجنس:</span>
                  <span className="font-medium">{profile.gender === 'male' ? 'ذكر' : profile.gender === 'female' ? 'أنثى' : 'آخر'}</span>
                </div>
              )}
              {profile.height && (
                <div className="flex justify-between">
                  <span className="text-gray-600">الطول:</span>
                  <span className="font-medium">{profile.height} سم</span>
                </div>
              )}
              {profile.relationship_goals && (
                <div className="flex justify-between">
                  <span className="text-gray-600">الهدف:</span>
                  <span className="font-medium">{profile.relationship_goals}</span>
                </div>
              )}
              {profile.education && (
                <div className="flex justify-between">
                  <span className="text-gray-600">التعليم:</span>
                  <span className="font-medium">{profile.education}</span>
                </div>
              )}
            </div>
          </Card>
        )}

        {/* Interests */}
        {profile?.interests && profile.interests.length > 0 && (
          <Card className="p-4">
            <h3 className="font-bold text-lg mb-3">الاهتمامات</h3>
            <div className="flex flex-wrap gap-2">
              {profile.interests.map((interest, i) => (
                <span 
                  key={i} 
                  className="px-3 py-1 bg-pink-100 text-pink-700 rounded-full text-sm"
                >
                  {interest}
                </span>
              ))}
            </div>
          </Card>
        )}

        {/* Stats */}
        <Card className="p-4">
          <div className="grid grid-cols-3 gap-4 text-center">
            <div>
              <div className="text-2xl font-bold text-pink-500">-</div>
              <div className="text-xs text-gray-600">الإعجابات</div>
            </div>
            <div>
              <div className="text-2xl font-bold text-purple-500">-</div>
              <div className="text-xs text-gray-600">التطابقات</div>
            </div>
            <div>
              <div className="text-2xl font-bold text-blue-500">-</div>
              <div className="text-xs text-gray-600">الزيارات</div>
            </div>
          </div>
        </Card>

        {/* Settings Options */}
        <Card className="p-4 space-y-3">
          <Button 
            variant="ghost" 
            className="w-full justify-start"
            onClick={() => navigate('/settings')}
          >
            <Settings className="w-5 h-5 ml-2" />
            الإعدادات
          </Button>
          
          <Button 
            variant="ghost" 
            className="w-full justify-start"
            onClick={() => navigate('/safety')}
          >
            <Shield className="w-5 h-5 ml-2" />
            الأمان والخصوصية
          </Button>

          <Button 
            variant="ghost" 
            className="w-full justify-start text-red-600 hover:text-red-700 hover:bg-red-50"
            onClick={handleLogout}
          >
            <LogOut className="w-5 h-5 ml-2" />
            تسجيل الخروج
          </Button>
        </Card>
      </main>

      {/* Photo Modal */}
      {showPhotoModal && profile?.photos && (
        <div 
          className="fixed inset-0 bg-black bg-opacity-90 z-50 flex items-center justify-center p-4"
          onClick={() => setShowPhotoModal(false)}
        >
          <div className="relative max-w-4xl w-full">
            <button
              onClick={() => setShowPhotoModal(false)}
              className="absolute top-4 right-4 bg-white rounded-full p-2 hover:bg-gray-100 z-10"
            >
              <X className="w-6 h-6" />
            </button>
            
            <img
              src={profile.photos[selectedPhotoIndex]}
              alt={`صورة ${selectedPhotoIndex + 1}`}
              className="w-full h-auto max-h-[80vh] object-contain rounded-lg"
              onClick={(e) => e.stopPropagation()}
            />
            
            {profile.photos.length > 1 && (
              <div className="flex gap-2 justify-center mt-4">
                {profile.photos.map((photo, index) => (
                  <button
                    key={index}
                    onClick={(e) => {
                      e.stopPropagation();
                      setSelectedPhotoIndex(index);
                    }}
                    className={`w-16 h-16 rounded-lg overflow-hidden border-2 ${
                      index === selectedPhotoIndex ? 'border-pink-500' : 'border-gray-500'
                    }`}
                  >
                    <img
                      src={photo}
                      alt={`صورة ${index + 1}`}
                      className="w-full h-full object-cover"
                    />
                  </button>
                ))}
              </div>
            )}
          </div>
        </div>
      )}

      <BottomNav />
    </div>
  );
};

export default Profile;
