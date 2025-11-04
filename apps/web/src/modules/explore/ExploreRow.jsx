import React from 'react';
import { useNavigate } from 'react-router-dom';
import { useTranslation } from 'react-i18next';

const ExploreRow = ({ title, profiles, onSeeAll }) => {
  const navigate = useNavigate();
  const { t } = useTranslation('explore');

  const handleProfileClick = (userId) => {
    navigate(`/profile/${userId}`);
  };

  if (!profiles || profiles.length === 0) {
    return null;
  }

  return (
    <div className="mb-8">
      <div className="flex justify-between items-center mb-4 px-4">
        <h2 className="text-xl font-bold text-gray-900 dark:text-white">
          {title}
        </h2>
        {onSeeAll && (
          <button
            onClick={onSeeAll}
            className="text-sm text-pink-500 hover:text-pink-600 font-medium"
          >
            {t('see_all')} →
          </button>
        )}
      </div>

      <div className="flex gap-3 overflow-x-auto px-4 pb-2 scrollbar-hide">
        {profiles.map((profile) => (
          <div
            key={profile.id || profile.user_id}
            onClick={() => handleProfileClick(profile.user_id || profile.id)}
            className="flex-shrink-0 w-40 cursor-pointer group"
          >
            <div className="relative overflow-hidden rounded-2xl mb-2 h-52 bg-gradient-to-br from-pink-100 to-purple-100 dark:from-pink-900 dark:to-purple-900">
              <img
                src={profile.photos?.[0] || 'https://via.placeholder.com/200'}
                alt={profile.name}
                className="w-full h-full object-cover group-hover:scale-110 transition-transform duration-300"
              />
              <div className="absolute inset-0 bg-gradient-to-t from-black/60 to-transparent" />
              
              {/* Name and Age overlay */}
              <div className="absolute bottom-0 left-0 right-0 p-3 text-white">
                <h3 className="font-bold text-sm truncate">
                  {profile.name}, {profile.age}
                </h3>
                {profile.location && (
                  <p className="text-xs opacity-90 truncate">
                    📍 {profile.location}
                  </p>
                )}
              </div>

              {/* Distance badge */}
              {profile.distance && (
                <div className="absolute top-2 right-2 bg-white/90 dark:bg-gray-800/90 backdrop-blur-sm px-2 py-1 rounded-full text-xs font-medium text-gray-900 dark:text-white">
                  {profile.distance} km
                </div>
              )}
            </div>
          </div>
        ))}
      </div>

      <style jsx>{`
        .scrollbar-hide::-webkit-scrollbar {
          display: none;
        }
        .scrollbar-hide {
          -ms-overflow-style: none;
          scrollbar-width: none;
        }
      `}</style>
    </div>
  );
};

export default ExploreRow;
