import React, { useState } from 'react';
import { User, Settings, LogOut, Camera } from 'lucide-react';
import type { ProfileCardProps } from '../types/profileCard';
import { ProfileEditMenu } from '../components/ProfileEditMenu';
import '../styles/profileCard.css';

const ProfileCard: React.FC<ProfileCardProps> = ({
  isOpen,
  onClose,
  userName,
  userPhoto,
  userRole,
  onLogout
}) => {
  const [isMenuEditOpen, setIsMenuEditOpen] = useState<boolean>(false);

  if (!isOpen) return null;

  const userInitialData = {
    email: 'colaborador@nexa.com',
    fotoUrl: userPhoto || ''
  };

  return (
    <>
      <div className="profile-overlay" onClick={onClose} />

      <div className="profile-card">
        <div className="profile-header">
          <div className="profile-image-container">
            {userPhoto ? (
              <img src={userPhoto} alt="Perfil" className="profile-img-large" />
            ) : (
              <div className="profile-placeholder-large">
                <User size={40} color="#4169E1" />
              </div>
            )}
            <button 
              className="change-photo-badge" 
              title="Mudar foto"
              onClick={() => setIsMenuEditOpen(true)}
            >
              <Camera size={14} />
            </button>
          </div>

          <div className="profile-info">
            <span className="profile-name">{userName}</span>
            <span className="profile-role">{userRole}</span>
          </div>
        </div>

        <div className="profile-divider" />

        <div className="profile-actions">
          <button 
            type="button"
            className="profile-action-item" 
            onClick={() => {
              setIsMenuEditOpen(true);
            }}
            style={{ width: '100%', background: 'none', border: 'none', textAlign: 'left', cursor: 'pointer' }}
          >
            <Settings size={18} />
            <span>Editar Cadastro</span>
          </button>
        </div>

        <div className="profile-divider" />

        <div className="profile-footer">
          <button className="logout-button" onClick={onLogout}>
            <LogOut size={18} />
            <span>Sair do Sistema</span>
          </button>
        </div>
      </div>

      <ProfileEditMenu 
        isOpen={isMenuEditOpen} 
        onClose={() => setIsMenuEditOpen(false)} 
        userInitialData={userInitialData}
      />
    </>
  );
};

export default ProfileCard;