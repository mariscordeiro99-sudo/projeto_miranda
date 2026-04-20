import React from 'react';
import { Routes, Route, Navigate } from 'react-router-dom';
import { useAuth } from '../feature/auth/hooks/Auth';
import { AuthRoutes } from './loginRoute';

export const AppRoutes: React.FC = () => {
  const { user } = useAuth();
  const isAuthenticated = !!user;

  return (
    <Routes>
      {AuthRoutes(isAuthenticated)}
      
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

      <Route path="*" element={<Navigate to={isAuthenticated ? "/home" : "/login"} />} />
    </Routes>
  );
};