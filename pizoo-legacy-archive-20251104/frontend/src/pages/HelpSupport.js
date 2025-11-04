import React from 'react';
import { useNavigate } from 'react-router-dom';
import { Button } from '../components/ui/button';
import { Card } from '../components/ui/card';
import { ArrowRight, Mail, Phone, MessageCircle, HelpCircle, BookOpen, AlertCircle } from 'lucide-react';
import { useTranslation } from 'react-i18next';

const HelpSupport = () => {
  const navigate = useNavigate();
  const { t, i18n } = useTranslation(['settings', 'common']);
  const isRTL = i18n.language === 'ar';

  const helpTopics = [
    {
      icon: <HelpCircle className="w-6 h-6 text-blue-500" />,
      title: isRTL ? 'الأسئلة الشائعة' : 'Frequently Asked Questions',
      description: isRTL ? 'إجابات للأسئلة الشائعة' : 'Answers to common questions',
      action: () => {}
    },
    {
      icon: <BookOpen className="w-6 h-6 text-purple-500" />,
      title: isRTL ? 'دليل الاستخدام' : 'User Guide',
      description: isRTL ? 'تعلم كيفية استخدام التطبيق' : 'Learn how to use the app',
      action: () => {}
    },
    {
      icon: <AlertCircle className="w-6 h-6 text-orange-500" />,
      title: isRTL ? 'الإبلاغ عن مشكلة' : 'Report an Issue',
      description: isRTL ? 'أخبرنا عن أي مشكلة تواجهها' : 'Let us know about any problems',
      action: () => {}
    }
  ];

  return (
    <div className="min-h-screen bg-gray-50 pb-20" dir={isRTL ? 'rtl' : 'ltr'}>
      {/* Header */}
      <header className="bg-gradient-to-r from-pink-500 to-purple-500 text-white p-4 shadow-lg sticky top-0 z-10">
        <div className="max-w-4xl mx-auto flex items-center gap-4">
          <Button
            variant="ghost"
            size="icon"
            onClick={() => navigate(-1)}
            className="text-white hover:bg-white/20"
          >
            <ArrowRight className={`w-6 h-6 ${isRTL ? '' : 'rotate-180'}`} />
          </Button>
          <h1 className="text-xl font-bold">{isRTL ? 'المساعدة والدعم' : 'Help & Support'}</h1>
        </div>
      </header>

      <main className="max-w-4xl mx-auto p-6 space-y-6">
        {/* Help Topics */}
        <Card className="p-6">
          <h2 className="text-2xl font-bold mb-6 bg-gradient-to-r from-pink-600 to-purple-600 bg-clip-text text-transparent">
            {isRTL ? 'كيف يمكننا مساعدتك؟' : 'How can we help you?'}
          </h2>
          
          <div className="space-y-4">
            {helpTopics.map((topic, index) => (
              <button
                key={index}
                onClick={topic.action}
                className="w-full p-4 border border-gray-200 rounded-xl hover:border-pink-500 hover:shadow-md transition-all group"
              >
                <div className="flex items-start gap-4">
                  <div className="p-3 bg-gray-50 rounded-lg group-hover:bg-pink-50 transition-colors">
                    {topic.icon}
                  </div>
                  <div className={`flex-1 ${isRTL ? 'text-right' : 'text-left'}`}>
                    <h3 className="font-bold text-lg mb-1">{topic.title}</h3>
                    <p className="text-gray-600 text-sm">{topic.description}</p>
                  </div>
                  <ArrowRight className={`w-5 h-5 text-gray-400 group-hover:text-pink-500 transition-colors ${isRTL ? '' : 'rotate-180'}`} />
                </div>
              </button>
            ))}
          </div>
        </Card>

        {/* Contact Us */}
        <Card className="p-6">
          <h2 className="text-xl font-bold mb-6">
            {isRTL ? 'اتصل بنا' : 'Contact Us'}
          </h2>
          
          <div className="space-y-4">
            <a
              href="mailto:support@pizoo.com"
              className="flex items-center gap-4 p-4 bg-blue-50 rounded-xl hover:bg-blue-100 transition-colors"
            >
              <Mail className="w-6 h-6 text-blue-500" />
              <div className={isRTL ? 'text-right' : 'text-left'}>
                <div className="font-medium">{isRTL ? 'البريد الإلكتروني' : 'Email'}</div>
                <div className="text-sm text-gray-600">support@pizoo.com</div>
              </div>
            </a>

            <a
              href="tel:+966123456789"
              className="flex items-center gap-4 p-4 bg-green-50 rounded-xl hover:bg-green-100 transition-colors"
            >
              <Phone className="w-6 h-6 text-green-500" />
              <div className={isRTL ? 'text-right' : 'text-left'}>
                <div className="font-medium">{isRTL ? 'الهاتف' : 'Phone'}</div>
                <div className="text-sm text-gray-600">+966 12 345 6789</div>
              </div>
            </a>

            <button className="w-full flex items-center gap-4 p-4 bg-purple-50 rounded-xl hover:bg-purple-100 transition-colors">
              <MessageCircle className="w-6 h-6 text-purple-500" />
              <div className={`flex-1 ${isRTL ? 'text-right' : 'text-left'}`}>
                <div className="font-medium">{isRTL ? 'الدردشة المباشرة' : 'Live Chat'}</div>
                <div className="text-sm text-gray-600">
                  {isRTL ? 'تحدث مع فريق الدعم' : 'Chat with support team'}
                </div>
              </div>
            </button>
          </div>
        </Card>

        {/* Quick Links */}
        <Card className="p-6">
          <h2 className="text-xl font-bold mb-4">
            {isRTL ? 'روابط سريعة' : 'Quick Links'}
          </h2>
          
          <div className="space-y-2">
            <button
              onClick={() => navigate('/terms')}
              className="w-full text-left p-3 hover:bg-gray-50 rounded-lg text-blue-600"
            >
              {isRTL ? '← الشروط والأحكام' : 'Terms & Conditions →'}
            </button>
            <button
              onClick={() => navigate('/privacy')}
              className="w-full text-left p-3 hover:bg-gray-50 rounded-lg text-blue-600"
            >
              {isRTL ? '← سياسة الخصوصية' : 'Privacy Policy →'}
            </button>
            <button
              onClick={() => navigate('/community')}
              className="w-full text-left p-3 hover:bg-gray-50 rounded-lg text-blue-600"
            >
              {isRTL ? '← إرشادات المجتمع' : 'Community Guidelines →'}
            </button>
          </div>
        </Card>
      </main>
    </div>
  );
};

export default HelpSupport;
