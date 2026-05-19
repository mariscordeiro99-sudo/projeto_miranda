import { AppRoutes } from '../types/loginReg';

export const useRoleRedirect = () => {
  const getInitialRoutePath = (): string => {
    const storedUser = localStorage.getItem('user_data');
    
    if (storedUser) {
      try {
        const user = JSON.parse(storedUser);
        
        if (user.role?.toLowerCase() === 'colaborador') {
          return AppRoutes.COMUNICADOS;
        }
      } catch (error) {
        console.error("Erro ao processar dados de acesso:", error);
      }
    }

    return AppRoutes.DASHBOARD;
  };

  return { getInitialRoutePath };
};