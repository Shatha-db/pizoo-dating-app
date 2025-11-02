import React, { useState } from 'react';
import { useTranslation } from 'react-i18next';
import PricingCard from './PricingCard';

export default function PricingCarousel({ onSelect }) {
  const { t } = useTranslation('premium');
  const [activeIndex, setActiveIndex] = useState(0);

  const cards = [
    {
      tier: 'gold',
      title: 'Pizoo GOLD',
      benefits: [
        { text: t('premium:benefits.unlimited_likes'), locked: false },
        { text: t('premium:benefits.see_who_likes_you'), locked: false },
        { text: t('premium:benefits.super_likes_weekly'), locked: false },
        { text: t('premium:benefits.rewind'), locked: false }
      ],
      ctaLabel: t('premium:upsell.get_gold')
    },
    {
      tier: 'platinum',
      title: 'Pizoo PLATINUM',
      benefits: [
        { text: t('premium:benefits.all_gold_features'), locked: false },
        { text: t('premium:benefits.priority_likes'), locked: false },
        { text: t('premium:benefits.top_profiles'), locked: false },
        { text: t('premium:benefits.message_before_match'), locked: false }
      ],
      ctaLabel: t('premium:pricing.continue')
    },
    {
      tier: 'plus',
      title: 'Pizoo PLUS',
      benefits: [
        { text: t('premium:benefits.unlimited_likes'), locked: false },
        { text: t('premium:benefits.passport'), locked: false },
        { text: t('premium:benefits.rewind'), locked: false },
        { text: t('premium:benefits.hide_ads'), locked: false }
      ],
      ctaLabel: t('premium:pricing.continue')
    }
  ];

  return (
    <div className="w-full py-4">
      {/* Swipeable Card Container */}
      <div 
        className="w-full overflow-x-auto flex gap-4 snap-x snap-mandatory px-4 pb-2 scrollbar-hide"
        style={{ scrollSnapType: 'x mandatory' }}
        onScroll={(e) => {
          const index = Math.round(e.target.scrollLeft / (e.target.offsetWidth - 32));
          setActiveIndex(index);
        }}
      >
        {cards.map((card, idx) => (
          <div 
            key={idx} 
            className="min-w-[85%] sm:min-w-[340px] snap-center flex-shrink-0"
          >
            <PricingCard 
              {...card} 
              onClick={() => onSelect?.(card.tier)} 
            />
          </div>
        ))}
      </div>

      {/* Dots Indicator */}
      <div className="flex items-center justify-center gap-2 mt-4">
        {cards.map((_, idx) => (
          <div
            key={idx}
            className={`h-2 rounded-full transition-all duration-300 ${
              idx === activeIndex 
                ? 'w-6 bg-pink-500' 
                : 'w-2 bg-gray-300'
            }`}
          />
        ))}
      </div>

      {/* Sticky CTA Bar (optional) */}
      <div className="mt-6 px-4">
        <div className="bg-gradient-to-r from-pink-50 to-orange-50 rounded-2xl p-4 border border-pink-200">
          <p className="text-sm text-gray-700 text-center mb-2">
            {t('premium:upsell.limited_time')}
          </p>
          <button 
            onClick={() => onSelect?.(cards[activeIndex].tier)}
            className="w-full h-12 rounded-full bg-gradient-to-r from-[#F59E0B] to-[#EA580C] text-white font-semibold shadow-lg hover:brightness-110 transition-all"
          >
            {t('premium:pricing.start_now')}
          </button>
        </div>
      </div>
    </div>
  );
}
