import React, { useEffect, useRef, useState } from 'react';
import { Room, createLocalVideoTrack, createLocalAudioTrack } from 'livekit-client';

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;

async function fetchLiveKitToken(roomName, mode = 'video') {
  const authToken = localStorage.getItem('token');
  
  const res = await fetch(`${BACKEND_URL}/api/livekit/token`, {
    method: 'POST',
    headers: { 
      'Content-Type': 'application/json',
      'Authorization': `Bearer ${authToken}`
    },
    credentials: 'include',
    body: JSON.stringify({ 
      match_id: roomName, 
      call_type: mode 
    }),
  });
  
  if (!res.ok) {
    const txt = await res.text();
    throw new Error(`Token API failed: ${res.status} - ${txt}`);
  }
  
  const data = await res.json();
  return { token: data.token, url: data.url };
}

export default function LiveKitCall({ roomName, mode = 'video', onClose }) {
  const localVideoRef = useRef(null);
  const remoteVideoRef = useRef(null);
  const [room, setRoom] = useState(null);
  const [connecting, setConnecting] = useState(false);
  const [error, setError] = useState(null);
  const [micMuted, setMicMuted] = useState(false);
  const [videoMuted, setVideoMuted] = useState(false);
  const [remoteParticipants, setRemoteParticipants] = useState([]);

  useEffect(() => () => { 
    room?.disconnect(); 
  }, [room]);

  const startCall = async () => {
    setConnecting(true);
    setError(null);
    
    try {
      const { token, url } = await fetchLiveKitToken(roomName, mode);
      const lkRoom = new Room({
        adaptiveStream: true,
        dynacast: true
      });
      
      await lkRoom.connect(url, token);
      console.log('✅ Connected to LiveKit room:', lkRoom.name);

      // Publish video track (if not audio-only)
      if (mode !== 'audio') {
        try {
          const videoTrack = await createLocalVideoTrack({
            facingMode: 'user',
            resolution: {
              width: 1280,
              height: 720
            }
          });
          await lkRoom.localParticipant.publishTrack(videoTrack);
          
          if (localVideoRef.current) {
            const mediaStream = new MediaStream([videoTrack.mediaStreamTrack]);
            localVideoRef.current.srcObject = mediaStream;
            await localVideoRef.current.play().catch(() => {});
          }
          console.log('✅ Video track published');
        } catch (videoErr) {
          console.warn('⚠️ Video track failed, continuing with audio-only:', videoErr);
        }
      }
      
      // Publish audio track
      try {
        const audioTrack = await createLocalAudioTrack();
        await lkRoom.localParticipant.publishTrack(audioTrack);
        console.log('✅ Audio track published');
      } catch (audioErr) {
        console.error('❌ Audio track failed:', audioErr);
      }

      // Handle remote tracks
      lkRoom.on('trackSubscribed', (track, publication, participant) => {
        console.log('📥 Track subscribed:', track.kind, 'from', participant.identity);
        
        if (track.kind === 'video' && remoteVideoRef.current) {
          remoteVideoRef.current.srcObject = new MediaStream([track.mediaStreamTrack]);
          remoteVideoRef.current.play().catch(() => {});
        }
        
        if (track.kind === 'audio') {
          const audio = new Audio();
          audio.srcObject = new MediaStream([track.mediaStreamTrack]);
          audio.play().catch(() => {});
        }
      });

      // Handle participant events
      lkRoom.on('participantConnected', (participant) => {
        console.log('👤 Participant connected:', participant.identity);
        setRemoteParticipants(prev => [...prev, participant]);
      });

      lkRoom.on('participantDisconnected', (participant) => {
        console.log('👋 Participant disconnected:', participant.identity);
        setRemoteParticipants(prev => prev.filter(p => p.identity !== participant.identity));
      });

      lkRoom.on('disconnected', () => {
        console.log('📴 Disconnected from room');
        endCall();
      });

      setRoom(lkRoom);
    } catch (err) {
      console.error('❌ LiveKit error:', err);
      setError(err.message);
      alert('Failed to start call: ' + err.message);
    } finally {
      setConnecting(false);
    }
  };

  const endCall = () => {
    if (room) {
      room.disconnect();
      setRoom(null);
    }
    if (localVideoRef.current) localVideoRef.current.srcObject = null;
    if (remoteVideoRef.current) remoteVideoRef.current.srcObject = null;
    setRemoteParticipants([]);
    if (onClose) onClose();
  };

  const toggleMic = () => {
    if (room) {
      room.localParticipant.setMicrophoneEnabled(!micMuted);
      setMicMuted(!micMuted);
    }
  };

  const toggleVideo = () => {
    if (room && mode === 'video') {
      room.localParticipant.setCameraEnabled(!videoMuted);
      setVideoMuted(!videoMuted);
    }
  };

  return (
    <div style={{ 
      position: 'fixed',
      inset: 0,
      background: '#000',
      zIndex: 9999,
      display: 'flex',
      flexDirection: 'column',
      padding: 16
    }}>
      {/* Header */}
      <div style={{
        display: 'flex',
        justifyContent: 'space-between',
        alignItems: 'center',
        padding: 16,
        color: 'white',
        background: 'rgba(0,0,0,0.5)',
        borderRadius: 8,
        marginBottom: 16
      }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
          <div style={{
            width: 8,
            height: 8,
            borderRadius: '50%',
            background: room ? '#10b981' : '#ef4444',
            animation: room ? 'pulse 2s infinite' : 'none'
          }} />
          <span>{mode === 'video' ? '🎥 Video Call' : '🎤 Voice Call'}</span>
          {remoteParticipants.length > 0 && (
            <span style={{ fontSize: 14, opacity: 0.7 }}>
              • {remoteParticipants.length} participant(s)
            </span>
          )}
        </div>
        <button 
          onClick={endCall}
          style={{
            padding: '8px 16px',
            background: '#ef4444',
            color: 'white',
            border: 'none',
            borderRadius: 8,
            cursor: 'pointer',
            fontWeight: 500
          }}
        >
          End Call
        </button>
      </div>

      {/* Video Grid */}
      <div style={{ 
        flex: 1,
        display: 'grid',
        gridTemplateColumns: remoteParticipants.length > 0 ? '1fr 1fr' : '1fr',
        gap: 16,
        marginBottom: 16
      }}>
        {/* Local Video */}
        <div style={{ 
          position: 'relative',
          background: '#1a1a1a',
          borderRadius: 12,
          overflow: 'hidden',
          display: 'flex',
          flexDirection: 'column',
          justifyContent: 'center',
          alignItems: 'center'
        }}>
          <div style={{
            position: 'absolute',
            top: 12,
            left: 12,
            background: 'rgba(0,0,0,0.7)',
            color: 'white',
            padding: '4px 12px',
            borderRadius: 6,
            fontSize: 14,
            fontWeight: 500,
            zIndex: 10
          }}>
            You (Local)
          </div>
          
          {mode === 'video' ? (
            <video 
              ref={localVideoRef} 
              autoPlay 
              muted 
              playsInline 
              style={{ 
                width: '100%', 
                height: '100%',
                objectFit: 'cover'
              }} 
            />
          ) : (
            <div style={{
              display: 'flex',
              flexDirection: 'column',
              alignItems: 'center',
              gap: 16,
              color: 'white'
            }}>
              <div style={{
                width: 120,
                height: 120,
                borderRadius: '50%',
                background: 'linear-gradient(135deg, #ec4899, #f43f5e)',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                fontSize: 48
              }}>
                🎤
              </div>
              <p style={{ fontSize: 18, opacity: 0.8 }}>Audio Only</p>
            </div>
          )}
        </div>

        {/* Remote Video */}
        {(room || remoteParticipants.length > 0) && (
          <div style={{ 
            position: 'relative',
            background: '#1a1a1a',
            borderRadius: 12,
            overflow: 'hidden',
            display: 'flex',
            flexDirection: 'column',
            justifyContent: 'center',
            alignItems: 'center'
          }}>
            <div style={{
              position: 'absolute',
              top: 12,
              left: 12,
              background: 'rgba(0,0,0,0.7)',
              color: 'white',
              padding: '4px 12px',
              borderRadius: 6,
              fontSize: 14,
              fontWeight: 500,
              zIndex: 10
            }}>
              Remote
            </div>
            
            <video 
              ref={remoteVideoRef} 
              autoPlay 
              playsInline 
              style={{ 
                width: '100%', 
                height: '100%',
                objectFit: 'cover'
              }} 
            />
            
            {remoteParticipants.length === 0 && (
              <div style={{
                position: 'absolute',
                inset: 0,
                display: 'flex',
                flexDirection: 'column',
                alignItems: 'center',
                justifyContent: 'center',
                color: 'white',
                gap: 12
              }}>
                <div style={{
                  width: 100,
                  height: 100,
                  borderRadius: '50%',
                  border: '4px solid rgba(255,255,255,0.2)',
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'center',
                  fontSize: 40
                }}>
                  ⏳
                </div>
                <p style={{ fontSize: 16, opacity: 0.7 }}>Waiting for others to join...</p>
              </div>
            )}
          </div>
        )}
      </div>

      {/* Controls */}
      <div style={{ 
        display: 'flex',
        justifyContent: 'center',
        gap: 16,
        padding: 16,
        background: 'rgba(0,0,0,0.5)',
        borderRadius: 12
      }}>
        {!room ? (
          <button 
            onClick={startCall} 
            disabled={connecting}
            style={{
              padding: '12px 32px',
              background: connecting ? '#666' : 'linear-gradient(135deg, #ec4899, #f43f5e)',
              color: 'white',
              border: 'none',
              borderRadius: 12,
              cursor: connecting ? 'not-allowed' : 'pointer',
              fontSize: 16,
              fontWeight: 600,
              transition: 'all 0.2s'
            }}
          >
            {connecting ? 'Connecting...' : '📞 Start Call'}
          </button>
        ) : (
          <>
            <button
              onClick={toggleMic}
              style={{
                padding: 12,
                width: 56,
                height: 56,
                borderRadius: '50%',
                border: 'none',
                background: micMuted ? '#ef4444' : 'rgba(255,255,255,0.2)',
                color: 'white',
                cursor: 'pointer',
                fontSize: 24,
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                transition: 'all 0.2s'
              }}
              title={micMuted ? 'Unmute' : 'Mute'}
            >
              {micMuted ? '🔇' : '🎤'}
            </button>

            {mode === 'video' && (
              <button
                onClick={toggleVideo}
                style={{
                  padding: 12,
                  width: 56,
                  height: 56,
                  borderRadius: '50%',
                  border: 'none',
                  background: videoMuted ? '#ef4444' : 'rgba(255,255,255,0.2)',
                  color: 'white',
                  cursor: 'pointer',
                  fontSize: 24,
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'center',
                  transition: 'all 0.2s'
                }}
                title={videoMuted ? 'Turn On Camera' : 'Turn Off Camera'}
              >
                {videoMuted ? '📹' : '🎥'}
              </button>
            )}

            <button
              onClick={endCall}
              style={{
                padding: 12,
                width: 56,
                height: 56,
                borderRadius: '50%',
                border: 'none',
                background: '#ef4444',
                color: 'white',
                cursor: 'pointer',
                fontSize: 24,
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                transition: 'all 0.2s'
              }}
              title="End Call"
            >
              📞
            </button>
          </>
        )}
      </div>

      {/* Error Display */}
      {error && (
        <div style={{
          position: 'absolute',
          top: 80,
          left: '50%',
          transform: 'translateX(-50%)',
          background: '#ef4444',
          color: 'white',
          padding: '12px 24px',
          borderRadius: 8,
          fontWeight: 500,
          boxShadow: '0 4px 12px rgba(0,0,0,0.3)'
        }}>
          ⚠️ {error}
        </div>
      )}

      {/* Pulse animation */}
      <style>{`
        @keyframes pulse {
          0%, 100% { opacity: 1; }
          50% { opacity: 0.5; }
        }
      `}</style>
    </div>
  );
}
