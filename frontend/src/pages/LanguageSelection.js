import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useTranslation } from 'react-i18next';
import { Card } from '../components/ui/card';
import { Button } from '../components/ui/button';
import CustomLogo from '../components/CustomLogo';
import { Globe, Check } from 'lucide-react';

const LanguageSelection = () => {
  const navigate = useNavigate();
  const { i18n } = useTranslation();
  const [selectedLanguage, setSelectedLanguage] = useState('en');

  const languages = [
    { code: 'en', name: 'English', flag: '🇬🇧', dir: 'ltr' },
    { code: 'ar', name: 'العربية', flag: '🇸🇦', dir: 'rtl' },
    { code: 'fr', name: 'Français', flag: '🇫🇷', dir: 'ltr' },
    { code: 'es', name: 'Español', flag: '🇪🇸', dir: 'ltr' }
  ];

  const handleContinue = () => {
    i18n.changeLanguage(selectedLanguage);
    document.documentElement.dir = languages.find(l => l.code === selectedLanguage)?.dir || 'ltr';
    localStorage.setItem('preferred_language', selectedLanguage);
    navigate('/register');
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-pink-100 via-pink-200 to-rose-200 flex items-center justify-center p-4">
      <Card className="w-full max-w-md p-8 backdrop-blur-sm bg-white/90">
        <div className="text-center mb-8">
          <CustomLogo size="xl" className="mb-6" />
          <Globe className="w-16 h-16 mx-auto text-pink-500 mb-4" />
          <h1 className="text-3xl font-bold mb-2">Select Your Language</h1>
          <p className="text-gray-600">Choose your preferred language for the app</p>
        </div>

        <div className="space-y-3 mb-8">
          {languages.map((lang) => (
            <button
              key={lang.code}
              onClick={() => setSelectedLanguage(lang.code)}
              className={`w-full p-4 rounded-xl border-2 transition-all flex items-center justify-between ${
                selectedLanguage === lang.code
                  ? 'border-pink-500 bg-pink-50 shadow-md'
                  : 'border-gray-200 hover:border-pink-300 hover:bg-pink-50/50'
              }`}
            >
              <div className="flex items-center gap-3">
                <span className="text-3xl">{lang.flag}</span>
                <span className={`text-lg font-medium ${
                  selectedLanguage === lang.code ? 'text-pink-600' : 'text-gray-700'
                }`}>
                  {lang.name}
                </span>
              </div>
              {selectedLanguage === lang.code && (
                <Check className="w-6 h-6 text-pink-500" />
              )}
            </button>
          ))}
        </div>

        <Button
          onClick={handleContinue}
          className="w-full bg-gradient-to-r from-pink-500 to-rose-500 hover:from-pink-600 hover:to-rose-600 text-white py-6 text-lg"
        >
          Continue
        </Button>
      </Card>
    </div>
  );
};

export default LanguageSelection;
