import React from 'react';
import { Navigate, Outlet } from 'react-router-dom';
import NavBar from '../common/components/NavBar';
import { AppRoutes } from './types/loginReg';

export const ProtectedRoute: React.FC = () => {
  const token = localStorage.getItem('auth_token');
  const storedUser = localStorage.getItem('user_data');

  if (!token || !storedUser) {
    return <Navigate to={AppRoutes.LOGIN} replace />;
  }

  return (
    <div className="app-layout">
      <NavBar />
      <div className="main-content-wrapper">
        <Outlet />
      </div>
    </div>
  );
};