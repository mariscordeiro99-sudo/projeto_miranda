import React from 'react';
import { Link } from 'react-router-dom';
import {
  X, LayoutDashboard, ShieldCheck, FileEdit,
  MessageCircle, Bell, Palette
} from 'lucide-react';
import { AppRoutes } from '../../routes/types/loginReg';
import type { SideMenuProps, NavBarPermissions } from '../types/navBar';
import '../styles/sideBar.css';

const SideMenu: React.FC<SideMenuProps> = ({ isOpen, onClose, userRole, permissions }) => {

  const canSee = (perm: keyof NavBarPermissions) => {
    return userRole === 'gestor' || permissions[perm] === true;
  };

  return (
    <>
      <div
        className={`menu-overlay ${isOpen ? 'active' : ''}`}
        onClick={onClose}
      />

      <aside className={`side-menu ${isOpen ? 'open' : ''}`}>
        <div className="menu-header">
          <div className="menu-title-group">
            <small className="user-role-badge">{userRole}</small>
            <h2 className="sidebar-title">Navegação</h2>
          </div>
          <button className="close-sidebar" onClick={onClose} aria-label="Fechar menu">
            <X size={24} />
          </button>
        </div>

        <nav className="menu-nav-list">

          {userRole === 'gestor' && (
            <div className="menu-section">
              <span className="section-label">Administração</span>

              {canSee('painelGestor') && (
                <Link to={AppRoutes.DASHBOARD} className="menu-link" onClick={onClose}>
                  <LayoutDashboard size={20} /> Painel do Gestor
                </Link>
              )}

              {canSee('controleAcessos') && (
                <Link to="/controle-acesso" className="menu-link" onClick={onClose}>
                  <ShieldCheck size={20} /> Controle de Acessos
                </Link>
              )}

              {canSee('editorComunicados') && (
                <Link to="/edicao-comunicados" className="menu-link" onClick={onClose}>
                  <FileEdit size={20} /> Editor de Comunicados
                </Link>
              )}

              {canSee('configIdentidade') && (
                <Link to="/identidade" className="menu-link" onClick={onClose}>
                  <Palette size={20} /> Identidade Visual
                </Link>
              )}
            </div>
          )}

          <div className="menu-section">
            <span className="section-label">Comunicação</span>

            {canSee('comunicados') && (
              <Link to={AppRoutes.COMUNICADOS} className="menu-link" onClick={onClose}>
                <Bell size={20} /> Comunicados
              </Link>
            )}

            {canSee('conversas') && (
              <Link to="/conversas" className="menu-link" onClick={onClose}>
                <MessageCircle size={20} /> Conversas
              </Link>
            )}
          </div>
        </nav>

        <div className="sidebar-footer-simple">
          <span className="version-text">v1.0.0</span>
        </div>
      </aside>
    </>
  );
};

export default SideMenu;