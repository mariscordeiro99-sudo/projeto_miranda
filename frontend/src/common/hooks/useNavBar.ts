import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import api from '../services/api';
import { AppRoutes } from '../../routes/types/loginReg';
import type { PermissoesUsuario } from '../../feature/controlAcess/types/typeAcess';
import BRASAO_PADRAO_SISTEMA from '../../assets/images/logo-sBg.png';

interface NavBarUserData {
  id: string;
  nome: string;
  foto: string | null;
  brasao: string | null;
  role: 'gestor' | 'colaborador';
  permissoes: PermissoesUsuario;
}

export const useNavBar = () => {
  const navigate = useNavigate();
  const [isMenuOpen, setIsMenuOpen] = useState<boolean>(false);
  const [isProfileCardOpen, setIsProfileCardOpen] = useState<boolean>(false);

  const [userData, setUserData] = useState<NavBarUserData | null>(() => {
    const storedUser = localStorage.getItem('user_data');
    const brasaoSalvo = localStorage.getItem('instituicao_brasao'); 
    
    if (storedUser) {
      try {
        const parsed = JSON.parse(storedUser);
        return {
          id: parsed.id || 'u1',
          nome: parsed.nome || 'Usuário',
          foto: parsed.fotoPerfil || parsed.foto || null,
          brasao: brasaoSalvo || parsed.brasaoUrl || parsed.brasao || BRASAO_PADRAO_SISTEMA,
          role: parsed.roleAtual || parsed.role || 'colaborador',
          permissoes: parsed.permissoes || {
            controlAcess: false,
            announcement: true,
            idtVisual: false,
            dashboardGestor: false,
            isAdmin: false
          }
        };
      } catch (error) {
        console.error("Erro ao processar dados do usuário na NavBar:", error);
        return null;
      }
    }
    return null;
  });

  useEffect(() => {
    const escutarMudancaBrasao = (e: Event) => {
      const customEvent = e as CustomEvent<string>;
      if (customEvent.detail) {
        setUserData((prevData) => {
          if (!prevData) return null;
          return {
            ...prevData,
            brasao: customEvent.detail
          };
        });
      }
    };

    window.addEventListener('nexa_brasao_updated', escutarMudancaBrasao);

    return () => {
      window.removeEventListener('nexa_brasao_updated', escutarMudancaBrasao);
    };
  }, []);

  useEffect(() => {
    if (!userData) {
      localStorage.clear();
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

  const handleLogout = async (): Promise<void> => {
    try {
      await api.post('/auth/logout/');
    } catch (error) {
      console.warn("Sessão já expirada no servidor ou offline:", error);
    } finally {
      localStorage.clear();
      navigate(AppRoutes.LOGIN, { replace: true });
    }
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