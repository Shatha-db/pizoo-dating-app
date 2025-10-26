import React, { useEffect, useState, useCallback, useRef } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import { Button } from '../components/ui/button';
import { Card } from '../components/ui/card';
import { X, MapPin, Users, Calendar, Navigation, Heart } from 'lucide-react';
import { MapContainer, TileLayer, Circle, Marker, Popup, useMap, useMapEvents } from 'react-leaflet';
import MarkerClusterGroup from 'react-leaflet-cluster';
import 'leaflet/dist/leaflet.css';
import L from 'leaflet';
import axios from 'axios';
import { debounce } from 'lodash';
import UserBottomSheet from '../components/UserBottomSheet';

// Fix for default marker icon in React Leaflet
delete L.Icon.Default.prototype._getIconUrl;
L.Icon.Default.mergeOptions({
  iconRetinaUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.7.1/images/marker-icon-2x.png',
  iconUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.7.1/images/marker-icon.png',
  shadowUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.7.1/images/marker-shadow.png',
});

// Custom user marker icon (pink heart)
const userMarkerIcon = L.divIcon({
  className: 'custom-marker',
  html: `<div style="
    background: linear-gradient(135deg, #ec4899 0%, #ef4444 100%);
    width: 40px;
    height: 40px;
    border-radius: 50%;
    display: flex;
    align-items: center;
    justify-content: center;
    box-shadow: 0 4px 12px rgba(236, 72, 153, 0.4);
    border: 3px solid white;
  ">
    <svg width="20" height="20" viewBox="0 0 24 24" fill="white">
      <path d="M12 21.35l-1.45-1.32C5.4 15.36 2 12.28 2 8.5 2 5.42 4.42 3 7.5 3c1.74 0 3.41.81 4.5 2.09C13.09 3.81 14.76 3 16.5 3 19.58 3 22 5.42 22 8.5c0 3.78-3.4 6.86-8.55 11.54L12 21.35z"/>
    </svg>
  </div>`,
  iconSize: [40, 40],
  iconAnchor: [20, 20],
});

// Current user marker icon (blue)
const currentUserIcon = L.divIcon({
  className: 'custom-marker',
  html: `<div style="
    background: linear-gradient(135deg, #3b82f6 0%, #2563eb 100%);
    width: 48px;
    height: 48px;
    border-radius: 50%;
    display: flex;
    align-items: center;
    justify-content: center;
    box-shadow: 0 4px 16px rgba(59, 130, 246, 0.5);
    border: 4px solid white;
    animation: pulse 2s infinite;
  ">
    <svg width="24" height="24" viewBox="0 0 24 24" fill="white">
      <path d="M12 2C8.13 2 5 5.13 5 9c0 5.25 7 13 7 13s7-7.75 7-13c0-3.87-3.13-7-7-7zm0 9.5c-1.38 0-2.5-1.12-2.5-2.5s1.12-2.5 2.5-2.5 2.5 1.12 2.5 2.5-1.12 2.5-2.5 2.5z"/>
    </svg>
  </div>
  <style>
    @keyframes pulse {
      0%, 100% { transform: scale(1); }
      50% { transform: scale(1.1); }
    }
  </style>`,
  iconSize: [48, 48],
  iconAnchor: [24, 24],
});

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

// Default radius constant
const DEFAULT_RADIUS = 25;

// Component to update map view when settings change
function MapUpdater({ center, zoom }) {
  const map = useMap();
  useEffect(() => {
    if (center && center[0] && center[1]) {
      map.setView(center, zoom);
    }
  }, [center, zoom, map]);
  return null;
}

// Component to handle map events with debounce
function MapEventHandler({ onMapMove }) {
  const map = useMap();
  
  useMapEvents({
    moveend: useCallback(() => {
      const center = map.getCenter();
      const bounds = map.getBounds();
      onMapMove({ center, bounds });
    }, [map, onMapMove]),
    zoomend: useCallback(() => {
      const center = map.getCenter();
      const bounds = map.getBounds();
      onMapMove({ center, bounds });
    }, [map, onMapMove]),
  });
  
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
  const [userLocation, setUserLocation] = useState({ lat: 47.5596, lng: 7.5886 }); // Default: Basel
  const [locationLoading, setLocationLoading] = useState(false);
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [mapKey, setMapKey] = useState(0);
  const [nearbyUsers, setNearbyUsers] = useState([]);
  const [loadingUsers, setLoadingUsers] = useState(false);
  const [selectedUser, setSelectedUser] = useState(null);
  const [locationPermission, setLocationPermission] = useState('prompt'); // 'granted', 'denied', 'prompt'
  const mapRef = useRef(null);

  useEffect(() => {
    fetchSettings();
    checkLocationPermission();
  }, []);

  useEffect(() => {
    if (userLocation.lat && userLocation.lng) {
      fetchNearbyUsers();
    }
  }, [userLocation, settings.max_distance]);

  const checkLocationPermission = async () => {
    if (!navigator.permissions) {
      getUserLocation();
      return;
    }

    try {
      const result = await navigator.permissions.query({ name: 'geolocation' });
      setLocationPermission(result.state);
      
      if (result.state === 'granted') {
        getUserLocation();
      }
      
      result.addEventListener('change', () => {
        setLocationPermission(result.state);
        if (result.state === 'granted') {
          getUserLocation();
        }
      });
    } catch (error) {
      console.error('Error checking permission:', error);
      getUserLocation();
    }
  };

  const getUserLocation = () => {
    if (navigator.geolocation) {
      navigator.geolocation.getCurrentPosition(
        (position) => {
          setUserLocation({
            lat: position.coords.latitude,
            lng: position.coords.longitude
          });
          setLocationPermission('granted');
        },
        (error) => {
          console.error('Error getting location:', error);
          if (error.code === error.PERMISSION_DENIED) {
            setLocationPermission('denied');
          }
        }
      );
    }
  };

  const detectLocation = () => {
    setLocationLoading(true);
    if (!navigator.geolocation) {
      alert('المتصفح لا يدعم تحديد الموقع');
      setLocationLoading(false);
      return;
    }

    navigator.geolocation.getCurrentPosition(
      async (position) => {
        const { latitude, longitude } = position.coords;
        setUserLocation({ lat: latitude, lng: longitude });
        setLocationPermission('granted');
        
        try {
          // Use Nominatim (OpenStreetMap) for reverse geocoding
          const response = await fetch(
            `https://nominatim.openstreetmap.org/reverse?format=json&lat=${latitude}&lon=${longitude}&accept-language=ar`
          );
          const data = await response.json();
          
          const city = data.address.city || data.address.town || data.address.village || data.address.state;
          const country = data.address.country;
          const locationStr = `${city}, ${country}`;
          
          setSettings(prev => ({ ...prev, location: locationStr }));
        } catch (error) {
          console.error('Error getting location name:', error);
          setSettings(prev => ({ ...prev, location: `${latitude.toFixed(2)}, ${longitude.toFixed(2)}` }));
        } finally {
          setLocationLoading(false);
        }
      },
      (error) => {
        console.error('Error getting location:', error);
        if (error.code === error.PERMISSION_DENIED) {
          setLocationPermission('denied');
          alert('يرجى السماح بالوصول إلى الموقع من إعدادات المتصفح');
        } else {
          alert('لم نتمكن من الحصول على موقعك');
        }
        setLocationLoading(false);
      }
    );
  };

  const recenterMap = () => {
    if (userLocation.lat && userLocation.lng) {
      setMapKey(prev => prev + 1);
    } else {
      detectLocation();
    }
  };

  // Fetch nearby users with viewport-based pagination
  const fetchNearbyUsers = useCallback(async () => {
    if (!userLocation.lat || !userLocation.lng) return;
    
    setLoadingUsers(true);
    try {
      const response = await axios.get(`${API}/profiles/discover`, {
        params: {
          max_distance: settings.max_distance,
          latitude: userLocation.lat,
          longitude: userLocation.lng,
          limit: 50 // Fetch more for clustering
        },
        headers: { Authorization: `Bearer ${token}` }
      });
      
      // Ensure we always set an array
      const users = Array.isArray(response.data) ? response.data : [];
      setNearbyUsers(users);
    } catch (error) {
      console.error('Error fetching nearby users:', error);
      setNearbyUsers([]); // Set empty array on error
    } finally {
      setLoadingUsers(false);
    }
  }, [userLocation, settings.max_distance, token]);

  // Debounced map movement handler (300ms)
  const debouncedMapMove = useCallback(
    debounce(({ center, bounds }) => {
      // Update viewport and potentially fetch more users
      console.log('Map moved:', center, bounds);
      // Could implement viewport pagination here
    }, 300),
    []
  );

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
        {
          ...settings,
          latitude: userLocation.lat,
          longitude: userLocation.lng
        },
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

  const handleLike = async (userId) => {
    try {
      await axios.post(
        `${API}/swipe`,
        {
          target_user_id: userId,
          action: 'like'
        },
        {
          headers: { Authorization: `Bearer ${token}` }
        }
      );
      setSelectedUser(null);
      alert('تم إرسال الإعجاب! ✅');
    } catch (error) {
      console.error('Error liking user:', error);
      alert('حدث خطأ. حاول مرة أخرى.');
    }
  };

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="animate-spin rounded-full h-16 w-16 border-b-4 border-pink-500"></div>
      </div>
    );
  }

  // Location Permission Denied UI
  if (locationPermission === 'denied') {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center p-4" dir="rtl">
        <Card className="max-w-md w-full p-8 text-center">
          <div className="mb-6">
            <MapPin className="w-20 h-20 mx-auto text-pink-500" />
          </div>
          <h2 className="text-2xl font-bold mb-4">نحتاج إلى موقعك</h2>
          <p className="text-gray-600 mb-4">
            لعرض المستخدمين القريبين منك، نحتاج إلى إذن الوصول إلى موقعك الجغرافي
          </p>
          
          {/* Instructions Card */}
          <div className="bg-pink-50 border border-pink-200 rounded-lg p-4 mb-6 text-right">
            <h3 className="font-bold text-pink-700 mb-3">كيفية تفعيل الموقع:</h3>
            <ol className="text-sm text-gray-700 space-y-2 list-decimal list-inside">
              <li>اضغط على أيقونة القفل 🔒 أو الإعدادات بجانب عنوان الموقع في المتصفح</li>
              <li>ابحث عن "الموقع" أو "Location"</li>
              <li>اختر "السماح" أو "Allow"</li>
              <li>قم بتحديث الصفحة</li>
            </ol>
          </div>

          <Button
            onClick={detectLocation}
            className="w-full bg-gradient-to-r from-pink-500 to-red-500 hover:from-pink-600 hover:to-red-600 text-white font-semibold py-3 rounded-xl mb-3"
          >
            <MapPin className="w-5 h-5 ml-2" />
            المحاولة مرة أخرى
          </Button>
          <Button
            onClick={() => navigate('/home')}
            variant="ghost"
            className="w-full"
          >
            العودة للرئيسية
          </Button>
        </Card>
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
            <h2 className="text-lg font-bold">الموقع والخريطة</h2>
          </div>
          
          {/* Map View with Clustering */}
          <div className="mb-4 rounded-lg overflow-hidden border-2 border-gray-200 relative" style={{ height: '400px' }}>
            {loadingUsers && (
              <div className="absolute top-4 right-4 bg-white rounded-lg px-4 py-2 shadow-lg z-[1000]">
                <div className="flex items-center gap-2">
                  <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-pink-500"></div>
                  <span className="text-sm text-gray-600">جاري التحميل...</span>
                </div>
              </div>
            )}
            
            {/* Recenter Button */}
            <button
              onClick={recenterMap}
              className="absolute top-4 left-4 bg-white rounded-lg p-3 shadow-lg hover:bg-gray-50 transition z-[1000]"
              title="إعادة التمركز"
            >
              <Navigation className="w-5 h-5 text-pink-500" />
            </button>

            <MapContainer 
              key={mapKey}
              ref={mapRef}
              center={[userLocation.lat, userLocation.lng]} 
              zoom={11} 
              style={{ height: '100%', width: '100%' }}
              zoomControl={true}
              scrollWheelZoom={true}
            >
              <TileLayer
                attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
                url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
              />
              
              {/* Current User Marker */}
              <Marker 
                position={[userLocation.lat, userLocation.lng]}
                icon={currentUserIcon}
              >
                <Popup>
                  <div className="text-center" dir="rtl">
                    <strong>موقعك الحالي</strong>
                  </div>
                </Popup>
              </Marker>
              
              {/* Distance radius circle */}
              <Circle
                center={[userLocation.lat, userLocation.lng]}
                radius={settings.max_distance * 1000} // Convert km to meters
                pathOptions={{ 
                  color: '#ec4899', 
                  fillColor: '#ec4899',
                  fillOpacity: 0.1,
                  weight: 2,
                  dashArray: '10, 10'
                }}
              />

              {/* Clustered User Markers */}
              <MarkerClusterGroup
                chunkedLoading
                showCoverageOnHover={false}
                spiderfyOnMaxZoom={true}
                maxClusterRadius={60}
                iconCreateFunction={(cluster) => {
                  const count = cluster.getChildCount();
                  return L.divIcon({
                    html: `<div style="
                      background: linear-gradient(135deg, #ec4899 0%, #ef4444 100%);
                      border-radius: 50%;
                      width: 50px;
                      height: 50px;
                      display: flex;
                      align-items: center;
                      justify-content: center;
                      color: white;
                      font-weight: bold;
                      font-size: 18px;
                      box-shadow: 0 4px 12px rgba(236, 72, 153, 0.5);
                      border: 3px solid white;
                    ">${count}</div>`,
                    className: 'custom-cluster-icon',
                    iconSize: [50, 50]
                  });
                }}
              >
                {Array.isArray(nearbyUsers) && nearbyUsers.map((user) => {
                  if (!user.latitude || !user.longitude) return null;
                  
                  return (
                    <Marker
                      key={user.id}
                      position={[user.latitude, user.longitude]}
                      icon={userMarkerIcon}
                      eventHandlers={{
                        click: () => setSelectedUser(user)
                      }}
                    >
                      <Popup>
                        <div className="text-center min-w-[150px]" dir="rtl">
                          <strong>{user.name}, {user.age}</strong>
                          {user.distance && (
                            <p className="text-xs text-gray-600 mt-1">
                              {user.distance < 1 ? '< 1' : Math.round(user.distance)} كم
                            </p>
                          )}
                        </div>
                      </Popup>
                    </Marker>
                  );
                })}
              </MarkerClusterGroup>

              <MapUpdater center={[userLocation.lat, userLocation.lng]} zoom={11} />
              <MapEventHandler onMapMove={debouncedMapMove} />
            </MapContainer>
          </div>

          {/* Users Count */}
          <div className="bg-pink-50 rounded-lg p-3 mb-3 flex items-center justify-between">
            <span className="text-sm text-gray-700">المستخدمون القريبون</span>
            <span className="text-lg font-bold text-pink-600">{nearbyUsers.length}</span>
          </div>

          <div className="flex gap-2 mb-3">
            <input
              type="text"
              value={settings.location}
              onChange={(e) => setSettings({ ...settings, location: e.target.value })}
              placeholder="غير الموقع للعثور على مُعجبين في أي مكان"
              className="flex-1 p-3 border rounded-lg focus:ring-2 focus:ring-pink-500 focus:border-transparent"
            />
            <Button
              onClick={detectLocation}
              disabled={locationLoading}
              className="bg-pink-500 hover:bg-pink-600 text-white px-4"
            >
              {locationLoading ? (
                <div className="animate-spin rounded-full h-5 w-5 border-b-2 border-white"></div>
              ) : (
                <Navigation className="w-5 h-5" />
              )}
            </Button>
          </div>
          <p className="text-sm text-gray-500">مثال: Basel, BS</p>
        </Card>

        {/* Maximum Distance */}
        <Card className="p-6">
          <h2 className="text-lg font-bold mb-2">أقصى مسافة</h2>
          <div className="flex items-center justify-between mb-4">
            <span className="text-3xl font-bold text-pink-500">{settings.max_distance} km</span>
            <span className="text-sm text-gray-600">نطاق البحث</span>
          </div>
          <input
            type="range"
            min="1"
            max="160"
            value={settings.max_distance}
            onChange={(e) => setSettings({ ...settings, max_distance: parseInt(e.target.value) })}
            className="w-full h-3 bg-gradient-to-r from-pink-200 to-pink-500 rounded-lg appearance-none cursor-pointer accent-pink-500 slider"
          />
          <div className="flex justify-between text-xs text-gray-500 mt-2">
            <span>1 km</span>
            <span>160 km</span>
          </div>
        </Card>

        {/* Age Range */}
        <Card className="p-6">
          <div className="flex items-center gap-3 mb-4">
            <Calendar className="w-6 h-6 text-pink-500" />
            <h2 className="text-lg font-bold">نطاق العمر</h2>
          </div>
          <div className="flex items-center gap-4 mb-4">
            <div className="flex-1">
              <label className="text-sm text-gray-600 mb-1 block">من</label>
              <input
                type="number"
                min="18"
                max={settings.max_age}
                value={settings.min_age}
                onChange={(e) => setSettings({ ...settings, min_age: parseInt(e.target.value) })}
                className="w-full p-3 border rounded-lg focus:ring-2 focus:ring-pink-500 focus:border-transparent"
              />
            </div>
            <div className="flex-1">
              <label className="text-sm text-gray-600 mb-1 block">إلى</label>
              <input
                type="number"
                min={settings.min_age}
                max="100"
                value={settings.max_age}
                onChange={(e) => setSettings({ ...settings, max_age: parseInt(e.target.value) })}
                className="w-full p-3 border rounded-lg focus:ring-2 focus:ring-pink-500 focus:border-transparent"
              />
            </div>
          </div>
          <p className="text-sm text-gray-500 text-center">
            {settings.min_age} - {settings.max_age} سنة
          </p>
        </Card>

        {/* Gender Preference */}
        <Card className="p-6">
          <div className="flex items-center gap-3 mb-4">
            <Users className="w-6 h-6 text-pink-500" />
            <h2 className="text-lg font-bold">مهتم بـ</h2>
          </div>
          <div className="grid grid-cols-3 gap-3">
            {['all', 'women', 'men'].map((option) => (
              <button
                key={option}
                onClick={() => setSettings({ ...settings, interested_in: option })}
                className={`p-4 rounded-xl border-2 transition ${
                  settings.interested_in === option
                    ? 'bg-gradient-to-r from-pink-500 to-red-500 text-white border-transparent'
                    : 'bg-white border-gray-200 hover:border-pink-300'
                }`}
              >
                <div className="text-center">
                  <span className="text-sm font-medium">
                    {option === 'all' ? 'الجميع' : option === 'women' ? 'نساء' : 'رجال'}
                  </span>
                </div>
              </button>
            ))}
          </div>
        </Card>

        {/* Additional Filters */}
        <Card className="p-6 space-y-4">
          <h2 className="text-lg font-bold">فلاتر إضافية</h2>
          
          <label className="flex items-center justify-between cursor-pointer">
            <span className="text-gray-700">الملفات الجديدة فقط</span>
            <input
              type="checkbox"
              checked={settings.show_new_profiles_only}
              onChange={(e) => setSettings({ ...settings, show_new_profiles_only: e.target.checked })}
              className="w-5 h-5 text-pink-500 rounded focus:ring-pink-500"
            />
          </label>

          <label className="flex items-center justify-between cursor-pointer">
            <span className="text-gray-700">الموثقون فقط</span>
            <input
              type="checkbox"
              checked={settings.show_verified_only}
              onChange={(e) => setSettings({ ...settings, show_verified_only: e.target.checked })}
              className="w-5 h-5 text-pink-500 rounded focus:ring-pink-500"
            />
          </label>
        </Card>
      </main>

      {/* User Bottom Sheet */}
      {selectedUser && (
        <UserBottomSheet
          user={selectedUser}
          onClose={() => setSelectedUser(null)}
          onLike={handleLike}
        />
      )}

      <style jsx>{`
        .slider::-webkit-slider-thumb {
          appearance: none;
          width: 24px;
          height: 24px;
          background: white;
          border: 3px solid #ec4899;
          border-radius: 50%;
          cursor: pointer;
          box-shadow: 0 2px 8px rgba(0, 0, 0, 0.2);
        }
        
        .slider::-moz-range-thumb {
          width: 24px;
          height: 24px;
          background: white;
          border: 3px solid #ec4899;
          border-radius: 50%;
          cursor: pointer;
          box-shadow: 0 2px 8px rgba(0, 0, 0, 0.2);
        }
      `}</style>
    </div>
  );
};

export default DiscoverySettings;
