import { useEffect, useState } from 'react';
import { Device } from '@twilio/voice-sdk';
import { Phone, PhoneOff } from 'lucide-react';
import { toast } from 'sonner';

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;

export default function VoiceCallButton({ calleeId, identity }) {
  const [device, setDevice] = useState(null);
  const [connection, setConnection] = useState(null);
  const [isConnecting, setIsConnecting] = useState(false);
  const [isConnected, setIsConnected] = useState(false);

  useEffect(() => {
    initDevice();
    return () => {
      if (device) {
        device.destroy();
      }
    };
  }, [identity]);

  async function initDevice() {
    try {
      // Get token from backend
      const token = localStorage.getItem('token');
      const response = await fetch(`${BACKEND_URL}/api/twilio/voice/token`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`
        },
        credentials: 'include',
        body: JSON.stringify({ identity: identity || 'user' })
      });

      if (!response.ok) {
        throw new Error('Failed to get voice token');
      }

      const data = await response.json();
      
      // Initialize Twilio Device
      const twilioDevice = new Device(data.token, {
        codecPreferences: ['opus', 'pcmu'],
        enableRingingState: true
      });

      twilioDevice.on('registered', () => {
        console.log('✅ Twilio Device ready');
      });

      twilioDevice.on('error', (error) => {
        console.error('❌ Twilio Device error:', error);
        toast.error('Voice call error: ' + error.message);
      });

      twilioDevice.on('incoming', (incomingConnection) => {
        console.log('📞 Incoming call');
        toast.info('Incoming call...');
        setConnection(incomingConnection);
        setupConnectionListeners(incomingConnection);
      });

      await twilioDevice.register();
      setDevice(twilioDevice);
    } catch (error) {
      console.error('Failed to initialize device:', error);
      toast.error('Failed to initialize voice: ' + error.message);
    }
  }

  function setupConnectionListeners(conn) {
    conn.on('accept', () => {
      console.log('✅ Call connected');
      setIsConnected(true);
      setIsConnecting(false);
      toast.success('Call connected!');
    });

    conn.on('disconnect', () => {
      console.log('📴 Call ended');
      setIsConnected(false);
      setIsConnecting(false);
      setConnection(null);
      toast.info('Call ended');
    });

    conn.on('reject', () => {
      console.log('❌ Call rejected');
      setIsConnecting(false);
      setConnection(null);
      toast.error('Call rejected');
    });

    conn.on('error', (error) => {
      console.error('❌ Call error:', error);
      setIsConnecting(false);
      setConnection(null);
      toast.error('Call error: ' + error.message);
    });
  }

  async function makeCall() {
    if (!device) {
      toast.error('Voice not initialized');
      return;
    }

    try {
      setIsConnecting(true);
      toast.info('Connecting call...');
      
      // Connect to the callee
      const conn = await device.connect({
        params: {
          To: calleeId || 'support'
        }
      });

      setConnection(conn);
      setupConnectionListeners(conn);
    } catch (error) {
      console.error('Failed to make call:', error);
      toast.error('Failed to connect call');
      setIsConnecting(false);
    }
  }

  function hangUp() {
    if (connection) {
      connection.disconnect();
    }
    setConnection(null);
    setIsConnected(false);
    setIsConnecting(false);
  }

  return (
    <div className="inline-flex items-center gap-2">
      {!isConnected && !isConnecting && (
        <button
          onClick={makeCall}
          disabled={!device}
          className="flex items-center gap-2 px-4 py-2 bg-green-500 hover:bg-green-600 text-white rounded-lg transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
        >
          <Phone className="w-4 h-4" />
          <span>Voice Call</span>
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
        <button
          onClick={hangUp}
          className="flex items-center gap-2 px-4 py-2 bg-red-500 hover:bg-red-600 text-white rounded-lg transition-colors"
        >
          <PhoneOff className="w-4 h-4" />
          <span>End Call</span>
        </button>
      )}
    </div>
  );
}
