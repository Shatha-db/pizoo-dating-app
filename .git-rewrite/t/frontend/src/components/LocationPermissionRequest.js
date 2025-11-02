import React, { useEffect, useState } from 'react';
import { MapPin, X } from 'lucide-react';
import { Button } from './ui/button';
import axios from 'axios';

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;

const LocationPermissionRequest = ({ onClose, token }) => {
  const [requesting, setRequesting] = useState(false);

  useEffect(() => {
    // Check if already has location
    const hasLocation = localStorage.getItem('location_granted');
    if (hasLocation) {
      onClose();
    }
  }, [onClose]);

  const requestLocation = async () => {
    setRequesting(true);
    
    if (!navigator.geolocation) {
      alert('متصفحك لا يدعم تحديد الموقع');
      setRequesting(false);
      return;
    }

    navigator.geolocation.getCurrentPosition(
      async (position) => {
        const { latitude, longitude } = position.coords;
        
        try {
          // Save location to backend
          await axios.put(
            `${BACKEND_URL}/api/discovery-settings`,
            {
              latitude,
              longitude
            },
            {
              headers: { Authorization: `Bearer ${token}` }
            }
          );
          
          localStorage.setItem('location_granted', 'true');
          onClose();
        } catch (error) {
          console.error('Error saving location:', error);
          localStorage.setItem('location_granted', 'true');
          onClose();
        }
      },
      (error) => {
        console.error('Location error:', error);
        setRequesting(false);
        
        if (error.code === error.PERMISSION_DENIED) {
          // User denied, show instructions
          alert('يرجى السماح بالوصول إلى الموقع من إعدادات المتصفح للحصول على أفضل تجربة');
        }
      }
    );
  };

  const skipForNow = () => {
    localStorage.setItem('location_skipped', 'true');
    onClose();
  };

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 z-50 flex items-center justify-center p-4" dir="rtl">
      <div className="bg-white rounded-2xl max-w-md w-full p-6 shadow-2xl">
        {/* Close button */}
        <button
          onClick={skipForNow}
          className="absolute top-4 left-4 text-gray-400 hover:text-gray-600"
        >
          <X className="w-6 h-6" />
        </button>

        {/* Icon */}
        <div className="flex justify-center mb-4">
          <div className="w-20 h-20 bg-pink-100 rounded-full flex items-center justify-center">
            <MapPin className="w-10 h-10 text-pink-500" />
          </div>
        </div>

        {/* Title */}
        <h2 className="text-2xl font-bold text-center mb-3">نحتاج إلى موقعك 📍</h2>
        
        {/* Description */}
        <p className="text-gray-600 text-center mb-6">
          لعرض المستخدمين القريبين منك ومساعدتك في العثور على أشخاص في منطقتك، نحتاج إلى إذن الوصول إلى موقعك الجغرافي.
        </p>

        {/* Info box */}
        <div className="bg-blue-50 border border-blue-200 rounded-lg p-4 mb-6">
          <p className="text-sm text-blue-800">
            <strong>🔒 خصوصيتك مهمة:</strong> لن نشارك موقعك الدقيق مع الآخرين. سنعرض فقط المسافة التقريبية.
          </p>
        </div>

        {/* Buttons */}
        <div className="space-y-3">
          <Button
            onClick={requestLocation}
            disabled={requesting}
            className="w-full bg-gradient-to-r from-pink-500 to-red-500 hover:from-pink-600 hover:to-red-600 text-white font-semibold py-3 rounded-xl"
          >
            {requesting ? (
              <div className="flex items-center justify-center gap-2">
                <div className="animate-spin rounded-full h-5 w-5 border-b-2 border-white"></div>
                <span>جاري الطلب...</span>
              </div>
            ) : (
              <>
                <MapPin className="w-5 h-5 ml-2" />
                السماح بالوصول إلى الموقع
              </>
            )}
          </Button>
          
          <Button
            onClick={skipForNow}
            variant="ghost"
            className="w-full text-gray-600"
          >
            ربما لاحقاً
          </Button>
        </div>
      </div>
    </div>
  );
};

export default LocationPermissionRequest;
