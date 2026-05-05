import api from '../../../common/services/api';
import type { LoginFormData } from '../types/loginForm';

export const authService = {
  login: async (data: LoginFormData) => {
    const loginValue = data.identificador.includes('@') 
      ? data.identificador 
      : data.identificador.replace(/\D/g, '');

    return await api.post('/auth/login/', {
      username: loginValue,
      password: data.senha
    });
  }
};