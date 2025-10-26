import React, { useState } from 'react';
import { X, MapPin, Globe } from 'lucide-react';
import { Button } from './ui/button';

// Safe number guard to prevent NaN
const safeNumber = (v, fallback = 0) => {
  const n = Number(v);
  return Number.isFinite(n) ? n : fallback;
};

const GeoPermissionModal = ({ onAllow, onDeny, onManual, onClose }) => {
  const [isOpen, setIsOpen] = useState(true);

  const handleAllow = () => {
    setIsOpen(false);
    onAllow();
  };

  const handleDeny = () => {
    setIsOpen(false);
    onDeny();
  };

  const handleManual = () => {
    setIsOpen(false);
    onManual();
  };

  const handleClose = () => {
    setIsOpen(false);
    onClose();
  };

  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 z-50 flex items-end justify-center bg-black/50 backdrop-blur-sm">
      {/* Bottom Sheet */}
      <div className="w-full max-w-md bg-white dark:bg-gray-800 rounded-t-3xl shadow-2xl animate-slide-up">
        {/* Header */}
        <div className="flex justify-between items-center p-4 border-b border-gray-200 dark:border-gray-700">
          <h3 className="text-lg font-semibold text-gray-900 dark:text-white">
            📍 نحتاج إلى موقعك
          </h3>
          <button
            onClick={handleClose}
            className="text-gray-400 hover:text-gray-600 dark:hover:text-gray-300"
          >
            <X className="w-5 h-5" />
          </button>
        </div>

        {/* Content */}
        <div className="p-6 space-y-4">
          {/* Icon */}
          <div className="flex justify-center mb-4">
            <div className="w-20 h-20 bg-pink-100 dark:bg-pink-900/30 rounded-full flex items-center justify-center">
              <MapPin className="w-10 h-10 text-pink-500" />
            </div>
          </div>

          {/* Description */}
          <div className="text-center space-y-2">
            <p className="text-gray-700 dark:text-gray-300">
              للعثور على أشخاص قريبين منك وتحسين تجربة الاكتشاف
            </p>
            <p className="text-sm text-gray-500 dark:text-gray-400">
              سنستخدم موقعك لعرض المسافة التقريبية فقط
            </p>
          </div>

          {/* Privacy Note */}
          <div className="bg-blue-50 dark:bg-blue-900/20 border border-blue-200 dark:border-blue-800 rounded-lg p-3">
            <p className="text-xs text-blue-700 dark:text-blue-300">
              🔒 خصوصيتك مهمة: لن نشارك موقعك الدقيق مع الآخرين
            </p>
          </div>

          {/* Buttons */}
          <div className="space-y-3 mt-6">
            {/* Allow Button */}
            <Button
              onClick={handleAllow}
              className="w-full bg-pink-500 hover:bg-pink-600 text-white py-6 text-lg font-semibold rounded-xl shadow-lg"
            >
              <MapPin className="w-5 h-5 mr-2" />
              السماح الآن
            </Button>

            {/* Manual Entry Button */}
            <Button
              onClick={handleManual}
              variant="outline"
              className="w-full border-2 border-gray-300 dark:border-gray-600 py-6 text-lg font-semibold rounded-xl"
            >
              <Globe className="w-5 h-5 mr-2" />
              إدخال المدينة يدوياً
            </Button>

            {/* Maybe Later Button */}
            <Button
              onClick={handleDeny}
              variant="ghost"
              className="w-full text-gray-600 dark:text-gray-400 py-4 text-base"
            >
              ربما لاحقاً
            </Button>
          </div>
        </div>
      </div>

      <style jsx>{`
        @keyframes slide-up {
          from {
            transform: translateY(100%);
          }
          to {
            transform: translateY(0);
          }
        }

        .animate-slide-up {
          animation: slide-up 0.3s ease-out;
        }
      `}</style>
    </div>
  );
};

export default GeoPermissionModal;
