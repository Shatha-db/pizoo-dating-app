import React from 'react';
import { useNavigate, useLocation } from 'react-router-dom';
import { Button } from '../components/ui/button';
import { Card } from '../components/ui/card';
import { X } from 'lucide-react';
import { useTranslation } from 'react-i18next';

const TermsNew = () => {
  const navigate = useNavigate();
  const location = useLocation();
  const { t, i18n } = useTranslation('terms');
  
  // Determine which content to show based on URL
  const isPrivacy = location.pathname === '/privacy';
  const isCookies = location.pathname === '/cookies';
  const isTerms = !isPrivacy && !isCookies;
  
  // Get the appropriate title
  const getTitle = () => {
    if (isPrivacy) return t('privacy_title');
    if (isCookies) return t('cookies_title');
    return t('terms_title');
  };

  return (
    <div className="min-h-screen bg-gray-50 pb-20" dir={i18n.language === 'ar' ? 'rtl' : 'ltr'}>
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
          <h1 className="text-xl font-bold">{getTitle()}</h1>
          <div className="w-10"></div>
        </div>
      </header>

      <main className="max-w-4xl mx-auto p-6">
        <Card className="p-8">
          {/* Terms and Conditions */}
          {isTerms && (
            <>
              <h2 className="text-3xl font-bold mb-6 text-center bg-gradient-to-r from-pink-600 to-purple-600 bg-clip-text text-transparent">
                {t('terms.heading')}
              </h2>

              <div className="space-y-6 text-gray-700 leading-relaxed">
                <section>
                  <h3 className="text-xl font-bold mb-3 text-gray-900">{t('terms.section1_title')}</h3>
                  <p>{t('terms.section1_content')}</p>
                </section>

                <section>
                  <h3 className="text-xl font-bold mb-3 text-gray-900">{t('terms.section2_title')}</h3>
                  <p>{t('terms.section2_content')}</p>
                </section>

                <section>
                  <h3 className="text-xl font-bold mb-3 text-gray-900">{t('terms.section3_title')}</h3>
                  <p className="mb-2">{t('terms.section3_content')}</p>
                  <ul className={`list-disc space-y-2 ${i18n.language === 'ar' ? 'list-inside mr-4' : 'list-inside ml-4'}`}>
                    <li>{t('terms.section3_item1')}</li>
                    <li>{t('terms.section3_item2')}</li>
                    <li>{t('terms.section3_item3')}</li>
                    <li>{t('terms.section3_item4')}</li>
                  </ul>
                </section>

                <section>
                  <h3 className="text-xl font-bold mb-3 text-gray-900">{t('terms.section4_title')}</h3>
                  <p className="mb-2">{t('terms.section4_content')}</p>
                  <ul className={`list-disc space-y-2 ${i18n.language === 'ar' ? 'list-inside mr-4' : 'list-inside ml-4'}`}>
                    <li>{t('terms.section4_item1')}</li>
                    <li>{t('terms.section4_item2')}</li>
                    <li>{t('terms.section4_item3')}</li>
                    <li>{t('terms.section4_item4')}</li>
                    <li>{t('terms.section4_item5')}</li>
                    <li>{t('terms.section4_item6')}</li>
                  </ul>
                </section>

                <section>
                  <h3 className="text-xl font-bold mb-3 text-gray-900">{t('terms.section5_title')}</h3>
                  <p>{t('terms.section5_content')}</p>
                </section>

                <section>
                  <h3 className="text-xl font-bold mb-3 text-gray-900">{t('terms.section6_title')}</h3>
                  <p className="mb-2">{t('terms.section6_content')}</p>
                  <ul className={`list-disc space-y-2 ${i18n.language === 'ar' ? 'list-inside mr-4' : 'list-inside ml-4'}`}>
                    <li>{t('terms.section6_item1')}</li>
                    <li>{t('terms.section6_item2')}</li>
                    <li>{t('terms.section6_item3')}</li>
                    <li>{t('terms.section6_item4')}</li>
                  </ul>
                </section>

                <section>
                  <h3 className="text-xl font-bold mb-3 text-gray-900">{t('terms.section7_title')}</h3>
                  <p>{t('terms.section7_content')}</p>
                </section>

                <section>
                  <h3 className="text-xl font-bold mb-3 text-gray-900">{t('terms.section8_title')}</h3>
                  <p>{t('terms.section8_content')}</p>
                </section>

                <section>
                  <h3 className="text-xl font-bold mb-3 text-gray-900">{t('terms.section9_title')}</h3>
                  <p>{t('terms.section9_content')}</p>
                </section>

                <section>
                  <h3 className="text-xl font-bold mb-3 text-gray-900">{t('terms.section10_title')}</h3>
                  <p>{t('terms.section10_content')}</p>
                  <div className="mt-2 p-4 bg-pink-50 rounded-lg">
                    <p className="font-medium">{t('email')}: support@pizoo.ch</p>
                    <p className="font-medium">{t('website')}: www.pizoo.ch</p>
                  </div>
                </section>
              </div>
            </>
          )}

          {/* Privacy Policy */}
          {isPrivacy && (
            <>
              <h2 className="text-3xl font-bold mb-6 text-center bg-gradient-to-r from-pink-600 to-purple-600 bg-clip-text text-transparent">
                {t('privacy.heading')}
              </h2>
              <div className="space-y-6 text-gray-700 leading-relaxed">
                <p className="text-lg">{t('privacy.intro')}</p>
                
                <section>
                  <h3 className="text-xl font-bold mb-3 text-gray-900">{t('privacy.section1_title')}</h3>
                  <p className="mb-2">{t('privacy.section1_content')}</p>
                  <ul className={`list-disc space-y-2 ${i18n.language === 'ar' ? 'list-inside mr-4' : 'list-inside ml-4'}`}>
                    <li>{t('privacy.section1_item1')}</li>
                    <li>{t('privacy.section1_item2')}</li>
                    <li>{t('privacy.section1_item3')}</li>
                    <li>{t('privacy.section1_item4')}</li>
                  </ul>
                </section>

                <section>
                  <h3 className="text-xl font-bold mb-3 text-gray-900">{t('privacy.section2_title')}</h3>
                  <p className="mb-2">{t('privacy.section2_content')}</p>
                  <ul className={`list-disc space-y-2 ${i18n.language === 'ar' ? 'list-inside mr-4' : 'list-inside ml-4'}`}>
                    <li>{t('privacy.section2_item1')}</li>
                    <li>{t('privacy.section2_item2')}</li>
                    <li>{t('privacy.section2_item3')}</li>
                    <li>{t('privacy.section2_item4')}</li>
                  </ul>
                </section>

                <section>
                  <h3 className="text-xl font-bold mb-3 text-gray-900">{t('privacy.section3_title')}</h3>
                  <p className="mb-2">{t('privacy.section3_content')}</p>
                  <ul className={`list-disc space-y-2 ${i18n.language === 'ar' ? 'list-inside mr-4' : 'list-inside ml-4'}`}>
                    <li>{t('privacy.section3_item1')}</li>
                    <li>{t('privacy.section3_item2')}</li>
                    <li>{t('privacy.section3_item3')}</li>
                  </ul>
                </section>

                <section>
                  <h3 className="text-xl font-bold mb-3 text-gray-900">{t('privacy.section4_title')}</h3>
                  <p className="mb-2">{t('privacy.section4_content')}</p>
                  <ul className={`list-disc space-y-2 ${i18n.language === 'ar' ? 'list-inside mr-4' : 'list-inside ml-4'}`}>
                    <li>{t('privacy.section4_item1')}</li>
                    <li>{t('privacy.section4_item2')}</li>
                    <li>{t('privacy.section4_item3')}</li>
                    <li>{t('privacy.section4_item4')}</li>
                  </ul>
                </section>

                <section>
                  <h3 className="text-xl font-bold mb-3 text-gray-900">{t('privacy.section5_title')}</h3>
                  <p>{t('privacy.section5_content')}</p>
                </section>

                <section>
                  <h3 className="text-xl font-bold mb-3 text-gray-900">{t('privacy.section6_title')}</h3>
                  <p>{t('privacy.section6_content')}</p>
                </section>
              </div>
            </>
          )}

          {/* Cookie Policy */}
          {isCookies && (
            <>
              <h2 className="text-3xl font-bold mb-6 text-center bg-gradient-to-r from-pink-600 to-purple-600 bg-clip-text text-transparent">
                {t('cookies.heading')}
              </h2>
              <div className="space-y-6 text-gray-700 leading-relaxed">
                <p className="text-lg">{t('cookies.intro')}</p>
                
                <section>
                  <h3 className="text-xl font-bold mb-3 text-gray-900">{t('cookies.section1_title')}</h3>
                  <p>{t('cookies.section1_content')}</p>
                </section>

                <section>
                  <h3 className="text-xl font-bold mb-3 text-gray-900">{t('cookies.section2_title')}</h3>
                  <ul className={`list-disc space-y-2 ${i18n.language === 'ar' ? 'list-inside mr-4' : 'list-inside ml-4'}`}>
                    <li>{t('cookies.section2_item1')}</li>
                    <li>{t('cookies.section2_item2')}</li>
                    <li>{t('cookies.section2_item3')}</li>
                  </ul>
                </section>

                <section>
                  <h3 className="text-xl font-bold mb-3 text-gray-900">{t('cookies.section3_title')}</h3>
                  <p>{t('cookies.section3_content')}</p>
                </section>

                <section>
                  <h3 className="text-xl font-bold mb-3 text-gray-900">{t('cookies.section4_title')}</h3>
                  <p>{t('cookies.section4_content')}</p>
                </section>
              </div>
            </>
          )}

          {/* Footer */}
          <div className="mt-8 pt-6 border-t text-center text-sm text-gray-600">
            <p>{t('last_updated')}: {new Date().toLocaleDateString(i18n.language)}</p>
            <p className="mt-2">© 2024 Pizoo. {t('all_rights_reserved')}</p>
          </div>
        </Card>
      </main>
    </div>
  );
};

export default TermsNew;
