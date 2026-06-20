import React from 'react';
import { X, Camera, Mail, Lock, ShieldCheck, ArrowLeft, Loader2 } from 'lucide-react';
import { useProfileEdit } from '../hooks/useProfileEdit';
import '../style/profileEdit.css';

interface ProfileEditMenuProps {
  isOpen: boolean;
  onClose: () => void;
  userInitialData: { email: string; fotoUrl: string };
}

export const ProfileEditMenu: React.FC<ProfileEditMenuProps> = ({
  isOpen,
  onClose,
  userInitialData
}) => {
  const {
    profileData,
    passwordData,
    step,
    isLoading,
    fileInputRef,
    handleProfileChange,
    handlePasswordChange,
    dispararSeletorFoto,
    handleMudarFoto,
    iniciarTrocaSenha,
    salvarAlteracoesPerfil,
    voltarParaFormulario
  } = useProfileEdit({ isOpen, onClose, initialData: userInitialData });

  if (!isOpen) return null;

  return (
    <div className="profile-menu-overlay" onClick={onClose}>
      <div className="profile-menu-panel" onClick={(e) => e.stopPropagation()}>
        
        <header className="profile-menu-header">
          <div className="profile-menu-title">
            {step === 'VERIFICACAO_CODIGO' && (
              <button className="btn-back-step" onClick={voltarParaFormulario}>
                <ArrowLeft size={20} />
              </button>
            )}
            <h2>Editar Perfil</h2>
          </div>
          <button className="btn-close-menu" onClick={onClose}>
            <X size={20} />
          </button>
        </header>

        <div className="profile-menu-body">
          {step === 'FORMULARIO' ? (
            <form onSubmit={(e) => e.preventDefault()} className="profile-menu-form">
              
              <div className="profile-avatar-section">
                <div className="profile-avatar-wrapper" onClick={dispararSeletorFoto}>
                  <img 
                    src={profileData.fotoUrl} 
                    alt="Foto de Perfil" 
                    className="profile-avatar-img" 
                  />
                  <div className="profile-avatar-hover">
                    <Camera size={20} color="#fff" />
                  </div>
                </div>
                <input 
                  type="file" 
                  ref={fileInputRef} 
                  onChange={handleMudarFoto} 
                  accept="image/*" 
                  style={{ display: 'none' }} 
                />
                <p className="avatar-hint">Clique na foto para alterar</p>
              </div>

              <div className="profile-input-group">
                <label htmlFor="email">E-mail Institucional</label>
                <div className="profile-input-wrapper">
                  <Mail size={18} className="input-icon" />
                  <input
                    type="email"
                    id="email"
                    name="email"
                    value={profileData.email}
                    onChange={handleProfileChange}
                    placeholder="seu.email@nexa.com"
                  />
                </div>
              </div>

              <div className="profile-divider" />

              <h3 className="section-subtitle">Alterar Senha</h3>
              
              <div className="profile-input-group">
                <label htmlFor="senhaAtual">Senha Atual</label>
                <div className="profile-input-wrapper">
                  <Lock size={18} className="input-icon" />
                  <input
                    type="password"
                    id="senhaAtual"
                    name="senhaAtual"
                    value={passwordData.senhaAtual}
                    onChange={handlePasswordChange}
                    placeholder="Digite sua senha atual"
                  />
                </div>
              </div>

              <div className="profile-input-group">
                <label htmlFor="novaSenha">Nova Senha</label>
                <div className="profile-input-wrapper">
                  <Lock size={18} className="input-icon" />
                  <input
                    type="password"
                    id="novaSenha"
                    name="novaSenha"
                    value={passwordData.novaSenha}
                    onChange={handlePasswordChange}
                    placeholder="Mínimo 6 caracteres"
                  />
                </div>
              </div>

              <div className="profile-input-group">
                <label htmlFor="confirmarNovaSenha">Confirmar Nova Senha</label>
                <div className="profile-input-wrapper">
                  <Lock size={18} className="input-icon" />
                  <input
                    type="password"
                    id="confirmarNovaSenha"
                    name="confirmarNovaSenha"
                    value={passwordData.confirmarNovaSenha}
                    onChange={handlePasswordChange}
                    placeholder="Confirme a nova senha"
                  />
                </div>
              </div>

              <button 
                type="button" 
                className="btn-trigger-password" 
                onClick={iniciarTrocaSenha}
                disabled={isLoading}
              >
                {isLoading ? <Loader2 className="spinner" size={18} /> : 'Validar e Alterar Senha'}
              </button>

              <div className="profile-footer-actions">
                <button 
                  type="button" 
                  className="btn-save-profile" 
                  onClick={salvarAlteracoesPerfil}
                  disabled={isLoading}
                >
                  {isLoading ? <Loader2 className="spinner" size={18} /> : 'Salvar Dados Cadastrais'}
                </button>
              </div>

            </form>
          ) : (
            <form onSubmit={salvarAlteracoesPerfil} className="profile-menu-form verification-step">
              <div className="verification-icon-wrapper">
                <ShieldCheck size={48} color="#4169E1" />
              </div>
              
              <h3>Código de Segurança</h3>
              <p className="verification-description">
                Enviamos um token de verificação para o e-mail <strong>{profileData.email}</strong>. 
                Insira o código abaixo para validar a troca de senha.
              </p>

              <div className="profile-input-group">
                <label htmlFor="codigoVerificacao">Código de 6 dígitos</label>
                <input
                  type="text"
                  id="codigoVerificacao"
                  name="codigoVerificacao"
                  maxLength={6}
                  value={passwordData.codigoVerificacao}
                  onChange={handlePasswordChange}
                  placeholder="Ex: 123456"
                  className="input-code-center"
                />
              </div>

              <div className="profile-footer-actions stack-vertical">
                <button type="submit" className="btn-save-profile" disabled={isLoading}>
                  {isLoading ? <Loader2 className="spinner" size={18} /> : 'Confirmar e Salvar Tudo'}
                </button>
                <p className="test-hint">Dica de teste: Digite <strong>123456</strong></p>
              </div>
            </form>
          )}
        </div>

      </div>
    </div>
  );
};