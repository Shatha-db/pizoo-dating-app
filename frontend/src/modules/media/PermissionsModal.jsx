import React from "react";

export default function PermissionsModal({
  onPick,
  label = "Pizoo يحتاج للوصول إلى مكتبة الصور",
  onClose
}) {
  return (
    <div className="fixed inset-0 z-[1000] bg-black/50 flex items-center justify-center p-4">
      <div className="w-full max-w-md bg-white dark:bg-gray-800 rounded-2xl shadow-xl overflow-hidden">
        <div className="p-6">
          <h3 className="text-lg font-bold mb-2 dark:text-white">{label}</h3>
          <p className="text-sm text-gray-600 dark:text-gray-300 mb-4">
            يسمح لك هذا برفع أو مشاركة الصور في ملفك الشخصي أو الدردشة. قد تحتوي الصور على بيانات الموقع والتعليقات.
          </p>
          
          {/* Sample Grid */}
          <div className="grid grid-cols-4 gap-2 mb-4">
            {[...Array(8)].map((_, i) => (
              <div
                key={i}
                className="aspect-square bg-gray-200 dark:bg-gray-700 rounded-lg"
              />
            ))}
          </div>
          
          {/* Action Buttons */}
          <div className="space-y-2">
            <button
              onClick={() => onPick?.('limited')}
              className="w-full h-12 rounded-full bg-gray-100 dark:bg-gray-700 dark:text-white font-medium hover:bg-gray-200 dark:hover:bg-gray-600 transition"
            >
              تحديد الوصول…
            </button>
            <button
              onClick={() => onPick?.('full')}
              className="w-full h-12 rounded-full bg-gradient-to-r from-pink-500 to-rose-500 text-white font-semibold hover:from-pink-600 hover:to-rose-600 transition"
            >
              السماح بالوصول الكامل
            </button>
            <button
              onClick={onClose}
              className="w-full h-12 rounded-full bg-white dark:bg-gray-800 border border-gray-300 dark:border-gray-600 dark:text-white font-medium hover:bg-gray-50 dark:hover:bg-gray-700 transition"
            >
              عدم السماح
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}
