export interface SidebarPermissions {
  painelGestor: boolean;
  controleAcessos: boolean;
  editorComunicados: boolean;
  comunicados: boolean;
  conversas: boolean;
  configIdentidade: boolean;
}

export interface SideMenuProps {
  isOpen: boolean;
  onClose: () => void;
  userRole: 'gestor' | 'colaborador';
  permissions: SidebarPermissions;
}