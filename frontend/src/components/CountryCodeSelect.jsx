import React, { useState } from 'react';
import { ChevronDown, Search } from 'lucide-react';
import { useTranslation } from 'react-i18next';
import { POPULAR_COUNTRIES, getAllCountries } from '../data/countries';

// Get all countries with popular section first
const ALL_COUNTRIES_LIST = getAllCountries();

const CountryCodeSelect = ({ value, onChange, className = '' }) => {
  const { t, i18n } = useTranslation('auth');
  const [isOpen, setIsOpen] = useState(false);
  const [search, setSearch] = useState('');
  
  const selectedCountry = COUNTRIES.find(c => c.dial === value) || COUNTRIES[0];
  
  const filteredCountries = COUNTRIES.filter(country => {
    const searchLower = search.toLowerCase();
    return (
      country.name.toLowerCase().includes(searchLower) ||
      country.nameAr.includes(search) ||
      country.dial.includes(search) ||
      country.code.toLowerCase().includes(searchLower)
    );
  });

  const handleSelect = (country) => {
    onChange(country.dial);
    setIsOpen(false);
    setSearch('');
  };

  return (
    <div className={`relative ${className}`}>
      {/* Selected Country Button */}
      <button
        type="button"
        onClick={() => setIsOpen(!isOpen)}
        className="flex items-center gap-2 px-3 h-12 bg-white border border-gray-300 rounded-lg hover:border-pink-500 transition-colors"
      >
        <span className="text-2xl">{selectedCountry.flag}</span>
        <span className="font-medium text-gray-700">{selectedCountry.dial}</span>
        <ChevronDown className={`w-4 h-4 text-gray-500 transition-transform ${isOpen ? 'rotate-180' : ''}`} />
      </button>

      {/* Dropdown */}
      {isOpen && (
        <>
          {/* Backdrop */}
          <div 
            className="fixed inset-0 z-40" 
            onClick={() => setIsOpen(false)}
          />
          
          {/* Dropdown Content */}
          <div className="absolute top-full mt-2 left-0 right-0 bg-white rounded-lg shadow-xl border border-gray-200 z-50 max-h-96 overflow-hidden flex flex-col">
            {/* Search */}
            <div className="p-3 border-b border-gray-200">
              <div className="relative">
                <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-gray-400" />
                <input
                  type="text"
                  value={search}
                  onChange={(e) => setSearch(e.target.value)}
                  placeholder={t('search_country')}
                  className="w-full pl-10 pr-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-pink-500 focus:border-transparent"
                  autoFocus
                />
              </div>
            </div>

            {/* Countries List */}
            <div className="overflow-y-auto">
              {filteredCountries.length > 0 ? (
                filteredCountries.map((country) => (
                  <button
                    key={country.code}
                    type="button"
                    onClick={() => handleSelect(country)}
                    className={`w-full flex items-center gap-3 px-4 py-3 hover:bg-pink-50 transition-colors ${
                      selectedCountry.code === country.code ? 'bg-pink-100' : ''
                    }`}
                  >
                    <span className="text-2xl">{country.flag}</span>
                    <span className="flex-1 text-left font-medium text-gray-700">
                      {i18n.language === 'ar' ? country.nameAr : country.name}
                    </span>
                    <span className="text-gray-600 font-mono">{country.dial}</span>
                  </button>
                ))
              ) : (
                <div className="px-4 py-8 text-center text-gray-500">
                  No countries found
                </div>
              )}
            </div>
          </div>
        </>
      )}
    </div>
  );
};

export default CountryCodeSelect;
