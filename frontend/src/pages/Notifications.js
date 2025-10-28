import React, { useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { useNotifications } from '../context/NotificationContext';
import { useTranslation } from 'react-i18next';
import { Button } from '../components/ui/button';
import { Card } from '../components/ui/card';
import { ArrowRight, Check, Trash2, Heart, MessageCircle, Star, Users } from 'lucide-react';
import { formatDistanceToNow } from 'date-fns';
import { ar, fr, es, de, tr, it, ptBR, ru, enUS } from 'date-fns/locale';

const Notifications = () => {
  const navigate = useNavigate();
  const { t, i18n } = useTranslation('notifications');
  const {
    notifications,
    unreadCount,
    loading,
    fetchNotifications,
    markAsRead,
    markAllAsRead,
    deleteNotification
  } = useNotifications();

  useEffect(() => {
    fetchNotifications();
  }, []);

  // Get date-fns locale based on current language
  const getDateLocale = () => {
    const localeMap = {
      'ar': ar,
      'fr': fr,
      'es': es,
      'de': de,
      'tr': tr,
      'it': it,
      'pt-BR': ptBR,
      'ru': ru,
      'en': enUS
    };
    return localeMap[i18n.language] || enUS;
  };

  const getNotificationIcon = (type) => {
    switch (type) {
      case 'new_match':
        return <Heart className="w-6 h-6 text-pink-500" />;
      case 'new_message':
        return <MessageCircle className="w-6 h-6 text-blue-500" />;
      case 'new_like':
        return <Heart className="w-6 h-6 text-red-500" />;
      case 'super_like':
        return <Star className="w-6 h-6 text-yellow-500" />;
      case 'profile_view':
        return <Users className="w-6 h-6 text-purple-500" />;
      default:
        return <MessageCircle className="w-6 h-6 text-gray-500" />;
    }
  };

  const handleNotificationClick = async (notification) => {
    if (!notification.is_read) {
      await markAsRead(notification.id);
    }
    
    if (notification.link) {
      navigate(notification.link);
    }
  };

  const formatTime = (dateString) => {
    try {
      return formatDistanceToNow(new Date(dateString), {
        addSuffix: true,
        locale: getDateLocale()
      });
    } catch (error) {
      return t('justNow');
    }
  };

  if (loading && notifications.length === 0) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-pink-50 via-pink-25 to-rose-50 dark:from-gray-200 dark:via-gray-300 dark:to-gray-400 pb-20" dir="rtl">
        <div className="flex items-center justify-center h-screen">
          <div className="text-center">
            <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-pink-500 mx-auto mb-4"></div>
            <p className="text-gray-600 dark:text-gray-700">جاري التحميل...</p>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-pink-50 via-pink-25 to-rose-50 dark:from-gray-200 dark:via-gray-300 dark:to-gray-400 pb-20" dir="rtl">
      {/* Header */}
      <header className="bg-pink-50/80 dark:bg-gray-200 shadow-sm p-4 sticky top-0 z-10 backdrop-blur-sm">
        <div className="flex items-center justify-between">
          <button onClick={() => navigate(-1)} className="p-2 hover:bg-gray-100 dark:hover:bg-gray-300 rounded-full">
            <ArrowRight className="w-6 h-6 dark:text-gray-900" />
          </button>
          <div className="text-center flex-1">
            <h1 className="text-xl font-bold dark:text-gray-900">الإشعارات</h1>
            {unreadCount > 0 && (
              <p className="text-sm text-gray-600 dark:text-gray-700">{unreadCount} غير مقروءة</p>
            )}
          </div>
          {unreadCount > 0 && (
            <Button
              variant="ghost"
              size="sm"
              onClick={markAllAsRead}
              className="text-pink-600"
            >
              <Check className="w-4 h-4 ml-1" />
              قراءة الكل
            </Button>
          )}
        </div>
      </header>

      <main className="max-w-3xl mx-auto p-4 space-y-3">
        {notifications.length === 0 ? (
          <Card className="p-12 text-center dark:bg-gray-200">
            <div className="text-6xl mb-4">🔔</div>
            <h2 className="text-xl font-bold mb-2 dark:text-gray-900">لا توجد إشعارات</h2>
            <p className="text-gray-600 dark:text-gray-700">
              سنخبرك عندما يكون هناك شيء جديد!
            </p>
          </Card>
        ) : (
          notifications.map((notification) => (
            <Card
              key={notification.id}
              className={`p-4 cursor-pointer transition-all hover:shadow-md ${
                !notification.is_read ? 'bg-pink-50 dark:bg-pink-100 border-l-4 border-pink-500' : 'dark:bg-gray-200'
              }`}
              onClick={() => handleNotificationClick(notification)}
            >
              <div className="flex items-start gap-3">
                {/* Icon */}
                <div className="flex-shrink-0 mt-1">
                  {getNotificationIcon(notification.type)}
                </div>

                {/* Content */}
                <div className="flex-1 min-w-0">
                  <div className="flex items-start justify-between gap-2">
                    <div className="flex-1">
                      <h3 className="font-bold text-gray-900 dark:text-gray-900 mb-1">
                        {notification.title}
                      </h3>
                      <p className="text-gray-700 dark:text-gray-800 text-sm mb-2">
                        {notification.message}
                      </p>
                      <p className="text-xs text-gray-500 dark:text-gray-600">
                        {formatTime(notification.created_at)}
                      </p>
                    </div>

                    {/* Photo */}
                    {notification.related_user_photo && (
                      <img
                        src={notification.related_user_photo}
                        alt={notification.related_user_name}
                        className="w-12 h-12 rounded-full object-cover"
                      />
                    )}
                  </div>
                </div>

                {/* Delete button */}
                <button
                  onClick={(e) => {
                    e.stopPropagation();
                    deleteNotification(notification.id);
                  }}
                  className="flex-shrink-0 p-2 hover:bg-gray-100 dark:hover:bg-gray-300 rounded-full transition-colors"
                >
                  <Trash2 className="w-4 h-4 text-gray-500" />
                </button>
              </div>
            </Card>
          ))
        )}
      </main>
    </div>
  );
};

export default Notifications;
