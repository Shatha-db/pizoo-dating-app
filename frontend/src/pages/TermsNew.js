import React from 'react';
import { useNavigate } from 'react-router-dom';
import { Button } from '../components/ui/button';
import { Card } from '../components/ui/card';
import { X } from 'lucide-react';

const Terms = () => {
  const navigate = useNavigate();

  return (
    <div className="min-h-screen bg-gray-50 pb-20" dir="rtl">
      {/* Header */}
      <header className="bg-white shadow-sm p-4 sticky top-0 z-10">
        <div className="max-w-4xl mx-auto flex items-center justify-between">
          <Button
            variant="ghost"
            size="icon"
            onClick={() => navigate(-1)}
          >
            <X className="w-6 h-6" />
          </Button>
          <h1 className="text-xl font-bold">الشروط والأحكام</h1>
          <div className="w-10"></div>
        </div>
      </header>

      <main className="max-w-4xl mx-auto p-6">
        <Card className="p-8">
          <h2 className="text-3xl font-bold mb-6 text-center bg-gradient-to-r from-pink-600 to-purple-600 bg-clip-text text-transparent">
            شروط استخدام خدمة Pizoo
          </h2>

          <div className="space-y-6 text-gray-700 leading-relaxed">
            <section>
              <h3 className="text-xl font-bold mb-3 text-gray-900">1. القبول بالشروط</h3>
              <p>
                بالوصول إلى تطبيق Pizoo واستخدامه، فإنك توافق على الالتزام بهذه الشروط والأحكام. 
                إذا كنت لا توافق على أي جزء من هذه الشروط، يجب عليك عدم استخدام التطبيق.
              </p>
            </section>

            <section>
              <h3 className="text-xl font-bold mb-3 text-gray-900">2. الأهلية</h3>
              <p>
                يجب أن تكون بعمر 18 عاماً أو أكثر لاستخدام Pizoo. باستخدامك للتطبيق، تقر وتضمن 
                أنك تستوفي هذا الشرط وأن لديك الحق القانوني والصلاحية والقدرة على الدخول في هذه الاتفاقية.
              </p>
            </section>

            <section>
              <h3 className="text-xl font-bold mb-3 text-gray-900">3. حسابك</h3>
              <p className="mb-2">عند إنشاء حساب على Pizoo، فإنك توافق على:</p>
              <ul className="list-disc list-inside space-y-2 mr-4">
                <li>تقديم معلومات دقيقة وكاملة وحديثة عن نفسك</li>
                <li>الحفاظ على أمان كلمة المرور الخاصة بك</li>
                <li>قبول المسؤولية الكاملة عن جميع الأنشطة التي تحدث تحت حسابك</li>
                <li>إخطارنا فوراً بأي استخدام غير مصرح به لحسابك</li>
              </ul>
            </section>

            <section>
              <h3 className="text-xl font-bold mb-3 text-gray-900">4. قواعد السلوك</h3>
              <p className="mb-2">أنت توافق على عدم:</p>
              <ul className="list-disc list-inside space-y-2 mr-4">
                <li>انتحال شخصية أي شخص أو كيان</li>
                <li>نشر محتوى غير لائق أو مسيء أو عنصري أو تمييزي</li>
                <li>استخدام التطبيق لأغراض تجارية دون موافقتنا</li>
                <li>التحرش أو إساءة معاملة مستخدمين آخرين</li>
                <li>نشر محتوى غير قانوني أو ضار أو مهدد</li>
                <li>جمع معلومات المستخدمين الآخرين دون موافقتهم</li>
              </ul>
            </section>

            <section>
              <h3 className="text-xl font-bold mb-3 text-gray-900">5. المحتوى</h3>
              <p>
                أنت المسؤول الوحيد عن المحتوى الذي تنشره على Pizoo. نحتفظ بالحق في إزالة أي 
                محتوى ينتهك هذه الشروط أو يُعتبر غير مناسب وفقاً لتقديرنا الخاص.
              </p>
            </section>

            <section>
              <h3 className="text-xl font-bold mb-3 text-gray-900">6. الاشتراكات المدفوعة</h3>
              <p className="mb-2">
                نحن نقدم ميزات اشتراك مدفوعة (Gold و Platinum). من خلال الاشتراك:
              </p>
              <ul className="list-disc list-inside space-y-2 mr-4">
                <li>أنت توافق على الرسوم المعلنة في وقت الشراء</li>
                <li>الاشتراكات تتجدد تلقائياً ما لم يتم إلغاؤها</li>
                <li>يمكنك إلغاء الاشتراك في أي وقت من إعدادات حسابك</li>
                <li>لا نقدم استرداداً للمبالغ عن الفترات غير المستخدمة</li>
              </ul>
            </section>

            <section>
              <h3 className="text-xl font-bold mb-3 text-gray-900">7. إنهاء الحساب</h3>
              <p>
                نحتفظ بالحق في تعليق أو إنهاء حسابك في أي وقت، مع أو بدون إشعار، 
                إذا انتهكت هذه الشروط أو لأي سبب آخر وفقاً لتقديرنا الخاص.
              </p>
            </section>

            <section>
              <h3 className="text-xl font-bold mb-3 text-gray-900">8. إخلاء المسؤولية</h3>
              <p>
                يتم توفير Pizoo "كما هو" دون أي ضمانات من أي نوع. نحن لا نضمن أن 
                الخدمة ستكون خالية من الأخطاء أو متاحة دون انقطاع.
              </p>
            </section>

            <section>
              <h3 className="text-xl font-bold mb-3 text-gray-900">9. التعديلات على الشروط</h3>
              <p>
                نحتفظ بالحق في تعديل هذه الشروط في أي وقت. سيتم إخطارك بأي تغييرات جوهرية 
                عبر التطبيق أو البريد الإلكتروني. استمرارك في استخدام الخدمة بعد هذه التغييرات 
                يشكل قبولك للشروط المعدلة.
              </p>
            </section>

            <section>
              <h3 className="text-xl font-bold mb-3 text-gray-900">10. الاتصال بنا</h3>
              <p>
                إذا كان لديك أي أسئلة حول هذه الشروط، يمكنك الاتصال بنا على:
              </p>
              <div className="mt-2 p-4 bg-pink-50 rounded-lg">
                <p className="font-medium">البريد الإلكتروني: support@pizoo.com</p>
                <p className="font-medium">الموقع الإلكتروني: www.pizoo.com</p>
              </div>
            </section>

            <div className="mt-8 pt-6 border-t text-center text-sm text-gray-600">
              <p>آخر تحديث: {new Date().toLocaleDateString('ar-SA')}</p>
              <p className="mt-2">© 2024 Pizoo. جميع الحقوق محفوظة.</p>
            </div>
          </div>
        </Card>
      </main>
    </div>
  );
};

export default Terms;
