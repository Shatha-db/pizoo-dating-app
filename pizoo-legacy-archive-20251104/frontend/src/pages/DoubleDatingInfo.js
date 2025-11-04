import React from 'react';
import { useNavigate } from 'react-router-dom';
import { Button } from '../components/ui/button';
import { Card } from '../components/ui/card';
import { X, Users, Heart, MessageCircle, Check, Sparkles } from 'lucide-react';

const DoubleDatingInfo = () => {
  const navigate = useNavigate();

  return (
    <div className="min-h-screen bg-gradient-to-br from-pink-50 via-purple-50 to-blue-50 pb-20" dir="rtl">
      {/* Header */}
      <header className="bg-white shadow-sm p-4 flex items-center justify-between sticky top-0 z-10">
        <Button
          variant="ghost"
          size="icon"
          onClick={() => navigate(-1)}
        >
          <X className="w-6 h-6" />
        </Button>
        <h1 className="text-xl font-bold">المواعدة المزدوجة</h1>
        <div className="w-10"></div>
      </header>

      <main className="max-w-2xl mx-auto p-4">
        {/* Hero Section */}
        <div className="text-center mb-8 mt-4">
          <div className="inline-flex items-center justify-center gap-2 mb-4">
            <div className="w-16 h-16 bg-gradient-to-br from-pink-400 to-purple-400 rounded-full flex items-center justify-center">
              <Users className="w-8 h-8 text-white" />
            </div>
            <Heart className="w-8 h-8 text-red-500 animate-pulse" />
            <div className="w-16 h-16 bg-gradient-to-br from-blue-400 to-purple-400 rounded-full flex items-center justify-center">
              <Users className="w-8 h-8 text-white" />
            </div>
          </div>
          <h2 className="text-3xl font-bold mb-3 bg-gradient-to-r from-pink-600 to-purple-600 bg-clip-text text-transparent">
            تشكيل ثُنائيًا مع أصدقائك في موعد مزدوج
          </h2>
          <p className="text-gray-600 text-lg">
            يُمكنك تشكيل ثُنائي مع ما يصل إلى 3 من أصدقائك في موعد مزدوج
          </p>
        </div>

        {/* How It Works */}
        <Card className="p-6 mb-6 bg-white">
          <h3 className="text-xl font-bold mb-4 flex items-center gap-2">
            <Sparkles className="w-6 h-6 text-yellow-500" />
            كيف تعمل المواعدة المزدوجة؟
          </h3>
          
          <div className="space-y-6">
            {/* Step 1 */}
            <div className="flex gap-4">
              <div className="flex-shrink-0 w-12 h-12 bg-gradient-to-br from-pink-500 to-red-500 rounded-full flex items-center justify-center text-white font-bold text-xl">
                1
              </div>
              <div className="flex-1">
                <h4 className="font-bold text-lg mb-2">ادعُ أصدقائك</h4>
                <p className="text-gray-600">
                  شكّل ثُنائيًا مع ما يصل إلى 3 أصدقاء في موعد مزدوج. اسحب بإمكانك تبادل الإعجاب مع أناس جدد مع أنواع أخرى.
                </p>
              </div>
            </div>

            {/* Step 2 */}
            <div className="flex gap-4">
              <div className="flex-shrink-0 w-12 h-12 bg-gradient-to-br from-purple-500 to-blue-500 rounded-full flex items-center justify-center text-white font-bold text-xl">
                2
              </div>
              <div className="flex-1">
                <h4 className="font-bold text-lg mb-2">تبادل الإعجاب معًا</h4>
                <p className="text-gray-600">
                  عند قبولك، ستبقى بإمكانك تبادل الإعجاب مع أناس مع أصدقائك. ستتقدم بإمكانكم على ثُنائيًا موعد مزدوج آخرى.
                </p>
              </div>
            </div>

            {/* Step 3 */}
            <div className="flex gap-4">
              <div className="flex-shrink-0 w-12 h-12 bg-gradient-to-br from-green-500 to-teal-500 rounded-full flex items-center justify-center text-white font-bold text-xl">
                3
              </div>
              <div className="flex-1">
                <h4 className="font-bold text-lg mb-2">إعجاب واحد كافٍ تبادل إعجاب</h4>
                <p className="text-gray-600">
                  يكفي شخص واحد من كل ثُنائي ليبضل تبادل إعجاب. هذا طريقة جديدة اسحب بإمكانكم بمفردكم على ثُنائيات موعد مزدوج أخرى.
                </p>
              </div>
            </div>

            {/* Step 4 */}
            <div className="flex gap-4">
              <div className="flex-shrink-0 w-12 h-12 bg-gradient-to-br from-orange-500 to-red-500 rounded-full flex items-center justify-center text-white font-bold text-xl">
                4
              </div>
              <div className="flex-1">
                <h4 className="font-bold text-lg mb-2">انضم إلى الدردشة الجماعية</h4>
                <p className="text-gray-600">
                  تفقد الأجواء في الدردشة الجماعية قبل التخطيط للقاء جماعي.
                </p>
              </div>
            </div>
          </div>
        </Card>

        {/* Benefits */}
        <Card className="p-6 mb-6 bg-gradient-to-br from-pink-50 to-purple-50">
          <h3 className="text-xl font-bold mb-4">مميزات المواعدة المزدوجة</h3>
          
          <div className="space-y-3">
            {[
              'قضاء وقت ممتع مع أصدقائك',
              'التعرف على أشخاص جدد معًا',
              'الشعور بالأمان والراحة',
              'تجربة مواعدة فريدة ومختلفة',
              'بناء صداقات جديدة',
              'مشاركة اللحظات الممتعة'
            ].map((benefit, index) => (
              <div key={index} className="flex items-center gap-3">
                <div className="w-6 h-6 bg-green-500 rounded-full flex items-center justify-center flex-shrink-0">
                  <Check className="w-4 h-4 text-white" />
                </div>
                <span className="text-gray-700">{benefit}</span>
              </div>
            ))}
          </div>
        </Card>

        {/* CTA */}
        <Button
          onClick={() => navigate('/double-dating')}
          className="w-full bg-gradient-to-r from-pink-500 to-purple-500 hover:from-pink-600 hover:to-purple-600 text-white font-bold py-6 text-lg rounded-xl mb-4"
        >
          <Users className="w-5 h-5 ml-2" />
          ابدأ المواعدة المزدوجة الآن
        </Button>

        {/* Note */}
        <p className="text-center text-sm text-gray-500">
          💡 يمكنك دعوة أصدقائك وبدء تجربة المواعدة المزدوجة مجانًا
        </p>
      </main>
    </div>
  );
};

export default DoubleDatingInfo;
