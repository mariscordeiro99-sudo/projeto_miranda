export interface ForgotPasswordState {
  email: string;
  codigoVerificacao: string;
  novaSenha: 'FORMULARIO_EMAIL' | 'VERIFICACAO_CODIGO' | 'NOVA_SENHA';
}

export interface NewPasswordData {
  novaSenha: string;
  confirmarNovaSenha: string;
}

export type ForgotPasswordStep = 'FORMULARIO_EMAIL' | 'VERIFICACAO_CODIGO' | 'NOVA_SENHA';