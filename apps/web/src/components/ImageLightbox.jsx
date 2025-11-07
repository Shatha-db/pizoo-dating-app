import { useEffect } from "react";

export default function ImageLightbox({ open, images = [], index = 0, onClose, onNext, onPrev }) {
  useEffect(() => {
    if (!open) return;
    
    const onKey = (e) => {
      if (e.key === 'Escape') onClose?.();
      if (e.key === 'ArrowRight') onNext?.();
      if (e.key === 'ArrowLeft') onPrev?.();
    };
    window.addEventListener('keydown', onKey);
    return () => window.removeEventListener('keydown', onKey);
  }, [open, onClose, onNext, onPrev]);

  if (!open) return null;

  return (
    <div className="fixed inset-0 z-50 bg-black/90 flex items-center justify-center">
      {/* Close Button */}
      <button 
        className="absolute top-4 right-4 text-white text-2xl hover:text-gray-300 z-10"
        onClick={onClose}
        aria-label="Close"
      >
        ✕
      </button>

      {/* Previous Button */}
      <button 
        className="absolute left-3 text-white text-5xl hover:text-gray-300"
        onClick={onPrev}
        aria-label="Previous"
      >
        ‹
      </button>

      {/* Main Image */}
      <img 
        src={images[index]?.url || images[index]} 
        className="max-h-[80vh] max-w-[90vw] object-contain rounded-lg"
        alt={`Image ${index + 1}`}
      />

      {/* Next Button */}
      <button 
        className="absolute right-3 text-white text-5xl hover:text-gray-300"
        onClick={onNext}
        aria-label="Next"
      >
        ›
      </button>

      {/* Thumbnail Strip */}
      <div className="absolute bottom-6 left-1/2 -translate-x-1/2 flex gap-2 overflow-x-auto max-w-[90vw] px-4">
        {images.map((src, i) => (
          <img 
            key={i} 
            src={typeof src === 'string' ? src : src.url} 
            onClick={() => onNext?.(i)} 
            className={
              "h-14 w-14 object-cover rounded-md border-2 cursor-pointer hover:opacity-80 transition-opacity " + 
              (i === index ? 'border-white' : 'border-transparent')
            }
            alt={`Thumbnail ${i + 1}`}
          />
        ))}
      </div>
    </div>
  );
}
