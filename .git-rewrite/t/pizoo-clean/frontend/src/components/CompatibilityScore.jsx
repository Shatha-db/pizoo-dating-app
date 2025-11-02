import React from 'react';
import { Heart, Star, Users, MessageCircle } from 'lucide-react';
import { useTranslation } from 'react-i18next';

/**
 * Compatibility Score Component
 * Displays match compatibility percentage with breakdown
 */
export default function CompatibilityScore({ score, breakdown }) {
  const { t } = useTranslation(['profile']);
  
  // Calculate color based on score
  const getScoreColor = (score) => {
    if (score >= 80) return 'from-green-500 to-emerald-500';
    if (score >= 60) return 'from-yellow-500 to-orange-500';
    return 'from-rose-500 to-pink-500';
  };

  const getScoreText = (score) => {
    if (score >= 80) return t('excellent_match', { ns: 'profile' });
    if (score >= 60) return t('good_match', { ns: 'profile' });
    return t('moderate_match', { ns: 'profile' });
  };

  const scoreColor = getScoreColor(score);

  return (
    <div className="bg-white dark:bg-gray-800 rounded-2xl p-6 shadow-lg">
      {/* Header */}
      <div className="text-center mb-6">
        <h3 className="text-lg font-bold mb-2 dark:text-white">
          {t('compatibility_score', { ns: 'profile' })}
        </h3>
        <div className="relative inline-block">
          {/* Circular Progress */}
          <svg className="w-32 h-32 transform -rotate-90">
            <circle
              cx="64"
              cy="64"
              r="56"
              stroke="currentColor"
              strokeWidth="8"
              fill="none"
              className="text-gray-200 dark:text-gray-700"
            />
            <circle
              cx="64"
              cy="64"
              r="56"
              stroke="url(#gradient)"
              strokeWidth="8"
              fill="none"
              strokeDasharray={`${2 * Math.PI * 56}`}
              strokeDashoffset={`${2 * Math.PI * 56 * (1 - score / 100)}`}
              strokeLinecap="round"
              className="transition-all duration-1000"
            />
            <defs>
              <linearGradient id="gradient" x1="0%" y1="0%" x2="100%" y2="100%">
                <stop offset="0%" className={`text-${scoreColor.split('-')[1]}`} stopColor="currentColor" />
                <stop offset="100%" className={`text-${scoreColor.split('-')[3]}`} stopColor="currentColor" />
              </linearGradient>
            </defs>
          </svg>
          
          {/* Score Text */}
          <div className="absolute inset-0 flex items-center justify-center">
            <div>
              <div className={`text-3xl font-bold bg-gradient-to-r ${scoreColor} bg-clip-text text-transparent`}>
                {score}%
              </div>
              <div className="text-xs text-gray-500 dark:text-gray-400 mt-1">
                {getScoreText(score)}
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Breakdown */}
      {breakdown && (
        <div className="space-y-3">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 rounded-full bg-pink-100 dark:bg-pink-900/30 flex items-center justify-center">
              <Heart className="w-5 h-5 text-pink-600 dark:text-pink-400" />
            </div>
            <div className="flex-1">
              <div className="flex justify-between items-center mb-1">
                <span className="text-sm font-medium dark:text-white">
                  {t('interests', { ns: 'profile' })}
                </span>
                <span className="text-sm font-bold text-pink-600 dark:text-pink-400">
                  {breakdown.interests}%
                </span>
              </div>
              <div className="h-2 bg-gray-200 dark:bg-gray-700 rounded-full overflow-hidden">
                <div 
                  className="h-full bg-gradient-to-r from-pink-500 to-rose-500 transition-all duration-500"
                  style={{ width: `${breakdown.interests}%` }}
                />
              </div>
            </div>
          </div>

          <div className="flex items-center gap-3">
            <div className="w-10 h-10 rounded-full bg-purple-100 dark:bg-purple-900/30 flex items-center justify-center">
              <Star className="w-5 h-5 text-purple-600 dark:text-purple-400" />
            </div>
            <div className="flex-1">
              <div className="flex justify-between items-center mb-1">
                <span className="text-sm font-medium dark:text-white">
                  {t('lifestyle', { ns: 'profile' })}
                </span>
                <span className="text-sm font-bold text-purple-600 dark:text-purple-400">
                  {breakdown.lifestyle}%
                </span>
              </div>
              <div className="h-2 bg-gray-200 dark:bg-gray-700 rounded-full overflow-hidden">
                <div 
                  className="h-full bg-gradient-to-r from-purple-500 to-indigo-500 transition-all duration-500"
                  style={{ width: `${breakdown.lifestyle}%` }}
                />
              </div>
            </div>
          </div>

          <div className="flex items-center gap-3">
            <div className="w-10 h-10 rounded-full bg-blue-100 dark:bg-blue-900/30 flex items-center justify-center">
              <MessageCircle className="w-5 h-5 text-blue-600 dark:text-blue-400" />
            </div>
            <div className="flex-1">
              <div className="flex justify-between items-center mb-1">
                <span className="text-sm font-medium dark:text-white">
                  {t('communication', { ns: 'profile' })}
                </span>
                <span className="text-sm font-bold text-blue-600 dark:text-blue-400">
                  {breakdown.communication}%
                </span>
              </div>
              <div className="h-2 bg-gray-200 dark:bg-gray-700 rounded-full overflow-hidden">
                <div 
                  className="h-full bg-gradient-to-r from-blue-500 to-cyan-500 transition-all duration-500"
                  style={{ width: `${breakdown.communication}%` }}
                />
              </div>
            </div>
          </div>

          <div className="flex items-center gap-3">
            <div className="w-10 h-10 rounded-full bg-green-100 dark:bg-green-900/30 flex items-center justify-center">
              <Users className="w-5 h-5 text-green-600 dark:text-green-400" />
            </div>
            <div className="flex-1">
              <div className="flex justify-between items-center mb-1">
                <span className="text-sm font-medium dark:text-white">
                  {t('values', { ns: 'profile' })}
                </span>
                <span className="text-sm font-bold text-green-600 dark:text-green-400">
                  {breakdown.values}%
                </span>
              </div>
              <div className="h-2 bg-gray-200 dark:bg-gray-700 rounded-full overflow-hidden">
                <div 
                  className="h-full bg-gradient-to-r from-green-500 to-emerald-500 transition-all duration-500"
                  style={{ width: `${breakdown.values}%` }}
                />
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
