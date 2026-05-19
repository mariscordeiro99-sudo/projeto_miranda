import React, { useEffect } from 'react';
import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import { SplashPage } from '../pages/splash';
import { LoginPage } from '../pages/login';
import { LoginSuccessPage } from '../pages/loginSuccess';
import { DashboardPage } from '../pages/dashboard';
import { useSessionGuard } from '../routes/hooks/useSessionsGuard';
import { useRoleRedirect } from '../routes/hooks/useRoleRedirect';
import { CommunicationPage } from '../pages/communication';
import { AppRoutes } from '../routes/types/loginReg';
import { RegisterPage } from '../pages/register';

export const AppRouter: React.FC = () => {
  const { shouldRequireLogin, saveExitTime } = useSessionGuard();
  const { getInitialRoutePath } = useRoleRedirect();

  useEffect(() => {
    const handleUnload = () => saveExitTime();
    window.addEventListener('beforeunload', handleUnload);

    return () => window.removeEventListener('beforeunload', handleUnload);
  }, []);

  const renderDashboardElement = () => {
    const targetPath = getInitialRoutePath();

    if (targetPath === AppRoutes.COMUNICADOS) {
      return <Navigate to={AppRoutes.COMUNICADOS} replace />;
    }

    return <DashboardPage />;
  };

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

        <Route
          path={AppRoutes.LOGIN_SUCCESS}
          element={<LoginSuccessPage />}
        />

        <Route
          path={AppRoutes.DASHBOARD}
          element={renderDashboardElement()}
        />

        <Route
          path={AppRoutes.COMUNICADOS}
          element={<CommunicationPage />}
        />
      </Routes>
    </BrowserRouter>
  );
};