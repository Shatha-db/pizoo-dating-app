import { useState, useMemo } from "react";
import { motion } from "framer-motion";

export default function ProfileCard({ user, onLike, onPass, onFavorite, onBoost, onRewind, onOpenFull }) {
  const photos = user?.photos?.length ? user.photos : [user?.avatarUrl].filter(Boolean);
  const [idx, setIdx] = useState(0);
  const go = (dir) => { if (!photos?.length) return; setIdx(p => (p + dir + photos.length) % photos.length); };
  const chips = useMemo(() => (user?.interests || []).slice(0, 4), [user]);

  return (
    <div className="w-full max-w-[680px] mx-auto rounded-3xl overflow-hidden shadow-[0_20px_60px_-20px_rgba(0,0,0,.25)] bg-white dark:bg-gray-800">
      {/* Image area */}
      <div className="relative aspect-[4/3]">
        {/* progress bars */}
        {photos?.length > 1 && (
          <div className="absolute top-3 left-0 right-0 px-4 flex gap-1 z-10">
            {photos.map((_, i) => (
              <div key={i}
                   className={`h-1.5 flex-1 rounded-full transition-all ${i <= idx ? 'bg-white/90' : 'bg-white/40'}`} />
            ))}
          </div>
        )}

        <motion.img
          key={idx}
          src={photos[idx]}
          alt={user?.name || 'profile'}
          initial={{ opacity: 0.4, scale: 1.02 }}
          animate={{ opacity: 1, scale: 1 }}
          transition={{ duration: .35 }}
          className="w-full h-full object-cover select-none"
        />

        <div className="absolute inset-0 bg-gradient-to-t from-black/50 via-black/10 to-transparent pointer-events-none" />

        <div className="absolute top-3 left-3 flex items-center gap-2 z-10">
          <div className="px-2 py-1 rounded-full bg-white/70 backdrop-blur text-xs font-medium">Safety</div>
        </div>
        <div className="absolute top-3 right-3 flex items-center gap-2 z-10">
          {user?.verified && (
            <span className="px-2 py-1 rounded-full bg-white/80 text-xs font-semibold">✅ Verified</span>
          )}
          {user?.online && (
            <span className="px-2 py-1 rounded-full bg-emerald-500 text-white text-xs font-semibold">Online</span>
          )}
        </div>

        {photos?.length > 1 && (
          <>
            <button onClick={() => go(-1)} className="absolute inset-y-0 left-0 w-1/3 z-10" aria-label="prev" />
            <button onClick={() => go(+1)} className="absolute inset-y-0 right-0 w-1/3 z-10" aria-label="next" />
          </>
        )}

        {photos?.length > 1 && (
          <button onClick={() => onOpenFull?.(idx)}
                  className="absolute bottom-3 right-4 text-xs px-3 py-1 rounded-full bg-white/80 hover:bg-white z-10">
            عرض كامل
          </button>
        )}
      </div>

      <div className="p-4">
        <div className="flex items-center gap-2">
          <h3 className="text-2xl font-extrabold dark:text-white">{user?.name || '—'}</h3>
          {user?.age && <span className="text-lg text-gray-500 dark:text-gray-400">, {user.age}</span>}
        </div>
        <div className="mt-1 text-gray-700 dark:text-gray-300">
          {user?.jobTitle && <span className="font-medium">{user.jobTitle}</span>}
          {(user?.city || user?.distanceText) && (
            <span className="text-gray-500 dark:text-gray-400"> • {user.city} {user.distanceText ? `• ${user.distanceText}` : ''}</span>
          )}
        </div>

        {!!(user?.interests || []).length && (
          <div className="mt-3 flex flex-wrap gap-2">
            {chips.map((c,i) => (
              <span key={i} className="px-3 py-1 rounded-full bg-pink-50 dark:bg-pink-900/30 text-pink-700 dark:text-pink-300 text-sm">{c}</span>
            ))}
          </div>
        )}

        {user?.icebreaker && (
          <button onClick={() => navigator.clipboard.writeText(user.icebreaker)}
                  className="mt-3 text-sm text-indigo-600 dark:text-indigo-400 hover:underline">
            اقترح بداية محادثة: "{user.icebreaker}"
          </button>
        )}
      </div>

      <div className="px-4 pb-4">
        <div className="grid grid-cols-5 gap-3">
          <ActionBtn color="violet" label="Boost" icon="⚡" onClick={onBoost} />
          <ActionBtn color="blue" label="Favorite" icon="⭐" onClick={onFavorite} />
          <ActionBtn color="rose" label="Like" icon="❤️" onClick={onLike} heavy />
          <ActionBtn color="orange" label="Pass" icon="✖️" onClick={onPass} />
          <ActionBtn color="amber" label="Rewind" icon="↩️" onClick={onRewind} />
        </div>
      </div>
    </div>
  );
}

function ActionBtn({ icon, label, onClick, color = 'gray', heavy }) {
  const ring = {
    violet: 'ring-violet-300 dark:ring-violet-600',
    blue: 'ring-blue-300 dark:ring-blue-600',
    rose: 'ring-rose-300 dark:ring-rose-600',
    orange: 'ring-orange-300 dark:ring-orange-600',
    amber: 'ring-amber-300 dark:ring-amber-600',
    gray: 'ring-gray-300 dark:ring-gray-600'
  }[color] || 'ring-gray-300 dark:ring-gray-600';

  return (
    <motion.button
      whileTap={{ scale: .96 }}
      onClick={onClick}
      className={`h-14 rounded-full bg-white dark:bg-gray-700 shadow-md flex flex-col items-center justify-center ring-2 ${ring} transition ${heavy ? 'hover:scale-[1.03]' : 'hover:scale-[1.02]'}`}>
      <span className="text-xl leading-none">{icon}</span>
      <span className="mt-0.5 text-[11px] text-gray-700 dark:text-gray-300">{label}</span>
    </motion.button>
  );
}
