import React from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../hooks/useAuth';
import { authService } from '../services/auth';
import { AppRoutes } from '../../../routes/types/loginReg';
import '../styles/login.css';

const Login: React.FC = () => {
  const navigate = useNavigate();
  const { 
    password, 
    setPassword, 
    loginId, 
    handleLoginIdChange 
  } = useAuth();

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      const response = await authService.login({ identificador: loginId, senha: password });
      console.log('Sucesso:', response.data);
    } catch (error) {
      console.error('Erro ao entrar:', error);
    }
  };

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

          <button type="submit" className="btn-submit">
            Entrar
          </button>
        </form>

        <div className="auth-footer">
          <button className="btn-link">Esqueceu sua senha?</button>
          <div className="divider"></div>
          <button 
            className="btn-switch" 
            onClick={() => navigate(AppRoutes.REGISTER)}
          >
            Criar nova conta
          </button>
          <button className="btn-switch">Criar nova conta</button>
        </div>
      </div>
    </div>
  );
};

export default Login;