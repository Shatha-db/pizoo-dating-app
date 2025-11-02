import React from 'react';
import { motion } from 'framer-motion';

export default function PricingCard({ tier = 'gold', title, benefits = [], ctaLabel, onClick }) {
  const gradients = {
    gold: 'from-[#F7C948] via-[#F59E0B] to-[#EA580C]',
    platinum: 'from-[#E5E7EB] via-[#CBD5E1] to-[#64748B]',
    plus: 'from-[#FF7AB5] via-[#FF4C61] to-[#F97316]'
  };

  const ctaGradients = {
    gold: 'from-[#F59E0B] to-[#EA580C]',
    platinum: 'from-[#94A3B8] to-[#64748B]',
    plus: 'from-[#FF4C61] to-[#F97316]'
  };

  return (
    <motion.div
      whileHover={{ scale: 1.02 }}
      className={`rounded-3xl shadow-xl overflow-hidden bg-gradient-to-b ${gradients[tier]} relative border-2 border-white/20`}
    >
      <div className="p-6">
        {/* Header */}
        <div className="flex items-center gap-3 mb-4">
          <div className="w-8 h-8 rounded-full bg-white/30 flex items-center justify-center">
            <span className="text-xl">🔥</span>
          </div>
          <h3 className="font-bold text-xl text-white drop-shadow-md">{title}</h3>
        </div>

        {/* Benefits List */}
        <ul className="space-y-3 bg-white/70 backdrop-blur-sm rounded-2xl p-4 mb-4">
          {benefits.map((benefit, idx) => (
            <li key={idx} className="flex items-start gap-3">
              <span className="text-lg flex-shrink-0 mt-0.5">
                {benefit.locked ? '🔒' : '✅'}
              </span>
              <span className="text-gray-800 text-sm leading-relaxed">
                {benefit.text}
              </span>
            </li>
          ))}
        </ul>

        {/* CTA Button */}
        <motion.button
          whileTap={{ scale: 0.98 }}
          onClick={onClick}
          className={`w-full h-12 rounded-full text-white font-semibold bg-gradient-to-r ${ctaGradients[tier]} shadow-lg hover:brightness-110 transition-all duration-200`}
        >
          {ctaLabel}
        </motion.button>
      </div>
    </motion.div>
  );
}
