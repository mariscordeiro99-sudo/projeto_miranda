export interface NavBarUserData {
  nome: string;
  foto: string | null;
  brasao: string | null;
  role: 'gestor' | 'colaborador';
}

export interface NavBarPermissions {
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
  permissions: NavBarPermissions;
}