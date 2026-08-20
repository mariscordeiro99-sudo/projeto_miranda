import React from 'react';
import { Navigate, Outlet, useLocation } from 'react-router-dom';
import NavBar from '../common/components/NavBar';
import { AppRoutes } from './types/loginReg';

export const ProtectedRoute: React.FC = () => {
  const location = useLocation();
  const token = localStorage.getItem('auth_token');
  const storedUser = localStorage.getItem('user');

  if (!token || !storedUser) {
    return <Navigate to={AppRoutes.LOGIN} replace />;
  }

  const userObj = JSON.parse(storedUser);
  const usuarioLogadoId = userObj?.id || "u1";
  const userRole = userObj?.role; 

  const permissoesSalvas = localStorage.getItem(`permissoes_${usuarioLogadoId}`);
  const permissoes = permissoesSalvas ? JSON.parse(permissoesSalvas) : {
    controlAcess: false,
    announcement: false,
    idtVisual: false,
    isAdmin: false
  };

  if (userRole === 'gestor' || permissoes.isAdmin) {
    return (
      <div className="app-layout">
        <NavBar />
        <div className="main-content-wrapper">
          <Outlet />
        </div>
      </div>
    );
  }

  if (location.pathname === AppRoutes.DASHBOARD) {
    return <Navigate to={AppRoutes.COMUNICADOS} replace />;
  }

  if (location.pathname === AppRoutes.CONTROLE_ACESSO && !permissoes.controlAcess) {
    return <Navigate to={AppRoutes.COMUNICADOS} replace />;
  }

  if (location.pathname === AppRoutes.EDICAO_COMUNICADOS && !permissoes.announcement) {
    return <Navigate to={AppRoutes.COMUNICADOS} replace />;
  }

  if (location.pathname === AppRoutes.IDENTIFICATION && !permissoes.idtVisual) {
    return <Navigate to={AppRoutes.COMUNICADOS} replace />;
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