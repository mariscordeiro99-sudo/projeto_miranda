import React, { useEffect, useState } from 'react';
import { Routes, Route, Navigate } from 'react-router-dom';
import { useAuth } from '../feature/auth/hooks/Auth';
import { DashboardPage } from '../pages/dashboard';
import { AuthRoutes } from './LoginRoute';
import { api } from '../common/services/api';

interface UserWithRole {
    role: string;
  }

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

  return (
    <Routes>
      <Route 
        path="/login" 
        element={!isAuthenticated ? <AuthRoutes isAuthenticated={isAuthenticated} /> : <Navigate to="/home" />} 
      />

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

      <Route
        path="/dashboard"
        element={
          isAdmin ? (
            <DashboardPage /> 
          ) : (
            <Navigate to="/home" replace /> 
          )
        }
      />

      <Route 
        path="*" 
        element={<Navigate to={isAuthenticated ? "/home" : "/login"} replace />} 
      />
    </Routes>
  );
};