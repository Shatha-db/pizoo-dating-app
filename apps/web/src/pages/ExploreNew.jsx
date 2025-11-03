import { useState, useEffect } from 'react';
import { useTranslation } from 'react-i18next';
import { useAuth } from '../context/AuthContext';
import ExploreRow from '../modules/explore/ExploreRow';
import BottomNav from '../components/BottomNav';
import '../styles/explore.css';

const ExploreNew = () => {
  const { t } = useTranslation('explore');
  const { user } = useAuth();
  const [sections, setSections] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchExploreSections();
  }, []);

  const fetchExploreSections = async () => {
    try {
      setLoading(true);
      const token = localStorage.getItem('token');
      const backendUrl = process.env.REACT_APP_BACKEND_URL || '';
      
      const response = await fetch(`${backendUrl}/api/explore/sections`, {
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json'
        }
      });

      if (response.ok) {
        const data = await response.json();
        setSections(data.sections || []);
      }
    } catch (error) {
      console.error('Error fetching explore sections:', error);
    } finally {
      setLoading(false);
    }
  };

  const translateSectionTitle = (type) => {
    // Map section types to translation keys
    const typeMap = {
      'most_active': 'most_active',
      'ready_chat': 'ready_chat',
      'near_you': 'near_you',
      'new_faces': 'new_faces',
      'serious_love': 'serious_love',
      'fun_date': 'fun_date',
      'smart_talks': 'smart_talks',
      'friends_only': 'friends_only',
      // Legacy support
      'trending': 'most_active',
      'nearby': 'near_you',
      'newcomers': 'new_faces'
    };
    
    const key = typeMap[type] || type;
    return t(key);
  };

  const handleSeeAll = (sectionType) => {
    // Navigate to filtered view or show all profiles of this type
    console.log('See all clicked for:', sectionType);
    // TODO: Implement navigation or filtering
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
    <div className="explore-new-container min-h-screen bg-gradient-to-br from-pink-50 to-purple-50 dark:from-gray-900 dark:to-gray-800 pb-24">
      {/* Header */}
      <header className="bg-white dark:bg-gray-800 shadow-sm sticky top-0 z-10">
        <div className="px-4 py-4">
          <h1 className="text-2xl font-bold text-transparent bg-clip-text bg-gradient-to-r from-pink-500 to-purple-600">
            {t('title')}
          </h1>
        </div>
      </header>

      {/* Sections */}
      <div className="py-6">
        {sections.length === 0 ? (
          <div className="text-center py-12 px-4">
            <div className="text-6xl mb-4">🔍</div>
            <p className="text-gray-600 dark:text-gray-300 text-lg">
              {t('no_profiles')}
            </p>
          </div>
        ) : (
          sections.map((section, index) => (
            <ExploreRow
              key={index}
              title={translateSectionTitle(section.type)}
              profiles={section.profiles}
              onSeeAll={() => handleSeeAll(section.type)}
            />
          ))
        )}
      </div>

      <BottomNav />
    </div>
  );
};

export default ExploreNew;
