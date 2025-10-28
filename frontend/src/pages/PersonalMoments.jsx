import React, { useState, useEffect, useContext } from 'react';
import { useTranslation } from 'react-i18next';
import { AuthContext } from '../../context/AuthContext';
import PersonalCard from '../../modules/personal/PersonalCard';
import BottomNav from '../../components/BottomNav';
import '../../styles/personal.css';

const PersonalMoments = () => {
  const { t } = useTranslation('personal');
  const { user } = useContext(AuthContext);
  const [moments, setMoments] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchPersonalMoments();
  }, []);

  const fetchPersonalMoments = async () => {
    try {
      setLoading(true);
      const token = localStorage.getItem('token');
      const backendUrl = process.env.REACT_APP_BACKEND_URL || '';
      
      const response = await fetch(`${backendUrl}/api/personal/list`, {
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json'
        }
      });

      if (response.ok) {
        const data = await response.json();
        setMoments(data.moments || []);
      }
    } catch (error) {
      console.error('Error fetching personal moments:', error);
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-screen bg-gradient-to-br from-pink-50 to-purple-50 dark:from-gray-900 dark:to-gray-800">
        <div className="text-center">
          <div className="animate-spin rounded-full h-16 w-16 border-b-4 border-pink-500 mx-auto mb-4"></div>
          <p className="text-gray-600 dark:text-gray-300">{t('loading')}</p>
        </div>
      </div>
    );
  }

  return (
    <div className="personal-moments-container min-h-screen bg-gradient-to-br from-pink-50 to-purple-50 dark:from-gray-900 dark:to-gray-800 pb-20">
      {/* Header */}
      <header className="bg-white dark:bg-gray-800 shadow-sm sticky top-0 z-10">
        <div className="px-4 py-4">
          <h1 className="text-2xl font-bold text-transparent bg-clip-text bg-gradient-to-r from-pink-500 to-purple-600">
            {t('title')}
          </h1>
          <p className="text-sm text-gray-600 dark:text-gray-300 mt-1">
            {t('subtitle')}
          </p>
        </div>
      </header>

      {/* Moments Grid */}
      <div className="py-6 px-4">
        {moments.length === 0 ? (
          <div className="text-center py-12">
            <div className="text-6xl mb-4">💫</div>
            <p className="text-gray-600 dark:text-gray-300 text-lg">
              {t('no_moments')}
            </p>
          </div>
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            {moments.map((moment) => (
              <PersonalCard key={moment.id} moment={moment} />
            ))}
          </div>
        )}
      </div>

      <BottomNav />
    </div>
  );
};

export default PersonalMoments;
