export type ForgotPasswordStep = 'FORMULARIO_EMAIL' | 'VERIFICACAO_CODIGO' | 'NOVA_SENHA';

export interface PasswordRules {
  length: boolean;
  upper: boolean;
  lower: boolean;
  number: boolean;
  special: boolean;
}

export interface NewPasswordData {
  novaSenha: string;
  confirmarNovaSenha: string;
}

export interface ForgotPasswordFormState {
  email: string;
  codigoVerificacao: string;
  senhas: NewPasswordData;
  step: ForgotPasswordStep;
  isLoading: boolean;
}