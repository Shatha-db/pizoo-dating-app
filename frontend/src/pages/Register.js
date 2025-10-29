import React, { useState } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import { Button } from '../components/ui/button';
import { Input } from '../components/ui/input';
import { Label } from '../components/ui/label';
import { Checkbox } from '../components/ui/checkbox';
import { Card, CardContent, CardDescription, CardFooter, CardHeader, CardTitle } from '../components/ui/card';
import { Alert, AlertDescription } from '../components/ui/alert';
import { Phone, Globe } from 'lucide-react';
import CustomLogo from '../components/CustomLogo';
import { useTranslation } from 'react-i18next';

const Register = () => {
  const navigate = useNavigate();
  const { register } = useAuth();
  const { t, i18n } = useTranslation('auth');
  const [formData, setFormData] = useState({
    name: '',
    email: '',
    phoneNumber: '',
    password: '',
    termsAccepted: false
  });
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);
  const [registerMethod, setRegisterMethod] = useState('social'); // social or email
  const [showLanguages, setShowLanguages] = useState(false);

  const changeLanguage = (lng) => {
    i18n.changeLanguage(lng);
    // i18n automatically saves to localStorage as 'i18nextLng'
    // No need for separate 'preferred_language' key
    setShowLanguages(false);
  };

  const handleChange = (e) => {
    const { name, value } = e.target;
    setFormData(prev => ({ ...prev, [name]: value }));
  };

  const handleCheckboxChange = (checked) => {
    setFormData(prev => ({ ...prev, termsAccepted: checked }));
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');

    if (!formData.termsAccepted) {
      setError('يجب الموافقة على الشروط والأحكام');
      return;
    }

    if (formData.password.length < 6) {
      setError('يجب أن تكون كلمة المرور 6 أحرف على الأقل');
      return;
    }

    setLoading(true);
    const result = await register(
      formData.name,
      formData.email,
      formData.phoneNumber,
      formData.password,
      formData.termsAccepted
    );
    setLoading(false);

    if (result.success) {
      // Save current language to backend
      try {
        const token = localStorage.getItem('token');
        const currentLanguage = i18n.language;
        await fetch(`${process.env.REACT_APP_BACKEND_URL}/api/user/language`, {
          method: 'PUT',
          headers: {
            'Authorization': `Bearer ${token}`,
            'Content-Type': 'application/json'
          },
          body: JSON.stringify({ language: currentLanguage })
        });
        console.log('✅ Language saved to backend:', currentLanguage);
      } catch (err) {
        console.error('Failed to save language:', err);
        // Don't block registration flow
      }
      
      navigate('/profile/setup');
    } else {
      setError(result.error);
    }
  };

  const handleAppleSignup = () => {
    alert('التسجيل بواسطة Apple - قريباً! 🍎');
  };

  const handleFacebookSignup = () => {
    alert('التسجيل عبر Facebook - قريباً! 📘');
  };

  const handlePhoneSignup = () => {
    setRegisterMethod('phone');
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-pink-100 via-pink-200 to-rose-200 dark:from-gray-300 dark:via-gray-400 dark:to-gray-500 flex items-center justify-center p-4" dir={i18n.language === 'ar' ? 'rtl' : 'ltr'}>
      {/* Language Selector - Floating Button */}
      <div className="fixed top-4 right-4 z-50">
        <Button
          onClick={() => setShowLanguages(!showLanguages)}
          variant="outline"
          size="icon"
          className="bg-white/90 hover:bg-white shadow-lg"
        >
          <Globe className="w-5 h-5" />
        </Button>
        
        {showLanguages && (
          <div className="absolute top-12 right-0 bg-white rounded-lg shadow-xl p-2 min-w-[150px] space-y-1">
            <button
              onClick={() => changeLanguage('ar')}
              className={`w-full text-right px-4 py-2 rounded-lg transition-colors ${
                i18n.language === 'ar' ? 'bg-pink-500 text-white' : 'hover:bg-gray-100'
              }`}
            >
              🇸🇦 العربية
            </button>
            <button
              onClick={() => changeLanguage('en')}
              className={`w-full text-left px-4 py-2 rounded-lg transition-colors ${
                i18n.language === 'en' ? 'bg-pink-500 text-white' : 'hover:bg-gray-100'
              }`}
            >
              🇬🇧 English
            </button>
            <button
              onClick={() => changeLanguage('fr')}
              className={`w-full text-left px-4 py-2 rounded-lg transition-colors ${
                i18n.language === 'fr' ? 'bg-pink-500 text-white' : 'hover:bg-gray-100'
              }`}
            >
              🇫🇷 Français
            </button>
            <button
              onClick={() => changeLanguage('es')}
              className={`w-full text-left px-4 py-2 rounded-lg transition-colors ${
                i18n.language === 'es' ? 'bg-pink-500 text-white' : 'hover:bg-gray-100'
              }`}
            >
              🇪🇸 Español
            </button>
          </div>
        )}
      </div>

      {/* Logo/Brand */}
      <div className="absolute top-8 left-1/2 transform -translate-x-1/2">
        <CustomLogo size="xl" />
      </div>

      <Card className="w-full max-w-md mt-20 dark:bg-gray-200 backdrop-blur-sm bg-white/90">
        <CardHeader className="text-center pb-2">
          <CardTitle className="text-2xl font-bold dark:text-gray-900 text-pink-700">{t('register_title')}</CardTitle>
          <CardDescription className="text-sm text-gray-700 dark:text-gray-700 mt-3 leading-relaxed">
            {t('terms_notice')}{' '}
            <Link to="/terms" className="text-pink-600 dark:text-pink-700 hover:underline font-medium">
              {t('our_terms')}
            </Link>
            . {t('learn_more')}{' '}
            <Link to="/privacy" className="text-pink-600 dark:text-pink-700 hover:underline font-medium">
              {t('privacy_policy')}
            </Link>
            {' '}{t('and')}{' '}
            <Link to="/cookies" className="text-pink-600 hover:underline font-medium">
              {t('cookie_policy')}
            </Link>
            {' '}.
          </CardDescription>
        </CardHeader>
        
        <CardContent className="space-y-3 pt-4">
          {registerMethod === 'social' ? (
            <>
              {/* Apple Sign Up */}
              <Button
                type="button"
                onClick={handleAppleSignup}
                className="w-full bg-black hover:bg-gray-900 text-white font-medium py-6 rounded-full flex items-center justify-center gap-3"
              >
                <svg className="w-6 h-6" viewBox="0 0 24 24" fill="currentColor">
                  <path d="M17.05 20.28c-.98.95-2.05.8-3.08.35-1.09-.46-2.09-.48-3.24 0-1.44.62-2.2.44-3.06-.35C2.79 15.25 3.51 7.59 9.05 7.31c1.35.07 2.29.74 3.08.8 1.18-.24 2.31-.93 3.57-.84 1.51.12 2.65.72 3.4 1.8-3.12 1.87-2.38 5.98.48 7.13-.57 1.5-1.31 2.99-2.54 4.09l.01-.01zM12.03 7.25c-.15-2.23 1.66-4.07 3.74-4.25.29 2.58-2.34 4.5-3.74 4.25z"/>
                </svg>
                {t('signup_with_apple')}
              </Button>

              {/* Facebook Signup */}
              <Button
                type="button"
                onClick={handleFacebookSignup}
                className="w-full bg-blue-600 hover:bg-blue-700 text-white font-medium py-6 rounded-full flex items-center justify-center gap-3"
              >
                <svg className="w-6 h-6" viewBox="0 0 24 24" fill="currentColor">
                  <path d="M24 12.073c0-6.627-5.373-12-12-12s-12 5.373-12 12c0 5.99 4.388 10.954 10.125 11.854v-8.385H7.078v-3.47h3.047V9.43c0-3.007 1.792-4.669 4.533-4.669 1.312 0 2.686.235 2.686.235v2.953H15.83c-1.491 0-1.956.925-1.956 1.874v2.25h3.328l-.532 3.47h-2.796v8.385C19.612 23.027 24 18.062 24 12.073z"/>
                </svg>
                {t('signup_with_facebook')}
              </Button>

              {/* Phone Number Signup */}
              <Button
                type="button"
                onClick={handlePhoneSignup}
                className="w-full bg-white hover:bg-gray-50 text-gray-900 font-medium py-6 rounded-full flex items-center justify-center gap-3 border-2 border-gray-200"
              >
                <Phone className="w-5 h-5" />
                {t('signup_with_phone')}
              </Button>

              {/* Divider */}
              <div className="relative py-4">
                <div className="absolute inset-0 flex items-center">
                  <div className="w-full border-t border-gray-200"></div>
                </div>
                <div className="relative flex justify-center text-sm">
                  <span className="bg-white px-4 text-gray-500">{t('or')}</span>
                </div>
              </div>

              {/* Email Signup Button */}
              <Button
                type="button"
                onClick={() => setRegisterMethod('email')}
                variant="outline"
                className="w-full py-6 rounded-full font-medium"
              >
                {t('signup_with_email')}
              </Button>
            </>
          ) : registerMethod === 'phone' ? (
            <div className="space-y-4">
              <div className="space-y-2">
                <Label htmlFor="phone" className="text-sm font-medium">{t('phone_number')}</Label>
                <Input
                  id="phone"
                  type="tel"
                  placeholder={t('placeholder_phone_number')}
                  className="h-12 rounded-lg"
                />
              </div>
              <Button
                type="button"
                className="w-full bg-gradient-to-r from-pink-500 to-red-500 hover:from-pink-600 hover:to-red-600 text-white font-bold py-6 rounded-full"
              >
                {t('send_verification_code')}
              </Button>
              <Button
                type="button"
                variant="ghost"
                onClick={() => setRegisterMethod('social')}
                className="w-full"
              >
                {t('back_to_other_methods')}
              </Button>
            </div>
          ) : (
            <form onSubmit={handleSubmit} className="space-y-4">
              {error && (
                <Alert variant="destructive">
                  <AlertDescription>{error}</AlertDescription>
                </Alert>
              )}

              <div className="space-y-2">
                <Label htmlFor="name" className="text-sm font-medium">{t('full_name')}</Label>
                <Input
                  id="name"
                  name="name"
                  type="text"
                  required
                  value={formData.name}
                  onChange={handleChange}
                  placeholder={t('placeholder_full_name')}
                  className="h-12 rounded-lg"
                />
              </div>

              <div className="space-y-2">
                <Label htmlFor="email" className="text-sm font-medium">{t('email')}</Label>
                <Input
                  id="email"
                  name="email"
                  type="email"
                  required
                  value={formData.email}
                  onChange={handleChange}
                  placeholder="example@email.com"
                  className="h-12 rounded-lg"
                />
              </div>

              <div className="space-y-2">
                <Label htmlFor="phoneNumber" className="text-sm font-medium">{t('phone_number')}</Label>
                <Input
                  id="phoneNumber"
                  name="phoneNumber"
                  type="tel"
                  required
                  value={formData.phoneNumber}
                  onChange={handleChange}
                  placeholder={t('placeholder_phone_number')}
                  className="h-12 rounded-lg"
                />
              </div>

              <div className="space-y-2">
                <Label htmlFor="password" className="text-sm font-medium">{t('password')}</Label>
                <Input
                  id="password"
                  name="password"
                  type="password"
                  required
                  value={formData.password}
                  onChange={handleChange}
                  placeholder={t('password_min_6')}
                  className="h-12 rounded-lg"
                />
              </div>

              <div className="flex items-center space-x-2 space-x-reverse">
                <Checkbox
                  id="terms"
                  checked={formData.termsAccepted}
                  onCheckedChange={handleCheckboxChange}
                />
                <label
                  htmlFor="terms"
                  className="text-sm text-gray-700 leading-relaxed cursor-pointer"
                >
                  {t('accept_terms')}{' '}
                  <Link to="/terms" className="text-blue-600 hover:underline font-medium">
                    {t('terms_and_conditions')}
                  </Link>
                </label>
              </div>

              <Button
                type="submit"
                disabled={loading}
                className="w-full bg-gradient-to-r from-pink-500 to-red-500 hover:from-pink-600 hover:to-red-600 text-white font-bold py-6 rounded-full"
              >
                {loading ? t('creating_account') : t('register_title')}
              </Button>

              <Button
                type="button"
                variant="ghost"
                onClick={() => setRegisterMethod('social')}
                className="w-full"
              >
                {t('back_to_other_methods')}
              </Button>
            </form>
          )}
        </CardContent>

        <CardFooter className="flex-col space-y-2 text-center text-sm border-t pt-4">
          <Link
            to="/login"
            className="text-pink-600 hover:text-pink-700 font-medium"
          >
            {t('have_account')} {t('sign_in')}
          </Link>
        </CardFooter>
      </Card>
    </div>
  );
};

export default Register;
