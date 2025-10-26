import React from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { useTranslation } from 'react-i18next';
import { X } from 'lucide-react';

export default function UpsellModal({ open, onClose, onChoose, reason = 'daily_limit' }) {
  const { t } = useTranslation(['premium']);

  const messages = {
    daily_limit: {
      title: t('premium:upsell.daily_limit_title'),
      subtitle: t('premium:upsell.daily_limit_subtitle')
    },
    likes_locked: {
      title: t('premium:upsell.unlock_likes_title'),
      subtitle: t('premium:upsell.unlock_likes_subtitle')
    },
    super_like: {
      title: t('premium:upsell.super_like_title'),
      subtitle: t('premium:upsell.super_like_subtitle')
    }
  };

  const message = messages[reason] || messages.daily_limit;

  return (
    <AnimatePresence>
      {open && (
        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          exit={{ opacity: 0 }}
          className="fixed inset-0 z-50 bg-black/60 backdrop-blur-sm flex items-end sm:items-center justify-center"
          onClick={onClose}
        >
          <motion.div
            initial={{ y: 100, opacity: 0 }}
            animate={{ y: 0, opacity: 1 }}
            exit={{ y: 100, opacity: 0 }}
            transition={{ type: 'spring', damping: 25 }}
            className="bg-white rounded-t-3xl sm:rounded-3xl w-full max-w-md p-6 shadow-2xl"
            onClick={(e) => e.stopPropagation()}
          >
            {/* Header */}
            <div className="flex justify-between items-center mb-4">
              <div className="flex items-center gap-2">
                <span className="text-2xl">🔥</span>
                <h3 className="font-bold text-xl text-gray-900">{message.title}</h3>
              </div>
              <button 
                onClick={onClose}
                className="w-8 h-8 rounded-full bg-gray-100 flex items-center justify-center hover:bg-gray-200 transition-colors"
              >
                <X size={18} className="text-gray-600" />
              </button>
            </div>

            {/* Subtitle */}
            <p className="text-sm text-gray-600 mb-6 leading-relaxed">
              {message.subtitle}
            </p>

            {/* Plan Buttons */}
            <div className="space-y-3">
              <motion.button
                whileTap={{ scale: 0.98 }}
                onClick={() => onChoose?.('gold')}
                className="w-full h-14 rounded-full text-white font-semibold bg-gradient-to-r from-[#F59E0B] to-[#EA580C] shadow-lg hover:brightness-110 transition-all flex items-center justify-center gap-2"
              >
                <span className="text-lg">👑</span>
                <span>Gold - {t('premium:pricing.popular')}</span>
              </motion.button>

              <motion.button
                whileTap={{ scale: 0.98 }}
                onClick={() => onChoose?.('platinum')}
                className="w-full h-14 rounded-full text-white font-semibold bg-gradient-to-r from-[#CBD5E1] to-[#64748B] shadow-lg hover:brightness-110 transition-all flex items-center justify-center gap-2"
              >
                <span className="text-lg">💎</span>
                <span>Platinum</span>
              </motion.button>

              <motion.button
                whileTap={{ scale: 0.98 }}
                onClick={() => onChoose?.('plus')}
                className="w-full h-14 rounded-full text-white font-semibold bg-gradient-to-r from-[#FF4C61] to-[#F97316] shadow-lg hover:brightness-110 transition-all flex items-center justify-center gap-2"
              >
                <span className="text-lg">⚡</span>
                <span>Plus</span>
              </motion.button>
            </div>

            {/* Close Link */}
            <button
              onClick={onClose}
              className="w-full mt-4 text-sm text-gray-500 hover:text-gray-700 transition-colors"
            >
              {t('premium:upsell.maybe_later')}
            </button>
          </motion.div>
        </motion.div>
      )}
    </AnimatePresence>
  );
}
