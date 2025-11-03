import React, { createContext, useState, useContext, useEffect } from 'react';
import axios from 'axios';

const AuthContext = createContext(null);

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

export const AuthProvider = ({ children }) => {
  const [user, setUser] = useState(null);
  const [token, setToken] = useState(null);
  const [loading, setLoading] = useState(true);

  // Initialize auth on mount
  useEffect(() => {
    const storedToken = localStorage.getItem('token');
    const storedUser = localStorage.getItem('user');
    
    if (storedToken) {
      setToken(storedToken);
      if (storedUser) {
        try {
          setUser(JSON.parse(storedUser));
        } catch (e) {
          console.error('Error parsing stored user:', e);
        }
      }
      // Verify token is still valid - wrapped in try-catch
      fetchUserProfile(storedToken).catch(err => {
        console.warn('Token validation failed on init:', err);
        setLoading(false);
      });
    } else {
      setLoading(false);
    }
  }, []);

  const fetchUserProfile = async (authToken = token) => {
    if (!authToken) {
      setLoading(false);
      return;
    }
    
    try {
      const response = await axios.get(`${API}/user/profile`, {
        headers: {
          Authorization: `Bearer ${authToken}`
        }
      });
      setUser(response.data);
      localStorage.setItem('user', JSON.stringify(response.data));
    } catch (error) {
      console.error('Error fetching user profile:', error);
      // Only logout if token is invalid (401)
      if (error.response?.status === 401) {
        logout();
      }
    } finally {
      setLoading(false);
    }
  };

  const login = async (email, password) => {
    try {
      const response = await axios.post(`${API}/auth/login`, {
        email,
        password
      });
      const { access_token, user: userData } = response.data;
      
      // Save to state and localStorage
      setToken(access_token);
      setUser(userData);
      localStorage.setItem('token', access_token);
      localStorage.setItem('user', JSON.stringify(userData));
      
      return { success: true };
    } catch (error) {
      return { 
        success: false, 
        error: error.response?.data?.detail || 'حدث خطأ أثناء تسجيل الدخول'
      };
    }
  };

  const register = async (name, email, phoneNumber, password, termsAccepted) => {
    try {
      const response = await axios.post(`${API}/auth/register`, {
        name,
        email,
        phone_number: phoneNumber,
        password,
        terms_accepted: termsAccepted
      });
      const { access_token, user: userData } = response.data;
      
      // Save to state and localStorage
      setToken(access_token);
      setUser(userData);
      localStorage.setItem('token', access_token);
      localStorage.setItem('user', JSON.stringify(userData));
      
      return { success: true };
    } catch (error) {
      // Handle FastAPI validation errors (array of objects)
      let errorMessage = 'حدث خطأ أثناء التسجيل';
      
      if (error.response?.data?.detail) {
        const detail = error.response.data.detail;
        
        // If detail is an array (validation errors)
        if (Array.isArray(detail)) {
          errorMessage = detail.map(err => {
            const field = err.loc?.[1] || err.loc?.[0] || 'field';
            return `${field}: ${err.msg}`;
          }).join(', ');
        } 
        // If detail is a string
        else if (typeof detail === 'string') {
          errorMessage = detail;
        }
        // If detail is an object with msg
        else if (detail.msg) {
          errorMessage = detail.msg;
        }
      }
      
      return { 
        success: false, 
        error: errorMessage
      };
    }
  };

  const logout = () => {
    setToken(null);
    setUser(null);
    localStorage.removeItem('token');
    localStorage.removeItem('user');
    window.location.href = '/login'; // Redirect to login
  };

  return (
    <AuthContext.Provider value={{ user, token, loading, login, register, logout }}>
      {children}
    </AuthContext.Provider>
  );
};

export const useAuth = () => {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
};