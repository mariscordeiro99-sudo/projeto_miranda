import React, { useEffect, useState } from 'react';
import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import { SplashPage } from '../pages/splash';
import { LoginPage } from '../pages/login';
import { RegisterPage } from '../pages/register';
import { useSessionGuard } from '../routes/hooks/useSessionsGuard';
import { AppRoutes as RoutePaths } from '../routes/types/loginReg';
import { useAuth } from '../feature/auth/hooks/Auth'; // Ajuste o caminho se necessário
import { api } from '../common/services/api'; // Caminho da sua conexão com o backend

// Definição de tipo para o usuário (ajuste conforme seu projeto)
interface UserWithRole {
  role: string;
}

export const AppRouter: React.FC = () => {
  const { shouldRequireLogin, saveExitTime } = useSessionGuard();
  const { loggedUser } = useAuth();
  const [apiMessage, setApiMessage] = useState<string>("");
  const [apiError, setApiError] = useState<string>("");

  const isAuthenticated = !!loggedUser;

  // Gerencia o tempo de saída (Sessão)
  useEffect(() => {
    const handleUnload = () => saveExitTime();
    window.addEventListener('beforeunload', handleUnload);
    return () => window.removeEventListener('beforeunload', handleUnload);
  }, [saveExitTime]);

  // Testa a comunicação com o seu Backend FastAPI
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
        {/* Rota da Splash Screen do Tagor */}
        <Route path={RoutePaths.SPLASH} element={<SplashPage />} />

        {/* Rota de Login com a lógica de sessão */}
        <Route 
          path={RoutePaths.LOGIN} 
          element={shouldRequireLogin() ? <LoginPage /> : <Navigate to="/home" />} 
        />

        {/* Rota de Cadastro */}
        <Route path={RoutePaths.REGISTER} element={<RegisterPage />} />

        {/* Home / Dashboard com integração do Backend */}
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

        {/* Redirecionamento padrão caso a rota não exista */}
        <Route path="*" element={<Navigate to={RoutePaths.SPLASH} replace />} />
      </Routes>
    </BrowserRouter>
  );
};