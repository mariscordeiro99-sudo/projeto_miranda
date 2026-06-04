import React from 'react';
import { Navigate, Outlet, useLocation } from 'react-router-dom';
import NavBar from '../common/components/NavBar';
import { AppRoutes } from './types/loginReg';

export const ProtectedRoute: React.FC = () => {
  const location = useLocation();
  const token = localStorage.getItem('auth_token');
  const storedUser = localStorage.getItem('user_data');

  if (!token || !storedUser) {
    return <Navigate to={AppRoutes.LOGIN} replace />;
  }

  const userObj = JSON.parse(storedUser);
  const usuarioLogadoId = userObj?.id || "u1"; 

  const permissoesSalvas = localStorage.getItem(`permissoes_${usuarioLogadoId}`);
  
  const permissoes = permissoesSalvas ? JSON.parse(permissoesSalvas) : {
    controlAcess: false,
    announcement: false,
    idtVisual: false,
    isAdmin: false
  };

  if (permissoes.isAdmin) {
    return (
      <div className="app-layout">
        <NavBar />
        <div className="main-content-wrapper">
          <Outlet />
        </div>
      </div>
    );
  }
 
  if (location.pathname === '/controle-acesso' && !permissoes.controlAcess) {
    return <Navigate to={AppRoutes.COMUNICADOS} replace />;
  }

  if (location.pathname === '/edicao-comunicados' && !permissoes.announcement) {
    return <Navigate to={AppRoutes.COMUNICADOS} replace />;
  }

  // Tentativa de acessar o Módulo de Identificação Visual
  if (location.pathname === '/configuracoes/visual' && !permissoes.idtVisual) {
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