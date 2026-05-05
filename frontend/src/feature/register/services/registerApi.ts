import api from '../../../common/services/api';
import type { RegisterFormData } from '../types/registerForm';

export const registerUser = async (data: RegisterFormData) => {
  const formData = new FormData();
  const phoneCleaned = data.telefone.replace(/\D/g, '');
  formData.append('first_name', data.nome);
  formData.append('email', data.email);
  formData.append('phone_number', phoneCleaned);
  formData.append('username', data.usuario);
  formData.append('password', data.senha);
  formData.append('is_gestor', String(data.isGestor));
  
  if (data.fotoPerfil) {
    formData.append('profile_picture', data.fotoPerfil);
  }

  return await api.post('/auth/register/', formData, {
    headers: { 'Content-Type': 'multipart/form-data' }
  });
};