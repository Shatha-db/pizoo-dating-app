import React, { useEffect, useState, useRef } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import { useWebSocket } from '../context/WebSocketContext';
import { Button } from '../components/ui/button';
import { Card } from '../components/ui/card';
import { ArrowRight, MoreVertical, Video, Send, Smile, Mic, Star, Phone } from 'lucide-react';
import axios from 'axios';
import SafetyConsentModal from '../modules/safety/SafetyConsentModal';
import EmojiPicker from '../modules/chat/EmojiPicker';
import CallModal from '../modules/chat/CallModal';
import { formatTimeOnly } from '../utils/timeFormat';

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

const ChatRoom = () => {
  const { matchId } = useParams();
  const navigate = useNavigate();
  const { token, user } = useAuth();
  const { isConnected, sendMessage: wsSendMessage, sendTypingIndicator, isUserOnline, isUserTyping, messages: wsMessages } = useWebSocket();
  const [messages, setMessages] = useState([]);
  const [newMessage, setNewMessage] = useState('');
  const [otherUser, setOtherUser] = useState(null);
  const [loading, setLoading] = useState(true);
  const [showSafetyConsent, setShowSafetyConsent] = useState(false);
  const [hasAgreedToSafety, setHasAgreedToSafety] = useState(false);
  const [showReadReceipts, setShowReadReceipts] = useState(false);
  const [showMessageLimitWarning, setShowMessageLimitWarning] = useState(false);
  const [showEmojiPicker, setShowEmojiPicker] = useState(false);
  const [showCallModal, setShowCallModal] = useState(false);
  const [callType, setCallType] = useState('video');
  const messagesEndRef = useRef(null);
  const typingTimeoutRef = useRef(null);

  useEffect(() => {
    fetchMessages();
    // Check for safety consent
    const agreed = localStorage.getItem('pizoo_safety_accepted');
    if (agreed === '1') {
      setHasAgreedToSafety(true);
    }
  }, [matchId]);

  // Listen to WebSocket messages
  useEffect(() => {
    const newWsMessages = wsMessages.filter(msg => msg.match_id === matchId);
    if (newWsMessages.length > 0) {
      setMessages(prev => {
        const existingIds = new Set(prev.map(m => m.id));
        const uniqueNew = newWsMessages.filter(m => !existingIds.has(m.id));
        return [...prev, ...uniqueNew];
      });
    }
  }, [wsMessages, matchId]);

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const fetchMessages = async () => {
    try {
      // First, fetch match data to get receiver info
      const matchResponse = await axios.get(`${API}/matches/${matchId}`, {
        headers: { Authorization: `Bearer ${token}` }
      });
      
      if (matchResponse.data) {
        const match = matchResponse.data;
        const otherId = match.user1_id === user?.id ? match.user2_id : match.user1_id;
        
        // Fetch other user's profile
        try {
          const profileResponse = await axios.get(`${API}/profiles/${otherId}`, {
            headers: { Authorization: `Bearer ${token}` }
          });
          setOtherUser({
            id: otherId,
            name: profileResponse.data.display_name || 'User',
            photo: profileResponse.data.photos?.[0] || null
          });
        } catch (err) {
          console.error('Error fetching other user profile:', err);
          setOtherUser({ id: otherId, name: 'User', photo: null });
        }
      }

      // Then fetch messages
      const response = await axios.get(`${API}/conversations/${matchId}/messages`, {
        headers: { Authorization: `Bearer ${token}` }
      });
      setMessages(response.data.messages || []);
    } catch (error) {
      console.error('Error fetching messages:', error);
    } finally {
      setLoading(false);
    }
  };

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  const [sending, setSending] = useState(false);

  const handleSendMessage = async () => {
    if (!newMessage.trim() || sending || !otherUser) return;

    // Check safety consent
    if (!hasAgreedToSafety) {
      setShowSafetyConsent(true);
      return;
    }

    const messageText = newMessage.trim();
    const tempId = `temp-${Date.now()}`;
    
    // Optimistic update - add message immediately to UI with UTC time
    const optimisticMessage = {
      id: tempId,
      content: messageText,
      sender_id: user?.id,
      receiver_id: otherUser.id,
      match_id: matchId,
      created_at: new Date().toISOString(),
      read: false,
      status: 'sending',
    };
    
    setMessages(prev => [...prev, optimisticMessage]);
    setNewMessage('');
    setSending(true);
    
    try {
      // Always use HTTP API for reliability
      const response = await axios.post(
        `${API}/conversations/${matchId}/messages`,
        { content: messageText },
        { 
          headers: { 
            Authorization: `Bearer ${token}`,
            'Content-Type': 'application/json'
          }
        }
      );
      
      // Replace optimistic message with actual server response
      if (response.data && response.data.data) {
        setMessages(prev => prev.map(msg => 
          msg.id === tempId ? { ...response.data.data, status: 'sent' } : msg
        ));
      } else {
        // Just mark as sent if no data returned
        setMessages(prev => prev.map(msg => 
          msg.id === tempId ? { ...msg, status: 'sent' } : msg
        ));
      }
    } catch (error) {
      console.error('Error sending message:', error);
      // Mark message as failed
      setMessages(prev => prev.map(msg => 
        msg.id === tempId ? { ...msg, status: 'failed' } : msg
      ));
      
      // Show error toast
      alert('فشل إرسال الرسالة. الرجاء المحاولة مرة أخرى.');
    } finally {
      setSending(false);
    }
  };

  const handleTyping = (e) => {
    setNewMessage(e.target.value);
    
    if (otherUser && isConnected) {
      sendTypingIndicator(otherUser.id, true);
      
      // Stop typing indicator after 2 seconds
      if (typingTimeoutRef.current) {
        clearTimeout(typingTimeoutRef.current);
      }
      typingTimeoutRef.current = setTimeout(() => {
        sendTypingIndicator(otherUser.id, false);
      }, 2000);
    }
  };

  const handleAgreeSafety = () => {
    localStorage.setItem('pizoo_safety_accepted', '1');
    setHasAgreedToSafety(true);
    setShowSafetyConsent(false);
    handleSendMessage();
  };

  const insertEmoji = (emoji) => {
    setNewMessage(prev => (prev || '') + emoji);
    setShowEmojiPicker(false);
  };

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="animate-spin rounded-full h-16 w-16 border-b-4 border-pink-500"></div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-100 flex flex-col" dir="rtl">
      {/* Header */}
      <header className="bg-white shadow-sm p-4 flex items-center justify-between sticky top-0 z-10">
        <div className="flex items-center gap-3">
          <button onClick={() => navigate(-1)}>
            <ArrowRight className="w-6 h-6" />
          </button>
          
          <div className="flex items-center gap-2">
            <div className="relative">
              <div className="w-10 h-10 rounded-full bg-gradient-to-br from-pink-300 to-purple-300 flex items-center justify-center">
                👤
              </div>
              {otherUser && isUserOnline(otherUser.id) && (
                <div className="absolute bottom-0 right-0 w-3 h-3 bg-green-500 border-2 border-white rounded-full"></div>
              )}
            </div>
            <div 
              className="cursor-pointer hover:opacity-80 transition-opacity"
              onClick={() => otherUser && navigate(`/profile/${otherUser.id}`)}
            >
              <h2 className="font-bold">{otherUser?.name || 'المستخدم'}</h2>
              <span className="text-xs text-gray-500">
                {otherUser && isUserOnline(otherUser.id) ? (
                  <span className="text-green-600">● نشط الآن</span>
                ) : (
                  'غير متصل'
                )}
              </span>
            </div>
          </div>
        </div>

        <div className="flex items-center gap-2">
          {/* Voice Call Button */}
          <button
            onClick={() => {
              setCallType('audio');
              setShowCallModal(true);
            }}
            className="p-2 hover:bg-gray-100 rounded-full transition-colors"
            title="مكالمة صوتية"
          >
            <Phone className="w-5 h-5 text-green-500" />
          </button>
          
          {/* Video Call Button */}
          <button
            onClick={() => {
              setCallType('video');
              setShowCallModal(true);
            }}
            className="p-2 hover:bg-gray-100 rounded-full transition-colors"
            title="مكالمة فيديو"
          >
            <Video className="w-5 h-5 text-blue-500" />
          </button>
          
          <button className="p-2 hover:bg-gray-100 rounded-full">
            <MoreVertical className="w-5 h-5" />
          </button>
        </div>
      </header>

      {/* Messages */}
      <main className="flex-1 overflow-y-auto p-4 space-y-4">
        {/* Match Notification */}
        <div className="text-center py-4">
          <div className="text-4xl mb-2">💕</div>
          <p className="text-sm text-gray-600">تبادلت الإعجاب قبل 6 ساعات</p>
        </div>

        {/* Read Receipts Toggle */}
        {!showReadReceipts && (
          <Card className="p-4 bg-blue-50 border-blue-200">
            <p className="text-sm mb-2">اعرف متى قرأ المستخدم رسالتك.</p>
            <Button
              onClick={() => setShowReadReceipts(true)}
              className="w-full bg-blue-500 hover:bg-blue-600"
            >
              ✓ استقبل إيصالات القراءة
            </Button>
          </Card>
        )}

        {/* Messages List */}
        {messages.map((msg, index) => {
          const isSent = msg.sender_id === user?.id;
          
          return (
            <div
              key={msg.id || index}
              className={`flex ${isSent ? 'justify-end' : 'justify-start'} animate-in slide-in-from-bottom-2`}
            >
              <div
                className={`max-w-[70%] rounded-2xl px-4 py-2 ${
                  isSent
                    ? 'bg-gradient-to-r from-pink-500 to-purple-500 text-white'
                    : 'bg-white text-gray-800 shadow-md'
                }`}
              >
                <p>{msg.content}</p>
                {isSent && (
                  <div className="text-xs mt-1 opacity-75">
                    {msg.status === 'read' ? '✓✓ تم القراءة' : '✓ تم الإرسال'}
                  </div>
                )}
              </div>
            </div>
          );
        })}
        
        {/* Typing Indicator */}
        {otherUser && isUserTyping(otherUser.id) && (
          <div className="flex justify-start animate-pulse">
            <div className="bg-gray-200 rounded-2xl px-4 py-2">
              <div className="flex gap-1">
                <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce"></div>
                <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{animationDelay: '0.1s'}}></div>
                <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{animationDelay: '0.2s'}}></div>
              </div>
            </div>
          </div>
        )}
        
        <div ref={messagesEndRef} />
      </main>

      {/* Input */}
      <footer className="bg-white border-t p-4">
        <div className="flex items-center gap-2">
          <button 
            onClick={() => setShowEmojiPicker(prev => !prev)}
            className="p-2 hover:bg-gray-100 rounded-full transition-colors"
          >
            <Smile className="w-5 h-5 text-gray-600" />
          </button>
          
          <input
            type="text"
            value={newMessage}
            onChange={handleTyping}
            onKeyPress={(e) => e.key === 'Enter' && handleSendMessage()}
            placeholder="اكتب رسالة..."
            className="flex-1 px-4 py-2 border rounded-full focus:outline-none focus:ring-2 focus:ring-pink-500"
          />
          
          {/* WebSocket Status Indicator */}
          {isConnected && (
            <div className="absolute -top-8 right-4 text-xs text-green-600 flex items-center gap-1">
              <div className="w-2 h-2 bg-green-500 rounded-full animate-pulse"></div>
              متصل
            </div>
          )}

          <button
            onClick={handleSendMessage}
            disabled={sending || !newMessage.trim()}
            className={`p-2 bg-gradient-to-r from-pink-500 to-purple-500 text-white rounded-full hover:shadow-lg transition-all ${
              sending || !newMessage.trim() ? 'opacity-50 cursor-not-allowed' : ''
            }`}
          >
            {sending ? (
              <div className="w-5 h-5 border-2 border-white border-t-transparent rounded-full animate-spin"></div>
            ) : (
              <Send className="w-5 h-5" />
            )}
          </button>
        </div>
      </footer>

      {/* Emoji Picker */}
      {showEmojiPicker && (
        <EmojiPicker 
          onSelect={insertEmoji}
          onClose={() => setShowEmojiPicker(false)}
        />
      )}

      {/* Safety Consent Modal */}
      <SafetyConsentModal 
        open={showSafetyConsent}
        onAccept={handleAgreeSafety}
        onClose={() => setShowSafetyConsent(false)}
      />

      {/* Message Limit Warning Modal */}
      {showMessageLimitWarning && (
        <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50 p-4">
          <Card className="max-w-md w-full p-6 bg-gradient-to-br from-purple-50 to-pink-50">
            <div className="text-center">
              <div className="text-6xl mb-4">💬</div>
              <h2 className="text-2xl font-bold mb-2 text-gray-800">
                وصلت إلى حد الرسائل الأسبوعي!
              </h2>
              <p className="text-gray-600 mb-4">
                المستخدمون المجانيون يمكنهم إرسال 10 رسائل كل أسبوع.
              </p>
              <p className="text-gray-600 mb-6">
                قم بالترقية إلى Premium للحصول على رسائل غير محدودة! 💎
              </p>

              <Button
                onClick={() => {
                  setShowMessageLimitWarning(false);
                  navigate('/premium');
                }}
                className="w-full bg-gradient-to-r from-pink-500 to-purple-500 hover:from-pink-600 hover:to-purple-600 text-white font-bold text-lg py-6 mb-3"
              >
                <Star className="w-5 h-5 ml-2" />
                ترقية إلى Premium
              </Button>
              
              <Button
                onClick={() => setShowMessageLimitWarning(false)}
                variant="ghost"
                className="w-full"
              >
                إغلاق
              </Button>
            </div>
          </Card>
        </div>
      )}
      
      {/* Call Modal */}
      {showCallModal && (
        <CallModal
          matchId={matchId}
          type={callType}
          onClose={() => setShowCallModal(false)}
        />
      )}
    </div>
  );
};

export default ChatRoom;
