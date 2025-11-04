import React from 'react';
import 'photoswipe/style.css';
import { Gallery, Item } from 'react-photoswipe-gallery';

/**
 * Photo Lightbox Component using PhotoSwipe
 * Allows users to view photos in fullscreen with swipe/zoom
 */
export default function PhotoLightbox({ photos = [], start = 0, onClose }) {
  if (!photos?.length) return null;

  return (
    <div className="fixed inset-0 z-50 bg-black/90 flex items-center justify-center">
      <Gallery withCaption>
        <div className="w-full h-full flex items-center justify-center p-4">
          {photos.map((src, i) => (
            <Item
              key={i}
              original={src}
              thumbnail={src}
              width={1600}
              height={1066}
            >
              {({ ref, open }) => (
                <img
                  ref={ref}
                  src={src}
                  alt={`Photo ${i + 1}`}
                  onClick={open}
                  className={`max-h-[80vh] max-w-full object-contain rounded-xl cursor-pointer ${
                    i === start ? 'block' : 'hidden'
                  }`}
                />
              )}
            </Item>
          ))}
        </div>
      </Gallery>
      
      {/* Close Button */}
      <button
        onClick={onClose}
        className="absolute top-4 right-4 w-12 h-12 rounded-full bg-white/20 backdrop-blur-sm hover:bg-white/30 transition-colors flex items-center justify-center text-white text-2xl z-50"
        aria-label="Close lightbox"
      >
        ✕
      </button>

      {/* Photo Counter */}
      <div className="absolute bottom-4 left-1/2 transform -translate-x-1/2 bg-black/50 backdrop-blur-sm text-white px-4 py-2 rounded-full text-sm z-50">
        {start + 1} / {photos.length}
      </div>
    </div>
  );
}
