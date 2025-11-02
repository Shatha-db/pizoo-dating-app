import { JitsiMeeting } from '@jitsi/react-sdk';
import { useState } from 'react';
import { Video, Phone, X } from 'lucide-react';

export default function JitsiButtons({ roomName, displayName }) {
  const [openVideo, setOpenVideo] = useState(false);
  const [openVoice, setOpenVoice] = useState(false);

  const domain = "meet.jit.si"; // Free Jitsi server

  const commonProps = {
    domain,
    configOverwrite: {
      startWithAudioMuted: false,
      prejoinPageEnabled: false, // ✅ Disabled - no external registration prompt
      enableWelcomePage: false,
      disableDeepLinking: true // Prevent app store redirects
    },
    interfaceConfigOverwrite: {
      DISABLE_JOIN_LEAVE_NOTIFICATIONS: false,
      SHOW_JITSI_WATERMARK: false,
      APP_NAME: 'Pizoo', // ✅ Custom branding
      TOOLBAR_BUTTONS: [
        'microphone', 'camera', 'closedcaptions', 'desktop', 'fullscreen',
        'fodeviceselection', 'hangup', 'profile', 'chat', 'recording',
        'etherpad', 'sharedvideo', 'settings', 'raisehand',
        'videoquality', 'filmstrip', 'feedback', 'stats', 'shortcuts',
        'tileview', 'download', 'help', 'mute-everyone'
      ]
    },
    userInfo: {
      displayName: displayName || 'Pizoo User'
    },
    getIFrameRef: (node) => {
      if (node) {
        node.style.height = '80vh';
        node.style.width = '100%';
      }
    }
  };

  return (
    <div className="flex gap-2 items-center">
      {/* Video Call Button */}
      <button
        onClick={() => {
          setOpenVideo(v => !v);
          setOpenVoice(false);
        }}
        className="flex items-center gap-2 px-3 py-2 bg-blue-500 hover:bg-blue-600 text-white rounded-lg transition-colors"
        title="Start video call"
      >
        <Video className="w-4 h-4" />
        <span className="hidden sm:inline">Video</span>
      </button>

      {/* Voice Call Button */}
      <button
        onClick={() => {
          setOpenVoice(v => !v);
          setOpenVideo(false);
        }}
        className="flex items-center gap-2 px-3 py-2 bg-green-500 hover:bg-green-600 text-white rounded-lg transition-colors"
        title="Start voice call"
      >
        <Phone className="w-4 h-4" />
        <span className="hidden sm:inline">Voice</span>
      </button>

      {/* Video Call Modal */}
      {openVideo && (
        <div className="fixed inset-0 z-50 bg-black/80 p-3 flex items-center justify-center">
          <div className="bg-white rounded-2xl overflow-hidden w-full max-w-5xl shadow-2xl">
            <div className="p-3 bg-gray-100 flex justify-between items-center">
              <h3 className="font-semibold text-gray-800">Video Call - {roomName}</h3>
              <button
                className="p-2 rounded-lg bg-red-500 hover:bg-red-600 text-white transition-colors"
                onClick={() => setOpenVideo(false)}
                title="Close"
              >
                <X className="w-5 h-5" />
              </button>
            </div>
            <JitsiMeeting
              roomName={roomName}
              {...commonProps}
            />
          </div>
        </div>
      )}

      {/* Voice Call Modal */}
      {openVoice && (
        <div className="fixed inset-0 z-50 bg-black/80 p-3 flex items-center justify-center">
          <div className="bg-white rounded-2xl overflow-hidden w-full max-w-3xl shadow-2xl">
            <div className="p-3 bg-gray-100 flex justify-between items-center">
              <h3 className="font-semibold text-gray-800">Voice Call - {roomName}</h3>
              <button
                className="p-2 rounded-lg bg-red-500 hover:bg-red-600 text-white transition-colors"
                onClick={() => setOpenVoice(false)}
                title="Close"
              >
                <X className="w-5 h-5" />
              </button>
            </div>
            <JitsiMeeting
              roomName={roomName}
              configOverwrite={{
                startWithAudioMuted: false,
                startWithVideoMuted: true, // Voice only
                prejoinPageEnabled: false, // ✅ Disabled - no external registration prompt
                enableWelcomePage: false,
                disableDeepLinking: true
              }}
              interfaceConfigOverwrite={{
                DISABLE_JOIN_LEAVE_NOTIFICATIONS: false,
                SHOW_JITSI_WATERMARK: false,
                APP_NAME: 'Pizoo'
              }}
              userInfo={{
                displayName: displayName || 'Pizoo User'
              }}
              getIFrameRef={(node) => {
                if (node) {
                  node.style.height = '60vh';
                  node.style.width = '100%';
                }
              }}
            />
          </div>
        </div>
      )}
    </div>
  );
}
