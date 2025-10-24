import React from 'react';
import { useNavigate } from 'react-router-dom';
import { Button } from '../components/ui/button';
import { CustomLogoPreview } from '../components/CustomLogo';
import { X, Check } from 'lucide-react';

const CustomLogoPage = () => {
  const navigate = useNavigate();

  const handleApply = () => {
    // Will apply this logo to all pages
    alert('سيتم تطبيق اللوجو على جميع الصفحات! 🎉');
    navigate('/');
  };

  return (
    <div className="min-h-screen bg-gray-50 pb-20" dir="rtl">
      {/* Header */}
      <header className="bg-white shadow-sm p-4 sticky top-0 z-10">
        <div className="max-w-6xl mx-auto flex items-center justify-between">
          <Button
            variant="ghost"
            size="icon"
            onClick={() => navigate(-1)}
          >
            <X className="w-6 h-6" />
          </Button>
          <h1 className="text-2xl font-bold">اللوجو المخصص</h1>
          <Button
            onClick={handleApply}
            className="bg-gradient-to-r from-pink-500 to-orange-500 hover:from-pink-600 hover:to-orange-600 text-white"
          >
            <Check className="w-4 h-4 ml-2" />
            تطبيق
          </Button>
        </div>
      </header>

      <CustomLogoPreview />
    </div>
  );
};

export default CustomLogoPage;
