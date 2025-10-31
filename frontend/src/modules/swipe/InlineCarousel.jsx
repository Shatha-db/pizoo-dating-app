import React, { useState, useRef } from 'react';
import { useTranslation } from 'react-i18next';

/**
 * Inline Carousel Component for Profile Cards
 * Swipe horizontally through photos with touch gestures
 * Shows progress dots/bars at the bottom
 */
export default function InlineCarousel({ photos = [], onOpenLightbox }) {
  const { t } = useTranslation(['chat']);
  const [idx, setIdx] = useState(0);
  const startX = useRef(0);
  const delta = useRef(0);

  if (!photos?.length) return null;

  // Handle photo array - can be strings or objects with url
  const photoUrls = photos.map(p => p?.url || p);
  const cur = photoUrls[idx];

  function next() {
    setIdx(i => (i + 1) % photoUrls.length);
  }

  function prev() {
    setIdx(i => (i - 1 + photoUrls.length) % photoUrls.length);
  }

  function onTouchStart(e) {
    startX.current = e.touches[0].clientX;
    delta.current = 0;
  }

  function onTouchMove(e) {
    delta.current = e.touches[0].clientX - startX.current;
  }

  function onTouchEnd() {
    if (Math.abs(delta.current) < 30) return; // tap threshold
    if (delta.current < 0) next();
    else prev();
  }

  return (
    <div className="relative select-none">
      {/* Main Photo */}
      <img
        src={cur}
        alt={`Photo ${idx + 1}`}
        className="w-full h-[64vh] object-cover cursor-pointer"
        onTouchStart={onTouchStart}
        onTouchMove={onTouchMove}
        onTouchEnd={onTouchEnd}
        onClick={next} // Tap to cycle
      />

      {/* Progress Dots/Bars */}
      {photoUrls.length > 1 && (
        <div className="absolute bottom-3 left-0 right-0 flex justify-center gap-1 px-4 z-10">
          {photoUrls.map((_, i) => (
            <span
              key={i}
              onClick={() => setIdx(i)}
              className={`h-1 rounded-full transition-all cursor-pointer ${
                i === idx
                  ? 'w-10 bg-white'
                  : 'w-6 bg-white/40 hover:bg-white/60'
              }`}
            />
          ))}
        </div>
      )}

      {/* Invisible Side Buttons for Click Navigation */}
      {photoUrls.length > 1 && (
        <>
          <button
            onClick={prev}
            className="absolute inset-y-0 left-0 w-1/4 z-5"
            aria-label="Previous photo"
          />
          <button
            onClick={next}
            className="absolute inset-y-0 right-0 w-1/4 z-5"
            aria-label="Next photo"
          />
        </>
      )}

      {/* Full View Button (Optional) */}
      {onOpenLightbox && photoUrls.length > 0 && (
        <button
          onClick={() => onOpenLightbox(idx)}
          className="absolute top-3 right-3 bg-black/40 hover:bg-black/60 backdrop-blur-sm text-white rounded-full px-3 py-1 text-sm font-medium transition-all z-10"
        >
          {t('view_full')}
        </button>
      )}

      {/* Photo Counter */}
      {photoUrls.length > 1 && (
        <div className="absolute top-3 left-3 bg-black/40 backdrop-blur-sm text-white px-2 py-1 rounded-full text-xs z-10">
          {idx + 1}/{photoUrls.length}
        </div>
      )}
    </div>
  );
}
