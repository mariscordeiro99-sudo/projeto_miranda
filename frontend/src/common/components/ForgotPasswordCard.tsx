import React from 'react';
import { Mail, Lock, ShieldCheck, ArrowLeft, Loader2, KeyRound } from 'lucide-react';
import { useForgotPassword } from '../hooks/useForgotPassword';
import '../styles/forgotPassword.css';

interface ForgotPasswordCardProps {
  onSuccess: () => void;
  onBackToLogin: () => void;
}

export const ForgotPasswordCard: React.FC<ForgotPasswordCardProps> = ({
  onSuccess,
  onBackToLogin
}) => {
  const {
    step,
    email,
    setEmail,
    codigoVerificacao,
    setCodigoVerificacao,
    passwordData,
    isLoading,
    rules,
    isPasswordValid,
    isConfirmationValid,
    handlePasswordChange,
    enviarEmailRecuperacao,
    validarCodigoSeguranca,
    atualizarNovaSenha,
    voltarPasso
  } = useForgotPassword({ onSuccess });

  return (
    <div className="forgot-password-card">
      <header className="forgot-card-header">
        {step !== 'FORMULARIO_EMAIL' ? (
          <button className="btn-back-auth" onClick={voltarPasso} title="Voltar passo">
            <ArrowLeft size={20} />
          </button>
        ) : (
          <button className="btn-back-auth" onClick={onBackToLogin} title="Voltar para o Login">
            <ArrowLeft size={20} />
          </button>
        )}
        <h2 className="forgot-title">Recuperar Senha</h2>
      </header>

      <div className="forgot-card-body">
        {step === 'FORMULARIO_EMAIL' && (
          <form onSubmit={enviarEmailRecuperacao} className="forgot-form-step">
            <div className="forgot-icon-intro">
              <KeyRound size={40} className="icon-brand" />
            </div>
            <p className="forgot-step-description">
              Digite o seu e-mail cadastrado. Enviaremos um código de segurança para validar a sua identidade.
            </p>

            <div className="forgot-input-group">
              <label htmlFor="forgot-email">E-mail Corporativo</label>
              <div className="forgot-input-wrapper">
                <Mail size={18} className="input-icon-auth" />
                <input
                  type="email"
                  id="forgot-email"
                  className="forgot-form-input"
                  value={email}
                  onChange={(e) => setEmail(e.target.value)}
                  placeholder="seu.email@nexa.com"
                  required
                  disabled={isLoading}
                />
              </div>
            </div>

            <button type="submit" className="btn-forgot-submit" disabled={isLoading}>
              {isLoading ? <Loader2 className="spinner" size={18} /> : 'Enviar Código'}
            </button>
          </form>
        )}

        {step === 'VERIFICACAO_CODIGO' && (
          <form onSubmit={validarCodigoSeguranca} className="forgot-form-step">
            <div className="forgot-icon-intro">
              <ShieldCheck size={40} className="icon-success" />
            </div>
            <p className="forgot-step-description">
              O código foi enviado para <strong>{email}</strong>. Digite os 6 dígitos abaixo.
            </p>

            <div className="forgot-input-group">
              <label htmlFor="forgot-code">Código de Verificação</label>
              <input
                type="text"
                id="forgot-code"
                maxLength={6}
                value={codigoVerificacao}
                onChange={(e) => setCodigoVerificacao(e.target.value)}
                placeholder="Ex: 123456"
                className="input-code-auth"
                required
                disabled={isLoading}
              />
            </div>

            <button type="submit" className="btn-forgot-submit" disabled={isLoading}>
              {isLoading ? <Loader2 className="spinner" size={18} /> : 'Validar Código'}
            </button>
            <p className="forgot-test-hint">Dica de teste: Digite <strong>123456</strong></p>
          </form>
        )}

        {step === 'NOVA_SENHA' && (
          <form onSubmit={atualizarNovaSenha} className="forgot-form-step">
            <p className="forgot-step-description">
              Código validado! Escolha uma nova senha de acesso segura para a sua conta.
            </p>

            <div className="forgot-input-group">
              <label htmlFor="novaSenha">Nova Senha</label>
              <div className="forgot-input-wrapper">
                <Lock size={18} className="input-icon-auth" />
                <input
                  type="password"
                  id="novaSenha"
                  name="novaSenha"
                  className={`forgot-form-input ${passwordData.novaSenha ? (isPasswordValid ? 'valid-border' : 'invalid-border') : ''}`}
                  value={passwordData.novaSenha}
                  onChange={handlePasswordChange}
                  placeholder="Digite sua nova senha"
                  required
                  disabled={isLoading}
                />
              </div>

              <div className="password-hints">
                <span className={rules.length ? 'valid' : 'invalid'}>6-15 caracteres</span>
                <span className={rules.upper ? 'valid' : 'invalid'}>Maiúscula</span>
                <span className={rules.lower ? 'valid' : 'invalid'}>Minúscula</span>
                <span className={rules.number ? 'valid' : 'invalid'}>Número</span>
                <span className={rules.special ? 'valid' : 'invalid'}>Especial</span>
              </div>
            </div>

            <div className="forgot-input-group">
              <label htmlFor="confirmarNovaSenha">Confirmar Nova Senha</label>
              <div className="forgot-input-wrapper">
                <Lock size={18} className="input-icon-auth" />
                <input
                  type="password"
                  id="confirmarNovaSenha"
                  name="confirmarNovaSenha"
                  className={`forgot-form-input ${passwordData.confirmarNovaSenha ? (isConfirmationValid ? 'valid-border' : 'invalid-border') : ''}`}
                  value={passwordData.confirmarNovaSenha}
                  onChange={handlePasswordChange}
                  placeholder="Repita a nova senha"
                  required
                  disabled={isLoading}
                />
              </div>
            </div>

            <button
              type="submit"
              className="btn-forgot-submit"
              disabled={isLoading || !isPasswordValid || !isConfirmationValid}
            >
              {isLoading ? <Loader2 className="spinner" size={18} /> : 'Redefinir Senha'}
            </button>
          </form>
        )}
      </div>
    </div>
  );
};