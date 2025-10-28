import React, { useEffect, useRef, useState } from "react";
import { X } from 'lucide-react';

export default function InlineJitsi({
  room,
  audioOnly = false,
  onClose,
  leftAvatar,
  rightAvatar,
  title
}) {
  const containerRef = useRef(null);
  const apiRef = useRef(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    if (!room) return;

    // Load Jitsi External API
    const loadJitsi = async () => {
      try {
        if (!window.JitsiMeetExternalAPI) {
          await new Promise((resolve, reject) => {
            const script = document.createElement("script");
            script.src = "https://meet.jit.si/external_api.js";
            script.async = true;
            script.onload = resolve;
            script.onerror = reject;
            document.body.appendChild(script);
          });
        }

        if (!containerRef.current) return;

        const domain = "meet.jit.si";
        const options = {
          roomName: room,
          parentNode: containerRef.current,
          width: '100%',
          height: 420,
          configOverwrite: {
            startWithAudioMuted: false,
            startWithVideoMuted: audioOnly,
            prejoinPageEnabled: false,
          },
          interfaceConfigOverwrite: {
            MOBILE_APP_PROMO: false,
            SHOW_JITSI_WATERMARK: false,
          },
        };

        // eslint-disable-next-line no-undef
        const api = new JitsiMeetExternalAPI(domain, options);
        apiRef.current = api;

        api.addEventListener('videoConferenceJoined', () => {
          setLoading(false);
        });

        api.addEventListener('readyToClose', () => {
          onClose?.();
        });

      } catch (error) {
        console.error('Failed to load Jitsi:', error);
        setLoading(false);
      }
    };

    loadJitsi();

    return () => {
      try {
        apiRef.current?.dispose();
      } catch (e) {
        console.error('Error disposing Jitsi:', e);
      }
    };
  }, [room, audioOnly, onClose]);

  return (
    <div className="fixed inset-0 z-[999] bg-black/60 flex items-center justify-center p-4">
      <div className="w-full max-w-2xl bg-white dark:bg-gray-800 rounded-2xl overflow-hidden shadow-2xl">
        {/* Header with Avatars */}
        <div className="bg-gradient-to-r from-pink-500 to-rose-500 text-white px-4 py-3 flex items-center justify-between">
          <div className="flex items-center gap-3">
            {leftAvatar && (
              <img
                src={leftAvatar}
                alt=""
                className="w-9 h-9 rounded-full border-2 border-white object-cover"
              />
            )}
            {rightAvatar && (
              <img
                src={rightAvatar}
                alt=""
                className="w-9 h-9 rounded-full border-2 border-white -ml-3 object-cover"
              />
            )}
            <div className="font-semibold">
              {title || (audioOnly ? "مكالمة صوتية" : "مكالمة فيديو")}
            </div>
          </div>
          <button
            onClick={onClose}
            className="bg-white/20 hover:bg-white/30 rounded-full p-2 transition"
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
          <div ref={containerRef} style={{ minHeight: '420px' }} />
        </div>

        {/* Footer */}
        <div className="p-3 bg-gray-50 dark:bg-gray-700">
          <button
            onClick={onClose}
            className="w-full h-11 rounded-full bg-rose-600 hover:bg-rose-700 text-white font-semibold transition"
          >
            إنهاء المكالمة
          </button>
        </div>
      </div>
    </div>
  );
}

