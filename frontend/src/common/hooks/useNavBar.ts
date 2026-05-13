import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { AppRoutes } from '../../routes/types/loginReg';

export const useNavBar = () => {
    const navigate = useNavigate();

    const [userData] = useState(() => {
        const storedUser = localStorage.getItem('user_data');
        if (storedUser) {
            try {
                return JSON.parse(storedUser);
            } catch { return null; }
        }
        return null;
    });

    const [brasaoUrl, setBrasaoUrl] = useState<string | null>(null);
    const [isMenuOpen, setIsMenuOpen] = useState(false);
    const [isProfileCardOpen, setIsProfileCardOpen] = useState(false);

    useEffect(() => {
        if (!userData) {
            navigate(AppRoutes.LOGIN);
            return;
        }

        // Simulação de busca do Brasão de outra tabela do banco
        // Aqui no futuro vamos colocar o fetch('/api/configuracao-instituicao/')
        const fetchInstituicao = async () => {
            try {
                const storedBrasao = localStorage.getItem('instituicao_brasao');
                setBrasaoUrl(storedBrasao);
            } catch {
                setBrasaoUrl(null);
            }
        };

        fetchInstituicao();
    }, [userData, navigate]);

    return {
        userData,
        brasaoUrl,
        isMenuOpen,
        isProfileCardOpen,
        toggleMenu: () => setIsMenuOpen(!isMenuOpen),
        toggleProfile: () => setIsProfileCardOpen(!isProfileCardOpen),
    };
};