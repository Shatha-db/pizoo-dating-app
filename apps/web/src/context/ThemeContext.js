import React, { createContext, useContext, useState, useEffect } from 'react';
import axios from 'axios';
import { useAuth } from './AuthContext';

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

const ThemeContext = createContext();

export const useTheme = () => {
  const context = useContext(ThemeContext);
  if (!context) {
    throw new Error('useTheme must be used within ThemeProvider');
  }
  return context;
};

export const ThemeProvider = ({ children }) => {
  const { token } = useAuth();
  const [theme, setTheme] = useState('system');
  const [actualTheme, setActualTheme] = useState('light'); // The actual applied theme
  const [loading, setLoading] = useState(true);

  // Fetch theme from backend settings
  useEffect(() => {
    if (token) {
      fetchThemeSettings();
    } else {
      // If not logged in, use system theme
      applySystemTheme();
      setLoading(false);
    }
  }, [token]);

  // Apply theme when it changes
  useEffect(() => {
    applyTheme(theme);
  }, [theme]);

  const fetchThemeSettings = async () => {
    try {
      const response = await axios.get(`${API}/settings`, {
        headers: { Authorization: `Bearer ${token}` }
      });
      const userTheme = response.data.theme || 'system';
      setTheme(userTheme);
    } catch (error) {
      console.error('Error fetching theme settings:', error);
      applySystemTheme();
    } finally {
      setLoading(false);
    }
  };

  const applyTheme = (themeValue) => {
    if (themeValue === 'system') {
      applySystemTheme();
    } else if (themeValue === 'dark') {
      document.documentElement.classList.add('dark');
      document.body.classList.add('dark');
      setActualTheme('dark');
    } else {
      document.documentElement.classList.remove('dark');
      document.body.classList.remove('dark');
      setActualTheme('light');
    }
  };

  const applySystemTheme = () => {
    const isDarkMode = window.matchMedia('(prefers-color-scheme: dark)').matches;
    if (isDarkMode) {
      document.documentElement.classList.add('dark');
      document.body.classList.add('dark');
      setActualTheme('dark');
    } else {
      document.documentElement.classList.remove('dark');
      document.body.classList.remove('dark');
      setActualTheme('light');
    }
  };

  const updateTheme = async (newTheme) => {
    setTheme(newTheme);
    
    if (token) {
      try {
        await axios.put(
          `${API}/settings`,
          { theme: newTheme },
          {
            headers: { Authorization: `Bearer ${token}` }
          }
        );
      } catch (error) {
        console.error('Error updating theme:', error);
      }
    }
  };

  // Listen for system theme changes
  useEffect(() => {
    if (theme === 'system') {
      const mediaQuery = window.matchMedia('(prefers-color-scheme: dark)');
      const handleChange = () => applySystemTheme();
      
      mediaQuery.addEventListener('change', handleChange);
      return () => mediaQuery.removeEventListener('change', handleChange);
    }
  }, [theme]);

  const value = {
    theme,
    actualTheme,
    updateTheme,
    loading
  };

  return <ThemeContext.Provider value={value}>{children}</ThemeContext.Provider>;
};
