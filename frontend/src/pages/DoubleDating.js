import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import { Button } from '../components/ui/button';
import { Card } from '../components/ui/card';
import { X, Users, Settings, Heart, MessageCircle, Share2, Trash2 } from 'lucide-react';
import axios from 'axios';

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

const DoubleDating = () => {
  const navigate = useNavigate();
  const { token, user } = useAuth();
  const [invitedFriends, setInvitedFriends] = useState([]);
  const [showSettings, setShowSettings] = useState(false);
  const [showInviteOptions, setShowInviteOptions] = useState(false);
  const [settings, setSettings] = useState({
    showOnFriendProfile: true,
    showFriendOnMyProfile: true,
    showPersonalAccounts: false
  });

  useEffect(() => {
    fetchFriends();
  }, []);

  const fetchFriends = async () => {
    try {
      const response = await axios.get(`${API}/double-dating/friends`, {
        headers: { Authorization: `Bearer ${token}` }
      });
      setInvitedFriends(response.data.friends || []);
    } catch (error) {
      console.error('Error fetching friends:', error);
    }
  };

  const removeFriend = async (friendId) => {
    try {
      await axios.delete(`${API}/double-dating/friends/${friendId}`, {
        headers: { Authorization: `Bearer ${token}` }
      });
      setInvitedFriends(invitedFriends.filter(f => f.id !== friendId));
    } catch (error) {
      console.error('Error removing friend:', error);
    }
  };

  const generateInviteMessage = () => {
    const appUrl = window.location.origin;
    const inviteCode = user?.id || 'PIZOO2024';
    
    return `🔥 مرحباً! انضم إليّ على Pizoo - أفضل تطبيق للمواعدة المزدوجة!

✨ أكثر من 100,000 مستخدم نشط
💕 تطبيق آمن وموثوق
👥 ميزة المواعدة المزدوجة الفريدة
🎉 انضم الآن وشكّل ثنائياً معي!

رابط التسجيل: ${appUrl}
كود الدعوة: ${inviteCode}

#Pizoo #مواعدة_مزدوجة #التعارف`;
  };

  const shareViaWhatsApp = () => {
    const message = encodeURIComponent(generateInviteMessage());
    window.open(`https://wa.me/?text=${message}`, '_blank');
    setShowInviteOptions(false);
  };

  const shareViaFacebook = () => {
    const appUrl = window.location.origin;
    window.open(`https://www.facebook.com/sharer/sharer.php?u=${encodeURIComponent(appUrl)}`, '_blank');
    setShowInviteOptions(false);
  };

  const shareViaTwitter = () => {
    const message = encodeURIComponent('انضم إليّ على Pizoo - أفضل تطبيق للمواعدة المزدوجة! 🔥💕');
    const appUrl = window.location.origin;
    window.open(`https://twitter.com/intent/tweet?text=${message}&url=${encodeURIComponent(appUrl)}`, '_blank');
    setShowInviteOptions(false);
  };

  const copyInviteLink = () => {
    const message = generateInviteMessage();
    navigator.clipboard.writeText(message).then(() => {
      alert('تم نسخ رسالة الدعوة! 📋');
      setShowInviteOptions(false);
    });
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-pink-50 via-white to-purple-50 pb-20" dir="rtl">
      {/* Header */}
      <header className="bg-white shadow-sm p-4 flex items-center justify-between sticky top-0 z-10">
        <Button
          variant="ghost"
          size="icon"
          onClick={() => navigate('/home')}
        >
          <X className="w-6 h-6" />
        </Button>
        <h1 className="text-xl font-bold">أصدقاء</h1>
        <Button
          variant="ghost"
          size="icon"
          onClick={() => setShowSettings(!showSettings)}
        >
          <Settings className="w-6 h-6" />
        </Button>
      </header>

      <main className="max-w-2xl mx-auto p-4">
        {/* Settings Panel */}
        {showSettings && (
          <Card className="p-6 mb-6 bg-gradient-to-br from-blue-50 to-purple-50">
            <h3 className="font-bold text-lg mb-4 flex items-center gap-2">
              <Settings className="w-5 h-5 text-purple-500" />
              المواعدة المزدوجة
            </h3>
            
            <div className="space-y-4">
              <div className="flex items-center justify-between py-2">
                <div>
                  <div className="font-medium">أظهرني على الحساب الشخصي لصديقي</div>
                  <div className="text-sm text-gray-600">
                    قد يظهر اسمك وصورتك على حساب صديقك المزدوج في الواعدة المزدوجة
                  </div>
                </div>
                <label className="relative inline-flex items-center cursor-pointer">
                  <input
                    type="checkbox"
                    checked={settings.showOnFriendProfile}
                    onChange={(e) => setSettings({ ...settings, showOnFriendProfile: e.target.checked })}
                    className="sr-only peer"
                  />
                  <div className="w-11 h-6 bg-gray-200 peer-focus:outline-none peer-focus:ring-4 peer-focus:ring-pink-300 rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:border-gray-300 after:border after:rounded-full after:h-5 after:w-5 after:transition-all peer-checked:bg-pink-500"></div>
                </label>
              </div>

              <div className="flex items-center justify-between py-2">
                <div>
                  <div className="font-medium">أظهر أصدقاء على حسابي الشخصي</div>
                  <div className="text-sm text-gray-600">
                    قد يظهر اسم وصورة صديقك المزدوج في الواعدة المزدوجة على حسابك الشخصي
                  </div>
                </div>
                <label className="relative inline-flex items-center cursor-pointer">
                  <input
                    type="checkbox"
                    checked={settings.showFriendOnMyProfile}
                    onChange={(e) => setSettings({ ...settings, showFriendOnMyProfile: e.target.checked })}
                    className="sr-only peer"
                  />
                  <div className="w-11 h-6 bg-gray-200 peer-focus:outline-none peer-focus:ring-4 peer-focus:ring-pink-300 rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:border-gray-300 after:border after:rounded-full after:h-5 after:w-5 after:transition-all peer-checked:bg-pink-500"></div>
                </label>
              </div>

              <div className="flex items-center justify-between py-2">
                <div>
                  <div className="font-medium">عرض الحسابات الشخصية لميزة موعد مزدوج</div>
                  <div className="text-sm text-gray-600">
                    عند تعطيل هذا الخيار، لن تظهر لك الحسابات الشخصية لميزة موعد مزدوج في وضع "من أحبك"
                  </div>
                </div>
                <label className="relative inline-flex items-center cursor-pointer">
                  <input
                    type="checkbox"
                    checked={settings.showPersonalAccounts}
                    onChange={(e) => setSettings({ ...settings, showPersonalAccounts: e.target.checked })}
                    className="sr-only peer"
                  />
                  <div className="w-11 h-6 bg-gray-200 peer-focus:outline-none peer-focus:ring-4 peer-focus:ring-pink-300 rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:border-gray-300 after:border after:rounded-full after:h-5 after:w-5 after:transition-all peer-checked:bg-pink-500"></div>
                </label>
              </div>
            </div>
          </Card>
        )}

        {/* Friends Grid */}
        <div className="mb-6">
          <div className="flex items-center justify-between mb-4">
            <h2 className="text-lg font-bold">أصدقاء موعد مزدوج ({invitedFriends.length}/3)</h2>
          </div>

          <div className="grid grid-cols-3 gap-4 mb-4">
            {[1, 2, 3].map((num) => (
              <div
                key={num}
                className="aspect-square rounded-2xl bg-gradient-to-br from-gray-100 to-gray-200 flex flex-col items-center justify-center relative border-2 border-dashed border-gray-300"
              >
                {invitedFriends[num - 1] ? (
                  <img
                    src={invitedFriends[num - 1].photo}
                    alt={invitedFriends[num - 1].name}
                    className="w-full h-full object-cover rounded-2xl"
                  />
                ) : (
                  <>
                    <Users className="w-12 h-12 text-gray-400 mb-2" />
                    <button className="w-8 h-8 bg-white rounded-full flex items-center justify-center shadow-md">
                      <span className="text-2xl text-pink-500">+</span>
                    </button>
                  </>
                )}
              </div>
            ))}
          </div>

          <div className="text-center mb-6">
            <p className="text-gray-600 mb-3">
              يُمكنك تشكيل ثُنائي مع ما يصل إلى 3 من أصدقائك في موعد مزدوج.
            </p>
            <button
              onClick={() => navigate('/double-dating-info')}
              className="text-blue-500 font-medium hover:underline"
            >
              اعرف أكثر
            </button>
          </div>
        </div>

        {/* Invitations Section */}
        <Card className="p-6 mb-6">
          <h3 className="font-bold text-lg mb-4 flex items-center gap-2">
            <MessageCircle className="w-5 h-5 text-pink-500" />
            دعوات من الأصدقاء
          </h3>
          
          <div className="flex flex-col items-center justify-center py-8 text-gray-400">
            <MessageCircle className="w-16 h-16 mb-3" />
            <p className="text-center">يُمكنك بيع دعوات موعدك المزدوج هنا.</p>
          </div>
        </Card>

        {/* Invite Button */}
        <Button
          onClick={() => setShowInviteOptions(true)}
          className="w-full bg-gradient-to-r from-pink-500 to-purple-500 hover:from-pink-600 hover:to-purple-600 text-white font-bold py-6 text-lg rounded-xl"
        >
          دعوة الأصدقاء
        </Button>

        {/* Invite Options Modal */}
        {showInviteOptions && (
          <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
            <Card className="w-full max-w-md p-6 bg-white">
              <div className="flex items-center justify-between mb-4">
                <h3 className="text-lg font-bold">مشاركة التطبيق</h3>
                <Button
                  variant="ghost"
                  size="icon"
                  onClick={() => setShowInviteOptions(false)}
                >
                  <X className="w-5 h-5" />
                </Button>
              </div>
              
              <div className="space-y-3">
                <Button
                  onClick={shareViaWhatsApp}
                  className="w-full bg-green-500 hover:bg-green-600 text-white flex items-center gap-3 justify-center py-3"
                >
                  <Share2 className="w-5 h-5" />
                  مشاركة عبر WhatsApp
                </Button>
                
                <Button
                  onClick={shareViaFacebook}
                  className="w-full bg-blue-600 hover:bg-blue-700 text-white flex items-center gap-3 justify-center py-3"
                >
                  <Share2 className="w-5 h-5" />
                  مشاركة عبر Facebook
                </Button>
                
                <Button
                  onClick={shareViaTwitter}
                  className="w-full bg-sky-500 hover:bg-sky-600 text-white flex items-center gap-3 justify-center py-3"
                >
                  <Share2 className="w-5 h-5" />
                  مشاركة عبر Twitter
                </Button>
                
                <Button
                  onClick={copyInviteLink}
                  variant="outline"
                  className="w-full flex items-center gap-3 justify-center py-3"
                >
                  <Share2 className="w-5 h-5" />
                  نسخ رسالة الدعوة
                </Button>
              </div>
            </Card>
          </div>
        )}

        {/* Info Cards */}
        <div className="grid md:grid-cols-2 gap-4 mt-6">
          <Card className="p-4 bg-gradient-to-br from-pink-50 to-red-50">
            <div className="flex items-center gap-3 mb-2">
              <div className="w-10 h-10 bg-pink-500 rounded-full flex items-center justify-center">
                <Heart className="w-5 h-5 text-white" />
              </div>
              <h4 className="font-bold">ادعُ أصدقائك</h4>
            </div>
            <p className="text-sm text-gray-600">
              شكّل ثُنائيًا مع ما يصل إلى 3 أصدقاء في موعد مزدوج
            </p>
          </Card>

          <Card className="p-4 bg-gradient-to-br from-purple-50 to-blue-50">
            <div className="flex items-center gap-3 mb-2">
              <div className="w-10 h-10 bg-purple-500 rounded-full flex items-center justify-center">
                <Users className="w-5 h-5 text-white" />
              </div>
              <h4 className="font-bold">تبادل الإعجاب معًا</h4>
            </div>
            <p className="text-sm text-gray-600">
              عند قبولك، ستبقى بإمكانك تبادل الإعجاب مع أناس مع أصدقائك
            </p>
          </Card>
        </div>
      </main>
    </div>
  );
};

export default DoubleDating;
