import React, { useEffect, useState, useRef } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import { Button } from '../components/ui/button';
import { Card } from '../components/ui/card';
import { X, MapPin, Users, Calendar, Navigation } from 'lucide-react';
import { MapContainer, TileLayer, Circle, Marker, Popup, useMap } from 'react-leaflet';
import 'leaflet/dist/leaflet.css';
import L from 'leaflet';
import axios from 'axios';

// Fix for default marker icon in React Leaflet
delete L.Icon.Default.prototype._getIconUrl;
L.Icon.Default.mergeOptions({
  iconRetinaUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.7.1/images/marker-icon-2x.png',
  iconUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.7.1/images/marker-icon.png',
  shadowUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.7.1/images/marker-shadow.png',
});

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

// Component to update map view when settings change
function MapUpdater({ center, zoom }) {
  const map = useMap();
  useEffect(() => {
    map.setView(center, zoom);
  }, [center, zoom, map]);
  return null;
}

const DiscoverySettings = () => {
  const navigate = useNavigate();
  const { token } = useAuth();
  const [settings, setSettings] = useState({
    location: '',
    max_distance: 50,
    interested_in: 'all',
    min_age: 18,
    max_age: 100,
    show_new_profiles_only: false,
    show_verified_only: false
  });
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);

  useEffect(() => {
    fetchSettings();
  }, []);

  const fetchSettings = async () => {
    try {
      const response = await axios.get(`${API}/discovery-settings`, {
        headers: { Authorization: `Bearer ${token}` }
      });
      if (response.data) {
        setSettings(response.data);
      }
    } catch (error) {
      console.error('Error fetching settings:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleSave = async () => {
    setSaving(true);
    try {
      await axios.put(
        `${API}/discovery-settings`,
        settings,
        {
          headers: { Authorization: `Bearer ${token}` }
        }
      );
      navigate('/home');
    } catch (error) {
      console.error('Error saving settings:', error);
      alert('حدث خطأ أثناء حفظ الإعدادات');
    } finally {
      setSaving(false);
    }
  };

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="animate-spin rounded-full h-16 w-16 border-b-4 border-pink-500"></div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50 pb-20" dir="rtl">
      {/* Header */}
      <header className="bg-white shadow-sm p-4 flex items-center justify-between sticky top-0 z-10">
        <Button
          variant="ghost"
          size="icon"
          onClick={() => navigate('/home')}
        >
          <X className="w-6 h-6" />
        </Button>
        <h1 className="text-xl font-bold">إعدادات الاكتشاف</h1>
        <Button
          onClick={handleSave}
          disabled={saving}
          className="bg-gradient-to-r from-pink-500 to-red-500 hover:from-pink-600 hover:to-red-600 text-white text-sm px-4"
        >
          {saving ? 'جاري الحفظ...' : 'حفظ'}
        </Button>
      </header>

      <main className="max-w-2xl mx-auto p-4 space-y-6">
        {/* Location */}
        <Card className="p-6">
          <div className="flex items-center gap-3 mb-4">
            <MapPin className="w-6 h-6 text-pink-500" />
            <h2 className="text-lg font-bold">الموقع</h2>
          </div>
          <input
            type="text"
            value={settings.location}
            onChange={(e) => setSettings({ ...settings, location: e.target.value })}
            placeholder="غير الموقع للعثور على مُعجبين في أي مكان"
            className="w-full p-3 border rounded-lg focus:ring-2 focus:ring-pink-500 focus:border-transparent"
          />
          <p className="text-sm text-gray-500 mt-2">مثال: Basel, BS</p>
        </Card>

        {/* Maximum Distance */}
        <Card className="p-6">
          <h2 className="text-lg font-bold mb-2">أقصى مسافة</h2>
          <div className="flex items-center justify-between mb-4">
            <span className="text-3xl font-bold text-pink-500">{settings.max_distance} km</span>
          </div>
          <input
            type="range"
            min="1"
            max="150"
            value={settings.max_distance}
            onChange={(e) => setSettings({ ...settings, max_distance: parseInt(e.target.value) })}
            className="w-full h-2 bg-gray-200 rounded-lg appearance-none cursor-pointer accent-pink-500"
          />
        </Card>

        {/* Interested In */}
        <Card className="p-6">
          <div className="flex items-center gap-3 mb-4">
            <Users className="w-6 h-6 text-pink-500" />
            <h2 className="text-lg font-bold">مهتم بـ</h2>
          </div>
          <div className="space-y-3">
            {[
              { value: 'female', label: 'سيدات', icon: '👩' },
              { value: 'male', label: 'رجال', icon: '👨' },
              { value: 'all', label: 'الجميع', icon: '👥' }
            ].map((option) => (
              <button
                key={option.value}
                onClick={() => setSettings({ ...settings, interested_in: option.value })}
                className={`w-full p-4 rounded-lg border-2 flex items-center justify-between transition-all ${
                  settings.interested_in === option.value
                    ? 'border-pink-500 bg-pink-50'
                    : 'border-gray-200 hover:border-pink-300'
                }`}
              >
                <div className="flex items-center gap-3">
                  <span className="text-2xl">{option.icon}</span>
                  <span className="font-medium">{option.label}</span>
                </div>
                {settings.interested_in === option.value && (
                  <div className="w-6 h-6 bg-pink-500 rounded-full flex items-center justify-center">
                    <span className="text-white text-sm">✓</span>
                  </div>
                )}
              </button>
            ))}
          </div>
        </Card>

        {/* Age Range */}
        <Card className="p-6">
          <div className="flex items-center gap-3 mb-4">
            <Calendar className="w-6 h-6 text-pink-500" />
            <h2 className="text-lg font-bold">نطاق الفئة العمرية</h2>
          </div>
          <div className="flex items-center justify-between mb-4">
            <span className="text-xl font-bold">{settings.min_age}</span>
            <span className="text-gray-500">-</span>
            <span className="text-xl font-bold">{settings.max_age}</span>
          </div>
          
          {/* Min Age Slider */}
          <div className="mb-6">
            <label className="text-sm text-gray-600 mb-2 block">الحد الأدنى للعمر</label>
            <input
              type="range"
              min="18"
              max="100"
              value={settings.min_age}
              onChange={(e) => {
                const newMin = parseInt(e.target.value);
                setSettings({ 
                  ...settings, 
                  min_age: newMin,
                  max_age: Math.max(newMin, settings.max_age)
                });
              }}
              className="w-full h-2 bg-gray-200 rounded-lg appearance-none cursor-pointer accent-pink-500"
            />
          </div>

          {/* Max Age Slider */}
          <div>
            <label className="text-sm text-gray-600 mb-2 block">الحد الأقصى للعمر</label>
            <input
              type="range"
              min="18"
              max="100"
              value={settings.max_age}
              onChange={(e) => {
                const newMax = parseInt(e.target.value);
                setSettings({ 
                  ...settings, 
                  max_age: newMax,
                  min_age: Math.min(settings.min_age, newMax)
                });
              }}
              className="w-full h-2 bg-gray-200 rounded-lg appearance-none cursor-pointer accent-pink-500"
            />
          </div>
        </Card>

        {/* Additional Filters */}
        <Card className="p-6">
          <h2 className="text-lg font-bold mb-4">خيارات إضافية</h2>
          
          <div className="space-y-4">
            <div className="flex items-center justify-between py-2">
              <div>
                <div className="font-medium">إظهار الأشخاص المتواجدين حديثاً فقط</div>
                <div className="text-sm text-gray-600">إذا لم يتبقَ هناك حسابات شخصية لعرضها</div>
              </div>
              <label className="relative inline-flex items-center cursor-pointer">
                <input
                  type="checkbox"
                  checked={settings.show_new_profiles_only}
                  onChange={(e) => setSettings({ ...settings, show_new_profiles_only: e.target.checked })}
                  className="sr-only peer"
                />
                <div className="w-11 h-6 bg-gray-200 peer-focus:outline-none peer-focus:ring-4 peer-focus:ring-pink-300 rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:border-gray-300 after:border after:rounded-full after:h-5 after:w-5 after:transition-all peer-checked:bg-pink-500"></div>
              </label>
            </div>

            <div className="flex items-center justify-between py-2">
              <div>
                <div className="font-medium">لديه معلومات شخصية</div>
              </div>
              <label className="relative inline-flex items-center cursor-pointer">
                <input
                  type="checkbox"
                  checked={settings.show_verified_only}
                  onChange={(e) => setSettings({ ...settings, show_verified_only: e.target.checked })}
                  className="sr-only peer"
                />
                <div className="w-11 h-6 bg-gray-200 peer-focus:outline-none peer-focus:ring-4 peer-focus:ring-pink-300 rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:border-gray-300 after:border after:rounded-full after:h-5 after:w-5 after:transition-all peer-checked:bg-pink-500"></div>
              </label>
            </div>
          </div>
        </Card>

        {/* Invite Friends Section */}
        <Card className="p-6 bg-gradient-to-br from-purple-50 to-pink-50">
          <h3 className="font-bold text-lg mb-2">دعوات من الأصدقاء</h3>
          <p className="text-sm text-gray-600 mb-4">
            يُمكنك تشكيل ثُنائي مع ما يصل إلى 3 من أصدقائك في موعد مزدوج
          </p>
          <div className="flex gap-2 mb-4">
            {[1, 2, 3].map((num) => (
              <div key={num} className="flex-1 aspect-square rounded-full bg-gray-200 flex items-center justify-center">
                <Users className="w-8 h-8 text-gray-400" />
              </div>
            ))}
          </div>
          <Button
            variant="outline"
            className="w-full"
            onClick={() => {/* Add invite functionality */}}
          >
            دعوة الأصدقاء
          </Button>
        </Card>
      </main>
    </div>
  );
};

export default DiscoverySettings;
