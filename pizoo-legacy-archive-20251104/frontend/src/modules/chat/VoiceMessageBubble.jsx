import React, { useState, useRef, useEffect } from 'react';
import { Play, Pause } from 'lucide-react';
import { useTranslation } from 'react-i18next';

/**
 * Voice Message Bubble Component
 * Displays and plays voice messages
 */
export default function VoiceMessageBubble({ audioUrl, duration, isSender, timestamp }) {
  const { t } = useTranslation(['chat']);
  const [isPlaying, setIsPlaying] = useState(false);
  const [currentTime, setCurrentTime] = useState(0);
  const audioRef = useRef(null);

  useEffect(() => {
    const audio = audioRef.current;
    if (!audio) return;

    const updateTime = () => setCurrentTime(audio.currentTime);
    const handleEnded = () => {
      setIsPlaying(false);
      setCurrentTime(0);
    };

    audio.addEventListener('timeupdate', updateTime);
    audio.addEventListener('ended', handleEnded);

    return () => {
      audio.removeEventListener('timeupdate', updateTime);
      audio.removeEventListener('ended', handleEnded);
    };
  }, []);

  const togglePlay = () => {
    const audio = audioRef.current;
    if (!audio) return;

    if (isPlaying) {
      audio.pause();
    } else {
      audio.play();
    }
    setIsPlaying(!isPlaying);
  };

  const formatTime = (seconds) => {
    const mins = Math.floor(seconds / 60);
    const secs = Math.floor(seconds % 60);
    return `${mins}:${secs.toString().padStart(2, '0')}`;
  };

  const progress = duration > 0 ? (currentTime / duration) * 100 : 0;

  return (
    <div className={`flex items-center gap-3 p-3 rounded-2xl ${
      isSender 
        ? 'bg-gradient-to-r from-pink-500 to-rose-500 text-white' 
        : 'bg-gray-100 dark:bg-gray-700 text-gray-900 dark:text-white'
    }`}>
      <audio ref={audioRef} src={audioUrl} preload="metadata" />
      
      {/* Play/Pause Button */}
      <button
        onClick={togglePlay}
        className={`w-10 h-10 rounded-full flex items-center justify-center transition-all ${
          isSender
            ? 'bg-white/20 hover:bg-white/30'
            : 'bg-rose-100 dark:bg-rose-900/30 hover:bg-rose-200 dark:hover:bg-rose-900/50'
        }`}
      >
        {isPlaying ? (
          <Pause className={`w-5 h-5 ${isSender ? 'text-white' : 'text-rose-600 dark:text-rose-400'}`} />
        ) : (
          <Play className={`w-5 h-5 ${isSender ? 'text-white' : 'text-rose-600 dark:text-rose-400'}`} />
        )}
      </button>

      {/* Waveform / Progress Bar */}
      <div className="flex-1 min-w-0">
        <div className="relative h-8 flex items-center">
          {/* Background bar */}
          <div className={`absolute inset-0 rounded-full ${
            isSender ? 'bg-white/20' : 'bg-gray-300 dark:bg-gray-600'
          }`}>
            {/* Progress bar */}
            <div
              className={`h-full rounded-full transition-all ${
                isSender ? 'bg-white' : 'bg-rose-500'
              }`}
              style={{ width: `${progress}%` }}
            />
          </div>
          
          {/* Time display */}
          <div className={`relative z-10 px-2 text-xs font-medium ${
            isSender ? 'text-white' : 'text-gray-600 dark:text-gray-300'
          }`}>
            {formatTime(currentTime || 0)} / {formatTime(duration)}
          </div>
        </div>
      </div>
    </div>
  );
}
