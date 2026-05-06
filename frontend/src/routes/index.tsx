import React, { useEffect } from 'react';
import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import {SplashPage} from '../pages/splash';
import {LoginPage} from '../pages/login';
import { useSessionGuard } from '../routes/hooks/useSessionsGuard';
import { AppRoutes } from '../routes/types/loginReg';
import { RegisterPage } from '../pages/register';

export const AppRouter: React.FC = () => {
  const { shouldRequireLogin, saveExitTime } = useSessionGuard();

  useEffect(() => {
    const handleUnload = () => saveExitTime();
    window.addEventListener('beforeunload', handleUnload);
    
    return () => window.removeEventListener('beforeunload', handleUnload);
  }, []);

  return (
    <BrowserRouter>
      <Routes>
        <Route path={AppRoutes.SPLASH} element={<SplashPage />} />

        <Route 
          path={AppRoutes.LOGIN} 
          element={shouldRequireLogin() ? <LoginPage /> : <Navigate to={AppRoutes.DASHBOARD} />} 
        />

        <Route 
          path={AppRoutes.REGISTER} 
          element={<RegisterPage />} 
        />

      </Routes>
    </BrowserRouter>
  );
};