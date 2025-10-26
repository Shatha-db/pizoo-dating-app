import React, { useEffect, useState, Suspense } from 'react';
import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import { AuthProvider } from './context/AuthContext';
import { WebSocketProvider } from './context/WebSocketContext';
import { ThemeProvider } from './context/ThemeContext';
import { NotificationProvider } from './context/NotificationContext';
import ProtectedRoute from './components/ProtectedRoute';
import Register from './pages/Register';
import Login from './pages/Login';
import AddPayment from './pages/AddPayment';
import ProfileSetup from './pages/ProfileSetup';
import Discover from './pages/Discover';
import Home from './pages/Home';
import Explore from './pages/Explore';
import Likes from './pages/Likes';
import LikesYou from './pages/LikesYou';
import Matches from './pages/Matches';
import ChatList from './pages/ChatList';
import ChatRoom from './pages/ChatRoom';
import Profile from './pages/Profile';
import ProfileNew from './pages/ProfileNew';
import ProfileView from './pages/ProfileView';
import EditProfile from './pages/EditProfile';
import TopPicks from './pages/TopPicks';
// ⚠️ Lazy load DiscoverySettings to prevent Leaflet loading on every page
const DiscoverySettings = React.lazy(() => import('./pages/DiscoverySettings'));
import DoubleDating from './pages/DoubleDating';
import DoubleDatingInfo from './pages/DoubleDatingInfo';
import Notifications from './pages/Notifications';
import Premium from './pages/Premium';
import Settings from './pages/Settings';
import TermsNew from './pages/TermsNew';
import CustomLogoPage from './pages/CustomLogoPage';
import SwipePage from './pages/SwipePage';
import { Toaster } from './components/ui/sonner';
import { useTranslation } from 'react-i18next';
import Loader from './components/Loader';
import './App.css';

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;

function AppRoot() {
  const { i18n } = useTranslation();
  const [ready, setReady] = useState(false);

  useEffect(() => {
    let done = false;
    // ⚠️ Timeout guard: prevent infinite white screen if /api/me hangs
    const timer = setTimeout(() => {
      if (!done) {
        console.warn('⏱️ App init timeout - forcing ready state');
        setReady(true);
      }
    }, 2000);

    (async () => {
      try {
        const token = localStorage.getItem('token');
        if (token) {
          const r = await fetch(`${BACKEND_URL}/api/me`, {
            headers: { Authorization: `Bearer ${token}` },
          });
          if (r.ok) {
            const me = await r.json();
            if (me?.language && i18n.language !== me.language) {
              await i18n.changeLanguage(me.language);
              console.log('✅ Language loaded from /me API:', me.language);
            }
          }
        }
      } catch (e) {
        console.warn('me fetch failed', e);
      } finally {
        done = true;
        setReady(true);
        clearTimeout(timer);
      }
    })();

    return () => clearTimeout(timer);
  }, [i18n]);

  if (!ready) {
    return (
      <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'center', minHeight: '100vh' }}>
        <div style={{ textAlign: 'center' }}>
          <div style={{ width: '64px', height: '64px', margin: '0 auto 1rem', border: '4px solid #ec4899', borderTopColor: 'transparent', borderRadius: '50%', animation: 'spin 1s linear infinite' }}></div>
          <p>Loading...</p>
        </div>
      </div>
    );
  }

  return (
    <div key={i18n.language}>
      <AuthProvider>
        <ThemeProvider>
          <NotificationProvider>
            <WebSocketProvider>
              <BrowserRouter>
                <Routes>
                  <Route path="/" element={<Navigate to="/login" replace />} />
                  <Route path="/register" element={<Register />} />
                  <Route path="/login" element={<Login />} />
                  <Route path="/terms" element={<TermsNew />} />
                  <Route path="/privacy" element={<TermsNew />} />
                  <Route path="/cookies" element={<TermsNew />} />
                  <Route path="/custom-logo" element={<CustomLogoPage />} />
                  <Route path="/dashboard" element={<Navigate to="/home" replace />} />
                  <Route
                    path="/add-payment"
                    element={
                      <ProtectedRoute>
                        <AddPayment />
                      </ProtectedRoute>
                    }
                  />
                  <Route
                    path="/profile/setup"
                    element={
                      <ProtectedRoute>
                        <ProfileSetup />
                      </ProtectedRoute>
                    }
                  />
                  <Route
                    path="/discover"
                    element={
                      <ProtectedRoute>
                        <Discover />
                      </ProtectedRoute>
                    }
                  />
                  <Route
                    path="/home"
                    element={
                      <ProtectedRoute>
                        <Home />
                      </ProtectedRoute>
                    }
                  />
                  <Route
                    path="/swipe"
                    element={
                      <ProtectedRoute>
                        <SwipePage />
                      </ProtectedRoute>
                    }
                  />
                  <Route
                    path="/explore"
                    element={
                      <ProtectedRoute>
                        <Explore />
                      </ProtectedRoute>
                    }
                  />
                  <Route
                    path="/top-picks"
                    element={
                      <ProtectedRoute>
                        <TopPicks />
                      </ProtectedRoute>
                    }
                  />
                  <Route
                    path="/discovery-settings"
                    element={
                      <ProtectedRoute>
                        <DiscoverySettings />
                      </ProtectedRoute>
                    }
                  />
                  <Route
                    path="/discovery"
                    element={
                      <ProtectedRoute>
                        <DiscoverySettings />
                      </ProtectedRoute>
                    }
                  />
                  <Route
                    path="/double-dating"
                    element={
                      <ProtectedRoute>
                        <DoubleDating />
                      </ProtectedRoute>
                    }
                  />
                  <Route
                    path="/double-dating-info"
                    element={
                      <ProtectedRoute>
                        <DoubleDatingInfo />
                      </ProtectedRoute>
                    }
                  />
                  <Route
                    path="/likes"
                    element={
                      <ProtectedRoute>
                        <Likes />
                      </ProtectedRoute>
                    }
                  />
                  <Route
                    path="/matches"
                    element={
                      <ProtectedRoute>
                        <Matches />
                      </ProtectedRoute>
                    }
                  />
                  <Route
                    path="/profile"
                    element={
                      <ProtectedRoute>
                        <ProfileNew />
                      </ProtectedRoute>
                    }
                  />
                  <Route
                    path="/profile/old"
                    element={
                      <ProtectedRoute>
                        <Profile />
                      </ProtectedRoute>
                    }
                  />
                  <Route
                    path="/profile/edit"
                    element={
                      <ProtectedRoute>
                        <EditProfile />
                      </ProtectedRoute>
                    }
                  />
                  <Route
                    path="/profile/:userId"
                    element={
                      <ProtectedRoute>
                        <ProfileView />
                      </ProtectedRoute>
                    }
                  />
                  <Route
                    path="/likes-you"
                    element={
                      <ProtectedRoute>
                        <LikesYou />
                      </ProtectedRoute>
                    }
                  />
                  <Route
                    path="/notifications"
                    element={
                      <ProtectedRoute>
                        <Notifications />
                      </ProtectedRoute>
                    }
                  />

                  <Route
                    path="/premium"
                    element={
                      <ProtectedRoute>
                        <Premium />
                      </ProtectedRoute>
                    }
                  />
                  <Route
                    path="/chat"
                    element={
                      <ProtectedRoute>
                        <ChatList />
                      </ProtectedRoute>
                    }
                  />
                  <Route
                    path="/chat/:matchId"
                    element={
                      <ProtectedRoute>
                        <ChatRoom />
                      </ProtectedRoute>
                    }
                  />
                  <Route
                    path="/settings"
                    element={
                      <ProtectedRoute>
                        <Settings />
                      </ProtectedRoute>
                    }
                  />
                </Routes>
                <Toaster />
              </BrowserRouter>
            </WebSocketProvider>
          </NotificationProvider>
        </ThemeProvider>
      </AuthProvider>
    </div>
  );
}

export default AppRoot;
