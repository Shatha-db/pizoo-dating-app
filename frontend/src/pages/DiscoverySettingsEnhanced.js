import React, { useEffect, useState, useRef } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import { Button } from '../components/ui/button';
import { Card } from '../components/ui/card';
import { X, MapPin, Users, Calendar, Navigation, ZoomIn, ZoomOut, Maximize2 } from 'lucide-react';
import { MapContainer, TileLayer, Circle, Marker, Popup, useMap, useMapEvents } from 'react-leaflet';
import MarkerClusterGroup from 'react-leaflet-cluster';
import 'leaflet/dist/leaflet.css';
import 'leaflet.markercluster/dist/MarkerCluster.css';
import 'leaflet.markercluster/dist/MarkerCluster.Default.css';
import L from 'leaflet';
import axios from 'axios';

// Fix for default marker icon
delete L.Icon.Default.prototype._getIconUrl;
L.Icon.Default.mergeOptions({
  iconRetinaUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.7.1/images/marker-icon-2x.png',
  iconUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.7.1/images/marker-icon.png',
  shadowUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.7.1/images/marker-shadow.png',
});

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

// Map controller to handle recenter
function MapController({ center, zoom, onBoundsChange }) {
  const map = useMap();
  
  useMapEvents({
    moveend: () => {
      const bounds = map.getBounds();
      if (onBoundsChange) {
        onBoundsChange(bounds);
      }
    },
  });
  
  useEffect(() => {
    map.setView(center, zoom);
  }, [center, zoom, map]);
  
  return null;
}

// Bottom Sheet Component for Profile Preview
function ProfileBottomSheet({ profile, onClose, onLike, onMessage }) {
  if (!profile) return null;

  return (
    <div 
      className="fixed bottom-0 left-0 right-0 bg-white dark:bg-gray-800 rounded-t-3xl shadow-2xl z-[1000] animate-slide-up"
      style={{
        maxHeight: '60vh',
        transition: 'transform 0.3s ease-out'
      }}
    >
      {/* Handle bar */}
      <div className="w-12 h-1.5 bg-gray-300 rounded-full mx-auto mt-3 mb-4"></div>
      
      <div className="px-6 pb-6 overflow-y-auto" style={{ maxHeight: 'calc(60vh - 40px)' }}>
        {/* Profile Header */}
        <div className="flex items-start gap-4 mb-4">
          <div className="relative">
            <img
              src={profile.photos?.[0] || 'https://via.placeholder.com/100'}
              alt={profile.display_name}
              className="w-20 h-20 rounded-full object-cover border-4 border-pink-500"
            />
            {profile.distance && (
              <div className="absolute -bottom-2 left-1/2 transform -translate-x-1/2 bg-pink-500 text-white text-xs px-2 py-0.5 rounded-full whitespace-nowrap">
                {profile.distance} km
              </div>
            )}
          </div>
          
          <div className="flex-1">
            <h3 className="text-2xl font-bold dark:text-white">{profile.display_name}</h3>
            <div className="flex items-center gap-2 text-gray-600 dark:text-gray-300 mt-1">
              <MapPin className="w-4 h-4" />
              <span className="text-sm">{profile.location}</span>
            </div>
          </div>
          
          <button
            onClick={onClose}
            className="p-2 hover:bg-gray-100 dark:hover:bg-gray-700 rounded-full transition-colors"
          >
            <X className="w-6 h-6 dark:text-white" />
          </button>
        </div>

        {/* Bio */}
        {profile.bio && (
          <p className="text-gray-700 dark:text-gray-300 mb-4 line-clamp-3">
            {profile.bio}
          </p>
        )}

        {/* Interests */}
        {profile.interests && profile.interests.length > 0 && (
          <div className="mb-4">
            <h4 className="font-semibold mb-2 dark:text-white">الاهتمامات</h4>
            <div className="flex flex-wrap gap-2">
              {profile.interests.slice(0, 5).map((interest, idx) => (
                <span
                  key={idx}
                  className="px-3 py-1 bg-pink-100 dark:bg-pink-900 text-pink-700 dark:text-pink-200 rounded-full text-sm"
                >
                  {interest}
                </span>
              ))}
            </div>
          </div>
        )}

        {/* Action Buttons */}
        <div className="flex gap-3 mt-4">
          <Button
            onClick={onMessage}
            variant="outline"
            className="flex-1 border-2 border-pink-500 text-pink-500 hover:bg-pink-50 dark:hover:bg-pink-900"
          >
            <MessageCircle className="w-5 h-5 mr-2" />
            رسالة
          </Button>
          <Button
            onClick={onLike}
            className="flex-1 bg-gradient-to-r from-pink-500 to-red-500 text-white"
          >
            <Heart className="w-5 h-5 mr-2" />
            إعجاب
          </Button>
        </div>

        {/* View Full Profile Button */}
        <Button
          onClick={() => window.location.href = `/profile/${profile.user_id}`}
          variant="ghost"
          className="w-full mt-2 text-pink-500"
        >
          عرض الملف الكامل
        </Button>
      </div>
    </div>
  );
}

const DiscoverySettingsEnhanced = () => {
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
  const [userLocation, setUserLocation] = useState({ lat: 47.5596, lng: 7.5886 });
  const [mapCenter, setMapCenter] = useState({ lat: 47.5596, lng: 7.5886 });
  const [mapZoom, setMapZoom] = useState(10);
  const [nearbyProfiles, setNearbyProfiles] = useState([]);
  const [selectedProfile, setSelectedProfile] = useState(null);
  const [locationLoading, setLocationLoading] = useState(false);
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const mapRef = useRef(null);

  useEffect(() => {
    fetchSettings();
    getUserLocation();
    fetchNearbyProfiles();
  }, []);

  const getUserLocation = () => {
    if (navigator.geolocation) {
      navigator.geolocation.getCurrentPosition(
        (position) => {
          const newLocation = {
            lat: position.coords.latitude,
            lng: position.coords.longitude
          };
          setUserLocation(newLocation);
          setMapCenter(newLocation);
        },
        (error) => {
          console.error('Error getting location:', error);
        }
      );
    }
  };

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

  const fetchNearbyProfiles = async () => {
    try {
      const response = await axios.get(`${API}/profiles/discover?limit=50&max_distance=${settings.max_distance}`, {
        headers: { Authorization: `Bearer ${token}` }
      });
      
      // Filter profiles that have GPS coordinates
      const profilesWithLocation = response.data.profiles.filter(
        p => p.latitude && p.longitude
      );
      setNearbyProfiles(profilesWithLocation);
    } catch (error) {
      console.error('Error fetching profiles:', error);
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
        const newLocation = { lat: latitude, lng: longitude };
        setUserLocation(newLocation);
        setMapCenter(newLocation);
        
        try {
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
        } finally {
          setLocationLoading(false);
        }
      },
      (error) => {
        console.error('Error getting location:', error);
        alert('لم نتمكن من الحصول على موقعك');
        setLocationLoading(false);
      }
    );
  };

  const recenterMap = () => {
    setMapCenter(userLocation);
    setMapZoom(12);
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

  const handleProfileLike = async (profile) => {
    try {
      await axios.post(`${API}/swipe`, {
        swiped_user_id: profile.user_id,
        action: 'like'
      }, {
        headers: { Authorization: `Bearer ${token}` }
      });
      alert('تم الإعجاب! 💕');
      setSelectedProfile(null);
    } catch (error) {
      console.error('Error liking profile:', error);
    }
  };

  const handleProfileMessage = (profile) => {
    // Check if match exists, if yes go to chat, else show message
    alert('يجب أن يكون هناك تطابق أولاً');
    setSelectedProfile(null);
  };

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="animate-spin rounded-full h-16 w-16 border-b-4 border-pink-500"></div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50 dark:bg-gray-900 pb-20" dir="rtl">
      {/* Header */}
      <header className="bg-white dark:bg-gray-800 shadow-sm p-4 flex items-center justify-between sticky top-0 z-[999]">
        <Button
          variant="ghost"
          size="icon"
          onClick={() => navigate('/home')}
        >
          <X className="w-6 h-6 dark:text-white" />
        </Button>
        <h1 className="text-xl font-bold dark:text-white">إعدادات الاكتشاف</h1>
        <Button
          onClick={handleSave}
          disabled={saving}
          className="bg-gradient-to-r from-pink-500 to-red-500 hover:from-pink-600 hover:to-red-600 text-white text-sm px-4"
        >
          {saving ? 'جاري الحفظ...' : 'حفظ'}
        </Button>
      </header>

      <main className="max-w-2xl mx-auto p-4 space-y-6">
        {/* Enhanced Map with Clustering */}
        <Card className="p-4">
          <div className="flex items-center gap-3 mb-4">
            <MapPin className="w-6 h-6 text-pink-500" />
            <h2 className="text-lg font-bold dark:text-white">خريطة الاكتشاف</h2>
            <span className="text-sm text-gray-600 dark:text-gray-300">
              ({nearbyProfiles.length} مستخدم قريب)
            </span>
          </div>
          
          {/* Map View with Clustering */}
          <div className="relative mb-4 rounded-lg overflow-hidden border-2 border-gray-200 dark:border-gray-700" style={{ height: '400px' }}>
            <MapContainer 
              center={[mapCenter.lat, mapCenter.lng]} 
              zoom={mapZoom} 
              style={{ height: '100%', width: '100%' }}
              zoomControl={false}
              ref={mapRef}
            >
              <TileLayer
                attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a>'
                url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
              />
              
              {/* User's location marker */}
              <Marker position={[userLocation.lat, userLocation.lng]}>
                <Popup>موقعك الحالي 📍</Popup>
              </Marker>
              
              {/* Distance radius circle */}
              <Circle
                center={[userLocation.lat, userLocation.lng]}
                radius={settings.max_distance * 1000}
                pathOptions={{ 
                  color: '#ec4899', 
                  fillColor: '#ec4899',
                  fillOpacity: 0.1,
                  weight: 2
                }}
              />
              
              {/* Clustered markers for nearby profiles */}
              <MarkerClusterGroup
                chunkedLoading
                maxClusterRadius={60}
                spiderfyOnMaxZoom={true}
                showCoverageOnHover={false}
              >
                {nearbyProfiles.map((profile, idx) => (
                  <Marker
                    key={idx}
                    position={[profile.latitude, profile.longitude]}
                    eventHandlers={{
                      click: () => setSelectedProfile(profile)
                    }}
                  >
                    <Popup>
                      <div className="text-center">
                        <img
                          src={profile.photos?.[0] || 'https://via.placeholder.com/60'}
                          alt={profile.display_name}
                          className="w-16 h-16 rounded-full mx-auto mb-2 object-cover"
                        />
                        <strong>{profile.display_name}</strong>
                        {profile.distance && <p className="text-sm text-gray-600">{profile.distance} km</p>}
                      </div>
                    </Popup>
                  </Marker>
                ))}
              </MarkerClusterGroup>
              
              <MapController center={[mapCenter.lat, mapCenter.lng]} zoom={mapZoom} />
            </MapContainer>
            
            {/* Map Control Buttons */}
            <div className="absolute top-4 left-4 z-[400] flex flex-col gap-2">
              <Button
                onClick={recenterMap}
                size="icon"
                className="bg-white hover:bg-gray-100 shadow-lg"
                title="إعادة التمركز"
              >
                <Navigation className="w-5 h-5 text-pink-500" />
              </Button>
              <Button
                onClick={detectLocation}
                size="icon"
                className="bg-white hover:bg-gray-100 shadow-lg"
                title="تحديد موقعي"
                disabled={locationLoading}
              >
                <MapPin className="w-5 h-5 text-blue-500" />
              </Button>
            </div>
          </div>

          {/* Location Input */}
          <div className="flex gap-2">
            <input
              type="text"
              value={settings.location}
              onChange={(e) => setSettings({ ...settings, location: e.target.value })}
              placeholder="غير الموقع للعثور على مُعجبين في أي مكان"
              className="flex-1 p-3 border rounded-lg focus:ring-2 focus:ring-pink-500 focus:border-transparent dark:bg-gray-700 dark:border-gray-600 dark:text-white"
            />
          </div>
          <p className="text-sm text-gray-500 dark:text-gray-400 mt-2">مثال: Basel, Switzerland</p>
        </Card>

        {/* Distance Slider */}
        <Card className="p-6">
          <h2 className="text-lg font-bold mb-2 dark:text-white">أقصى مسافة</h2>
          <div className="flex items-center justify-between mb-4">
            <span className="text-3xl font-bold text-pink-500">{settings.max_distance} km</span>
            <span className="text-sm text-gray-600 dark:text-gray-300">نطاق البحث</span>
          </div>
          <input
            type="range"
            min="1"
            max="150"
            value={settings.max_distance}
            onChange={(e) => {
              const newDistance = parseInt(e.target.value);
              setSettings({ ...settings, max_distance: newDistance });
              // Refresh profiles when distance changes
              fetchNearbyProfiles();
            }}
            className="w-full h-3 bg-gray-200 rounded-lg appearance-none cursor-pointer accent-pink-500"
          />
          <div className="flex justify-between text-xs text-gray-500 dark:text-gray-400 mt-2">
            <span>1 km</span>
            <span>75 km</span>
            <span>150 km</span>
          </div>
        </Card>

        {/* Other settings (Gender, Age, etc.) - Keep existing */}
        {/* ... rest of settings ... */}
      </main>

      {/* Bottom Sheet for Profile Preview */}
      {selectedProfile && (
        <ProfileBottomSheet
          profile={selectedProfile}
          onClose={() => setSelectedProfile(null)}
          onLike={() => handleProfileLike(selectedProfile)}
          onMessage={() => handleProfileMessage(selectedProfile)}
        />
      )}
    </div>
  );
};

export default DiscoverySettingsEnhanced;
