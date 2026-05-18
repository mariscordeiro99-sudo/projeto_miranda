import React from 'react';
import { useNavigate } from 'react-router-dom';
import { AppRoutes } from '../routes/types/loginReg';
import '../feature/auth/styles/login.css';

export const LoginSuccessPage: React.FC = () => {
  const navigate = useNavigate();
  const user = typeof window !== 'undefined' ? localStorage.getItem('user') : null;
  const userName = user ? JSON.parse(user).first_name || JSON.parse(user).username : null;

  return (
    <div className="auth-container">
      <div className="auth-card">
        <h2 className="auth-title">Login feito com sucesso!</h2>
        <p className="auth-message">
          {userName ? `Bem-vindo, ${userName}!` : 'Estamos conectados ao backend com sucesso.'}
        </p>
        <p className="auth-message">A comunicação entre frontend e backend está funcionando corretamente.</p>
        <button className="btn-submit" onClick={() => navigate(AppRoutes.DASHBOARD)}>
          Ir para o Painel
        </button>
      </div>
    </div>
  );
};
