import React from 'react';
import { Routes, Route, Navigate } from 'react-router-dom';
import { useAuth } from '../feature/auth/hooks/Auth';
import { AuthRoutes } from './LoginRoute';
import { DashRoute } from './dashboardRoute';


export const AppRoutes: React.FC = () => {
  const { loggedUser } = useAuth();
  const isAuthenticated = !!loggedUser;
  const isAdmin = loggedUser?.role === 'admin';

  return (
    <Routes>
      {AuthRoutes(isAuthenticated)}
      {DashRoute(isAdmin)}
      
      <Route 
        path="/home" 
        element={
          isAuthenticated ? (
            <div className="page-wrapper">
              <h1>Logado com sucesso!</h1>
            </div>
          ) : (
            <Navigate to="/login" />
          )
        } 
      />

      <Route
        path="/dashboard"
        element={
          isAdmin ? (
            <Navigate to="/dashboard" />
          ) : (
            <div className="page-wrapper">
              <h1>Bem Vindo</h1>
            </div>
          )
        }
      />

      <Route path="*" element={<Navigate to={isAuthenticated ? "/home" : "/login"} />} />
    </Routes>
  );
};