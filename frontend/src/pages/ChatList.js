import React, { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import { useWebSocket } from '../context/WebSocketContext';
import { Card } from '../components/ui/card';
import { Button } from '../components/ui/button';
import BottomNav from '../components/BottomNav';
import { Shield, Flag, Settings as SettingsIcon, Heart, Camera } from 'lucide-react';
import axios from 'axios';

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

const ChatList = () => {
  const navigate = useNavigate();
  const { token, user } = useAuth();
  const { isUserOnline, isConnected } = useWebSocket();
  const [conversations, setConversations] = useState([]);
  const [matches, setMatches] = useState([]);
  const [loading, setLoading] = useState(true);
  const [showSafetyTools, setShowSafetyTools] = useState(false);
  const [showWelcomeMessage, setShowWelcomeMessage] = useState(true);
  const fileInputRef = React.useRef(null);

  useEffect(() => {
    fetchData();
    checkWelcomeMessage();
  }, []);

  const checkWelcomeMessage = () => {
    const dismissed = localStorage.getItem(`welcome_message_${user?.id}`);
    setShowWelcomeMessage(!dismissed);
  };

  const dismissWelcomeMessage = () => {
    localStorage.setItem(`welcome_message_${user?.id}`, 'true');
    setShowWelcomeMessage(false);
  };

  const handleAddPhotos = () => {
    // Open file picker
    if (fileInputRef.current) {
      fileInputRef.current.click();
    }
  };

  const handleFileChange = async (event) => {
    const files = event.target.files;
    if (files && files.length > 0) {
      // Navigate to edit profile page
      navigate('/edit-profile');
    }
  };

  const fetchData = async () => {
    try {
      // Fetch both matches and conversations
      const [matchesRes, conversationsRes] = await Promise.all([
        axios.get(`${API}/matches`, { headers: { Authorization: `Bearer ${token}` } }),
        axios.get(`${API}/conversations`, { headers: { Authorization: `Bearer ${token}` } })
      ]);
      
      setMatches(matchesRes.data.matches || []);
      setConversations(conversationsRes.data.conversations || []);
    } catch (error) {
      console.error('Error fetching data:', error);
    } finally {
      setLoading(false);
    }
  };

  const formatTime = (timestamp) => {
    const date = new Date(timestamp);
    const now = new Date();
    const diffMs = now - date;
    const diffMins = Math.floor(diffMs / 60000);
    const diffHours = Math.floor(diffMs / 3600000);
    const diffDays = Math.floor(diffMs / 86400000);

    if (diffMins < 1) return 'الآن';
    if (diffMins < 60) return `${diffMins} د`;
    if (diffHours < 24) return `${diffHours} س`;
    if (diffDays === 1) return 'أمس';
    if (diffDays < 7) return `${diffDays} يوم`;
    return date.toLocaleDateString('ar');
  };

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="animate-spin rounded-full h-16 w-16 border-b-4 border-pink-500"></div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-white pb-20" dir="rtl">
      {/* Header */}
      <header className="bg-white shadow-sm p-4 sticky top-0 z-10 border-b border-gray-100">
        <div className="flex items-center justify-between max-w-2xl mx-auto">
          <div>
            <h1 className="text-2xl font-bold text-gray-800">الرسائل</h1>
          </div>
          <div className="flex gap-2">
            <button
              onClick={() => navigate('/double-dating')}
              className="p-2 hover:bg-gray-100 rounded-full"
            >
              <svg className="w-6 h-6 text-gray-600" viewBox="0 0 24 24" fill="none" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M17 20h5v-2a3 3 0 00-5.356-1.857M17 20H7m10 0v-2c0-.656-.126-1.283-.356-1.857M7 20H2v-2a3 3 0 015.356-1.857M7 20v-2c0-.656.126-1.283.356-1.857m0 0a5.002 5.002 0 019.288 0M15 7a3 3 0 11-6 0 3 3 0 016 0zm6 3a2 2 0 11-4 0 2 2 0 014 0zM7 10a2 2 0 11-4 0 2 2 0 014 0z" />
              </svg>
            </button>
            <button
              onClick={() => setShowSafetyTools(true)}
              className="p-2 hover:bg-gray-100 rounded-full"
            >
              <Shield className="w-6 h-6 text-gray-600" />
            </button>
          </div>
        </div>
      </header>

      <main className="max-w-2xl mx-auto">
        {/* Welcome Message from Team Pizoo */}
        {showWelcomeMessage && (
          <div className="px-4 py-4 border-b border-gray-100">
            <div className="flex gap-3">
              <div className="flex-shrink-0">
                <div className="w-12 h-12 bg-gradient-to-br from-pink-500 to-red-500 rounded-full flex items-center justify-center">
                  <Heart className="w-6 h-6 text-white" />
                </div>
              </div>
              <div className="flex-1">
                <div className="flex items-center justify-between mb-1">
                  <h3 className="font-bold text-gray-800">Team Pizoo</h3>
                  <button
                    onClick={dismissWelcomeMessage}
                    className="text-gray-400 hover:text-gray-600"
                  >
                    <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                    </svg>
                  </button>
                </div>
                <div className="bg-gray-100 rounded-2xl rounded-tr-none p-3 mb-2">
                  <p className="text-gray-700 text-sm leading-relaxed">
                    مرحباً بك في Pizoo! 🎉 عُد لدينا لنشاركك معك نصائح للتأكد من حصولك على أفضل تجربة ممكنة. وعندما تشعر بالخيرة؟ اسحب لليمين.
                  </p>
                </div>
                <div className="bg-gray-100 rounded-2xl rounded-tr-none p-3">
                  <p className="text-gray-700 text-sm mb-2">
                    <span className="font-bold">الجميع هنا ليروك:</span> أضف المزيد من الصور لزيادة فرصك في تبادل الإعجاب.
                  </p>
                  <Button
                    onClick={() => navigate('/edit-profile')}
                    className="w-full bg-gradient-to-r from-pink-500 to-red-500 hover:from-pink-600 hover:to-red-600 text-white text-sm py-2 mt-2"
                  >
                    <Camera className="w-4 h-4 ml-2" />
                    إضافة صور
                  </Button>
                </div>
                <p className="text-xs text-gray-400 mt-2">اليوم 9:16 ص</p>
              </div>
            </div>
          </div>
        )}

        {/* New Matches Section - Horizontal Scroll */}
        {matches.length > 0 && (
          <div className="py-4 border-b border-gray-100">
            <div className="px-4 mb-3">
              <h2 className="font-bold text-base text-gray-800">المعجبون الجُدد</h2>
            </div>
            
            <div className="flex gap-3 overflow-x-auto px-4 pb-2 scrollbar-hide">
              {matches.map((match) => (
                <div
                  key={match.match_id}
                  className="flex-shrink-0 cursor-pointer"
                  onClick={() => navigate(`/chat/${match.match_id}`)}
                >
                  <div className="relative">
                    <div className="w-20 h-20 rounded-full overflow-hidden border-4 border-pink-400 bg-gradient-to-br from-pink-300 to-purple-300">
                      {match.profile.photos && match.profile.photos.length > 0 ? (
                        <img
                          src={match.profile.photos[0]}
                          alt={match.profile.display_name}
                          className="w-full h-full object-cover"
                        />
                      ) : (
                        <div className="w-full h-full flex items-center justify-center text-3xl">
                          ❤️
                        </div>
                      )}
                    </div>
                    {isUserOnline(match.profile.user_id) && (
                      <div className="absolute bottom-0 right-0 w-5 h-5 bg-green-500 border-2 border-white rounded-full"></div>
                    )}
                  </div>
                  <p className="text-xs text-center mt-2 font-medium truncate w-20">
                    {match.profile.display_name}
                  </p>
                </div>
              ))}
            </div>
          </div>
        )}

        {/* Messages Section */}
        {conversations.length > 0 ? (
          <div>
            <div className="px-4 py-3 bg-gray-100">
              <h2 className="font-bold text-sm text-gray-600">الرسائل</h2>
            </div>
            <div className="divide-y">
              {conversations.map((conv) => (
                <div
                  key={conv.match_id}
                  className="bg-white p-4 hover:bg-gray-50 cursor-pointer transition-colors"
                  onClick={() => navigate(`/chat/${conv.match_id}`)}
                >
                  <div className="flex items-center gap-4">
                    {/* Profile Picture */}
                    <div className="relative">
                      <div className="w-16 h-16 rounded-full overflow-hidden bg-gradient-to-br from-pink-300 to-purple-300">
                        {conv.user.photo ? (
                          <img
                            src={conv.user.photo}
                            alt={conv.user.display_name}
                            className="w-full h-full object-cover"
                          />
                        ) : (
                          <div className="w-full h-full flex items-center justify-center text-3xl">
                            👤
                          </div>
                        )}
                      </div>
                      {isUserOnline(conv.user.id) && (
                        <div className="absolute bottom-0 right-0 w-4 h-4 bg-green-500 border-2 border-white rounded-full animate-pulse"></div>
                      )}
                    </div>

                    {/* Message Info */}
                    <div className="flex-1 min-w-0">
                      <div className="flex items-center justify-between mb-1">
                        <h3 className="font-bold text-lg truncate">
                          {conv.user.display_name}
                        </h3>
                        <span className="text-xs text-gray-500">
                          {formatTime(conv.last_message.created_at)}
                        </span>
                      </div>
                      
                      <div className="flex items-center justify-between">
                        <p className="text-sm text-gray-600 truncate">
                          {conv.last_message.content || 'ابدأ المحادثة...'}
                        </p>
                        {conv.unread_count > 0 && (
                          <span className="bg-pink-500 text-white text-xs px-2 py-1 rounded-full min-w-[20px] text-center">
                            {conv.unread_count}
                          </span>
                        )}
                      </div>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          </div>
        ) : (
          <div className="text-center py-20 px-4">
            <div className="text-8xl mb-4">💬</div>
            <h2 className="text-2xl font-bold text-gray-700 mb-2">
              لا توجد محادثات بعد
            </h2>
            <p className="text-gray-600 mb-6">
              ابدأ بالإعجاب بالملفات الشخصية للحصول على تطابقات!
            </p>
            <Button
              onClick={() => navigate('/home')}
              className="bg-gradient-to-r from-pink-500 to-purple-500 text-white"
            >
              ابدأ التصفح
            </Button>
          </div>
        )}
      </main>

      {/* Safety Tools Modal */}
      {showSafetyTools && (
        <div className="fixed inset-0 bg-black/50 flex items-end z-50" onClick={() => setShowSafetyTools(false)}>
          <Card className="w-full bg-white rounded-t-3xl p-6 animate-slide-up" onClick={(e) => e.stopPropagation()}>
            <h2 className="text-xl font-bold mb-4">أدوات السلامة</h2>
            
            <div className="space-y-3">
              <button className="w-full flex items-center gap-3 p-4 hover:bg-gray-50 rounded-lg transition-colors text-right">
                <Flag className="w-6 h-6 text-red-500" />
                <div>
                  <div className="font-medium">إبلاغ</div>
                  <div className="text-sm text-gray-600">
                    أبلغ عن شخص أو محتوى غير لائق
                  </div>
                </div>
              </button>

              <button className="w-full flex items-center gap-3 p-4 hover:bg-gray-50 rounded-lg transition-colors text-right">
                <SettingsIcon className="w-6 h-6 text-blue-500" />
                <div>
                  <div className="font-medium">تحديث إعدادات الرسائل</div>
                  <div className="text-sm text-gray-600">
                    حدد من يمكنه إرسال رسائل إليك
                  </div>
                </div>
              </button>

              <button 
                onClick={() => navigate('/safety-center')}
                className="w-full flex items-center gap-3 p-4 hover:bg-gray-50 rounded-lg transition-colors text-right"
              >
                <Shield className="w-6 h-6 text-green-500" />
                <div>
                  <div className="font-medium">الاتصال بمركز السلامة</div>
                  <div className="text-sm text-gray-600">
                    موارد السلامة والأدوات
                  </div>
                </div>
              </button>
            </div>

            <Button
              onClick={() => setShowSafetyTools(false)}
              variant="ghost"
              className="w-full mt-4"
            >
              إغلاق
            </Button>
          </Card>
        </div>
      )}

      <BottomNav />
    </div>
  );
};

export default ChatList;
