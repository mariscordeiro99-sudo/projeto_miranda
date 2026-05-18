import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { AppRoutes } from '../../routes/types/loginReg';

export const useNavBar = () => {
    const navigate = useNavigate();

    const [userData] = useState(() => {
        const storedUser = localStorage.getItem('user_data');
        if (storedUser) {
            try {
                const parsed = JSON.parse(storedUser);
                return {
                    nome: parsed.nome,
                    foto: parsed.fotoPerfil || parsed.foto,
                    brasao: parsed.brasaoUrl || parsed.brasao,
                    role: parsed.role || 'Colaborador'
                };
            } catch {
                return null;
            }
        }
        return null;
    });

    const [isMenuOpen, setIsMenuOpen] = useState(false);
    const [isProfileCardOpen, setIsProfileCardOpen] = useState(false);

    useEffect(() => {
        if (!userData) {
            navigate(AppRoutes.LOGIN);
        }
    }, [userData, navigate]);

    const toggleMenu = () => {
        setIsMenuOpen(!isMenuOpen);
        if (isProfileCardOpen) setIsProfileCardOpen(false);
    };

    const toggleProfile = () => {
        setIsProfileCardOpen(!isProfileCardOpen);
        if (isMenuOpen) setIsMenuOpen(false);
    };

    const handleLogout = () => {
        localStorage.removeItem('auth_token');
        localStorage.removeItem('user_data');
        localStorage.removeItem('instituicao_brasao');
        navigate(AppRoutes.LOGIN);
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