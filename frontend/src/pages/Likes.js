import React, { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import { useTranslation } from 'react-i18next';
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
  const { t } = useTranslation('likes');
  const [sent, setSent] = useState([]);
  const [received, setReceived] = useState([]);
  const [loading, setLoading] = useState(true);
  const [toast, setToast] = useState(null);
  const [showUpsell, setShowUpsell] = useState(false);
  const [upsellReason, setUpsellReason] = useState('view');

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

  const handleViewProfile = async (profile) => {
    try {
      // Check usage limit
      const usage = await fetchUsage();
      
      // Premium users bypass limits
      if (!usage.isPremium && usage.remainingViews <= 0) {
        setUpsellReason('view');
        setShowUpsell(true);
        return;
      }
      
      // Increment view counter
      await incUsage('view');
      
      // Navigate to profile
      navigate(`/profile/${profile.user_id}`);
    } catch (error) {
      console.error('Error viewing profile:', error);
      if (error.message.includes('429') || error.message.includes('limit')) {
        setUpsellReason('view');
        setShowUpsell(true);
      } else {
        showToast('حدث خطأ، حاول مرة أخرى');
      }
    }
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
        // Check like limit before sending like
        const usage = await fetchUsage();
        
        if (!usage.isPremium && usage.remainingLikes <= 0) {
          setUpsellReason('like');
          setShowUpsell(true);
          return;
        }
        
        // Send like
        await axios.post(`${API}/swipe`, {
          swiped_user_id: profile.user_id,
          action: 'like'
        }, {
          headers: { Authorization: `Bearer ${token}` }
        });
        
        // Increment like counter
        await incUsage('like');
        
        showToast(t('likeSuccess'));
      }
    } catch (error) {
      console.error('Error:', error);
      if (error.message.includes('429') || error.message.includes('limit')) {
        setUpsellReason('like');
        setShowUpsell(true);
      } else {
        showToast(t('errorTryAgain'));
      }
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
            <div className="absolute inset-0 bg-gradient-to-t from-black/70 via-transparent to-transparent flex flex-col justify-end p-3 overlay-no-pointer">
              <h3 className="text-white font-bold text-base clamp-1">
                {profile.display_name}
                {profile.age && `, ${profile.age}`}
              </h3>
              {profile.location && (
                <p className="text-white/90 text-xs mb-2 clamp-1">📍 {profile.location}</p>
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
            <Button
              onClick={() => handleLike(profile.id || profile.user_id)}
              size="sm"
              className="flex-1 bg-rose-500 hover:bg-rose-600 text-white text-xs"
            >
              ❤️
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
      
      {/* Upsell Modal */}
      {showUpsell && (
        <UpsellModal 
          reason={upsellReason}
          onClose={() => setShowUpsell(false)}
        />
      )}
    </div>
  );
};

export default Likes;
