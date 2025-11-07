import React, { useState } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import { Button } from '../components/ui/button';
import { Input } from '../components/ui/input';
import { Label } from '../components/ui/label';
import { Checkbox } from '../components/ui/checkbox';
import { Card, CardContent, CardDescription, CardFooter, CardHeader, CardTitle } from '../components/ui/card';
import { Alert, AlertDescription } from '../components/ui/alert';
import { LogIn, Eye, EyeOff, Mail, Phone } from 'lucide-react';
import CustomLogo from '../components/CustomLogo';
import CountryCodeSelect from '../components/CountryCodeSelect';
import { useTranslation } from 'react-i18next';
import LanguageSelector from '../modules/i18n/LanguageSelector';
import axios from 'axios';

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;

const Login = () => {
  const navigate = useNavigate();
  const { login } = useAuth();
  const { t } = useTranslation('auth'); // Load auth namespace
  const [formData, setFormData] = useState({
    email: '',
    phoneNumber: '',
    password: '',
    rememberMe: false
  });
  const [countryCode, setCountryCode] = useState('+966'); // Default to Saudi Arabia
  const [loginMethod, setLoginMethod] = useState('email'); // 'email' or 'phone'
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);
  const [showPassword, setShowPassword] = useState(false); // ✅ Password visibility state

  const handleChange = (e) => {
    const { name, value } = e.target;
    setFormData(prev => ({ ...prev, [name]: value }));
  };

  const handleCheckboxChange = (checked) => {
    setFormData(prev => ({ ...prev, rememberMe: checked }));
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');
    setLoading(true);

    // Determine the login identifier (email or phone with country code)
    const identifier = loginMethod === 'phone' 
      ? `${countryCode}${formData.phoneNumber}`
      : formData.email;

    const result = await login(identifier, formData.password);

    if (result.success) {
      // Save remember me preference
      if (formData.rememberMe) {
        localStorage.setItem('rememberMe', 'true');
      }
      
      // Check if user has a profile
      try {
        const profileResponse = await axios.get(`${BACKEND_URL}/api/profile/me`, {
          headers: {
            Authorization: `Bearer ${result.token}`
          }
        });
        
        // If profile exists, go to home
        if (profileResponse.data && profileResponse.data.display_name) {
          navigate('/home');
        } else {
          // If no profile, go to profile setup
          navigate('/profile/setup');
        }
      } catch (error) {
        // If profile doesn't exist (404), go to profile setup
        if (error.response?.status === 404) {
          navigate('/profile/setup');
        } else {
          // For other errors, still go to home
          navigate('/home');
        }
      }
    } else {
      setError(result.error);
    }
    
    setLoading(false);
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-pink-500 via-red-500 to-orange-500 dark:from-gray-300 dark:via-gray-400 dark:to-gray-500 flex items-center justify-center p-4">
      {/* Language Selector - Floating */}
      <div className="fixed top-4 right-4 z-50">
        <LanguageSelector variant="compact" />
      </div>

      {/* Logo/Brand */}
      <div className="absolute top-8 left-1/2 transform -translate-x-1/2">
        <CustomLogo size="xl" />
      </div>

      <Card className="w-full max-w-md mt-20 dark:bg-gray-200" data-testid="login-card">
        <CardHeader className="text-center">
          <CardTitle className="text-2xl font-bold dark:text-gray-900">{t('login_title')}</CardTitle>
          <CardDescription className="text-gray-600 dark:text-gray-700">
            {t('welcome_back')}
          </CardDescription>
        </CardHeader>
        
        <CardContent>
          <form onSubmit={handleSubmit} className="space-y-4">
            {error && (
              <Alert variant="destructive" data-testid="error-alert">
                <AlertDescription>
                  {typeof error === 'string' ? error : JSON.stringify(error)}
                </AlertDescription>
              </Alert>
            )}

            {/* Login Method Toggle */}
            <div className="flex gap-2 p-1 bg-gray-100 rounded-lg">
              <button
                type="button"
                onClick={() => setLoginMethod('email')}
                className={`flex-1 flex items-center justify-center gap-2 py-2 px-4 rounded-md transition-all ${
                  loginMethod === 'email'
                    ? 'bg-white text-pink-600 shadow-sm font-medium'
                    : 'text-gray-600 hover:text-gray-900'
                }`}
              >
                <Mail className="w-4 h-4" />
                {t('email')}
              </button>
              <button
                type="button"
                onClick={() => setLoginMethod('phone')}
                className={`flex-1 flex items-center justify-center gap-2 py-2 px-4 rounded-md transition-all ${
                  loginMethod === 'phone'
                    ? 'bg-white text-pink-600 shadow-sm font-medium'
                    : 'text-gray-600 hover:text-gray-900'
                }`}
              >
                <Phone className="w-4 h-4" />
                {t('phone')}
              </button>
            </div>

            {/* Email or Phone Input */}
            {loginMethod === 'email' ? (
              <div className="space-y-2">
                <Label htmlFor="email" className="text-sm font-medium">
                  {t('email')}
                </Label>
                <Input
                  id="email"
                  name="email"
                  type="email"
                  required
                  value={formData.email}
                  onChange={handleChange}
                  placeholder={t('placeholder_email')}
                  className="h-12 rounded-lg"
                  data-testid="email-input"
                />
              </div>
            ) : (
              <div className="space-y-2">
                <Label htmlFor="phone" className="text-sm font-medium">
                  {t('phone_number')}
                </Label>
                <div className="flex gap-2">
                  <CountryCodeSelect 
                    value={countryCode} 
                    onChange={setCountryCode}
                    className="w-auto"
                  />
                  <Input
                    id="phoneNumber"
                    name="phoneNumber"
                    type="tel"
                    required
                    value={formData.phoneNumber}
                    onChange={handleChange}
                    placeholder="501234567"
                    className="flex-1 h-12 rounded-lg"
                    data-testid="phone-input"
                  />
                </div>
              </div>
            )}

            <div className="space-y-2">
              <Label htmlFor="password" className="text-sm font-medium">
                {t('password')}
              </Label>
              <div className="relative">
                <Input
                  id="password"
                  name="password"
                  type={showPassword ? "text" : "password"}
                  required
                  value={formData.password}
                  onChange={handleChange}
                  placeholder={t('placeholder_password')}
                  className="h-12 rounded-lg pr-10"
                  data-testid="password-input"
                />
                <button
                  type="button"
                  onClick={() => setShowPassword(!showPassword)}
                  className="absolute right-3 top-1/2 -translate-y-1/2 text-gray-500 hover:text-gray-700 transition-colors"
                  aria-label={showPassword ? "Hide password" : "Show password"}
                >
                  {showPassword ? <EyeOff className="w-5 h-5" /> : <Eye className="w-5 h-5" />}
                </button>
              </div>
            </div>

            {/* Remember Me Checkbox */}
            <div className="flex items-center space-x-2 space-x-reverse">
              <Checkbox
                id="rememberMe"
                checked={formData.rememberMe}
                onCheckedChange={handleCheckboxChange}
              />
              <label
                htmlFor="rememberMe"
                className="text-sm text-gray-700 cursor-pointer"
              >
                {t('remember_me')}
              </label>
            </div>

            <Button
              type="submit"
              disabled={loading}
              className="w-full bg-gradient-to-r from-pink-500 to-red-500 hover:from-pink-600 hover:to-red-600 text-white font-bold py-6 rounded-full"
              data-testid="submit-button"
            >
              {loading ? `${t('sign_in')}...` : t('sign_in')}
            </Button>
          </form>
        </CardContent>

        <CardFooter className="flex-col space-y-3 text-center text-sm border-t pt-4">
          <Link
            to="/forgot-password"
            className="text-gray-600 hover:text-gray-800"
          >
            {t('forgot_password')}
          </Link>
          <Link
            to="/register"
            className="text-pink-600 hover:text-pink-700 font-medium"
            data-testid="register-link"
          >
            {t('no_account')} {t('register_now')} 💕
          </Link>
        </CardFooter>
      </Card>
    </div>
  );
};

export default Login;
