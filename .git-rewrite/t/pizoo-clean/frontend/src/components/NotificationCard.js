import React, { useState } from 'react';
import { ChevronDown, ChevronUp, X } from 'lucide-react';
import { Button } from './ui/button';

const NotificationCard = ({ 
  title, 
  message, 
  icon, 
  actionLabel, 
  onAction, 
  onDismiss,
  defaultExpanded = false 
}) => {
  const [isExpanded, setIsExpanded] = useState(defaultExpanded);
  const [isDismissed, setIsDismissed] = useState(false);

  if (isDismissed) return null;

  const handleDismiss = () => {
    setIsDismissed(true);
    if (onDismiss) onDismiss();
  };

  return (
    <div className="bg-pink-50 border-l-4 border-pink-500 rounded-lg mb-3 overflow-hidden shadow-sm">
      {/* Header - Always visible */}
      <div
        className="flex items-center justify-between p-4 cursor-pointer hover:bg-pink-100 transition"
        onClick={() => setIsExpanded(!isExpanded)}
      >
        <div className="flex items-center gap-3 flex-1">
          {icon && <span className="text-2xl">{icon}</span>}
          <div className="flex-1">
            <h4 className="font-bold text-gray-800 text-sm">{title}</h4>
            {!isExpanded && (
              <p className="text-xs text-gray-600 truncate">{message}</p>
            )}
          </div>
        </div>
        <div className="flex items-center gap-2">
          {isExpanded ? (
            <ChevronUp className="w-5 h-5 text-gray-500" />
          ) : (
            <ChevronDown className="w-5 h-5 text-gray-500" />
          )}
          <button
            onClick={(e) => {
              e.stopPropagation();
              handleDismiss();
            }}
            className="p-1 hover:bg-pink-200 rounded-full transition"
          >
            <X className="w-4 h-4 text-gray-500" />
          </button>
        </div>
      </div>

      {/* Expanded Content */}
      {isExpanded && (
        <div className="px-4 pb-4 pt-2 border-t border-pink-200">
          <p className="text-gray-700 text-sm mb-3 leading-relaxed">{message}</p>
          {actionLabel && onAction && (
            <Button
              onClick={onAction}
              className="w-full bg-gradient-to-r from-pink-500 to-red-500 hover:from-pink-600 hover:to-red-600 text-white text-sm py-2"
            >
              {actionLabel}
            </Button>
          )}
        </div>
      )}
    </div>
  );
};

export default NotificationCard;
