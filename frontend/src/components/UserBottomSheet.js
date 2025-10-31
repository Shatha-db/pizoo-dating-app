import React from 'react';
import { X, Heart, MessageCircle, MapPin, Shield } from 'lucide-react';
import { useNavigate } from 'react-router-dom';
import { Button } from './ui/button';

const UserBottomSheet = ({ user, onClose, onLike }) => {
  const navigate = useNavigate();

  if (!user) return null;

  const primaryPhoto = user.photos?.find(p => p.is_primary)?.url || user.photos?.[0]?.url || 
    'https://via.placeholder.com/400x500?text=No+Photo';

  return (
    <>
      {/* Overlay */}
      <div 
        className="fixed inset-0 bg-black bg-opacity-50 z-40 transition-opacity"
        onClick={onClose}
      />
      
      {/* Bottom Sheet */}
      <div className="fixed bottom-0 left-0 right-0 bg-white rounded-t-3xl shadow-2xl z-50 animate-slide-up max-h-[70vh] overflow-y-auto">
        {/* Header Image */}
        <div className="relative h-64">
          <img
            src={primaryPhoto}
            alt={user.name}
            className="w-full h-full object-cover"
          />
          <button
            onClick={onClose}
            className="absolute top-4 right-4 bg-white rounded-full p-2 shadow-lg hover:bg-gray-100 transition"
          >
            <X className="w-5 h-5 text-gray-700" />
          </button>
        </div>

        {/* User Info */}
        <div className="p-6" dir="rtl">
          {/* Name & Age */}
          <div className="flex items-center justify-between mb-3">
            <div className="flex items-center gap-2">
              <h2 className="text-2xl font-bold">{user.name}</h2>
              <span className="text-2xl font-semibold text-gray-600">{user.age}</span>
              {user.verified && (
                <Shield className="w-5 h-5 text-blue-500 fill-blue-500" />
              )}
            </div>
          </div>

          {/* Distance */}
          {user.distance !== undefined && (
            <div className="flex items-center gap-2 text-gray-600 mb-4">
              <MapPin className="w-4 h-4" />
              <span className="text-sm">{user.distance < 1 ? '< 1' : Math.round(user.distance)} كم بعيد</span>
            </div>
          )}

          {/* Bio */}
          {user.bio && (
            <p className="text-gray-700 mb-4 leading-relaxed">{user.bio}</p>
          )}

          {/* Interests */}
          {user.interests && user.interests.length > 0 && (
            <div className="flex flex-wrap gap-2 mb-4">
              {user.interests.map((interest, idx) => (
                <span
                  key={idx}
                  className="px-3 py-1 bg-pink-100 text-pink-600 rounded-full text-sm font-medium"
                >
                  {interest}
                </span>
              ))}
            </div>
          )}

          {/* Action Buttons */}
          <div className="flex gap-3">
            <Button
              onClick={() => navigate(`/profile/${user.id}`)}
              className="flex-1 bg-white border-2 border-pink-500 text-pink-500 hover:bg-pink-50 font-semibold py-6 text-lg rounded-xl transition"
            >
              عرض الملف الشخصي
            </Button>
            <Button
              onClick={() => onLike(user.id)}
              className="flex-1 bg-gradient-to-r from-pink-500 to-red-500 hover:from-pink-600 hover:to-red-600 text-white font-semibold py-6 text-lg rounded-xl transition shadow-lg"
            >
              <Heart className="w-5 h-5 ml-2" />
              إعجاب
            </Button>
          </div>

          {/* Secondary Action */}
          <Button
            onClick={() => navigate(`/chat/new/${user.id}`)}
            variant="ghost"
            className="w-full mt-3 text-gray-600 hover:text-pink-500 py-4"
          >
            <MessageCircle className="w-5 h-5 ml-2" />
            إرسال رسالة
          </Button>
        </div>
      </div>

      <style jsx>{`
        @keyframes slide-up {
          from {
            transform: translateY(100%);
          }
          to {
            transform: translateY(0);
          }
        }
        .animate-slide-up {
          animation: slide-up 0.3s ease-out;
        }
      `}</style>
    </>
  );
};

export default UserBottomSheet;
