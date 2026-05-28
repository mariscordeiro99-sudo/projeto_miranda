import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { AppRoutes } from '../../routes/types/loginReg';

// Criamos uma interface interna para o estado do usuário, evitando o tipo 'any' implícito
interface NavBarUserData {
  nome: string;
  foto: string | null;
  brasao: string | null;
  role: string;
}

export const useNavBar = () => {
  const navigate = useNavigate();

  const [userData] = useState<NavBarUserData | null>(() => {
    const storedUser = localStorage.getItem('user_data');
    if (storedUser) {
      try {
        const parsed = JSON.parse(storedUser);
        return {
          nome: parsed.nome || 'Usuário',
          foto: parsed.fotoPerfil || parsed.foto || null,
          brasao: parsed.brasaoUrl || parsed.brasao || null,
          role: parsed.role || 'Colaborador'
        };
      } catch (error) {
        console.error("Erro ao processar dados do usuário na NavBar:", error);
        return null;
      }
    }
    return null;
  });

  const [isMenuOpen, setIsMenuOpen] = useState<boolean>(false);
  const [isProfileCardOpen, setIsProfileCardOpen] = useState<boolean>(false);

  useEffect(() => {
    // Se não houver dados do usuário no estado local, significa que a sessão caiu.
    // Limpamos os resíduos do storage e mandamos para o Login de forma limpa.
    if (!userData) {
      localStorage.removeItem('auth_token');
      localStorage.removeItem('user_data');
      navigate(AppRoutes.LOGIN, { replace: true });
    }
  }, [userData, navigate]);

  const toggleMenu = (): void => {
    setIsMenuOpen((prev) => !prev);
    if (isProfileCardOpen) setIsProfileCardOpen(false);
  };

  const toggleProfile = (): void => {
    setIsProfileCardOpen((prev) => !prev);
    if (isMenuOpen) setIsMenuOpen(false);
  };

  const handleLogout = (): void => {
    localStorage.removeItem('auth_token');
    localStorage.removeItem('user_data');
    localStorage.removeItem('instituicao_brasao');
    navigate(AppRoutes.LOGIN, { replace: true });
  };

  return {
    userData,
    isMenuOpen,
    isProfileCardOpen,
    toggleMenu,
    toggleProfile,
    handleLogout,
  };
};