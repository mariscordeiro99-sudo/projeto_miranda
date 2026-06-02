export interface PermissoesUsuario {
  permissaoA: boolean;
  permissaoB: boolean;
  permissaoC: boolean;
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