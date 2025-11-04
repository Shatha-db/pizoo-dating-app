import React, { useState, useRef, useEffect } from 'react';
import { Mic, X, Send, Trash2 } from 'lucide-react';
import { useTranslation } from 'react-i18next';

/**
 * Voice Message Recorder Component
 * Records audio messages for chat
 */
export default function VoiceRecorder({ onSend, onCancel }) {
  const { t } = useTranslation(['chat']);
  const [isRecording, setIsRecording] = useState(false);
  const [duration, setDuration] = useState(0);
  const [audioBlob, setAudioBlob] = useState(null);
  const mediaRecorderRef = useRef(null);
  const audioChunksRef = useRef([]);
  const timerRef = useRef(null);
  const streamRef = useRef(null);

  useEffect(() => {
    startRecording();
    return () => {
      cleanup();
    };
  }, []);

  const startRecording = async () => {
    try {
      const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
      streamRef.current = stream;
      
      const mediaRecorder = new MediaRecorder(stream);
      mediaRecorderRef.current = mediaRecorder;
      audioChunksRef.current = [];

      mediaRecorder.ondataavailable = (event) => {
        if (event.data.size > 0) {
          audioChunksRef.current.push(event.data);
        }
      };

      mediaRecorder.onstop = () => {
        const blob = new Blob(audioChunksRef.current, { type: 'audio/webm' });
        setAudioBlob(blob);
      };

      mediaRecorder.start();
      setIsRecording(true);

      // Start timer
      timerRef.current = setInterval(() => {
        setDuration(d => {
          if (d >= 120) { // Max 2 minutes
            stopRecording();
            return 120;
          }
          return d + 1;
        });
      }, 1000);
    } catch (error) {
      console.error('Error accessing microphone:', error);
      onCancel();
    }
  };

  const stopRecording = () => {
    if (mediaRecorderRef.current && isRecording) {
      mediaRecorderRef.current.stop();
      setIsRecording(false);
      if (timerRef.current) {
        clearInterval(timerRef.current);
      }
    }
  };

  const cleanup = () => {
    if (timerRef.current) {
      clearInterval(timerRef.current);
    }
    if (streamRef.current) {
      streamRef.current.getTracks().forEach(track => track.stop());
    }
  };

  const handleSend = () => {
    if (audioBlob) {
      onSend(audioBlob, duration);
    }
    cleanup();
  };

  const handleCancel = () => {
    cleanup();
    onCancel();
  };

  const formatTime = (seconds) => {
    const mins = Math.floor(seconds / 60);
    const secs = seconds % 60;
    return `${mins}:${secs.toString().padStart(2, '0')}`;
  };

  return (
    <div className="fixed inset-0 z-50 bg-black/60 flex items-center justify-center p-4">
      <div className="bg-white dark:bg-gray-800 rounded-2xl p-6 w-full max-w-md">
        <div className="text-center mb-6">
          <div className="inline-flex items-center justify-center w-20 h-20 bg-rose-100 dark:bg-rose-900/30 rounded-full mb-4">
            {isRecording ? (
              <div className="relative">
                <Mic className="w-10 h-10 text-rose-600 dark:text-rose-400" />
                <div className="absolute inset-0 bg-rose-500 rounded-full animate-ping opacity-75" />
              </div>
            ) : (
              <Mic className="w-10 h-10 text-rose-600 dark:text-rose-400" />
            )}
          </div>
          <h3 className="text-xl font-bold mb-2 dark:text-white">
            {isRecording ? t('recording_voice', { ns: 'chat' }) : t('voice_recorded', { ns: 'chat' })}
          </h3>
          <p className="text-3xl font-mono text-gray-700 dark:text-gray-300">
            {formatTime(duration)}
          </p>
          {duration >= 120 && (
            <p className="text-sm text-rose-600 dark:text-rose-400 mt-2">
              {t('max_duration_reached', { ns: 'chat' })}
            </p>
          )}
        </div>

        {/* Audio Preview */}
        {audioBlob && !isRecording && (
          <div className="mb-6 p-4 bg-gray-50 dark:bg-gray-700 rounded-xl">
            <audio 
              controls 
              src={URL.createObjectURL(audioBlob)}
              className="w-full"
            />
          </div>
        )}

        {/* Actions */}
        <div className="flex gap-3">
          <button
            onClick={handleCancel}
            className="flex-1 h-12 rounded-xl bg-gray-200 dark:bg-gray-700 text-gray-700 dark:text-gray-300 font-medium hover:bg-gray-300 dark:hover:bg-gray-600 transition-colors flex items-center justify-center gap-2"
          >
            {isRecording ? <X className="w-5 h-5" /> : <Trash2 className="w-5 h-5" />}
            {t('cancel', { ns: 'common' })}
          </button>
          
          {isRecording ? (
            <button
              onClick={stopRecording}
              className="flex-1 h-12 rounded-xl bg-rose-600 hover:bg-rose-700 text-white font-semibold transition-colors"
            >
              {t('stop', { ns: 'chat' })}
            </button>
          ) : (
            <button
              onClick={handleSend}
              disabled={!audioBlob}
              className="flex-1 h-12 rounded-xl bg-gradient-to-r from-pink-500 to-rose-500 hover:from-pink-600 hover:to-rose-600 text-white font-semibold transition-all disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center gap-2"
            >
              <Send className="w-5 h-5" />
              {t('send', { ns: 'common' })}
            </button>
          )}
        </div>
      </div>
    </div>
  );
}
