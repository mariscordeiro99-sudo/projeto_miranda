import React from 'react';
import { Menu, User, Image as ImageIcon } from 'lucide-react';
import { useNavBar } from '../hooks/useNavBar';
import ProfileCard from '../components/ProfileCard';
import SideMenu from '../components/SideBar';
import '../styles/navBar.css';

const NavBar: React.FC = () => {
  const {
    userData,
    toggleMenu,
    toggleProfile,
    isProfileCardOpen,
    isMenuOpen,
    handleLogout
  } = useNavBar();

  if (!userData) {
    return (
      <nav className="navbar-fixed">
        <div className="nav-section nav-left">
          <div className="nav-brasao-placeholder" />
        </div>
        <div className="nav-section nav-center">
          <h1 className="nav-app-title">Nexa</h1>
        </div>
        <div className="nav-section nav-right" />
      </nav>
    );
  }

  const roleAtual = userData.role;

  const permissions = {
    painelGestor: userData.permissoes.isAdmin || userData.permissoes.dashboardGestor,
    controleAcessos: userData.permissoes.isAdmin || userData.permissoes.controlAcess,
    editorComunicados: userData.permissoes.isAdmin || userData.permissoes.announcement,
    configIdentidade: userData.permissoes.isAdmin || userData.permissoes.idtVisual,
    comunicados: true,
    conversas: true
  };

  return (
    <>
      <nav className="navbar-fixed">
        <div className="nav-section nav-left">
          <button className="nav-icon-btn" onClick={toggleMenu} aria-label="Abrir menu">
            <Menu size={26} />
          </button>

          <div className="nav-divider"></div>

          <div className="nav-brasao-container">
            {userData.brasao ? (
              <img src={userData.brasao} alt="Brasão da Instituição" className="nav-brasao-img" />
            ) : (
              <div className="nav-brasao-placeholder">
                <ImageIcon size={18} color="#94a3b8" />
              </div>
            )}
          </div>
        </div>

        <div className="nav-section nav-center">
          <h1 className="nav-app-title">Nexa</h1>
        </div>

        <div className="nav-section nav-right" onClick={toggleProfile} style={{ cursor: 'pointer' }}>
          <span className="nav-username">{userData.nome}</span>
          <div className="nav-profile-circle">
            {userData.foto ? (
              <img src={userData.foto} alt={`Foto de ${userData.nome}`} className="nav-avatar" />
            ) : (
              <User size={20} color="#4169E1" />
            )}
          </div>
        </div>
      </nav>

      <SideMenu
        isOpen={isMenuOpen}
        onClose={toggleMenu}
        userRole={roleAtual}
        permissions={permissions}
      />

      <ProfileCard
        isOpen={isProfileCardOpen}
        onClose={toggleProfile}
        userName={userData.nome}
        userPhoto={userData.foto}
        userRole={roleAtual.toUpperCase()}
        onLogout={handleLogout}
      />
    </>
  );
};

export default NavBar;