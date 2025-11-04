import React, { useState } from 'react';
import { ChevronDown, Search } from 'lucide-react';
import { COUNTRY_CODES } from '../utils/countryCodes';
import { useTranslation } from 'react-i18next';

const CountryCodeSelector = ({ selectedCountry, onChange }) => {
  const { i18n } = useTranslation();
  const [isOpen, setIsOpen] = useState(false);
  const [searchTerm, setSearchTerm] = useState('');
  
  const isRTL = i18n.language === 'ar';

  const filteredCountries = COUNTRY_CODES.filter(country => {
    const search = searchTerm.toLowerCase();
    return (
      country.name.toLowerCase().includes(search) ||
      country.nameAr.includes(searchTerm) ||
      country.dial.includes(search) ||
      country.code.toLowerCase().includes(search)
    );
  });

  const handleSelect = (country) => {
    onChange(country);
    setIsOpen(false);
    setSearchTerm('');
  };

  return (
    <div className="relative">
      {/* Selected Country Display */}
      <button
        type="button"
        onClick={() => setIsOpen(!isOpen)}
        className="flex items-center gap-2 px-3 py-3 bg-gray-50 dark:bg-gray-700 rounded-lg border border-gray-300 dark:border-gray-600 hover:border-pink-500 transition-colors"
      >
        <span className="text-2xl">{selectedCountry.flag}</span>
        <span className="font-semibold text-gray-900 dark:text-white">{selectedCountry.dial}</span>
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
          
          {/* Dropdown Menu */}
          <div className={`absolute ${isRTL ? 'left-0' : 'right-0'} mt-2 w-80 bg-white dark:bg-gray-800 rounded-xl shadow-2xl border border-gray-200 dark:border-gray-700 z-50 max-h-96 overflow-hidden flex flex-col`}>
            {/* Search */}
            <div className="p-3 border-b border-gray-200 dark:border-gray-700">
              <div className="relative">
                <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-gray-400" />
                <input
                  type="text"
                  placeholder="Search country..."
                  value={searchTerm}
                  onChange={(e) => setSearchTerm(e.target.value)}
                  className="w-full pl-10 pr-3 py-2 bg-gray-50 dark:bg-gray-700 rounded-lg border border-gray-300 dark:border-gray-600 focus:border-pink-500 focus:outline-none text-sm"
                  autoFocus
                />
              </div>
            </div>

            {/* Country List */}
            <div className="overflow-y-auto">
              {filteredCountries.length > 0 ? (
                filteredCountries.map((country) => (
                  <button
                    key={country.code}
                    type="button"
                    onClick={() => handleSelect(country)}
                    className={`w-full flex items-center gap-3 px-4 py-3 hover:bg-gray-50 dark:hover:bg-gray-700 transition-colors ${
                      selectedCountry.code === country.code ? 'bg-pink-50 dark:bg-pink-900/20' : ''
                    }`}
                  >
                    <span className="text-2xl">{country.flag}</span>
                    <div className="flex-1 text-left">
                      <p className="font-medium text-gray-900 dark:text-white text-sm">
                        {isRTL ? country.nameAr : country.name}
                      </p>
                      <p className="text-xs text-gray-500 dark:text-gray-400">
                        {country.code}
                      </p>
                    </div>
                    <span className="font-semibold text-gray-700 dark:text-gray-300 text-sm">
                      {country.dial}
                    </span>
                  </button>
                ))
              ) : (
                <div className="p-8 text-center text-gray-500 dark:text-gray-400">
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

export default CountryCodeSelector;
