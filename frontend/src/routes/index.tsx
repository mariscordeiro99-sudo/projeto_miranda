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

<<<<<<< HEAD
export const AppRoutes: React.FC = () => {
  const { loggedUser } = useAuth();
  const [apiMessage, setApiMessage] = useState<string>("");
  const [apiError, setApiError] = useState<string>("");
  const isAuthenticated = !!loggedUser;
  const isAdmin = (loggedUser as unknown as UserWithRole)?.role === 'admin';

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

=======
>>>>>>> 7fb4cf0231632375067a315a78aced8991f9504c
  return (
    <BrowserRouter>
      <Routes>
        <Route path={AppRoutes.SPLASH} element={<SplashPage />} />

<<<<<<< HEAD
      <Route 
        path="/home" 
        element={
          isAuthenticated ? (
            <div className="page-wrapper">
              <h1>Logado com sucesso!</h1>
              <div>
                <h2>Backend FastAPI</h2>
                {apiMessage && <p>{apiMessage}</p>}
                {apiError && <p style={{ color: 'red' }}>{apiError}</p>}
              </div>
            </div>
          ) : (
            <Navigate to="/login" replace />
          )
        } 
      />
=======
        <Route 
          path={AppRoutes.LOGIN} 
          element={shouldRequireLogin() ? <LoginPage /> : <Navigate to={AppRoutes.DASHBOARD} />} 
        />
>>>>>>> 7fb4cf0231632375067a315a78aced8991f9504c

        <Route 
          path={AppRoutes.REGISTER} 
          element={<RegisterPage />} 
        />

      </Routes>
    </BrowserRouter>
  );
};