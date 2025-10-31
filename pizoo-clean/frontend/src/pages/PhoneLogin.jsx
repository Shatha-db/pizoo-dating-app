import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useTranslation } from 'react-i18next';
import { useAuth } from '../context/AuthContext';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '../components/ui/card';
import { Button } from '../components/ui/button';
import { Input } from '../components/ui/input';
import { Label } from '../components/ui/label';
import CustomLogo from '../components/CustomLogo';
import LanguageSelector from '../modules/i18n/LanguageSelector';

const API = process.env.REACT_APP_BACKEND_URL || '';

export default function PhoneLogin() {
  const { t } = useTranslation(['auth']);
  const navigate = useNavigate();
  const { login: authLogin } = useAuth();
  
  const [phone, setPhone] = useState('+');
  const [otpId, setOtpId] = useState('');
  const [code, setCode] = useState('');
  const [stage, setStage] = useState('phone'); // 'phone' or 'code'
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [ttl, setTtl] = useState(0);

  const sendOtp = async () => {
    if (phone.length < 8) {
      setError(t('phone_invalid') || 'Invalid phone number');
      return;
    }

    setLoading(true);
    setError('');

    try {
      const response = await fetch(`${API}/api/auth/phone/send-otp`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        credentials: 'include',
        body: JSON.stringify({ phone })
      });

      const data = await response.json();

      if (!response.ok) {
        if (response.status === 429) {
          setError(t('too_many_requests') || 'Please wait before requesting another code');
        } else {
          setError(data.detail || t('otp_send_failed') || 'Failed to send OTP');
        }
        return;
      }

      setOtpId(data.otpId);
      setTtl(data.ttl);
      setStage('code');
      setError('');
    } catch (err) {
      console.error('Send OTP error:', err);
      setError(t('otp_send_failed') || 'Failed to send verification code');
    } finally {
      setLoading(false);
    }
  };

  const verify = async () => {
    if (code.length !== 6) {
      setError(t('code_invalid') || 'Code must be 6 digits');
      return;
    }

    setLoading(true);
    setError('');

    try {
      const response = await fetch(`${API}/api/auth/phone/verify-otp`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        credentials: 'include',
        body: JSON.stringify({ phone, code, otpId })
      });

      const data = await response.json();

      if (!response.ok) {
        if (response.status === 429) {
          setError(t('otp_locked') || 'Too many attempts. Please request a new code.');
        } else if (response.status === 410) {
          setError(t('otp_expired') || 'Code expired. Please request a new one.');
        } else {
          setError(data.detail || t('otp_invalid') || 'Invalid code');
        }
        return;
      }

      // Save token and redirect
      if (data.token) {
        localStorage.setItem('token', data.token);
        localStorage.setItem('user', JSON.stringify({ phone, id: data.user_id }));
        
        // Use auth context if available
        if (authLogin) {
          authLogin(data.token);
        }

        // Redirect to home or profile setup
        navigate('/profile/setup');
      }
    } catch (err) {
      console.error('Verify OTP error:', err);
      setError(t('verify_failed') || 'Verification failed');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-pink-500 via-red-500 to-orange-500 flex items-center justify-center p-4">
      {/* Language Selector */}
      <div className="fixed top-4 right-4 z-50">
        <LanguageSelector variant="compact" />
      </div>

      {/* Logo */}
      <div className="absolute top-8 left-1/2 transform -translate-x-1/2">
        <CustomLogo size="xl" />
      </div>

      <Card className="w-full max-w-md mt-20">
        <CardHeader>
          <CardTitle className="text-2xl font-bold text-center">
            {t('phone_login') || 'Phone Login'}
          </CardTitle>
          <CardDescription className="text-center">
            {stage === 'phone'
              ? t('phone_login_desc') || 'Enter your phone number to receive a verification code'
              : t('enter_code_desc') || 'Enter the 6-digit code sent to your phone'}
          </CardDescription>
        </CardHeader>

        <CardContent className="space-y-4">
          {error && (
            <div className="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded-lg text-sm">
              {error}
            </div>
          )}

          {stage === 'phone' && (
            <>
              <div>
                <Label htmlFor="phone">{t('phone_number') || 'Phone Number'}</Label>
                <Input
                  id="phone"
                  type="tel"
                  value={phone}
                  onChange={(e) => setPhone(e.target.value)}
                  placeholder="+41791234567"
                  className="text-lg"
                  disabled={loading}
                />
                <p className="text-xs text-gray-500 mt-1">
                  {t('phone_format') || 'Include country code (e.g., +41 for Switzerland)'}
                </p>
              </div>

              <Button
                onClick={sendOtp}
                disabled={loading || phone.length < 8}
                className="w-full"
              >
                {loading ? t('sending') || 'Sending...' : t('send_code') || 'Send Code'}
              </Button>

              <div className="text-center text-sm text-gray-600">
                {t('have_account') || 'Have an email account?'}{' '}
                <button
                  onClick={() => navigate('/login')}
                  className="text-pink-600 hover:underline font-medium"
                >
                  {t('login_email') || 'Login with Email'}
                </button>
              </div>
            </>
          )}

          {stage === 'code' && (
            <>
              <div>
                <Label htmlFor="code">{t('verification_code') || 'Verification Code'}</Label>
                <Input
                  id="code"
                  type="text"
                  value={code}
                  onChange={(e) => setCode(e.target.value.replace(/\D/g, ''))}
                  maxLength={6}
                  placeholder="123456"
                  className="text-center text-2xl tracking-widest font-mono"
                  disabled={loading}
                  autoFocus
                />
                <p className="text-xs text-gray-500 mt-1 text-center">
                  {t('code_sent_to') || 'Code sent to'} {phone}
                </p>
                {ttl > 0 && (
                  <p className="text-xs text-green-600 mt-1 text-center">
                    {t('code_expires') || 'Expires in'} {Math.floor(ttl / 60)} {t('minutes') || 'minutes'}
                  </p>
                )}
              </div>

              <Button
                onClick={verify}
                disabled={loading || code.length !== 6}
                className="w-full"
              >
                {loading ? t('verifying') || 'Verifying...' : t('verify') || 'Verify'}
              </Button>

              <div className="text-center">
                <button
                  onClick={() => {
                    setStage('phone');
                    setCode('');
                    setError('');
                  }}
                  className="text-sm text-gray-600 hover:text-gray-800"
                >
                  {t('change_phone') || 'Change phone number'}
                </button>
              </div>
            </>
          )}
        </CardContent>
      </Card>
    </div>
  );
}
