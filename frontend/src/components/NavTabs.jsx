import React from 'react';
import { NavLink } from 'react-router-dom';
import { motion } from 'framer-motion';
import { useTranslation } from 'react-i18next';

const Tab = ({ to, icon, label, badge }) => {
  const { t } = useTranslation('common');
  
  return (
    <NavLink 
      to={to} 
      className={({ isActive }) =>
        `flex flex-col items-center justify-center gap-1 flex-1 py-2 relative transition-all duration-200 ${
          isActive 
            ? "text-white" 
            : "text-gray-500 hover:text-gray-700"
        }`
      }
    >
      {({ isActive }) => (
        <>
          {isActive && (
            <motion.div
              layoutId="activeTab"
              className="absolute inset-0 bg-gradient-to-r from-pink-500 to-orange-400 rounded-2xl mx-1 shadow-lg"
              initial={false}
              transition={{
                type: "spring",
                stiffness: 500,
                damping: 30
              }}
            />
          )}
          <div className="relative z-10 flex flex-col items-center gap-1">
            <div className="relative">
              {icon}
              {badge && badge > 0 ? (
                <motion.span
                  initial={{ scale: 0 }}
                  animate={{ scale: 1 }}
                  transition={{
                    type: "spring",
                    stiffness: 500,
                    damping: 15
                  }}
                  className="absolute -top-2 -right-2 bg-yellow-400 text-black text-[10px] font-bold rounded-full min-w-[18px] h-[18px] flex items-center justify-center px-1"
                >
                  {badge > 99 ? '99+' : badge}
                </motion.span>
              ) : null}
            </div>
            <span className="text-[11px] font-medium">{label}</span>
          </div>
        </>
      )}
    </NavLink>
  );
};

export default function NavTabs({ likesCount = 0, messagesCount = 0 }) {
  const { t } = useTranslation(['common']);
  
  return (
    <motion.nav
      initial={{ y: 100 }}
      animate={{ y: 0 }}
      className="fixed bottom-0 inset-x-0 bg-white/90 backdrop-blur-lg border-t border-gray-200 px-2 py-1 z-50 flex safe-area-bottom"
      style={{ 
        boxShadow: '0 -2px 16px rgba(0, 0, 0, 0.08)'
      }}
    >
      <Tab 
        to="/home" 
        label={t('common:home')}
        icon={
          <svg className="w-7 h-7" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
            <path d="M3 9l9-7 9 7v11a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2z"/>
            <polyline points="9 22 9 12 15 12 15 22"/>
          </svg>
        }
      />
      
      <Tab 
        to="/discovery" 
        label={t('common:discover')}
        icon={
          <svg className="w-7 h-7" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
            <circle cx="12" cy="12" r="10"/>
            <polygon points="16.24 7.76 14.12 14.12 7.76 16.24 9.88 9.88 16.24 7.76"/>
          </svg>
        }
      />
      
      <Tab 
        to="/likes" 
        label={t('common:likes')}
        badge={likesCount}
        icon={
          <svg className="w-7 h-7" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
            <path d="M20.84 4.61a5.5 5.5 0 0 0-7.78 0L12 5.67l-1.06-1.06a5.5 5.5 0 0 0-7.78 7.78l1.06 1.06L12 21.23l7.78-7.78 1.06-1.06a5.5 5.5 0 0 0 0-7.78z"/>
          </svg>
        }
      />
      
      <Tab 
        to="/chat" 
        label={t('common:chat')}
        badge={messagesCount}
        icon={
          <svg className="w-7 h-7" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
            <path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z"/>
          </svg>
        }
      />
      
      <Tab 
        to="/profile" 
        label={t('common:account')}
        icon={
          <svg className="w-7 h-7" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
            <path d="M20 21v-2a4 4 0 0 0-4-4H8a4 4 0 0 0-4 4v2"/>
            <circle cx="12" cy="7" r="4"/>
          </svg>
        }
      />
    </motion.nav>
  );
}
