import React from 'react';
import { X, Video, Phone, Mic, Camera } from 'lucide-react';
import { useTranslation } from 'react-i18next';

/**
 * Permissions Modal - Can be used for both image gallery and call permissions
 */
export default function PermissionsModal({ 
  isOpen, 
  onClose, 
  onProceed, 
  onPick,
  callType = null,
  label = null
}) {
  const { t } = useTranslation(['chat']);
  // If not open, don't render
  if (!isOpen && !onPick) return null;

  // Determine if this is for calls or images
  const isForCalls = callType !== null;
  
  // For calls (audio/video)
  if (isForCalls) {
    return (
      <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50 p-4" onClick={onClose}>
        <div 
          className="bg-white dark:bg-gray-800 rounded-2xl max-w-md w-full p-6 relative animate-in zoom-in-95 duration-200"
          onClick={(e) => e.stopPropagation()}
          dir="rtl"
        >
          {/* Close Button */}
          <button
            onClick={onClose}
            className="absolute top-4 left-4 p-2 hover:bg-gray-100 dark:hover:bg-gray-700 rounded-full transition-colors"
          >
            <X className="w-5 h-5 text-gray-600 dark:text-gray-300" />
          </button>

          {/* Icon */}
          <div className="flex justify-center mb-4">
            <div className="w-20 h-20 bg-gradient-to-br from-pink-500 to-purple-500 rounded-full flex items-center justify-center">
              {callType === 'video' ? (
                <Video className="w-10 h-10 text-white" />
              ) : (
                <Phone className="w-10 h-10 text-white" />
              )}
            </div>
          </div>

          {/* Title */}
          <h2 className="text-2xl font-bold text-center text-gray-900 dark:text-white mb-2">
            {t(callType === 'video' ? 'video_call' : 'voice_call')}
          </h2>

          {/* Description */}
          <p className="text-center text-gray-600 dark:text-gray-300 mb-6">
            {t('permissions_request')} {t(callType === 'video' ? 'camera_and_mic' : 'mic_only')}.{' '}
            {t('permissions_necessary')}
          </p>

          {/* Permissions List */}
          <div className="bg-blue-50 dark:bg-blue-900/30 border border-blue-100 dark:border-blue-800 rounded-lg p-4 mb-6">
            <h3 className="font-semibold text-sm text-gray-900 dark:text-white mb-3">{t('permissions_required')}:</h3>
            <div className="space-y-2">
              {callType === 'video' && (
                <div className="flex items-center gap-3">
                  <Camera className="w-5 h-5 text-blue-600 dark:text-blue-400" />
                  <span className="text-sm text-gray-700 dark:text-gray-200">{t('camera_access')}</span>
                </div>
              )}
              <div className="flex items-center gap-3">
                <Mic className="w-5 h-5 text-blue-600 dark:text-blue-400" />
                <span className="text-sm text-gray-700 dark:text-gray-200">{t('microphone_access')}</span>
              </div>
            </div>
          </div>

          {/* Privacy Note */}
          <div className="bg-green-50 dark:bg-green-900/30 border border-green-100 dark:border-green-800 rounded-lg p-3 mb-6">
            <p className="text-xs text-green-800 dark:text-green-200 text-center">
              {t('encryption_notice')}
            </p>
          </div>

          {/* Actions */}
          <div className="space-y-2">
            <button
              onClick={onProceed}
              className="w-full bg-gradient-to-r from-pink-500 to-purple-500 hover:from-pink-600 hover:to-purple-600 text-white font-semibold py-3 rounded-full transition-all"
            >
              {t('continue_call')}
            </button>
            <button
              onClick={onClose}
              className="w-full bg-gray-100 dark:bg-gray-700 hover:bg-gray-200 dark:hover:bg-gray-600 text-gray-700 dark:text-gray-200 font-medium py-3 rounded-full transition-colors"
            >
              {t('cancel', { ns: 'common' })}
            </button>
          </div>
        </div>
      </div>
    );
  }

  // For images (original functionality)
  return (
    <div className="fixed inset-0 z-[1000] bg-black/50 flex items-center justify-center p-4">
      <div className="w-full max-w-md bg-white dark:bg-gray-800 rounded-2xl shadow-xl overflow-hidden">
        <div className="p-6">
          <h3 className="text-lg font-bold mb-2 dark:text-white">
            {label || t('photo_permission')}
          </h3>
          <p className="text-sm text-gray-600 dark:text-gray-300 mb-4">
            {t('photo_permission_desc')}
          </p>
          
          {/* Sample Grid */}
          <div className="grid grid-cols-4 gap-2 mb-4">
            {[...Array(8)].map((_, i) => (
              <div
                key={i}
                className="aspect-square bg-gray-200 dark:bg-gray-700 rounded-lg"
              />
            ))}
          </div>
          
          {/* Action Buttons */}
          <div className="space-y-2">
            <button
              onClick={() => onPick?.('limited')}
              className="w-full h-12 rounded-full bg-gray-100 dark:bg-gray-700 dark:text-white font-medium hover:bg-gray-200 dark:hover:bg-gray-600 transition"
            >
              تحديد الوصول…
            </button>
            <button
              onClick={() => onPick?.('full')}
              className="w-full h-12 rounded-full bg-gradient-to-r from-pink-500 to-rose-500 text-white font-semibold hover:from-pink-600 hover:to-rose-600 transition"
            >
              السماح بالوصول الكامل
            </button>
            <button
              onClick={onClose}
              className="w-full h-12 rounded-full bg-white dark:bg-gray-800 border border-gray-300 dark:border-gray-600 dark:text-white font-medium hover:bg-gray-50 dark:hover:bg-gray-700 transition"
            >
              عدم السماح
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}
