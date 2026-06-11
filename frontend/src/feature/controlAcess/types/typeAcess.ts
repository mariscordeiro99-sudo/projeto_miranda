export interface PermissoesUsuario {
  controlAcess: boolean;
  announcement: boolean;
  idtVisual: boolean;
  dashboardGestor: boolean;
  isAdmin: boolean;
}

export interface UsuarioAcesso {
  id: string;
  nome: string;
  email: string;
  foto: string | null;
  roleAtual: 'gestor' | 'colaborador';
  permissoes: PermissoesUsuario;
}