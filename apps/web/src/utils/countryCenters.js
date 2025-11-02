// Country centroids for map centering when GPS is not available
export const COUNTRY_CENTERS = {
  'SA': { lat: 24.7, lng: 46.7, zoom: 6 },      // Saudi Arabia
  'EG': { lat: 26.8, lng: 30.8, zoom: 5 },      // Egypt
  'CH': { lat: 46.8182, lng: 8.2275, zoom: 7 }, // Switzerland
  'FR': { lat: 46.2276, lng: 2.2137, zoom: 6 }, // France
  'ES': { lat: 40.4637, lng: -3.7492, zoom: 6 }, // Spain
  'GB': { lat: 54.0, lng: -2.0, zoom: 6 },      // United Kingdom
  'TR': { lat: 39.0, lng: 35.0, zoom: 6 },      // Turkey
  'IT': { lat: 41.9, lng: 12.5, zoom: 6 },      // Italy
  'RU': { lat: 61.5, lng: 105.3, zoom: 3 },     // Russia
  'DE': { lat: 51.1657, lng: 10.4515, zoom: 6 }, // Germany
  'BR': { lat: -14.2350, lng: -51.9253, zoom: 4 }, // Brazil
  'US': { lat: 37.0902, lng: -95.7129, zoom: 4 }, // USA
  'CA': { lat: 56.1304, lng: -106.3468, zoom: 4 }, // Canada
  'AU': { lat: -25.2744, lng: 133.7751, zoom: 4 }, // Australia
  'IN': { lat: 20.5937, lng: 78.9629, zoom: 5 },  // India
  'CN': { lat: 35.8617, lng: 104.1954, zoom: 4 }, // China
  'JP': { lat: 36.2048, lng: 138.2529, zoom: 5 }, // Japan
  'AE': { lat: 23.4241, lng: 53.8478, zoom: 7 },  // UAE
  'QA': { lat: 25.3548, lng: 51.1839, zoom: 8 },  // Qatar
  'KW': { lat: 29.3117, lng: 47.4818, zoom: 8 },  // Kuwait
  'MA': { lat: 31.7917, lng: -7.0926, zoom: 6 },  // Morocco
  'TN': { lat: 33.8869, lng: 9.5375, zoom: 7 },   // Tunisia
  'DZ': { lat: 28.0339, lng: 1.6596, zoom: 5 },   // Algeria
  'LB': { lat: 33.8547, lng: 35.8623, zoom: 8 },  // Lebanon
  'JO': { lat: 30.5852, lng: 36.2384, zoom: 7 },  // Jordan
  'IQ': { lat: 33.2232, lng: 43.6793, zoom: 6 },  // Iraq
  'SY': { lat: 34.8021, lng: 38.9968, zoom: 7 },  // Syria
  'YE': { lat: 15.5527, lng: 48.5164, zoom: 6 },  // Yemen
  'OM': { lat: 21.4735, lng: 55.9754, zoom: 6 },  // Oman
};

export const DEFAULT_CENTER = { lat: 20, lng: 0, zoom: 2 }; // Global fallback
export const DEFAULT_RADIUS = 25; // Default radius in km
