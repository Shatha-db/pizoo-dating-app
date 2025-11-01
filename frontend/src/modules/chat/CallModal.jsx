import React, { useEffect, useRef } from 'react';
import { X } from 'lucide-react';
import { useTranslation } from 'react-i18next';

export default function CallModal({ matchId, type = 'video', onClose }) {
  const { t } = useTranslation(['chat', 'common']);
  const iframeRef = useRef(null);
  
  const roomName = `pizoo-match-${matchId}`;
  
  // ✅ Properly formatted Jitsi URL to skip prejoin page
  const baseUrl = `https://meet.jit.si/${roomName}`;
  const hashParams = [
    'config.prejoinPageEnabled=false',
    `config.startWithAudioMuted=false`,
    `config.startWithVideoMuted=${type === 'audio' ? 'true' : 'false'}`,
    'config.disableDeepLinking=true',
    'interfaceConfig.SHOW_JITSI_WATERMARK=false',
    'interfaceConfig.APP_NAME=Pizoo',
    'interfaceConfig.SHOW_BRAND_WATERMARK=false',
    'interfaceConfig.SHOW_POWERED_BY=false',
    'interfaceConfig.MOBILE_APP_PROMO=false',
    'userInfo.displayName=Pizoo User'
  ];
  
  const jitsiUrl = `${baseUrl}#${hashParams.join('&')}`;

  useEffect(() => {
    // Auto-close modal on ESC key
    const handleEsc = (e) => {
      if (e.key === 'Escape') onClose();
    };
    window.addEventListener('keydown', handleEsc);
    return () => window.removeEventListener('keydown', handleEsc);
  }, [onClose]);

  return (
    <div className="fixed inset-0 bg-black/95 flex items-center justify-center z-[9999]">
      <div className="w-full h-full flex flex-col">
        {/* Minimal Header */}
        <div className="bg-gradient-to-r from-pink-500 to-rose-500 px-4 py-3 flex justify-between items-center flex-shrink-0">
          <div className="flex items-center gap-2">
            <div className="w-2 h-2 bg-red-500 rounded-full animate-pulse"></div>
            <span className="text-white text-sm font-medium">
              {type === 'video' ? '🎥 ' + t('Video Call', { ns: 'chat' }) : '🎤 ' + t('Voice Call', { ns: 'chat' })}
            </span>
          </div>
          <button
            onClick={onClose}
            className="p-2 rounded-full hover:bg-white/10 transition-colors"
            title={t('Close', { ns: 'common' })}
          >
            <X className="w-5 h-5 text-white" />
          </button>
        </div>

        {/* Full-screen Jitsi */}
        <div className="flex-1 bg-gray-900">
          <iframe
            ref={iframeRef}
            src={jitsiUrl}
            allow="camera; microphone; fullscreen; display-capture; autoplay"
            style={{
              width: '100%',
              height: '100%',
              border: 'none'
            }}
            title={t('Video Call', { ns: 'chat' })}
          />
        </div>
      </div>
    </div>
  );
}
