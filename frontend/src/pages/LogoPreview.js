import React from 'react';
import { useNavigate } from 'react-router-dom';
import { Button } from '../components/ui/button';
import { 
  Logo1_MinimalistHeart,
  Logo2_InterlockingCircles,
  Logo3_PMonogram,
  Logo4_ModernFlame,
  Logo5_DoodleStyle,
  Logo6_3DCube,
  Logo7_AbstractInfinity,
  Logo8_LowercaseModern
} from '../components/LogoOptions';
import { X } from 'lucide-react';

const LogoPreview = () => {
  const navigate = useNavigate();

  return (
    <div className="min-h-screen bg-gray-50 pb-20" dir="rtl">
      {/* Header */}
      <header className="bg-white shadow-sm p-4 sticky top-0 z-10">
        <div className="max-w-6xl mx-auto flex items-center justify-between">
          <Button
            variant="ghost"
            size="icon"
            onClick={() => navigate(-1)}
          >
            <X className="w-6 h-6" />
          </Button>
          <h1 className="text-2xl font-bold">معرض تصاميم اللوجو</h1>
          <div className="w-10"></div>
        </div>
      </header>

      <main className="max-w-6xl mx-auto p-6">
        <div className="text-center mb-12">
          <h2 className="text-4xl font-bold mb-3">اختر اللوجو المناسب لـ Pizoo</h2>
          <p className="text-gray-600 text-lg">
            8 تصاميم احترافية مستوحاة من أحدث اتجاهات 2025
          </p>
        </div>

        <div className="grid md:grid-cols-2 gap-8">
          {/* Option 1 - Minimalist Geometric Heart */}
          <div className="bg-white p-8 rounded-2xl shadow-sm hover:shadow-xl transition-all hover:scale-105 cursor-pointer border-2 border-transparent hover:border-pink-500">
            <div className="flex items-center justify-between mb-6">
              <span className="text-5xl font-bold text-gray-200">01</span>
            </div>
            <div className="flex justify-center mb-6">
              <Logo1_MinimalistHeart size={80} />
            </div>
            <h3 className="text-xl font-bold mb-2 text-center">قلب هندسي بسيط</h3>
            <p className="text-sm text-gray-600 text-center">
              تصميم نظيف وأنيق مع خطوط هندسية واضحة. مثالي للمظهر الاحترافي.
            </p>
            <div className="mt-6 flex justify-center">
              <span className="px-4 py-1 bg-pink-100 text-pink-700 rounded-full text-xs font-medium">
                Minimalist
              </span>
            </div>
          </div>

          {/* Option 2 - Interlocking Circles */}
          <div className="bg-white p-8 rounded-2xl shadow-sm hover:shadow-xl transition-all hover:scale-105 cursor-pointer border-2 border-transparent hover:border-pink-500">
            <div className="flex items-center justify-between mb-6">
              <span className="text-5xl font-bold text-gray-200">02</span>
            </div>
            <div className="flex justify-center mb-6">
              <Logo2_InterlockingCircles size={80} />
            </div>
            <h3 className="text-xl font-bold mb-2 text-center">دوائر متداخلة</h3>
            <p className="text-sm text-gray-600 text-center">
              يرمز للاتصال والتقاء شخصين. تصميم رمزي ومجرد.
            </p>
            <div className="mt-6 flex justify-center">
              <span className="px-4 py-1 bg-purple-100 text-purple-700 rounded-full text-xs font-medium">
                Abstract
              </span>
            </div>
          </div>

          {/* Option 3 - P Monogram */}
          <div className="bg-white p-8 rounded-2xl shadow-sm hover:shadow-xl transition-all hover:scale-105 cursor-pointer border-2 border-transparent hover:border-pink-500">
            <div className="flex items-center justify-between mb-6">
              <span className="text-5xl font-bold text-gray-200">03</span>
            </div>
            <div className="flex justify-center mb-6">
              <Logo3_PMonogram size={80} />
            </div>
            <h3 className="text-xl font-bold mb-2 text-center">حرف P مع قلب</h3>
            <p className="text-sm text-gray-600 text-center">
              مونوجرام احترافي مع قلب صغير مدمج. فريد ومميز.
            </p>
            <div className="mt-6 flex justify-center">
              <span className="px-4 py-1 bg-blue-100 text-blue-700 rounded-full text-xs font-medium">
                Monogram
              </span>
            </div>
          </div>

          {/* Option 4 - Modern Flame */}
          <div className="bg-white p-8 rounded-2xl shadow-sm hover:shadow-xl transition-all hover:scale-105 cursor-pointer border-2 border-transparent hover:border-pink-500">
            <div className="flex items-center justify-between mb-6">
              <span className="text-5xl font-bold text-gray-200">04</span>
            </div>
            <div className="flex justify-center mb-6">
              <Logo4_ModernFlame size={80} />
            </div>
            <h3 className="text-xl font-bold mb-2 text-center">لهب عصري</h3>
            <p className="text-sm text-gray-600 text-center">
              يعبر عن الطاقة والحماس والشغف. جريء ومميز.
            </p>
            <div className="mt-6 flex justify-center">
              <span className="px-4 py-1 bg-orange-100 text-orange-700 rounded-full text-xs font-medium">
                Energetic
              </span>
            </div>
          </div>

          {/* Option 5 - Doodle Style */}
          <div className="bg-white p-8 rounded-2xl shadow-sm hover:shadow-xl transition-all hover:scale-105 cursor-pointer border-2 border-transparent hover:border-pink-500">
            <div className="flex items-center justify-between mb-6">
              <span className="text-5xl font-bold text-gray-200">05</span>
            </div>
            <div className="flex justify-center mb-6">
              <Logo5_DoodleStyle size={80} />
            </div>
            <h3 className="text-xl font-bold mb-2 text-center">رسم يدوي</h3>
            <p className="text-sm text-gray-600 text-center">
              أسلوب دافئ وإنساني مع لمسة شخصية. ودود ومريح.
            </p>
            <div className="mt-6 flex justify-center">
              <span className="px-4 py-1 bg-yellow-100 text-yellow-700 rounded-full text-xs font-medium">
                Hand-Drawn
              </span>
            </div>
          </div>

          {/* Option 6 - 3D Cube */}
          <div className="bg-white p-8 rounded-2xl shadow-sm hover:shadow-xl transition-all hover:scale-105 cursor-pointer border-2 border-transparent hover:border-pink-500">
            <div className="flex items-center justify-between mb-6">
              <span className="text-5xl font-bold text-gray-200">06</span>
            </div>
            <div className="flex justify-center mb-6">
              <Logo6_3DCube size={80} />
            </div>
            <h3 className="text-xl font-bold mb-2 text-center">مكعب ثلاثي الأبعاد</h3>
            <p className="text-sm text-gray-600 text-center">
              تصميم حديث مع عمق بصري. يعبر عن التكنولوجيا والابتكار.
            </p>
            <div className="mt-6 flex justify-center">
              <span className="px-4 py-1 bg-indigo-100 text-indigo-700 rounded-full text-xs font-medium">
                3D Modern
              </span>
            </div>
          </div>

          {/* Option 7 - Abstract Infinity */}
          <div className="bg-white p-8 rounded-2xl shadow-sm hover:shadow-xl transition-all hover:scale-105 cursor-pointer border-2 border-transparent hover:border-pink-500">
            <div className="flex items-center justify-between mb-6">
              <span className="text-5xl font-bold text-gray-200">07</span>
            </div>
            <div className="flex justify-center mb-6">
              <Logo7_AbstractInfinity size={80} />
            </div>
            <h3 className="text-xl font-bold mb-2 text-center">رمز اللانهاية</h3>
            <p className="text-sm text-gray-600 text-center">
              يرمز للاتصالات اللانهائية. تصميم فلسفي وعميق.
            </p>
            <div className="mt-6 flex justify-center">
              <span className="px-4 py-1 bg-pink-100 text-pink-700 rounded-full text-xs font-medium">
                Symbolic
              </span>
            </div>
          </div>

          {/* Option 8 - Lowercase Modern */}
          <div className="bg-white p-8 rounded-2xl shadow-sm hover:shadow-xl transition-all hover:scale-105 cursor-pointer border-2 border-transparent hover:border-pink-500">
            <div className="flex items-center justify-between mb-6">
              <span className="text-5xl font-bold text-gray-200">08</span>
            </div>
            <div className="flex justify-center mb-6">
              <Logo8_LowercaseModern size={80} />
            </div>
            <h3 className="text-xl font-bold mb-2 text-center">أحرف صغيرة عصرية</h3>
            <p className="text-sm text-gray-600 text-center">
              تصميم بسيط وودود مع حرف p مدمج. عصري وسهل.
            </p>
            <div className="mt-6 flex justify-center">
              <span className="px-4 py-1 bg-green-100 text-green-700 rounded-full text-xs font-medium">
                Friendly
              </span>
            </div>
          </div>
        </div>

        {/* Footer Note */}
        <div className="mt-12 text-center">
          <p className="text-gray-600 mb-4">
            💡 جميع التصاميم مستوحاة من أحدث اتجاهات 2025 لتطبيقات المواعدة
          </p>
          <p className="text-sm text-gray-500">
            يمكن تخصيص أي تصميم حسب رغبتك
          </p>
        </div>
      </main>
    </div>
  );
};

export default LogoPreview;
