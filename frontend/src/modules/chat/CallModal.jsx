import React, { useEffect, useRef } from 'react';
import { X } from 'lucide-react';

export default function CallModal({ matchId, type = 'video', onClose }) {
  const containerRef = useRef(null);
  const apiRef = useRef(null);

  useEffect(() => {
    if (!matchId || !containerRef.current) return;

    // Load Jitsi External API script if not loaded
    const loadJitsi = () => {
      return new Promise((resolve, reject) => {
        if (window.JitsiMeetExternalAPI) {
          resolve();
          return;
        }

        const script = document.createElement('script');
        script.src = 'https://meet.jit.si/external_api.js';
        script.async = true;
        script.onload = resolve;
        script.onerror = reject;
        document.head.appendChild(script);
      });
    };

    loadJitsi()
      .then(() => {
        const domain = 'meet.jit.si';
        const options = {
          roomName: `pizoo-match-${matchId}`,
          parentNode: containerRef.current,
          width: '100%',
          height: '500px',
          configOverwrite: {
            startWithAudioMuted: false,
            startWithVideoMuted: type === 'audio',
            prejoinPageEnabled: false,
            enableWelcomePage: false
          },
          interfaceConfigOverwrite: {
            SHOW_JITSI_WATERMARK: false,
            TOOLBAR_BUTTONS: [
              'microphone', 'camera', 'hangup', 'chat',
              'desktop', 'fullscreen', 'settings'
            ]
          },
          userInfo: {
            displayName: 'Pizoo User'
          }
        };

        apiRef.current = new window.JitsiMeetExternalAPI(domain, options);
        
        // Handle call end
        apiRef.current.addEventListener('readyToClose', () => {
          onClose();
        });
      })
      .catch((error) => {
        console.error('Failed to load Jitsi:', error);
      });

    return () => {
      if (apiRef.current) {
        apiRef.current.dispose();
        apiRef.current = null;
      }
    };
  }, [matchId, type]);

  return (
    <div className="fixed inset-0 bg-black/80 flex items-center justify-center z-50 p-4">
      <div className="bg-white rounded-2xl overflow-hidden shadow-2xl w-full max-w-4xl">
        {/* Header */}
        <div className="bg-gradient-to-r from-pink-500 to-rose-500 p-4 flex justify-between items-center">
          <h3 className="text-white font-semibold text-lg">
            {type === 'video' ? '🎥 مكالمة فيديو' : '🎤 مكالمة صوتية'}
          </h3>
          <button
            onClick={onClose}
            className="p-2 rounded-full bg-white/20 hover:bg-white/30 transition-colors"
          >
            <X className="w-5 h-5 text-white" />
          </button>
        </div>

        {/* Jitsi Container */}
        <div ref={containerRef} className="bg-gray-900" style={{ minHeight: '500px' }}></div>

        {/* Footer */}
        <div className="bg-gray-100 p-4 text-center">
          <button
            onClick={onClose}
            className="px-6 py-2 bg-red-500 hover:bg-red-600 text-white rounded-full font-medium transition-colors"
          >
            إنهاء المكالمة
          </button>
        </div>
      </div>
    </div>
  );
}
