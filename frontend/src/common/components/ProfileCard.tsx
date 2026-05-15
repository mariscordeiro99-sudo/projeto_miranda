import React from 'react';
import { Link } from 'react-router-dom';
import { User, Settings, LogOut, Camera } from 'lucide-react';
import type { ProfileCardProps } from '../types/profileCard';
import '../style/profileCard.css';

const ProfileCard: React.FC<ProfileCardProps> = ({
    isOpen,
    onClose,
    userName,
    userPhoto,
    userRole,
    onLogout
}) => {
    if (!isOpen) return null;

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
                        <button className="change-photo-badge" title="Mudar foto">
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
                    <Link to="/perfil/editar" className="profile-action-item" onClick={onClose}>
                        <Settings size={18} />
                        <span>Editar Cadastro</span>
                    </Link>
                </div>

                <div className="profile-divider" />

                <div className="profile-footer">
                    <button className="logout-button" onClick={onLogout}>
                        <LogOut size={18} />
                        <span>Sair do Sistema</span>
                    </button>
                </div>
            </div>
        </>
    );
};

export default ProfileCard;