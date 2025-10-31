/**
 * Geo Utilities for Pizoo
 * Handles GPS, reverse geocoding, and GeoIP fallback
 */

// Country-specific discovery defaults
export const COUNTRY_DEFAULTS = {
  // GCC Countries (Small)
  'BH': { radius: 10, label: 'Bahrain', flag: '🇧🇭' },
  'QA': { radius: 15, label: 'Qatar', flag: '🇶🇦' },
  'KW': { radius: 20, label: 'Kuwait', flag: '🇰🇼' },
  
  // Medium Countries
  'AE': { radius: 25, label: 'UAE', flag: '🇦🇪' },
  'OM': { radius: 30, label: 'Oman', flag: '🇴🇲' },
  'LB': { radius: 20, label: 'Lebanon', flag: '🇱🇧' },
  'JO': { radius: 25, label: 'Jordan', flag: '🇯🇴' },
  
  // Large Countries
  'SA': { radius: 50, label: 'Saudi Arabia', flag: '🇸🇦' },
  'EG': { radius: 50, label: 'Egypt', flag: '🇪🇬' },
  'IQ': { radius: 50, label: 'Iraq', flag: '🇮🇶' },
  'MA': { radius: 50, label: 'Morocco', flag: '🇲🇦' },
  'DZ': { radius: 75, label: 'Algeria', flag: '🇩🇿' },
  
  // Europe
  'FR': { radius: 50, label: 'France', flag: '🇫🇷' },
  'DE': { radius: 40, label: 'Germany', flag: '🇩🇪' },
  'ES': { radius: 50, label: 'Spain', flag: '🇪🇸' },
  'IT': { radius: 40, label: 'Italy', flag: '🇮🇹' },
  'GB': { radius: 40, label: 'United Kingdom', flag: '🇬🇧' },
  'TR': { radius: 50, label: 'Turkey', flag: '🇹🇷' },
  
  // Americas
  'US': { radius: 100, label: 'United States', flag: '🇺🇸' },
  'CA': { radius: 100, label: 'Canada', flag: '🇨🇦' },
  'BR': { radius: 100, label: 'Brazil', flag: '🇧🇷' },
  'MX': { radius: 75, label: 'Mexico', flag: '🇲🇽' },
  
  // Default fallback
  'default': { radius: 25, label: 'Global', flag: '🌍' }
};

/**
 * Get current GPS location
 * @returns {Promise<{latitude: number, longitude: number}>}
 */
export const getCurrentPosition = () => {
  return new Promise((resolve, reject) => {
    if (!navigator.geolocation) {
      reject(new Error('Geolocation not supported'));
      return;
    }

    navigator.geolocation.getCurrentPosition(
      (position) => {
        resolve({
          latitude: position.coords.latitude,
          longitude: position.coords.longitude,
          accuracy: position.coords.accuracy
        });
      },
      (error) => {
        reject(error);
      },
      {
        enableHighAccuracy: true,
        timeout: 10000,
        maximumAge: 0
      }
    );
  });
};

/**
 * Reverse geocode coordinates to get country
 * Uses Nominatim (OpenStreetMap) - Free API
 * @param {number} latitude 
 * @param {number} longitude 
 * @returns {Promise<{country: string, countryCode: string, city: string}>}
 */
export const reverseGeocode = async (latitude, longitude) => {
  try {
    const response = await fetch(
      `https://nominatim.openstreetmap.org/reverse?format=json&lat=${latitude}&lon=${longitude}&accept-language=en`,
      {
        headers: {
          'User-Agent': 'Pizoo Dating App'
        }
      }
    );

    if (!response.ok) {
      throw new Error('Reverse geocoding failed');
    }

    const data = await response.json();
    
    if (!data.address) {
      throw new Error('No address found');
    }

    return {
      country: data.address.country || 'Unknown',
      countryCode: data.address.country_code?.toUpperCase() || null,
      city: data.address.city || data.address.town || data.address.village || 'Unknown',
      state: data.address.state || null
    };
  } catch (error) {
    console.error('Reverse geocoding error:', error);
    throw error;
  }
};

/**
 * Get country from IP address (GeoIP fallback)
 * Uses ipapi.co - Free tier: 1000 requests/day
 * @returns {Promise<{country: string, countryCode: string, city: string}>}
 */
export const getCountryFromIP = async () => {
  try {
    const response = await fetch('https://ipapi.co/json/');
    
    if (!response.ok) {
      throw new Error('GeoIP lookup failed');
    }

    const data = await response.json();
    
    return {
      country: data.country_name || 'Unknown',
      countryCode: data.country_code || null,
      city: data.city || 'Unknown',
      region: data.region || null,
      ip: data.ip
    };
  } catch (error) {
    console.error('GeoIP error:', error);
    throw error;
  }
};

/**
 * Get default radius for country
 * @param {string} countryCode - ISO 3166-1 alpha-2 code
 * @returns {number} - Default radius in km
 */
export const getDefaultRadius = (countryCode) => {
  if (!countryCode) return COUNTRY_DEFAULTS.default.radius;
  
  const country = COUNTRY_DEFAULTS[countryCode.toUpperCase()];
  return country ? country.radius : COUNTRY_DEFAULTS.default.radius;
};

/**
 * Get country info
 * @param {string} countryCode 
 * @returns {object} - Country info (radius, label, flag)
 */
export const getCountryInfo = (countryCode) => {
  if (!countryCode) return COUNTRY_DEFAULTS.default;
  
  return COUNTRY_DEFAULTS[countryCode.toUpperCase()] || COUNTRY_DEFAULTS.default;
};

/**
 * Calculate distance between two coordinates (Haversine formula)
 * @param {number} lat1 
 * @param {number} lon1 
 * @param {number} lat2 
 * @param {number} lon2 
 * @returns {number} - Distance in kilometers
 */
export const calculateDistance = (lat1, lon1, lat2, lon2) => {
  const R = 6371; // Earth's radius in km
  const dLat = (lat2 - lat1) * Math.PI / 180;
  const dLon = (lon2 - lon1) * Math.PI / 180;
  
  const a = 
    Math.sin(dLat / 2) * Math.sin(dLat / 2) +
    Math.cos(lat1 * Math.PI / 180) * Math.cos(lat2 * Math.PI / 180) *
    Math.sin(dLon / 2) * Math.sin(dLon / 2);
  
  const c = 2 * Math.atan2(Math.sqrt(a), Math.sqrt(1 - a));
  const distance = R * c;
  
  return Math.round(distance);
};

/**
 * Validate coordinates
 * @param {number} latitude 
 * @param {number} longitude 
 * @returns {boolean}
 */
export const validateCoordinates = (latitude, longitude) => {
  if (typeof latitude !== 'number' || typeof longitude !== 'number') {
    return false;
  }
  
  if (!Number.isFinite(latitude) || !Number.isFinite(longitude)) {
    return false;
  }
  
  if (latitude < -90 || latitude > 90) {
    return false;
  }
  
  if (longitude < -180 || longitude > 180) {
    return false;
  }
  
  return true;
};
