import React from 'react';
import { useNavigate } from 'react-router-dom';
import { Button } from '../components/ui/button';
import CustomLogo from '../components/CustomLogo';
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

      <main className="max-w-4xl mx-auto p-8">
        <div className="bg-white rounded-2xl shadow-lg p-12">
          <div className="flex flex-col items-center gap-8">
            <h2 className="text-3xl font-bold text-center">شعار Pizoo</h2>
            
            <div className="bg-gradient-to-br from-pink-50 to-purple-50 p-12 rounded-xl">
              <CustomLogo size="xl" />
            </div>
            
            <div className="grid md:grid-cols-3 gap-6 w-full">
              <div className="bg-white p-6 rounded-lg border-2">
                <p className="text-sm text-gray-600 mb-4 text-center">كبير</p>
                <CustomLogo size="lg" />
              </div>
              
              <div className="bg-white p-6 rounded-lg border-2">
                <p className="text-sm text-gray-600 mb-4 text-center">متوسط</p>
                <CustomLogo size="md" />
              </div>
              
              <div className="bg-white p-6 rounded-lg border-2">
                <p className="text-sm text-gray-600 mb-4 text-center">صغير</p>
                <CustomLogo size="sm" />
              </div>
            </div>
          </div>
        </div>
      </main>
    </div>
  );
};

export default CustomLogoPage;
