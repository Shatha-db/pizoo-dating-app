import React from 'react';
import { useNavigate } from 'react-router-dom';
import { Button } from '../components/ui/button';
import { Card } from '../components/ui/card';
import { ArrowRight, Shield, Lock, Eye, AlertCircle, Phone, MapPin, UserX } from 'lucide-react';
import { useTranslation } from 'react-i18next';

const SafetyCenter = () => {
  const navigate = useNavigate();
  const { i18n } = useTranslation();
  const isRTL = i18n.language === 'ar';

  const safetyTips = [
    {
      icon: <Eye className="w-6 h-6 text-blue-500" />,
      title: isRTL ? 'احذر من الاحتيال' : 'Watch for Scams',
      description: isRTL
        ? 'لا ترسل أموالاً أو معلومات مالية لأي شخص. كن حذراً من الطلبات المشبوهة.'
        : 'Never send money or financial information to anyone. Be wary of suspicious requests.'
    },
    {
      icon: <Lock className="w-6 h-6 text-green-500" />,
      title: isRTL ? 'احمِ معلوماتك الشخصية' : 'Protect Personal Info',
      description: isRTL
        ? 'لا تشارك عنوانك، رقم هاتفك، أو معلومات حساسة مع أشخاص لا تثق بهم.'
        : 'Don\'t share your address, phone number, or sensitive information with people you don\'t trust.'
    },
    {
      icon: <MapPin className="w-6 h-6 text-purple-500" />,
      title: isRTL ? 'التقِ في أماكن عامة' : 'Meet in Public Places',
      description: isRTL
        ? 'عند اللقاء الأول، اختر مكاناً عاماً ومزدحماً وأخبر صديقاً بمكانك.'
        : 'For first meetings, choose a public, crowded place and tell a friend where you\'ll be.'
    },
    {
      icon: <Phone className="w-6 h-6 text-orange-500" />,
      title: isRTL ? 'أخبر شخصاً تثق به' : 'Tell Someone You Trust',
      description: isRTL
        ? 'دع صديقاً أو فرداً من العائلة يعرف متى وأين ستلتقي بشخص جديد.'
        : 'Let a friend or family member know when and where you\'re meeting someone new.'
    },
    {
      icon: <UserX className="w-6 h-6 text-red-500" />,
      title: isRTL ? 'ثق بحدسك' : 'Trust Your Instincts',
      description: isRTL
        ? 'إذا شعرت بعدم الارتياح، غادر فوراً. سلامتك أهم من أي شيء.'
        : 'If something feels wrong, leave immediately. Your safety is more important than anything.'
    }
  ];

  const resources = [
    {
      title: isRTL ? 'خط ساخن للطوارئ' : 'Emergency Hotline',
      number: isRTL ? '٩١١' : '911',
      description: isRTL ? 'للحالات الطارئة فقط' : 'For emergencies only',
      color: 'red'
    },
    {
      title: isRTL ? 'دعم الأزمات' : 'Crisis Support',
      number: isRTL ? '٩٢٠٠٣٣٧٧٧' : '920033777',
      description: isRTL ? 'دعم نفسي 24/7' : '24/7 mental health support',
      color: 'blue'
    },
    {
      title: isRTL ? 'دعم PiZOO' : 'PiZOO Support',
      number: 'support@pizoo.ch',
      description: isRTL ? 'للإبلاغ عن مشاكل الأمان' : 'Report safety concerns',
      color: 'purple'
    }
  ];

  return (
    <div className="min-h-screen bg-gray-50 pb-20" dir={isRTL ? 'rtl' : 'ltr'}>
      {/* Header */}
      <header className="bg-gradient-to-r from-green-500 to-blue-500 text-white p-4 shadow-lg sticky top-0 z-10">
        <div className="max-w-4xl mx-auto flex items-center gap-4">
          <Button
            variant="ghost"
            size="icon"
            onClick={() => navigate(-1)}
            className="text-white hover:bg-white/20"
          >
            <ArrowRight className={`w-6 h-6 ${isRTL ? '' : 'rotate-180'}`} />
          </Button>
          <div className="flex items-center gap-3">
            <Shield className="w-6 h-6" />
            <h1 className="text-xl font-bold">
              {isRTL ? 'مركز الأمان' : 'Safety Center'}
            </h1>
          </div>
        </div>
      </header>

      <main className="max-w-4xl mx-auto p-6 space-y-6">
        {/* Introduction */}
        <Card className="p-6 bg-gradient-to-r from-green-50 to-blue-50">
          <h2 className="text-2xl font-bold mb-4 bg-gradient-to-r from-green-600 to-blue-600 bg-clip-text text-transparent">
            {isRTL ? 'سلامتك أولويتنا' : 'Your Safety is Our Priority'}
          </h2>
          <p className="text-gray-700 leading-relaxed">
            {isRTL
              ? 'في Pizoo، نلتزم بتوفير بيئة آمنة لجميع مستخدمينا. يرجى قراءة نصائح الأمان هذه والحفاظ على يقظتك أثناء استخدام التطبيق.'
              : 'At Pizoo, we\'re committed to providing a safe environment for all our users. Please read these safety tips and stay vigilant while using the app.'}
          </p>
        </Card>

        {/* Safety Tips */}
        <Card className="p-6">
          <h2 className="text-xl font-bold mb-6 flex items-center gap-2">
            <AlertCircle className="w-6 h-6 text-orange-500" />
            <span>{isRTL ? 'نصائح السلامة' : 'Safety Tips'}</span>
          </h2>
          
          <div className="space-y-4">
            {safetyTips.map((tip, index) => (
              <div
                key={index}
                className="p-4 border border-gray-200 rounded-xl hover:border-blue-300 hover:shadow-md transition-all"
              >
                <div className="flex items-start gap-4">
                  <div className="p-3 bg-gray-50 rounded-lg">
                    {tip.icon}
                  </div>
                  <div className={`flex-1 ${isRTL ? 'text-right' : 'text-left'}`}>
                    <h3 className="font-bold text-lg mb-2">{tip.title}</h3>
                    <p className="text-gray-700">{tip.description}</p>
                  </div>
                </div>
              </div>
            ))}
          </div>
        </Card>

        {/* Emergency Resources */}
        <Card className="p-6">
          <h2 className="text-xl font-bold mb-6">
            {isRTL ? 'موارد الطوارئ' : 'Emergency Resources'}
          </h2>
          
          <div className="space-y-4">
            {resources.map((resource, index) => (
              <a
                key={index}
                href={resource.number.includes('@') ? `mailto:${resource.number}` : `tel:${resource.number}`}
                className={`block p-4 bg-${resource.color}-50 border-2 border-${resource.color}-200 rounded-xl hover:bg-${resource.color}-100 transition-colors`}
              >
                <div className={`flex items-center justify-between ${isRTL ? 'flex-row-reverse' : ''}`}>
                  <div className={isRTL ? 'text-right' : 'text-left'}>
                    <h3 className="font-bold text-lg">{resource.title}</h3>
                    <p className="text-sm text-gray-600">{resource.description}</p>
                  </div>
                  <div className={`text-2xl font-bold text-${resource.color}-600`}>
                    {resource.number}
                  </div>
                </div>
              </a>
            ))}
          </div>
        </Card>

        {/* Report Concerns */}
        <Card className="p-6 bg-red-50 border-2 border-red-200">
          <h2 className="text-xl font-bold mb-4 text-red-900">
            {isRTL ? 'الإبلاغ عن مخاوف الأمان' : 'Report Safety Concerns'}
          </h2>
          
          <p className="text-gray-700 mb-4">
            {isRTL
              ? 'إذا واجهت أي سلوك مشبوه أو شعرت بالتهديد، يرجى الإبلاغ عنه فوراً. نحن نأخذ جميع المخاوف الأمنية على محمل الجد.'
              : 'If you encounter any suspicious behavior or feel threatened, please report it immediately. We take all safety concerns seriously.'}
          </p>
          
          <div className="space-y-2">
            <Button
              className="w-full bg-red-600 hover:bg-red-700 text-white"
              onClick={() => navigate('/help')}
            >
              {isRTL ? 'الإبلاغ عن مستخدم' : 'Report a User'}
            </Button>
            <Button
              variant="outline"
              className="w-full border-red-600 text-red-600 hover:bg-red-50"
              onClick={() => navigate('/help')}
            >
              {isRTL ? 'حظر مستخدم' : 'Block a User'}
            </Button>
          </div>
        </Card>

        {/* Additional Resources */}
        <Card className="p-6 bg-gray-100">
          <h2 className="text-xl font-bold mb-4">
            {isRTL ? 'موارد إضافية' : 'Additional Resources'}
          </h2>
          
          <div className="space-y-2">
            <button
              onClick={() => navigate('/community')}
              className="w-full text-left p-3 hover:bg-white rounded-lg text-blue-600"
            >
              {isRTL ? '← إرشادات المجتمع' : 'Community Guidelines →'}
            </button>
            <button
              onClick={() => navigate('/privacy')}
              className="w-full text-left p-3 hover:bg-white rounded-lg text-blue-600"
            >
              {isRTL ? '← سياسة الخصوصية' : 'Privacy Policy →'}
            </button>
            <button
              onClick={() => navigate('/terms')}
              className="w-full text-left p-3 hover:bg-white rounded-lg text-blue-600"
            >
              {isRTL ? '← الشروط والأحكام' : 'Terms & Conditions →'}
            </button>
          </div>
        </Card>
      </main>
    </div>
  );
};

export default SafetyCenter;
