import React, { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import { Button } from '../components/ui/button';
import { Card } from '../components/ui/card';
import BottomNav from '../components/BottomNav';
import ImageLightbox from '../components/ImageLightbox';
import { Settings, Edit, Shield, Crown, Zap, Camera, MapPin, Briefcase, Heart, Star, Check } from 'lucide-react';
import axios from 'axios';

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

const ProfileNew = () => {
  const navigate = useNavigate();
  const { token, user } = useAuth();
  const [profile, setProfile] = useState(null);
  const [userInfo, setUserInfo] = useState(null);
  const [loading, setLoading] = useState(true);
  const [completionScore, setCompletionScore] = useState(0);
  const [lightboxOpen, setLightboxOpen] = useState(false);
  const [lightboxIndex, setLightboxIndex] = useState(0);

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
      setProfile(profileRes.data);
      setUserInfo(userRes.data);
      
      // Calculate completion score
      calculateCompletionScore(profileRes.data);
    } catch (error) {
      console.error('Error fetching profile:', error);
    } finally {
      setLoading(false);
    }
  };

  const calculateCompletionScore = (profileData) => {
    if (!profileData) return;

    let score = 0;
    if (profileData.photos && profileData.photos.length > 0) score += Math.min(profileData.photos.length * 10, 30);
    if (profileData.display_name) score += 5;
    if (profileData.age) score += 5;
    if (profileData.location) score += 5;
    if (profileData.occupation) score += 5;
    if (profileData.bio && profileData.bio.length > 50) score += 10;
    if (profileData.interests && profileData.interests.length >= 3) score += 10;
    if (profileData.languages && profileData.languages.length >= 2) score += 10;
    if (profileData.relationship_goals) score += 5;
    if (profileData.education) score += 5;

    setCompletionScore(Math.min(score, 100));
  };

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="animate-spin rounded-full h-16 w-16 border-b-4 border-pink-500"></div>
      </div>
    );
  }

  const primaryPhoto = profile?.primary_photo || profile?.photos?.[0];

  return (
    <div className="min-h-screen bg-gradient-to-br from-gray-50 to-gray-100 pb-20" dir="rtl">
      {/* Header */}
      <div className="bg-white border-b sticky top-0 z-10">
        <div className="max-w-2xl mx-auto px-4 py-4 flex items-center justify-between">
          <h1 className="text-2xl font-bold">بروفايلي</h1>
          <Button
            variant="ghost"
            size="icon"
            onClick={() => navigate('/settings')}
          >
            <Settings className="w-6 h-6" />
          </Button>
        </div>
      </div>

      <main className="max-w-2xl mx-auto p-4 space-y-4">
        {/* Profile Card with Photo */}
        <Card className="overflow-hidden">
          {/* Cover/Hero Section */}
          <div className="relative h-80 bg-gradient-to-br from-pink-400 via-purple-400 to-blue-400">
            {primaryPhoto ? (
              <img
                src={primaryPhoto}
                alt={profile?.display_name || 'Profile'}
                className="w-full h-full object-cover"
              />
            ) : (
              <div className="w-full h-full flex flex-col items-center justify-center text-white">
                <Camera className="w-16 h-16 mb-2 opacity-50" />
                <p className="text-lg">أضف صورة لبروفايلك</p>
              </div>
            )}
            
            {/* Edit Button Overlay */}
            <Button
              onClick={() => navigate('/profile/edit')}
              className="absolute bottom-4 right-4 bg-white text-pink-600 hover:bg-gray-100 rounded-full shadow-lg"
            >
              <Edit className="w-4 h-4 ml-2" />
              تعديل البروفايل
            </Button>
          </div>

          {/* Profile Info */}
          <div className="p-6">
            <div className="flex items-start justify-between mb-4">
              <div>
                <div className="flex items-center gap-2 mb-1">
                  <h2 className="text-3xl font-bold">{profile?.display_name || 'اسمك'}</h2>
                  {userInfo?.premium_tier !== 'free' && (
                    <Crown className="w-6 h-6 text-yellow-500 fill-yellow-500" />
                  )}
                </div>
                <p className="text-gray-600 text-lg">
                  {profile?.age ? `${profile.age} سنة` : ''} {profile?.location && `• ${profile.location}`}
                </p>
              </div>
            </div>

            {/* Quick Stats */}
            <div className="grid grid-cols-3 gap-4 mb-6">
              <div className="text-center p-3 bg-pink-50 rounded-lg">
                <div className="text-2xl font-bold text-pink-600">{completionScore}%</div>
                <div className="text-xs text-gray-600">اكتمال البروفايل</div>
              </div>
              <div className="text-center p-3 bg-purple-50 rounded-lg">
                <div className="text-2xl font-bold text-purple-600">{profile?.photos?.length || 0}</div>
                <div className="text-xs text-gray-600">الصور</div>
              </div>
              <div className="text-center p-3 bg-blue-50 rounded-lg">
                <div className="text-2xl font-bold text-blue-600">{profile?.interests?.length || 0}</div>
                <div className="text-xs text-gray-600">الاهتمامات</div>
              </div>
            </div>

            {/* Bio */}
            {profile?.bio && (
              <div className="mb-6">
                <h3 className="font-bold text-lg mb-2">نبذة عني</h3>
                <p className="text-gray-700 leading-relaxed">{profile.bio}</p>
              </div>
            )}

            {/* Occupation & Education */}
            {(profile?.occupation || profile?.education) && (
              <div className="space-y-3 mb-6">
                {profile?.occupation && (
                  <div className="flex items-center gap-3">
                    <Briefcase className="w-5 h-5 text-gray-400" />
                    <span className="text-gray-700">{profile.occupation}</span>
                  </div>
                )}
                {profile?.education && (
                  <div className="flex items-center gap-3">
                    <svg className="w-5 h-5 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 14l9-5-9-5-9 5 9 5z M12 14l6.16-3.422a12.083 12.083 0 01.665 6.479A11.952 11.952 0 0012 20.055a11.952 11.952 0 00-6.824-2.998 12.078 12.078 0 01.665-6.479L12 14z M12 14l9-5-9-5-9 5 9 5zm0 0l6.16-3.422a12.083 12.083 0 01.665 6.479A11.952 11.952 0 0012 20.055a11.952 11.952 0 00-6.824-2.998 12.078 12.078 0 01.665-6.479L12 14z" />
                    </svg>
                    <span className="text-gray-700">{profile.education}</span>
                  </div>
                )}
              </div>
            )}

            {/* Interests */}
            {profile?.interests && profile.interests.length > 0 && (
              <div className="mb-6">
                <h3 className="font-bold text-lg mb-3">الاهتمامات</h3>
                <div className="flex flex-wrap gap-2">
                  {profile.interests.map((interest, index) => (
                    <span
                      key={index}
                      className="px-4 py-2 bg-gradient-to-r from-pink-100 to-purple-100 text-pink-700 rounded-full text-sm font-medium"
                    >
                      {interest}
                    </span>
                  ))}
                </div>
              </div>
            )}

            {/* Languages */}
            {profile?.languages && profile.languages.length > 0 && (
              <div className="mb-6">
                <h3 className="font-bold text-lg mb-3">اللغات</h3>
                <div className="flex flex-wrap gap-2">
                  {profile.languages.map((lang, index) => (
                    <span
                      key={index}
                      className="px-4 py-2 bg-blue-50 text-blue-700 rounded-full text-sm"
                    >
                      {lang}
                    </span>
                  ))}
                </div>
              </div>
            )}
          </div>
        </Card>

        {/* Premium Upsell (if free user) */}
        {userInfo?.premium_tier === 'free' && (
          <Card className="p-6 bg-gradient-to-r from-yellow-50 to-orange-50 border-2 border-yellow-200">
            <div className="flex items-start gap-4">
              <div className="flex-shrink-0 w-12 h-12 bg-gradient-to-br from-yellow-400 to-orange-400 rounded-full flex items-center justify-center">
                <Crown className="w-6 h-6 text-white" />
              </div>
              <div className="flex-1">
                <h3 className="font-bold text-lg mb-1">ترقية إلى Premium</h3>
                <p className="text-gray-700 text-sm mb-3">
                  احصل على إعجابات ورسائل غير محدودة، وشاهد من أعجب بك!
                </p>
                <Button
                  onClick={() => navigate('/premium')}
                  className="bg-gradient-to-r from-yellow-400 to-orange-400 hover:from-yellow-500 hover:to-orange-500 text-black font-bold"
                >
                  <Zap className="w-4 h-4 ml-2" />
                  اشترك الآن
                </Button>
              </div>
            </div>
          </Card>
        )}

        {/* Account Safety */}
        <Card className="p-6">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-3">
              <Shield className="w-6 h-6 text-green-600" />
              <div>
                <h3 className="font-bold">حسابك آمن</h3>
                <p className="text-sm text-gray-600">تم التحقق من هويتك</p>
              </div>
            </div>
            <Check className="w-6 h-6 text-green-600" />
          </div>
        </Card>
      </main>

      <BottomNav />
    </div>
  );
};

export default ProfileNew;
