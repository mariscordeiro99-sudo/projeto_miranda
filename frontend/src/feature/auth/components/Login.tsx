<<<<<<< HEAD
import React from "react";
import { Card } from "../../../common/components/Card";
import { Input } from "../../../common/components/Input";
import { Button } from "../../../common/components/button";
import { useAuth } from "../hooks/Auth";
import { useLoginBtn } from "../hooks/LoginBtn";
import "../styles/login.css";
=======
import React from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../hooks/useAuth';
import { authService } from '../services/auth';
import { AppRoutes } from '../../../routes/types/loginReg';
import '../styles/login.css';
>>>>>>> 7fb4cf0231632375067a315a78aced8991f9504c

const Login: React.FC = () => {
  const navigate = useNavigate();
  const { 
    password, 
    setPassword, 
    loginId, 
    handleLoginIdChange 
  } = useAuth();

<<<<<<< HEAD
        const { isLoading, error, handleLoginSubmit } = useLoginBtn({
        user,
        password,
        hasErrors: !!userError || !!passwordError
    });
=======
  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      const response = await authService.login({ identificador: loginId, senha: password });
      console.log('Sucesso:', response.data);
    } catch (error) {
      console.error('Erro ao entrar:', error);
    }
  };
>>>>>>> 7fb4cf0231632375067a315a78aced8991f9504c

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

<<<<<<< HEAD
    return (
        <Card
            title="Login"
            classCard="card"
            classCardHeader="card-header"
            classTitle="card-title"
            classCardContent="card-content"
            contentCard={
                <form className="login-form" onSubmit={handleLoginSubmit}>
                    {error && <div style={{ color: "red", marginBottom: "10px" }}>{error}</div>}
                    <div className="input-group">
                        <Input
                            label="Usuário"
                            value={user}
                            onChange={handleUserChange}
                            error={userError}
                            classLabel="login-label"
                            classInput={`login-input ${getUserStatusClass()}`}
                        />
                        {userError && <span className="tooltip-error">{userError}</span>}
                    </div>
                    <div className="input-group">
                        <Input
                            label="Senha"
                            value={password}
                            onChange={handlePasswordChange}
                            error={passwordError}
                            classLabel="login-label"
                            classInput={`login-input ${getPasswordStatusClass()}`}
                            type="password"
                        />
                        {passwordError && <span className="tooltip-error">{passwordError}</span>}
                    </div>
=======
          <div className="auth-footer">
          <button className="btn-link">Esqueceu sua senha?</button>
          <div className="divider"></div>
          <button 
            className="btn-switch" 
            onClick={() => navigate(AppRoutes.REGISTER)}
          >
            Criar nova conta
          </button>
        </div>
>>>>>>> 7fb4cf0231632375067a315a78aced8991f9504c

          <button type="submit" className="btn-submit">
            Entrar
          </button>
        </form>
      </div>
    </div>
  );
};

export default Login;