import React, { useState } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import { Button } from '../components/ui/button';
import { Input } from '../components/ui/input';
import { Label } from '../components/ui/label';
import { Checkbox } from '../components/ui/checkbox';
import { Card, CardContent, CardDescription, CardFooter, CardHeader, CardTitle } from '../components/ui/card';
import { Alert, AlertDescription } from '../components/ui/alert';
import { LogIn } from 'lucide-react';
import CustomLogo from '../components/CustomLogo';

const Login = () => {
  const navigate = useNavigate();
  const { login } = useAuth();
  const [formData, setFormData] = useState({
    email: '',
    password: '',
    rememberMe: false
  });
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);

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

    const result = await login(formData.email, formData.password);
    setLoading(false);

    if (result.success) {
      // Save remember me preference
      if (formData.rememberMe) {
        localStorage.setItem('rememberMe', 'true');
      }
      navigate('/home');
    } else {
      setError(result.error);
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-pink-500 via-red-500 to-orange-500 dark:from-gray-300 dark:via-gray-400 dark:to-gray-500 flex items-center justify-center p-4" dir="rtl">
      {/* Logo/Brand */}
      <div className="absolute top-8 left-1/2 transform -translate-x-1/2">
        <CustomLogo size="lg" />
      </div>

      <Card className="w-full max-w-md mt-20 dark:bg-gray-200" data-testid="login-card">
        <CardHeader className="text-center">
          <CardTitle className="text-2xl font-bold dark:text-gray-900">تسجيل الدخول</CardTitle>
          <CardDescription className="text-gray-600 dark:text-gray-700">
            أهلاً بعودتك! نحن سعداء برؤيتك مجدداً
          </CardDescription>
        </CardHeader>
        
        <CardContent>
          <form onSubmit={handleSubmit} className="space-y-4">
            {error && (
              <Alert variant="destructive" data-testid="error-alert">
                <AlertDescription>{error}</AlertDescription>
              </Alert>
            )}

            <div className="space-y-2">
              <Label htmlFor="email" className="text-sm font-medium">
                البريد الإلكتروني أو رقم الهاتف
              </Label>
              <Input
                id="email"
                name="email"
                type="text"
                required
                value={formData.email}
                onChange={handleChange}
                placeholder="example@email.com أو +966XXXXXXXX"
                className="h-12 rounded-lg"
                data-testid="email-input"
              />
            </div>

            <div className="space-y-2">
              <Label htmlFor="password" className="text-sm font-medium">
                كلمة المرور
              </Label>
              <Input
                id="password"
                name="password"
                type="password"
                required
                value={formData.password}
                onChange={handleChange}
                placeholder="أدخل كلمة المرور"
                className="h-12 rounded-lg"
                data-testid="password-input"
              />
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
                حفظ تسجيل الدخول
              </label>
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
        </CardContent>

        <CardFooter className="flex-col space-y-3 text-center text-sm border-t pt-4">
          <Link
            to="/forgot-password"
            className="text-gray-600 hover:text-gray-800"
          >
            هل نسيت كلمة المرور؟
          </Link>
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
