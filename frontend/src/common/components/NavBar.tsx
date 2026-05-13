import React from 'react';
import { Menu, User, Image as ImageIcon } from 'lucide-react';
import { useNavBar } from '../hooks/useNavBar';
import '../styles/navBar.css';

const NavBar: React.FC = () => {
  const { userData, toggleMenu, toggleProfile } = useNavBar();

  if (!userData) return null;

  return (
    <nav className="navbar-fixed">
      <div className="nav-section nav-left">
        <button className="nav-icon-btn" onClick={toggleMenu}>
          <Menu size={26} />
        </button>
        <div className="nav-divider"></div>
        <div className="nav-brasao-container">
          {userData.brasao ? (
            <img src={userData.brasao} alt="Brasão" className="nav-brasao-img" />
          ) : (
            <div className="nav-brasao-placeholder">
              <ImageIcon size={18} color="#94a3b8" />
            </div>
          )}
        </div>
      </div>

      <div className="nav-section nav-center">
        <h1 className="nav-app-title">SISTEMA GESTOR</h1>
      </div>

      <div className="nav-section nav-right" onClick={toggleProfile}>
        <span className="nav-username">{userData.nome}</span>
        <div className="nav-profile-circle">
          {userData.foto ? (
            <img src={userData.foto} alt="Perfil" className="nav-avatar" />
          ) : (
            <User size={20} color="#4169E1" />
          )}
        </div>
      </div>
    </nav>
  );
};

export default NavBar;