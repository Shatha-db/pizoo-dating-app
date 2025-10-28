import { useEffect, useRef, useState } from 'react';
import { X } from 'lucide-react';

const JitsiModal = ({ room, open, onClose, displayName = 'User' }) => {
  const containerRef = useRef(null);
  const apiRef = useRef(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    if (!open || !room) {
      return;
    }

    const loadJitsi = async () => {
      try {
        setLoading(true);
        setError(null);

        // Check if script is already loaded
        if (!window.JitsiMeetExternalAPI) {
          await new Promise((resolve, reject) => {
            const script = document.createElement('script');
            script.src = 'https://meet.jit.si/external_api.js';
            script.async = true;
            script.onload = resolve;
            script.onerror = () => reject(new Error('Failed to load Jitsi script'));
            document.body.appendChild(script);
          });
        }

        if (!containerRef.current) return;

        // Initialize Jitsi Meet
        const domain = 'meet.jit.si';
        const options = {
          roomName: `pizoo-${room}`,
          width: '100%',
          height: 520,
          parentNode: containerRef.current,
          userInfo: {
            displayName: displayName || 'User',
          },
          configOverwrite: {
            startWithAudioMuted: false,
            startWithVideoMuted: false,
            prejoinPageEnabled: false,
            disableDeepLinking: true,
          },
          interfaceConfigOverwrite: {
            TOOLBAR_BUTTONS: [
              'microphone',
              'camera',
              'closedcaptions',
              'desktop',
              'fullscreen',
              'fodeviceselection',
              'hangup',
              'chat',
              'recording',
              'livestreaming',
              'etherpad',
              'settings',
              'raisehand',
              'videoquality',
              'filmstrip',
              'feedback',
              'stats',
              'shortcuts',
              'tileview',
              'download',
              'help',
              'mute-everyone',
            ],
            SHOW_JITSI_WATERMARK: false,
            SHOW_WATERMARK_FOR_GUESTS: false,
          },
        };

        const api = new window.JitsiMeetExternalAPI(domain, options);
        apiRef.current = api;

        // Listen for ready event
        api.addEventListener('videoConferenceJoined', () => {
          setLoading(false);
        });

        // Listen for close event
        api.addEventListener('readyToClose', () => {
          onClose?.();
        });

        setLoading(false);
      } catch (err) {
        console.error('Jitsi initialization error:', err);
        setError('فشل تحميل المكالمة. الرجاء المحاولة مرة أخرى.');
        setLoading(false);
      }
    };

    loadJitsi();

    // Cleanup
    return () => {
      if (apiRef.current) {
        try {
          apiRef.current.dispose();
        } catch (err) {
          console.error('Error disposing Jitsi:', err);
        }
        apiRef.current = null;
      }
    };
  }, [open, room, displayName, onClose]);

  if (!open) return null;

  return (
    <div className="fixed inset-0 bg-black/80 z-50 flex items-center justify-center p-4">
      <div className="bg-white dark:bg-gray-800 rounded-2xl w-full max-w-5xl overflow-hidden shadow-2xl">
        {/* Header */}
        <div className="flex items-center justify-between p-4 bg-gradient-to-r from-pink-500 to-purple-600">
          <h3 className="text-white font-bold text-lg">مكالمة فيديو</h3>
          <button
            onClick={onClose}
            className="text-white hover:bg-white/20 p-2 rounded-full transition"
          >
            <X className="w-5 h-5" />
          </button>
        </div>

        {/* Jitsi Container */}
        <div className="relative bg-gray-900">
          {loading && (
            <div className="absolute inset-0 flex items-center justify-center">
              <div className="text-center text-white">
                <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-white mx-auto mb-4"></div>
                <p>جاري تحميل المكالمة...</p>
              </div>
            </div>
          )}
          {error && (
            <div className="absolute inset-0 flex items-center justify-center">
              <div className="text-center text-white">
                <p className="mb-4">{error}</p>
                <button
                  onClick={onClose}
                  className="px-4 py-2 bg-pink-500 hover:bg-pink-600 rounded-lg"
                >
                  إغلاق
                </button>
              </div>
            </div>
          )}
          <div ref={containerRef} className="w-full" style={{ minHeight: '520px' }} />
        </div>

        {/* Footer */}
        <div className="p-3 bg-gray-100 dark:bg-gray-700 text-center">
          <button
            onClick={onClose}
            className="px-6 py-2 bg-red-500 hover:bg-red-600 text-white rounded-full font-medium"
          >
            إنهاء المكالمة
          </button>
        </div>
      </div>
    </div>
  );
};

export default JitsiModal;
