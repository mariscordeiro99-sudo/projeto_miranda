export interface RegisterFormData {
  nome: string;
  email: string;
  usuario: string;
  telefone: string;
  senha: string;
  isGestor: boolean;
  fotoPerfil: File | null;
}