import React from 'react';
import { Routes, Route, Navigate } from 'react-router-dom';
import { useAuth } from '../feature/auth/hooks/Auth';
import { DashboardPage } from '../pages/dashboard';
import { AuthRoutes } from './LoginRoute';

interface UserWithRole {
    role: string;
  }

export const AppRoutes: React.FC = () => {
  const { loggedUser } = useAuth();
  const isAuthenticated = !!loggedUser;
  const isAdmin = (loggedUser as unknown as UserWithRole)?.role === 'admin';
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