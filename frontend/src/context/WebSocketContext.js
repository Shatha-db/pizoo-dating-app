import React, { createContext, useContext, useEffect, useState, useRef } from 'react';
import { useAuth } from './AuthContext';

const WebSocketContext = createContext(null);

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
// Fix WebSocket URL to use correct backend URL without replacing the full domain
const WS_URL = BACKEND_URL ? BACKEND_URL.replace('https://', 'wss://').replace('http://', 'ws://') : 'ws://localhost:8001';

export const WebSocketProvider = ({ children }) => {
  const { user } = useAuth();
  const [isConnected, setIsConnected] = useState(false);
  const [messages, setMessages] = useState([]);
  const [onlineUsers, setOnlineUsers] = useState(new Set());
  const [typingUsers, setTypingUsers] = useState(new Set());
  const ws = useRef(null);
  const reconnectTimeout = useRef(null);

  useEffect(() => {
    if (user?.id) {
      connectWebSocket();
    }

    return () => {
      if (ws.current) {
        ws.current.close();
      }
      if (reconnectTimeout.current) {
        clearTimeout(reconnectTimeout.current);
      }
    };
  }, [user?.id]);

  const connectWebSocket = () => {
    if (!user?.id) return;

    try {
      // Only connect if we have a valid user
      const wsEndpoint = `${WS_URL}/ws/${user.id}`;
      console.log('Attempting WebSocket connection to:', wsEndpoint);
      ws.current = new WebSocket(wsEndpoint);

      ws.current.onopen = () => {
        console.log('✅ WebSocket connected');
        setIsConnected(true);
      };

      ws.current.onmessage = (event) => {
        const data = JSON.parse(event.data);
        handleMessage(data);
      };

      ws.current.onerror = (error) => {
        console.error('❌ WebSocket error:', error);
      };

      ws.current.onclose = () => {
        console.log('🔌 WebSocket disconnected');
        setIsConnected(false);
        
        // Auto-reconnect after 3 seconds
        reconnectTimeout.current = setTimeout(() => {
          console.log('🔄 Reconnecting...');
          connectWebSocket();
        }, 3000);
      };
    } catch (error) {
      console.error('Failed to connect WebSocket:', error);
    }
  };

  const handleMessage = (data) => {
    switch (data.type) {
      case 'new_message':
        setMessages(prev => [...prev, data]);
        break;
      
      case 'user_status':
        if (data.online) {
          setOnlineUsers(prev => new Set([...prev, data.user_id]));
        } else {
          setOnlineUsers(prev => {
            const newSet = new Set(prev);
            newSet.delete(data.user_id);
            return newSet;
          });
        }
        break;
      
      case 'typing':
        if (data.is_typing) {
          setTypingUsers(prev => new Set([...prev, data.user_id]));
        } else {
          setTypingUsers(prev => {
            const newSet = new Set(prev);
            newSet.delete(data.user_id);
            return newSet;
          });
        }
        break;
      
      case 'message_sent':
        // Message confirmation
        break;
      
      case 'read_receipt':
        // Update message status
        setMessages(prev => prev.map(msg => 
          msg.match_id === data.match_id && msg.sender_id === user.id
            ? { ...msg, status: 'read' }
            : msg
        ));
        break;
      
      default:
        break;
    }
  };

  const sendMessage = (matchId, receiverId, message) => {
    if (ws.current && ws.current.readyState === WebSocket.OPEN) {
      ws.current.send(JSON.stringify({
        type: 'message',
        match_id: matchId,
        receiver_id: receiverId,
        message: message
      }));
      return true;
    }
    return false;
  };

  const sendTypingIndicator = (receiverId, isTyping) => {
    if (ws.current && ws.current.readyState === WebSocket.OPEN) {
      ws.current.send(JSON.stringify({
        type: 'typing',
        receiver_id: receiverId,
        is_typing: isTyping
      }));
    }
  };

  const sendReadReceipt = (matchId, senderId) => {
    if (ws.current && ws.current.readyState === WebSocket.OPEN) {
      ws.current.send(JSON.stringify({
        type: 'read_receipt',
        match_id: matchId,
        sender_id: senderId
      }));
    }
  };

  const isUserOnline = (userId) => {
    return onlineUsers.has(userId);
  };

  const isUserTyping = (userId) => {
    return typingUsers.has(userId);
  };

  const value = {
    isConnected,
    messages,
    onlineUsers,
    sendMessage,
    sendTypingIndicator,
    sendReadReceipt,
    isUserOnline,
    isUserTyping
  };

  return (
    <WebSocketContext.Provider value={value}>
      {children}
    </WebSocketContext.Provider>
  );
};

export const useWebSocket = () => {
  const context = useContext(WebSocketContext);
  if (!context) {
    throw new Error('useWebSocket must be used within WebSocketProvider');
  }
  return context;
};
