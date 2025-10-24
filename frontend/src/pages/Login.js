import React, { useState } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import { Button } from '../components/ui/button';
import { Input } from '../components/ui/input';
import { Label } from '../components/ui/label';
import { Card, CardContent, CardDescription, CardFooter, CardHeader, CardTitle } from '../components/ui/card';
import { Alert, AlertDescription } from '../components/ui/alert';
import { LogIn, Phone } from 'lucide-react';

const Login = () => {
  const navigate = useNavigate();
  const { login } = useAuth();
  const [formData, setFormData] = useState({
    email: '',
    password: ''
  });
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);
  const [loginMethod, setLoginMethod] = useState('email'); // email, phone

  const handleChange = (e) => {
    const { name, value } = e.target;
    setFormData(prev => ({ ...prev, [name]: value }));
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');
    setLoading(true);

    const result = await login(formData.email, formData.password);
    setLoading(false);

    if (result.success) {
      navigate('/home');
    } else {
      setError(result.error);
    }
  };

  const handleAppleLogin = () => {
    // TODO: Implement Apple Sign In
    alert('تسجيل الدخول بواسطة Apple - قريباً! 🍎');
  };

  const handleFacebookLogin = () => {
    // TODO: Implement Facebook Login
    alert('تسجيل الدخول عبر Facebook - قريباً! 📘');
  };

  const handlePhoneLogin = () => {
    setLoginMethod('phone');
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-pink-500 via-red-500 to-orange-500 flex items-center justify-center p-4" dir="rtl">
      {/* Logo/Brand */}
      <div className="absolute top-8 left-1/2 transform -translate-x-1/2">
        <h1 className="text-6xl font-bold text-white drop-shadow-lg">❤️‍🔥 Pizoo</h1>
      </div>

      <Card className="w-full max-w-md mt-20" data-testid="login-card">
        <CardHeader className="text-center pb-2">
          <CardTitle className="text-2xl font-bold">تسجيل الدخول</CardTitle>
          <CardDescription className="text-sm text-gray-600">
            من خلال النقر على "إنشاء حساب" أو "تسجيل الدخول"، فإنك توافق على شروطنا. تعرّف على طريقة تعاملنا مع بياناتك في سياسة الخصوصية وسياسة ملفات تعريف الارتباط الخاصة بنا.
          </CardDescription>
        </CardHeader>
        
        <CardContent className="space-y-3 pt-4">
          {/* Apple Sign In */}
          <Button
            type="button"
            onClick={handleAppleLogin}
            className="w-full bg-black hover:bg-gray-900 text-white font-medium py-6 rounded-full flex items-center justify-center gap-3"
          >
            <svg className="w-6 h-6" viewBox="0 0 24 24" fill="currentColor">
              <path d="M17.05 20.28c-.98.95-2.05.8-3.08.35-1.09-.46-2.09-.48-3.24 0-1.44.62-2.2.44-3.06-.35C2.79 15.25 3.51 7.59 9.05 7.31c1.35.07 2.29.74 3.08.8 1.18-.24 2.31-.93 3.57-.84 1.51.12 2.65.72 3.4 1.8-3.12 1.87-2.38 5.98.48 7.13-.57 1.5-1.31 2.99-2.54 4.09l.01-.01zM12.03 7.25c-.15-2.23 1.66-4.07 3.74-4.25.29 2.58-2.34 4.5-3.74 4.25z"/>
            </svg>
            تسجيل الدخول باستخدام Apple
          </Button>

          {/* Facebook Login */}
          <Button
            type="button"
            onClick={handleFacebookLogin}
            className="w-full bg-blue-600 hover:bg-blue-700 text-white font-medium py-6 rounded-full flex items-center justify-center gap-3"
          >
            <svg className="w-6 h-6" viewBox="0 0 24 24" fill="currentColor">
              <path d="M24 12.073c0-6.627-5.373-12-12-12s-12 5.373-12 12c0 5.99 4.388 10.954 10.125 11.854v-8.385H7.078v-3.47h3.047V9.43c0-3.007 1.792-4.669 4.533-4.669 1.312 0 2.686.235 2.686.235v2.953H15.83c-1.491 0-1.956.925-1.956 1.874v2.25h3.328l-.532 3.47h-2.796v8.385C19.612 23.027 24 18.062 24 12.073z"/>
            </svg>
            سجّل الدخول من خلال الفيس بوك
          </Button>

          {/* Phone Number Login */}
          <Button
            type="button"
            onClick={handlePhoneLogin}
            className="w-full bg-white hover:bg-gray-50 text-gray-900 font-medium py-6 rounded-full flex items-center justify-center gap-3 border-2 border-gray-200"
          >
            <Phone className="w-5 h-5" />
            تسجيل الدخول باستخدام رقم الهاتف
          </Button>

          {/* Divider */}
          <div className="relative py-4">
            <div className="absolute inset-0 flex items-center">
              <div className="w-full border-t border-gray-200"></div>
            </div>
            <div className="relative flex justify-center text-sm">
              <span className="bg-white px-4 text-gray-500">أو</span>
            </div>
          </div>

          {/* Email/Password Form */}
          {loginMethod === 'email' ? (
            <form onSubmit={handleSubmit} className="space-y-4">
              {error && (
                <Alert variant="destructive" data-testid="error-alert">
                  <AlertDescription>{error}</AlertDescription>
                </Alert>
              )}

              <div className="space-y-2">
                <Label htmlFor="email" className="text-sm font-medium">البريد الإلكتروني</Label>
                <Input
                  id="email"
                  name="email"
                  type="email"
                  required
                  value={formData.email}
                  onChange={handleChange}
                  placeholder="example@email.com"
                  className="h-12 rounded-lg"
                  data-testid="email-input"
                />
              </div>

              <div className="space-y-2">
                <Label htmlFor="password" className="text-sm font-medium">كلمة المرور</Label>
                <Input
                  id="password"
                  name="password"
                  type="password"
                  required
                  value={formData.password}
                  onChange={handleChange}
                  placeholder="6 أحرف على الأقل"
                  className="h-12 rounded-lg"
                  data-testid="password-input"
                />
              </div>

              <Button
                type="submit"
                disabled={loading}
                className="w-full bg-gradient-to-r from-pink-500 to-red-500 hover:from-pink-600 hover:to-red-600 text-white font-bold py-6 rounded-full"
                data-testid="submit-button"
              >
                {loading ? 'جاري تسجيل الدخول...' : 'تسجيل الدخول'}
              </Button>
            </form>
          ) : (
            <div className="space-y-4">
              <div className="space-y-2">
                <Label htmlFor="phone" className="text-sm font-medium">رقم الهاتف</Label>
                <Input
                  id="phone"
                  type="tel"
                  placeholder="+966 XX XXX XX XX"
                  className="h-12 rounded-lg"
                />
              </div>
              <Button
                type="button"
                className="w-full bg-gradient-to-r from-pink-500 to-red-500 hover:from-pink-600 hover:to-red-600 text-white font-bold py-6 rounded-full"
              >
                إرسال رمز التحقق
              </Button>
              <Button
                type="button"
                variant="ghost"
                onClick={() => setLoginMethod('email')}
                className="w-full"
              >
                العودة إلى البريد الإلكتروني
              </Button>
            </div>
          )}
        </CardContent>

        <CardFooter className="flex-col space-y-2 text-center text-sm">
          <p className="text-gray-600">
            هل تواجه مشكلة في تسجيل الدخول؟
          </p>
          <Link
            to="/register"
            className="text-pink-600 hover:text-pink-700 font-medium"
            data-testid="register-link"
          >
            ليس لديك حساب؟ سجّل الآن 💕
          </Link>
        </CardFooter>
      </Card>
    </div>
  );
};

export default Login;
                onChange={handleChange}
                placeholder="أدخل كلمة المرور"
                data-testid="password-input"
              />
            </div>

            <Button
              type="submit"
              className="w-full"
              disabled={loading}
              data-testid="login-submit-button"
            >
              {loading ? 'جاري تسجيل الدخول...' : 'تسجيل الدخول'}
            </Button>
          </form>
        </CardContent>
        <CardFooter className="flex justify-center">
          <p className="text-sm text-gray-600">
            ليس لديك حساب؟{' '}
            <Link to="/register" className="text-blue-600 hover:underline" data-testid="register-link">
              إنشاء حساب جديد
            </Link>
          </p>
        </CardFooter>
      </Card>
    </div>
  );
};

export default Login;
