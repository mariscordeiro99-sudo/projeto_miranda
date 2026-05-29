import React, { useEffect } from 'react';
import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import { SplashPage } from '../pages/splash';
import { LoginPage } from '../pages/login';
import { LoginSuccessPage } from '../pages/loginSuccess';
import { DashboardPage } from '../pages/dashboard';
import { useSessionGuard } from '../routes/hooks/useSessionsGuard';
import { useRoleRedirect } from '../routes/hooks/useRoleRedirect';
import { CommunicationPage } from '../pages/communication';
import { ConversationPage } from '../pages/conversation';
import { AnnouncementsEdtPage } from '../pages/announEdt';
import { AppRoutes } from '../routes/types/loginReg';
import { RegisterPage } from '../pages/register';
import { ProtectedRoute } from './protectedRoute';

export const AppRouter: React.FC = () => {
  const { shouldRequireLogin, saveExitTime } = useSessionGuard();
  const { getInitialRoutePath } = useRoleRedirect();

  useEffect(() => {
    const handleUnload = () => saveExitTime();
    window.addEventListener('beforeunload', handleUnload);

    return () => window.removeEventListener('beforeunload', handleUnload);
  }, [saveExitTime]);

  const renderDashboardElement = () => {
    const targetPath = getInitialRoutePath();

    if (targetPath && targetPath !== AppRoutes.DASHBOARD) {
      return <Navigate to={targetPath} replace />;
    }

    return <DashboardPage />;
  };

  return (
    <BrowserRouter>
      <Routes>
        <Route path={AppRoutes.SPLASH} element={<SplashPage />} />

        <Route
          path={AppRoutes.LOGIN}
          element={shouldRequireLogin() ? <LoginPage /> : <Navigate to={AppRoutes.DASHBOARD} replace />}
        />

        <Route path={AppRoutes.REGISTER} element={<RegisterPage />} />
        <Route path={AppRoutes.LOGIN_SUCCESS} element={<LoginSuccessPage />} />

        <Route element={<ProtectedRoute />}>
          <Route path={AppRoutes.DASHBOARD} element={renderDashboardElement()} />
          <Route path={AppRoutes.COMUNICADOS} element={<CommunicationPage />} />
          <Route path={AppRoutes.CONVERSAS} element={<ConversationPage />} />
          <Route path={AppRoutes.EDICAO_COMUNICADOS} element={<AnnouncementsEdtPage />} />

        </Route>

        <Route path="*" element={<Navigate to={AppRoutes.LOGIN} replace />} />
      </Routes>
    </BrowserRouter>
  );
};