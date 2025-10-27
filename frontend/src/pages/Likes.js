import React, { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import { Card } from '../components/ui/card';
import { Button } from '../components/ui/button';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '../components/ui/tabs';
import BottomNav from '../components/BottomNav';
import { Eye, MessageCircle } from 'lucide-react';
import axios from 'axios';
import { fetchUsage, incUsage } from '../modules/premium/usage';
import UpsellModal from '../modules/premium/UpsellModal';

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

const Likes = () => {
  const navigate = useNavigate();
  const { token } = useAuth();
  const [sent, setSent] = useState([]);
  const [received, setReceived] = useState([]);
  const [loading, setLoading] = useState(true);
  const [toast, setToast] = useState(null);

  useEffect(() => {
    fetchLikes();
  }, []);

  const fetchLikes = async () => {
    try {
      const [sentRes, receivedRes] = await Promise.all([
        axios.get(`${API}/likes/sent`, { headers: { Authorization: `Bearer ${token}` } }),
        axios.get(`${API}/likes/received`, { headers: { Authorization: `Bearer ${token}` } })
      ]);
      setSent(sentRes.data.profiles);
      setReceived(receivedRes.data.profiles);
    } catch (error) {
      console.error('Error:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleViewProfile = (profile) => {
    navigate(`/profile/${profile.user_id}`);
  };

  const handleMessage = async (profile) => {
    try {
      // Check if match exists
      const matchesRes = await axios.get(`${API}/matches`, {
        headers: { Authorization: `Bearer ${token}` }
      });
      
      const match = matchesRes.data.matches.find(m => 
        m.profile.user_id === profile.user_id
      );

      if (match) {
        // Match exists, go to chat
        navigate(`/chat/${match.match_id}`);
      } else {
        // No match, send like
        await axios.post(`${API}/swipe`, {
          swiped_user_id: profile.user_id,
          action: 'like'
        }, {
          headers: { Authorization: `Bearer ${token}` }
        });
        
        showToast('تم الإعجاب! 💕 انتظر إعجاب الطرف الآخر لفتح الدردشة');
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

  const ProfileGrid = ({ profiles }) => (
    <div className="grid grid-cols-2 md:grid-cols-3 gap-4">
      {profiles.map((profile, i) => (
        <Card key={i} className="overflow-hidden">
          <div className="aspect-[3/4] relative bg-gradient-to-br from-pink-200 to-purple-200">
            {profile.photos && profile.photos.length > 0 ? (
              <img src={profile.photos[0]} alt="" className="w-full h-full object-cover" />
            ) : (
              <div className="w-full h-full flex items-center justify-center text-4xl">❤️</div>
            )}
            
            {/* Profile Info Overlay */}
            <div className="absolute inset-0 bg-gradient-to-t from-black/70 via-transparent to-transparent flex flex-col justify-end p-3">
              <h3 className="text-white font-bold text-base">
                {profile.display_name}
                {profile.age && `, ${profile.age}`}
              </h3>
              {profile.location && (
                <p className="text-white/90 text-xs mb-2">📍 {profile.location}</p>
              )}
            </div>
          </div>
          
          {/* Action Buttons */}
          <div className="p-2 flex gap-2">
            <Button
              onClick={() => handleViewProfile(profile)}
              variant="outline"
              size="sm"
              className="flex-1 text-xs"
            >
              <Eye className="w-3 h-3 ml-1" />
              عرض
            </Button>
            <Button
              onClick={() => handleMessage(profile)}
              size="sm"
              className="flex-1 bg-pink-500 hover:bg-pink-600 text-white text-xs"
            >
              <MessageCircle className="w-3 h-3 ml-1" />
              رسالة
            </Button>
          </div>
        </Card>
      ))}
    </div>
  );

  return (
    <div className="min-h-screen bg-gray-50 pb-20" dir="rtl">
      {/* Toast Notification */}
      {toast && (
        <div className="fixed top-4 left-1/2 transform -translate-x-1/2 bg-black/90 text-white px-6 py-3 rounded-full z-50 shadow-lg">
          {toast}
        </div>
      )}

      <header className="bg-white shadow-sm p-4">
        <h1 className="text-2xl font-bold text-center">الإعجابات 💕</h1>
      </header>

      <main className="max-w-6xl mx-auto p-4">
        <Tabs defaultValue="sent" className="w-full">
          <TabsList className="grid w-full grid-cols-2">
            <TabsTrigger value="sent">أرسلت ({sent.length})</TabsTrigger>
            <TabsTrigger value="received">استلمت ({received.length})</TabsTrigger>
          </TabsList>
          
          <TabsContent value="sent" className="mt-4">
            {loading ? <div className="text-center py-10">جاري التحميل...</div> : 
              sent.length > 0 ? <ProfileGrid profiles={sent} /> : 
              <div className="text-center py-20 text-gray-500">لم ترسل إعجابات بعد</div>
            }
          </TabsContent>
          
          <TabsContent value="received" className="mt-4">
            {loading ? <div className="text-center py-10">جاري التحميل...</div> :
              received.length > 0 ? <ProfileGrid profiles={received} /> :
              <div className="text-center py-20 text-gray-500">لم تستلم إعجابات بعد</div>
            }
          </TabsContent>
        </Tabs>
      </main>

      <BottomNav />
    </div>
  );
};

export default Likes;
