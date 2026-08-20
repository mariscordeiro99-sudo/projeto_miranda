import React, { useEffect, useState } from 'react';
import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import { SplashPage } from '../pages/splash';
import { LoginPage } from '../pages/login';
import { RegisterPage } from '../pages/register';
import { useSessionGuard } from '../routes/hooks/useSessionsGuard';
import { AppRoutes as RoutePaths } from '../routes/types/loginReg';
import { useAuth } from '../feature/auth/hooks/Auth';
import { api } from '../common/services/api';

export const AppRouter: React.FC = () => {
  const { shouldRequireLogin, saveExitTime } = useSessionGuard();
  const { loggedUser } = useAuth();
  const [apiMessage, setApiMessage] = useState<string>("");
  const [apiError, setApiError] = useState<string>("");

  const isAuthenticated = !!loggedUser;

  useEffect(() => {
    const handleUnload = () => saveExitTime();
    window.addEventListener('beforeunload', handleUnload);
    return () => window.removeEventListener('beforeunload', handleUnload);
  }, [saveExitTime]);

  useEffect(() => {
    if (!isAuthenticated) return;

    api.get('/hello')
      .then((response) => {
        setApiMessage(response.data.message || 'Comunicação estabelecida.');
      })
      .catch((error) => {
        console.error('Erro ao chamar backend FastAPI:', error);
        setApiError('Não foi possível conectar ao backend.');
      });
  }, [isAuthenticated]);

  return (
    <BrowserRouter>
      <Routes>
        <Route path={RoutePaths.SPLASH} element={<SplashPage />} />

        <Route 
          path={RoutePaths.LOGIN} 
          element={shouldRequireLogin() ? <LoginPage /> : <Navigate to="/home" />} 
        />

        <Route path={RoutePaths.REGISTER} element={<RegisterPage />} />

        <Route 
          path="/home" 
          element={
            isAuthenticated ? (
              <div className="page-wrapper">
                <h1>Logado com sucesso!</h1>
                <div>
                  <h2>Status do Backend FastAPI</h2>
                  {apiMessage && <p style={{ color: 'green' }}>{apiMessage}</p>}
                  {apiError && <p style={{ color: 'red' }}>{apiError}</p>}
                </div>
              </div>
            ) : (
              <Navigate to={RoutePaths.LOGIN} replace />
            )
          } 
        />

        <Route path="*" element={<Navigate to={RoutePaths.SPLASH} replace />} />
      </Routes>
    </BrowserRouter>
  );
};
