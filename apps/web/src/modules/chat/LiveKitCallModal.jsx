import React, { useState, useEffect } from 'react';
import {
  LiveKitRoom,
  VideoConference,
  RoomAudioRenderer,
} from '@livekit/components-react';
import { X, PhoneOff } from 'lucide-react';
import { useTranslation } from 'react-i18next';
import axios from 'axios';

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;

export default function LiveKitCallModal({ matchId, type = 'video', onClose }) {
  const { t } = useTranslation(['chat', 'common']);
  const [connectionState, setConnectionState] = useState('connecting'); // connecting, connected, failed
  const [token, setToken] = useState(null);
  const [serverUrl, setServerUrl] = useState(null);
  const [roomName, setRoomName] = useState(null);
  const [error, setError] = useState(null);

  // Fetch LiveKit token on mount
  useEffect(() => {
    const fetchToken = async () => {
      try {
        const authToken = localStorage.getItem('token');
        
        const response = await axios.post(
          `${BACKEND_URL}/api/livekit/token`,
          {
            match_id: matchId,
            call_type: type
          },
          {
            headers: {
              'Authorization': `Bearer ${authToken}`,
              'Content-Type': 'application/json'
            }
          }
        );

        if (response.data.success) {
          setToken(response.data.token);
          setServerUrl(response.data.url);
          setRoomName(response.data.room_name);
          setConnectionState('connected');
        } else {
          setError(response.data.error || 'Failed to connect');
          setConnectionState('failed');
        }
      } catch (err) {
        console.error('LiveKit token error:', err);
        setError(err.response?.data?.detail || 'فشل الاتصال بخدمة المكالمات');
        setConnectionState('failed');
      }
    };

    fetchToken();
  }, [matchId, type]);

  // Handle ESC key
  useEffect(() => {
    const handleEsc = (e) => {
      if (e.key === 'Escape') onClose();
    };
    window.addEventListener('keydown', handleEsc);
    return () => window.removeEventListener('keydown', handleEsc);
  }, [onClose]);

  // Render loading state
  if (connectionState === 'connecting') {
    return (
      <div className="fixed inset-0 bg-black/95 flex items-center justify-center z-[9999]">
        <div className="text-center space-y-4">
          <div className="animate-spin rounded-full h-16 w-16 border-t-4 border-b-4 border-pink-500 mx-auto"></div>
          <p className="text-white text-lg">{t('Connecting...', { ns: 'chat' })}</p>
        </div>
      </div>
    );
  }

  // Render error state
  if (connectionState === 'failed' || error) {
    return (
      <div className="fixed inset-0 bg-black/95 flex items-center justify-center z-[9999]">
        <div className="bg-white rounded-2xl p-8 max-w-md mx-4 text-center space-y-4">
          <div className="w-16 h-16 bg-red-100 rounded-full flex items-center justify-center mx-auto">
            <X className="w-8 h-8 text-red-500" />
          </div>
          <h2 className="text-xl font-bold text-gray-900">
            {t('Connection Failed', { ns: 'chat' })}
          </h2>
          <p className="text-gray-600">{error}</p>
          <button
            onClick={onClose}
            className="w-full px-6 py-3 bg-gradient-to-r from-pink-500 to-rose-500 text-white rounded-xl font-medium hover:shadow-lg transition-shadow"
          >
            {t('Close', { ns: 'common' })}
          </button>
        </div>
      </div>
    );
  }

  // Render LiveKit room
  return (
    <div className="fixed inset-0 bg-black z-[9999]">
      {/* Add basic LiveKit styles inline */}
      <style>{`
        .lk-room-container {
          height: 100%;
          width: 100%;
          display: flex;
          flex-direction: column;
        }
        .lk-video-conference {
          height: 100%;
          width: 100%;
          display: flex;
          flex-direction: column;
        }
        .lk-grid-layout {
          display: grid;
          gap: 8px;
          padding: 8px;
          height: 100%;
        }
        .lk-participant-tile {
          position: relative;
          background: #1a1a1a;
          border-radius: 8px;
          overflow: hidden;
        }
        .lk-participant-tile video {
          width: 100%;
          height: 100%;
          object-fit: cover;
        }
        .lk-participant-name {
          position: absolute;
          bottom: 8px;
          left: 8px;
          background: rgba(0, 0, 0, 0.7);
          color: white;
          padding: 4px 8px;
          border-radius: 4px;
          font-size: 14px;
        }
        .lk-control-bar {
          position: absolute;
          bottom: 0;
          left: 0;
          right: 0;
          display: flex;
          justify-content: center;
          gap: 12px;
          padding: 24px;
          background: linear-gradient(to top, rgba(0,0,0,0.8), transparent);
        }
        .lk-button {
          padding: 12px;
          border-radius: 50%;
          border: none;
          cursor: pointer;
          transition: all 0.2s;
          background: rgba(255, 255, 255, 0.2);
          color: white;
        }
        .lk-button:hover {
          background: rgba(255, 255, 255, 0.3);
        }
        .lk-button.active {
          background: #ef4444;
        }
      `}</style>
      
      <LiveKitRoom
        video={type === 'video'}
        audio={true}
        token={token}
        serverUrl={serverUrl}
        style={{ height: '100vh', width: '100%' }}
        onDisconnected={onClose}
      >
        {/* Header */}
        <div className="absolute top-0 left-0 right-0 bg-gradient-to-b from-black/80 to-transparent p-4 flex justify-between items-center z-50">
          <div className="flex items-center gap-2">
            <div className="w-2 h-2 bg-red-500 rounded-full animate-pulse"></div>
            <span className="text-white text-sm font-medium">
              {type === 'video' ? '🎥 ' + t('Video Call', { ns: 'chat' }) : '🎤 ' + t('Voice Call', { ns: 'chat' })}
            </span>
          </div>
          <button
            onClick={onClose}
            className="p-2 rounded-full bg-white/10 hover:bg-white/20 transition-colors backdrop-blur-sm"
            title={t('End Call', { ns: 'chat' })}
          >
            <PhoneOff className="w-5 h-5 text-white" />
          </button>
        </div>

        {/* Video Conference (handles layout automatically) */}
        <VideoConference />

        {/* Audio renderer (for audio-only participants) */}
        <RoomAudioRenderer />

        {/* Custom Control Bar (optional - VideoConference includes one) */}
        {/* Uncomment if you want custom controls */}
        {/* 
        <div className="absolute bottom-0 left-0 right-0 bg-gradient-to-t from-black/80 to-transparent p-6 flex justify-center gap-4">
          <button
            onClick={() => setMicMuted(!micMuted)}
            className={`p-4 rounded-full transition-colors ${
              micMuted ? 'bg-red-500 hover:bg-red-600' : 'bg-white/20 hover:bg-white/30'
            }`}
          >
            {micMuted ? <MicOff className="w-6 h-6 text-white" /> : <Mic className="w-6 h-6 text-white" />}
          </button>
          
          {type === 'video' && (
            <button
              onClick={() => setVideoMuted(!videoMuted)}
              className={`p-4 rounded-full transition-colors ${
                videoMuted ? 'bg-red-500 hover:bg-red-600' : 'bg-white/20 hover:bg-white/30'
              }`}
            >
              {videoMuted ? <VideoOff className="w-6 h-6 text-white" /> : <Video className="w-6 h-6 text-white" />}
            </button>
          )}
          
          <button
            onClick={onClose}
            className="p-4 rounded-full bg-red-500 hover:bg-red-600 transition-colors"
          >
            <PhoneOff className="w-6 h-6 text-white" />
          </button>
        </div>
        */}
      </LiveKitRoom>
    </div>
  );
}
