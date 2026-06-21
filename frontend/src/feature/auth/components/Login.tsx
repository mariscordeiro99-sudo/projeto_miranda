import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../hooks/useAuth';
import { authService } from '../services/auth';
import { AppRoutes } from '../../../routes/types/loginReg';
import type { ApiError } from '../../../common/types/apiError';
import { ForgotPasswordCard } from '../../../common/components/ForgotPasswordCard';
import '../styles/login.css';

const Login: React.FC = () => {
  const navigate = useNavigate();
  const { 
    password, 
    setPassword, 
    loginId, 
    handleLoginIdChange 
  } = useAuth();

  const [isRecovering, setIsRecovering] = useState<boolean>(false);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      const response = await authService.login({ identificador: loginId, senha: password });
      localStorage.setItem('auth_token', response.data.access_token);
      localStorage.setItem('user', JSON.stringify(response.data.user));
      console.log('Sucesso:', response.data);
      navigate(AppRoutes.LOGIN_SUCCESS);
    } catch (error) {
      console.error('Erro ao entrar:', error);
      
      const apiError = error as ApiError;
      const mensagemErro = apiError.response?.data?.detail || 'Erro ao efetuar login.';
      
      alert(mensagemErro);
    }
  };

  if (isRecovering) {
    return (
      <div className="auth-container">
        <ForgotPasswordCard 
          onSuccess={() => setIsRecovering(false)} 
          onBackToLogin={() => setIsRecovering(false)}
        />
      </div>
    );
  }

  return (
    <div className="auth-container">
      <div className="auth-card">
        <h2 className="auth-title">Bem-vindo</h2>
        
        <form className="auth-form" onSubmit={handleSubmit}>
          <div className="form-group">
            <label>E-mail ou Telefone</label>
            <input 
              type="text" 
              className="form-input" 
              value={loginId}
              onChange={handleLoginIdChange}
              placeholder="seu@dominio.com ou (00) 00000-0000"
              required
            />
          </div>

          <div className="form-group">
            <label>Senha</label>
            <input 
              type="password" 
              className="form-input" 
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              required
            />
          </div>

          <div className="auth-footer">
            <button 
              type="button" 
              className="btn-link"
              onClick={() => setIsRecovering(true)}
            >
              Esqueceu sua senha?
            </button>
            <div className="divider"></div>
            <button 
              type="button"
              className="btn-switch" 
              onClick={() => navigate(AppRoutes.REGISTER)}
            >
              Criar nova conta
            </button>
          </div>

          <button type="submit" className="btn-submit">
            Entrar
          </button>
        </form>
      </div>
    </div>
  );
};

export default Login;