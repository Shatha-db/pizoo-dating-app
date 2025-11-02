import React from 'react';
import { useNavigate } from 'react-router-dom';
import { useTranslation } from 'react-i18next';

const PersonalCard = ({ moment }) => {
  const navigate = useNavigate();
  const { t } = useTranslation('personal');

  const handleClick = () => {
    if (moment.action === 'view_profile' && moment.userId) {
      navigate(`/profile/${moment.userId}`);
    } else if (moment.action === 'open_link' && moment.link) {
      window.open(moment.link, '_blank');
    }
  };

  return (
    <div
      onClick={handleClick}
      className="bg-white dark:bg-gray-800 rounded-2xl shadow-lg overflow-hidden cursor-pointer hover:shadow-xl transition-shadow duration-300"
    >
      {/* Image */}
      <div className="relative h-48 bg-gradient-to-br from-pink-200 to-purple-200 dark:from-pink-800 dark:to-purple-800">
        <img
          src={moment.image || 'https://via.placeholder.com/400x300'}
          alt={moment.title}
          className="w-full h-full object-cover"
        />
        
        {/* Badges */}
        <div className="absolute top-3 right-3 flex gap-2">
          {moment.isPremium && (
            <span className="bg-gradient-to-r from-yellow-400 to-orange-500 text-white px-3 py-1 rounded-full text-xs font-bold shadow-md">
              ⭐ {t('premium_badge')}
            </span>
          )}
          {moment.isNew && (
            <span className="bg-green-500 text-white px-3 py-1 rounded-full text-xs font-bold shadow-md">
              ✨ {t('new_badge')}
            </span>
          )}
        </div>
      </div>

      {/* Content */}
      <div className="p-4">
        <h3 className="font-bold text-lg text-gray-900 dark:text-white mb-2">
          {moment.title}
        </h3>
        <p className="text-sm text-gray-600 dark:text-gray-300 mb-3 line-clamp-2">
          {moment.description}
        </p>
        
        {/* CTA Button */}
        <button className="w-full bg-gradient-to-r from-pink-500 to-purple-600 text-white font-medium py-2 px-4 rounded-xl hover:from-pink-600 hover:to-purple-700 transition-all duration-200">
          {moment.ctaText || t('view_details')}
        </button>
      </div>
    </div>
  );
};

export default PersonalCard;
