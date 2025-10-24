import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import BottomNav from '../components/BottomNav';
import { Card } from '../components/ui/card';
import { Moon, Zap, Heart, Users, Globe, Music, Coffee, Mountain, ArrowRight, Loader2 } from 'lucide-react';
import axios from 'axios';
import { toast, Toaster } from 'react-hot-toast';

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

const Explore = () => {
  const navigate = useNavigate();
  const { token } = useAuth();
  const [activeCategory, setActiveCategory] = useState(null);
  const [filteredProfiles, setFilteredProfiles] = useState([]);
  const [loading, setLoading] = useState(false);
  const [showResults, setShowResults] = useState(false);
  const [selectedMood, setSelectedMood] = useState(null);
  const [moodLoading, setMoodLoading] = useState(false);

  const categories = [
    {
      id: 'new-friends',
      title: 'أصدقاء جُدد',
      subtitle: 'ابحث عن أصدقاء جدد',
      emoji: '👋',
      gradient: 'from-orange-400 to-red-400',
      users: 2847,
      icon: Users
    },
    {
      id: 'long-term',
      title: 'شريك لفترة طويلة',
      subtitle: 'علاقة جدية',
      emoji: '💕',
      gradient: 'from-purple-400 to-pink-400',
      users: 3521,
      icon: Heart
    },
    {
      id: 'fun-time',
      title: 'قضاء وقت ممتع',
      subtitle: 'مواعدة عفوية',
      emoji: '🎉',
      gradient: 'from-blue-400 to-purple-400',
      users: 1892,
      icon: Zap
    },
    {
      id: 'night-owl',
      title: 'Night Owl',
      subtitle: 'نشطون الآن',
      emoji: '🌙',
      gradient: 'from-indigo-500 to-purple-600',
      users: 456,
      icon: Moon,
      badge: 'جديد'
    },
    {
      id: 'travelers',
      title: 'محبو السفر',
      subtitle: 'مغامرون حول العالم',
      emoji: '✈️',
      gradient: 'from-cyan-400 to-blue-400',
      users: 1247,
      icon: Globe
    },
    {
      id: 'music-lovers',
      title: 'محبو الموسيقى',
      subtitle: 'عشاق الموسيقى والحفلات',
      emoji: '🎵',
      gradient: 'from-pink-400 to-red-400',
      users: 2103,
      icon: Music
    },
    {
      id: 'coffee-dates',
      title: 'عشاق القهوة',
      subtitle: 'لقاءات مقهى مريحة',
      emoji: '☕',
      gradient: 'from-amber-400 to-orange-400',
      users: 987,
      icon: Coffee
    },
    {
      id: 'nature-lovers',
      title: 'محبو الطبيعة',
      subtitle: 'مشي لمسافات طويلة والهواء الطلق',
      emoji: '🌿',
      gradient: 'from-green-400 to-emerald-400',
      users: 1564,
      icon: Mountain
    }
  ];

  const moods = [
    {
      id: 'serious',
      title: 'جاد',
      emoji: '💼',
      color: 'bg-blue-500'
    },
    {
      id: 'casual',
      title: 'غير رسمي',
      emoji: '😊',
      color: 'bg-green-500'
    },
    {
      id: 'fun',
      title: 'ممتع',
      emoji: '🎊',
      color: 'bg-purple-500'
    },
    {
      id: 'romantic',
      title: 'رومانسي',
      emoji: '💖',
      color: 'bg-pink-500'
    }
  ];

  const handleCategoryClick = async (categoryId) => {
    setActiveCategory(categoryId);
    setShowResults(true);
    setLoading(true);
    
    try {
      // Fetch profiles with category filter
      const response = await axios.get(`${API}/profiles/discover?category=${categoryId}&limit=20`, {
        headers: { Authorization: `Bearer ${token}` }
      });
      setFilteredProfiles(response.data.profiles || []);
    } catch (error) {
      console.error('Error fetching profiles:', error);
      setFilteredProfiles([]);
    } finally {
      setLoading(false);
    }
  };

  const handleBackToCategories = () => {
    setShowResults(false);
    setActiveCategory(null);
    setFilteredProfiles([]);
  };

  const handleProfileClick = (profile) => {
    navigate('/home');
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-gray-50 to-gray-100 pb-20" dir="rtl">
      {/* Header */}
      <header className="bg-white shadow-sm p-4 sticky top-0 z-10">
        {showResults ? (
          <div className="flex items-center gap-3">
            <button
              onClick={handleBackToCategories}
              className="p-2 hover:bg-gray-100 rounded-full"
            >
              <ArrowRight className="w-6 h-6" />
            </button>
            <div>
              <h1 className="text-2xl font-bold">النتائج</h1>
              <p className="text-gray-600 text-sm">{filteredProfiles.length} نتيجة</p>
            </div>
          </div>
        ) : (
          <>
            <h1 className="text-2xl font-bold">استكشاف 🔍</h1>
            <p className="text-gray-600 text-sm">اكتشف أشخاص جدد حسب اهتماماتك</p>
          </>
        )}
      </header>

      <main className="max-w-6xl mx-auto p-4 space-y-6">
        {!showResults ? (
          <>
            {/* Moods Section */}
            <section>
              <h2 className="text-lg font-bold mb-3">كيف تشعر اليوم؟</h2>
              <div className="flex gap-3 overflow-x-auto pb-2">
                {moods.map((mood) => (
                  <button
                    key={mood.id}
                    className={`${mood.color} text-white px-6 py-3 rounded-full flex items-center gap-2 whitespace-nowrap shadow-lg hover:shadow-xl transition-shadow`}
                  >
                    <span className="text-xl">{mood.emoji}</span>
                    <span className="font-medium">{mood.title}</span>
                  </button>
                ))}
              </div>
            </section>

            {/* Categories Grid */}
            <section>
              <h2 className="text-lg font-bold mb-3">تصفح حسب الاهتمامات</h2>
              <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-4">
                {categories.map((category) => {
                  const IconComponent = category.icon;
                  
                  return (
                    <Card
                      key={category.id}
                      className={`relative p-6 cursor-pointer transition-all hover:scale-105 bg-gradient-to-br ${category.gradient} text-white overflow-hidden group`}
                      onClick={() => handleCategoryClick(category.id)}
                    >
                      {/* Badge */}
                      {category.badge && (
                        <div className="absolute top-2 left-2 bg-yellow-400 text-black text-xs px-2 py-1 rounded-full font-bold">
                          {category.badge}
                        </div>
                      )}

                      {/* Background Icon */}
                      <div className="absolute -bottom-4 -right-4 opacity-20">
                        <IconComponent className="w-24 h-24" />
                      </div>

                      {/* Content */}
                      <div className="relative z-10">
                        <div className="text-4xl mb-2">{category.emoji}</div>
                        <h3 className="font-bold text-lg mb-1">{category.title}</h3>
                        <p className="text-white/80 text-sm mb-3">{category.subtitle}</p>
                        
                        <div className="flex items-center gap-1 text-sm font-medium">
                          <span>{category.users.toLocaleString()}</span>
                          <span className="text-white/80">مستخدم</span>
                        </div>
                      </div>

                      {/* Hover Effect */}
                      <div className="absolute inset-0 bg-black/0 group-hover:bg-black/10 transition-colors" />
                    </Card>
                  );
                })}
              </div>
            </section>

            {/* Pagination Dots */}
            <div className="flex justify-center gap-2 py-4">
              {[1, 2, 3].map((dot) => (
                <div
                  key={dot}
                  className={`w-2 h-2 rounded-full ${
                    dot === 1 ? 'bg-pink-500 w-8' : 'bg-gray-300'
                  }`}
                />
              ))}
            </div>

            {/* Featured Section */}
            <section className="bg-gradient-to-r from-pink-500 to-purple-500 rounded-xl p-6 text-white">
              <h2 className="text-2xl font-bold mb-2">🌟 اختيارات اليوم المميزة</h2>
              <p className="mb-4">ملفات شخصية مختارة خصيصاً لك</p>
              <button
                onClick={() => navigate('/home')}
                className="bg-white text-pink-600 px-6 py-3 rounded-full font-bold hover:bg-gray-100 transition-colors"
              >
                اكتشف الآن
              </button>
            </section>
          </>
        ) : (
          <>
            {/* Loading State */}
            {loading && (
              <div className="flex flex-col items-center justify-center py-20">
                <Loader2 className="w-12 h-12 animate-spin text-pink-500 mb-4" />
                <p className="text-gray-600">جاري التحميل...</p>
              </div>
            )}

            {/* Results Grid */}
            {!loading && filteredProfiles.length > 0 && (
              <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-4">
                {filteredProfiles.map((profile, index) => (
                  <Card
                    key={index}
                    className="relative cursor-pointer group overflow-hidden hover:shadow-xl transition-shadow"
                    onClick={() => handleProfileClick(profile)}
                  >
                    <div className="aspect-[3/4] relative">
                      {profile.photos && profile.photos.length > 0 ? (
                        <img
                          src={profile.photos[0]}
                          alt={profile.display_name}
                          className="w-full h-full object-cover"
                        />
                      ) : (
                        <div className="w-full h-full bg-gradient-to-br from-pink-300 to-purple-300 flex items-center justify-center text-5xl">
                          ❤️
                        </div>
                      )}
                      
                      {/* Overlay */}
                      <div className="absolute inset-0 bg-gradient-to-t from-black/70 via-transparent to-transparent flex flex-col justify-end p-4">
                        <h3 className="text-white font-bold text-lg">
                          {profile.display_name}
                          {profile.age && `, ${profile.age}`}
                        </h3>
                        {profile.location && (
                          <p className="text-white/90 text-sm">📍 {profile.location}</p>
                        )}
                        {profile.interests && profile.interests.length > 0 && (
                          <div className="flex gap-1 mt-2 flex-wrap">
                            {profile.interests.slice(0, 2).map((interest, i) => (
                              <span
                                key={i}
                                className="bg-white/20 backdrop-blur-sm text-white text-xs px-2 py-1 rounded-full"
                              >
                                {interest}
                              </span>
                            ))}
                          </div>
                        )}
                      </div>
                    </div>
                  </Card>
                ))}
              </div>
            )}

            {/* Empty State */}
            {!loading && filteredProfiles.length === 0 && (
              <div className="flex flex-col items-center justify-center py-20">
                <div className="text-8xl mb-4">😔</div>
                <h2 className="text-2xl font-bold text-gray-700 mb-2">لا مزيد من النتائج</h2>
                <p className="text-gray-600 mb-6">جرب فئة أخرى أو عد لاحقاً</p>
                <button
                  onClick={handleBackToCategories}
                  className="bg-gradient-to-r from-pink-500 to-purple-500 text-white px-6 py-3 rounded-full font-bold hover:shadow-lg transition-shadow"
                >
                  العودة إلى الفئات
                </button>
              </div>
            )}
          </>
        )}
      </main>

      <BottomNav />
    </div>
  );
};

export default Explore;
