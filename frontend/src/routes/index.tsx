import React, { useEffect, useState } from 'react';
import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import {SplashPage} from '../pages/splash';
import {LoginPage} from '../pages/login';
import { useSessionGuard } from '../routes/hooks/useSessionsGuard';
import { AppRoutes } from '../routes/types/loginReg';
import { RegisterPage } from '../pages/register';
import { DashboardPage } from '../pages/dashboard';

const LogoutRoute: React.FC = () => {
  useEffect(() => {
    sessionStorage.removeItem('auth_token');
    sessionStorage.removeItem('token');
    sessionStorage.removeItem('user');
    sessionStorage.removeItem('user_data');
    localStorage.removeItem('auth_token');
    localStorage.removeItem('token');
    localStorage.removeItem('user');
    localStorage.removeItem('user_data');
  }, []);

  return <Navigate to={AppRoutes.LOGIN} replace />;
};

const clearAuthSession = () => {
  sessionStorage.removeItem('auth_token');
  sessionStorage.removeItem('token');
  sessionStorage.removeItem('user');
  sessionStorage.removeItem('user_data');
  localStorage.removeItem('auth_token');
  localStorage.removeItem('token');
  localStorage.removeItem('user');
  localStorage.removeItem('user_data');
};

export const AppRouter: React.FC = () => {
  const { saveExitTime } = useSessionGuard();
  const [, setAuthTick] = useState(0);
  const [ready, setReady] = useState(() => {
    const navigation = performance.getEntriesByType('navigation')[0] as PerformanceNavigationTiming | undefined;
    if (navigation?.type === 'reload') {
      clearAuthSession();
    }

    return true;
  });

  const isAuthenticated = () => {
    return Boolean(
      sessionStorage.getItem('auth_token') || sessionStorage.getItem('token')
    );
  };

  useEffect(() => {
    const handleUnload = () => saveExitTime();
    const handleAuthChanged = () => setAuthTick((value) => value + 1);

    setReady(true);
    window.addEventListener('beforeunload', handleUnload);
    window.addEventListener('auth-changed', handleAuthChanged);
    
    return () => {
      window.removeEventListener('beforeunload', handleUnload);
      window.removeEventListener('auth-changed', handleAuthChanged);
    };
  }, []);

  if (!ready) return null;

  return (
    <BrowserRouter>
      <Routes>
        <Route path={AppRoutes.SPLASH} element={<SplashPage />} />

        <Route 
          path={AppRoutes.LOGIN} 
          element={<LoginPage />} 
        />

        <Route 
          path={AppRoutes.REGISTER} 
          element={<RegisterPage />} 
        />

        <Route
          path={AppRoutes.DASHBOARD}
          element={isAuthenticated() ? <DashboardPage /> : <Navigate to={AppRoutes.LOGIN} replace />}
        />

        <Route
          path="/home"
          element={isAuthenticated() ? <Navigate to={AppRoutes.DASHBOARD} replace /> : <Navigate to={AppRoutes.LOGIN} replace />}
        />

        <Route
          path="/logout"
          element={<LogoutRoute />}
        />

        <Route
          path="*"
          element={<Navigate to={AppRoutes.SPLASH} replace />}
        />

      </Routes>
    </BrowserRouter>
  );
};
