import React, { useState } from 'react';
import { X } from 'lucide-react';

/**
 * Simple Emoji Picker Component
 * Mobile-friendly emoji selection for chat
 */
const EmojiPicker = ({ onSelect, onClose }) => {
  const [activeCategory, setActiveCategory] = useState('smileys');

  const emojiCategories = {
    smileys: {
      name: 'وجوه ومشاعر',
      icon: '😀',
      emojis: [
        '😀', '😃', '😄', '😁', '😆', '😅', '🤣', '😂',
        '🙂', '🙃', '😉', '😊', '😇', '🥰', '😍', '🤩',
        '😘', '😗', '😚', '😙', '😋', '😛', '😜', '🤪',
        '😝', '🤗', '🤭', '🤫', '🤔', '🤐', '🤨', '😐',
        '😑', '😶', '😏', '😒', '🙄', '😬', '🤥', '😌',
        '😔', '😪', '🤤', '😴', '😷', '🤒', '🤕', '🤢',
        '🤮', '🤧', '🥵', '🥶', '😵', '🤯', '🤠', '🥳'
      ]
    },
    hearts: {
      name: 'قلوب',
      icon: '❤️',
      emojis: [
        '❤️', '🧡', '💛', '💚', '💙', '💜', '🖤', '🤍',
        '🤎', '💔', '❣️', '💕', '💞', '💓', '💗', '💖',
        '💘', '💝', '💟', '💌', '💋', '😻', '😽', '😼'
      ]
    },
    gestures: {
      name: 'إيماءات',
      icon: '👋',
      emojis: [
        '👋', '🤚', '🖐️', '✋', '🖖', '👌', '🤌', '🤏',
        '✌️', '🤞', '🤟', '🤘', '🤙', '👈', '👉', '👆',
        '🖕', '👇', '☝️', '👍', '👎', '✊', '👊', '🤛',
        '🤜', '👏', '🙌', '👐', '🤲', '🤝', '🙏', '💪'
      ]
    },
    objects: {
      name: 'أشياء',
      icon: '🎁',
      emojis: [
        '🎁', '🎈', '🎉', '🎊', '🎂', '🎀', '💐', '🌹',
        '🌺', '🌸', '💮', '🏵️', '🌻', '🌼', '🌷', '⭐',
        '✨', '💫', '☀️', '🌙', '⭐', '🌟', '💥', '🔥'
      ]
    }
  };

  return (
    <div className="fixed inset-x-0 bottom-0 z-50 bg-white rounded-t-3xl shadow-2xl max-h-[60vh] flex flex-col animate-in slide-in-from-bottom duration-300" dir="rtl">
      {/* Header */}
      <div className="flex items-center justify-between p-4 border-b">
        <h3 className="text-lg font-bold text-gray-800">اختر إيموجي</h3>
        <button
          onClick={onClose}
          className="p-2 hover:bg-gray-100 rounded-full transition-colors"
        >
          <X className="w-5 h-5 text-gray-600" />
        </button>
      </div>

      {/* Category Tabs */}
      <div className="flex gap-2 p-3 border-b overflow-x-auto scrollbar-hide">
        {Object.entries(emojiCategories).map(([key, category]) => (
          <button
            key={key}
            onClick={() => setActiveCategory(key)}
            className={`flex-shrink-0 px-4 py-2 rounded-full text-2xl transition-all ${
              activeCategory === key
                ? 'bg-pink-500 shadow-md scale-110'
                : 'bg-gray-100 hover:bg-gray-200'
            }`}
          >
            {category.icon}
          </button>
        ))}
      </div>

      {/* Emoji Grid */}
      <div className="flex-1 overflow-y-auto p-4">
        <div className="grid grid-cols-8 gap-2">
          {emojiCategories[activeCategory].emojis.map((emoji, index) => (
            <button
              key={index}
              onClick={() => {
                onSelect(emoji);
                onClose();
              }}
              className="text-2xl p-2 hover:bg-gray-100 rounded-lg transition-all hover:scale-125 active:scale-95"
            >
              {emoji}
            </button>
          ))}
        </div>
      </div>
    </div>
  );
};

export default EmojiPicker;
