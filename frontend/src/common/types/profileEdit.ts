export interface UserProfileData {
  email: string;
  fotoUrl: string;
  fotoFile?: File;
}

export interface PasswordChangeState {
  senhaAtual: string;
  novaSenha: string;
  confirmarNovaSenha: string;
  codigoVerificacao: string;
}

export type ProfileStep = 'FORMULARIO' | 'VERIFICACAO_CODIGO';