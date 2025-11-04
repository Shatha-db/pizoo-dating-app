import React from 'react';
import { useNavigate } from 'react-router-dom';
import { Button } from '../components/ui/button';
import { Card } from '../components/ui/card';
import { ArrowRight, Heart, Shield, Users, AlertTriangle, ThumbsUp, Ban } from 'lucide-react';
import { useTranslation } from 'react-i18next';

const CommunityGuidelines = () => {
  const navigate = useNavigate();
  const { i18n } = useTranslation();
  const isRTL = i18n.language === 'ar';

  const guidelines = [
    {
      icon: <Heart className="w-6 h-6 text-pink-500" />,
      title: isRTL ? 'كن محترماً' : 'Be Respectful',
      description: isRTL 
        ? 'عامل الآخرين بلطف واحترام. لا تستخدم لغة مسيئة أو تمييزية.'
        : 'Treat others with kindness and respect. Don\'t use abusive or discriminatory language.',
      color: 'pink'
    },
    {
      icon: <Shield className="w-6 h-6 text-green-500" />,
      title: isRTL ? 'كن صادقاً' : 'Be Authentic',
      description: isRTL
        ? 'استخدم صورك الحقيقية ومعلوماتك الصحيحة. لا تنتحل شخصية أي شخص آخر.'
        : 'Use your real photos and accurate information. Don\'t impersonate anyone else.',
      color: 'green'
    },
    {
      icon: <Users className="w-6 h-6 text-blue-500" />,
      title: isRTL ? 'كن آمناً' : 'Stay Safe',
      description: isRTL
        ? 'لا تشارك معلوماتك الشخصية (عنوان، حساب بنكي) مع أشخاص لا تعرفهم جيداً.'
        : 'Don\'t share personal information (address, bank details) with people you don\'t know well.',
      color: 'blue'
    },
    {
      icon: <ThumbsUp className="w-6 h-6 text-purple-500" />,
      title: isRTL ? 'كن إيجابياً' : 'Be Positive',
      description: isRTL
        ? 'حافظ على الأجواء الإيجابية. إذا لم تكن مهتماً بشخص ما، كن لطيفاً في الرفض.'
        : 'Keep the atmosphere positive. If you\'re not interested in someone, be kind in declining.',
      color: 'purple'
    }
  ];

  const prohibitedContent = [
    isRTL ? 'محتوى جنسي صريح أو مسيء' : 'Explicit sexual or offensive content',
    isRTL ? 'خطاب الكراهية أو التمييز' : 'Hate speech or discrimination',
    isRTL ? 'التحرش أو التنمر' : 'Harassment or bullying',
    isRTL ? 'العنف أو التهديدات' : 'Violence or threats',
    isRTL ? 'الإعلانات أو الترويج التجاري' : 'Spam or commercial promotion',
    isRTL ? 'المعلومات المضللة' : 'Misinformation',
    isRTL ? 'انتهاك الخصوصية' : 'Privacy violations'
  ];

  return (
    <div className="min-h-screen bg-gray-50 pb-20" dir={isRTL ? 'rtl' : 'ltr'}>
      {/* Header */}
      <header className="bg-gradient-to-r from-purple-500 to-pink-500 text-white p-4 shadow-lg sticky top-0 z-10">
        <div className="max-w-4xl mx-auto flex items-center gap-4">
          <Button
            variant="ghost"
            size="icon"
            onClick={() => navigate(-1)}
            className="text-white hover:bg-white/20"
          >
            <ArrowRight className={`w-6 h-6 ${isRTL ? '' : 'rotate-180'}`} />
          </Button>
          <h1 className="text-xl font-bold">
            {isRTL ? 'إرشادات المجتمع' : 'Community Guidelines'}
          </h1>
        </div>
      </header>

      <main className="max-w-4xl mx-auto p-6 space-y-6">
        {/* Introduction */}
        <Card className="p-6">
          <h2 className="text-2xl font-bold mb-4 bg-gradient-to-r from-purple-600 to-pink-600 bg-clip-text text-transparent">
            {isRTL ? 'مرحباً بك في مجتمع Pizoo!' : 'Welcome to the Pizoo Community!'}
          </h2>
          <p className="text-gray-700 leading-relaxed">
            {isRTL
              ? 'نحن ملتزمون بتوفير بيئة آمنة وودية لجميع المستخدمين. يرجى قراءة هذه الإرشادات بعناية واتباعها لضمان تجربة إيجابية للجميع.'
              : 'We\'re committed to providing a safe and friendly environment for all users. Please read these guidelines carefully and follow them to ensure a positive experience for everyone.'}
          </p>
        </Card>

        {/* Guidelines */}
        <Card className="p-6">
          <h2 className="text-xl font-bold mb-6">
            {isRTL ? 'قواعدنا الأساسية' : 'Our Core Values'}
          </h2>
          
          <div className="space-y-4">
            {guidelines.map((guideline, index) => (
              <div
                key={index}
                className={`p-4 bg-${guideline.color}-50 rounded-xl border border-${guideline.color}-100`}
              >
                <div className="flex items-start gap-4">
                  <div className={`p-3 bg-white rounded-lg shadow-sm`}>
                    {guideline.icon}
                  </div>
                  <div className={`flex-1 ${isRTL ? 'text-right' : 'text-left'}`}>
                    <h3 className="font-bold text-lg mb-2">{guideline.title}</h3>
                    <p className="text-gray-700">{guideline.description}</p>
                  </div>
                </div>
              </div>
            ))}
          </div>
        </Card>

        {/* Prohibited Content */}
        <Card className="p-6 border-2 border-red-200 bg-red-50">
          <div className="flex items-center gap-3 mb-4">
            <Ban className="w-8 h-8 text-red-500" />
            <h2 className="text-xl font-bold text-red-900">
              {isRTL ? 'المحتوى المحظور' : 'Prohibited Content'}
            </h2>
          </div>
          
          <p className="text-gray-700 mb-4">
            {isRTL
              ? 'المحتوى التالي محظور بشكل صارم على Pizoo:'
              : 'The following content is strictly prohibited on Pizoo:'}
          </p>
          
          <ul className={`space-y-2 ${isRTL ? 'list-inside mr-4' : 'list-inside ml-4'}`}>
            {prohibitedContent.map((item, index) => (
              <li key={index} className="flex items-start gap-2">
                <span className="text-red-500 mt-1">✗</span>
                <span className="flex-1 text-gray-700">{item}</span>
              </li>
            ))}
          </ul>
        </Card>

        {/* Reporting */}
        <Card className="p-6">
          <div className="flex items-center gap-3 mb-4">
            <AlertTriangle className="w-8 h-8 text-orange-500" />
            <h2 className="text-xl font-bold">
              {isRTL ? 'الإبلاغ عن المخالفات' : 'Report Violations'}
            </h2>
          </div>
          
          <p className="text-gray-700 mb-4">
            {isRTL
              ? 'إذا رأيت محتوى أو سلوكاً ينتهك هذه الإرشادات، يرجى الإبلاغ عنه فوراً. نحن نأخذ جميع التقارير على محمل الجد ونتخذ الإجراءات المناسبة.'
              : 'If you see content or behavior that violates these guidelines, please report it immediately. We take all reports seriously and will take appropriate action.'}
          </p>
          
          <Button
            className="w-full bg-gradient-to-r from-orange-500 to-red-500 hover:from-orange-600 hover:to-red-600 text-white"
            onClick={() => navigate('/help')}
          >
            {isRTL ? 'الإبلاغ عن مشكلة' : 'Report an Issue'}
          </Button>
        </Card>

        {/* Consequences */}
        <Card className="p-6 bg-gray-100">
          <h2 className="text-xl font-bold mb-4">
            {isRTL ? 'عواقب المخالفة' : 'Consequences of Violation'}
          </h2>
          
          <p className="text-gray-700">
            {isRTL
              ? 'انتهاك هذه الإرشادات قد يؤدي إلى: تحذير، تعليق مؤقت للحساب، أو حظر دائم من Pizoo. نحتفظ بالحق في اتخاذ الإجراء المناسب حسب شدة المخالفة.'
              : 'Violation of these guidelines may result in: a warning, temporary account suspension, or permanent ban from Pizoo. We reserve the right to take appropriate action based on the severity of the violation.'}
          </p>
        </Card>
      </main>
    </div>
  );
};

export default CommunityGuidelines;
