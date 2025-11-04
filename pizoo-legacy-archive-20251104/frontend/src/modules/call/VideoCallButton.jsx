import { useState, useEffect, useRef } from 'react';
import Video from 'twilio-video';
import { Video as VideoIcon, VideoOff, Mic, MicOff } from 'lucide-react';
import { toast } from 'sonner';

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;

export default function VideoCallButton({ roomName, identity }) {
  const [room, setRoom] = useState(null);
  const [isConnecting, setIsConnecting] = useState(false);
  const [isConnected, setIsConnected] = useState(false);
  const [isMuted, setIsMuted] = useState(false);
  const [isVideoOff, setIsVideoOff] = useState(false);
  
  const localVideoRef = useRef(null);
  const remoteVideoRef = useRef(null);

  useEffect(() => {
    return () => {
      if (room) {
        room.disconnect();
      }
    };
  }, [room]);

  async function joinRoom() {
    try {
      setIsConnecting(true);
      toast.info('Connecting to video call...');

      // Get token from backend
      const token = localStorage.getItem('token');
      const response = await fetch(`${BACKEND_URL}/api/twilio/video/token`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`
        },
        credentials: 'include',
        body: JSON.stringify({
          identity: identity || 'user',
          room: roomName || 'default-room'
        })
      });

      if (!response.ok) {
        throw new Error('Failed to get video token');
      }

      const data = await response.json();

      // Connect to Twilio Video room
      const twilioRoom = await Video.connect(data.token, {
        name: data.room,
        audio: true,
        video: { width: 640, height: 480 }
      });

      setRoom(twilioRoom);
      setIsConnected(true);
      setIsConnecting(false);
      toast.success('Connected to video call!');

      // Attach local video
      twilioRoom.localParticipant.tracks.forEach((publication) => {
        if (publication.track && localVideoRef.current) {
          localVideoRef.current.appendChild(publication.track.attach());
        }
      });

      // Handle participants already in room
      twilioRoom.participants.forEach((participant) => {
        attachParticipantTracks(participant);
      });

      // Handle new participants joining
      twilioRoom.on('participantConnected', (participant) => {
        console.log(`Participant ${participant.identity} connected`);
        attachParticipantTracks(participant);
        toast.info(`${participant.identity} joined`);
      });

      // Handle participants leaving
      twilioRoom.on('participantDisconnected', (participant) => {
        console.log(`Participant ${participant.identity} disconnected`);
        toast.info(`${participant.identity} left`);
      });

      // Handle room disconnection
      twilioRoom.on('disconnected', () => {
        console.log('Disconnected from room');
        setRoom(null);
        setIsConnected(false);
        toast.info('Video call ended');
      });

    } catch (error) {
      console.error('Failed to join room:', error);
      toast.error('Failed to join video call: ' + error.message);
      setIsConnecting(false);
    }
  }

  function attachParticipantTracks(participant) {
    participant.tracks.forEach((publication) => {
      if (publication.isSubscribed) {
        attachTrack(publication.track);
      }
    });

    participant.on('trackSubscribed', (track) => {
      attachTrack(track);
    });
  }

  function attachTrack(track) {
    if (track && remoteVideoRef.current) {
      remoteVideoRef.current.appendChild(track.attach());
    }
  }

  function leaveRoom() {
    if (room) {
      room.disconnect();
      setRoom(null);
      setIsConnected(false);
      
      // Clear video elements
      if (localVideoRef.current) {
        localVideoRef.current.innerHTML = '';
      }
      if (remoteVideoRef.current) {
        remoteVideoRef.current.innerHTML = '';
      }
    }
  }

  function toggleMute() {
    if (room) {
      room.localParticipant.audioTracks.forEach((publication) => {
        if (isMuted) {
          publication.track.enable();
        } else {
          publication.track.disable();
        }
      });
      setIsMuted(!isMuted);
    }
  }

  function toggleVideo() {
    if (room) {
      room.localParticipant.videoTracks.forEach((publication) => {
        if (isVideoOff) {
          publication.track.enable();
        } else {
          publication.track.disable();
        }
      });
      setIsVideoOff(!isVideoOff);
    }
  }

  return (
    <div className="inline-flex flex-col gap-4">
      {/* Action Buttons */}
      <div className="flex items-center gap-2">
        {!isConnected && !isConnecting && (
          <button
            onClick={joinRoom}
            className="flex items-center gap-2 px-4 py-2 bg-blue-500 hover:bg-blue-600 text-white rounded-lg transition-colors"
          >
            <VideoIcon className="w-4 h-4" />
            <span>Video Call</span>
          </button>
        )}

        {isConnecting && (
          <button
            disabled
            className="flex items-center gap-2 px-4 py-2 bg-yellow-500 text-white rounded-lg"
          >
            <div className="animate-spin rounded-full h-4 w-4 border-2 border-white border-t-transparent"></div>
            <span>Connecting...</span>
          </button>
        )}

        {isConnected && (
          <>
            <button
              onClick={toggleMute}
              className={`p-2 rounded-lg transition-colors ${
                isMuted ? 'bg-red-500 hover:bg-red-600' : 'bg-gray-500 hover:bg-gray-600'
              } text-white`}
              title={isMuted ? 'Unmute' : 'Mute'}
            >
              {isMuted ? <MicOff className="w-4 h-4" /> : <Mic className="w-4 h-4" />}
            </button>

            <button
              onClick={toggleVideo}
              className={`p-2 rounded-lg transition-colors ${
                isVideoOff ? 'bg-red-500 hover:bg-red-600' : 'bg-gray-500 hover:bg-gray-600'
              } text-white`}
              title={isVideoOff ? 'Turn On Video' : 'Turn Off Video'}
            >
              {isVideoOff ? <VideoOff className="w-4 h-4" /> : <VideoIcon className="w-4 h-4" />}
            </button>

            <button
              onClick={leaveRoom}
              className="flex items-center gap-2 px-4 py-2 bg-red-500 hover:bg-red-600 text-white rounded-lg transition-colors"
            >
              <span>End Call</span>
            </button>
          </>
        )}
      </div>

      {/* Video Display */}
      {isConnected && (
        <div className="flex gap-4">
          <div className="relative">
            <div
              ref={localVideoRef}
              className="w-48 h-36 bg-gray-800 rounded-lg overflow-hidden"
            ></div>
            <div className="absolute bottom-2 left-2 text-white text-xs bg-black/50 px-2 py-1 rounded">
              You
            </div>
          </div>
          
          <div className="relative">
            <div
              ref={remoteVideoRef}
              className="w-96 h-72 bg-gray-800 rounded-lg overflow-hidden"
            ></div>
            <div className="absolute bottom-2 left-2 text-white text-xs bg-black/50 px-2 py-1 rounded">
              Remote
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
