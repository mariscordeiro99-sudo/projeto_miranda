import { useState, useEffect, useCallback } from 'react';
import type { UsuarioAcesso, PermissoesUsuario } from '../types/typeAcess';

export const useControleAcesso = () => {
    const [usuarios, setUsuarios] = useState<UsuarioAcesso[]>([]);
    const [isLoading, setIsLoading] = useState<boolean>(true);
    const [busca, setBusca] = useState<string>('');

    useEffect(() => {
        const carregarUsuarios = async () => {
            try {
                await new Promise(resolve => setTimeout(resolve, 400));

                const listaBase = [
                    {
                        id: "u1",
                        nome: "Carlos Eduardo",
                        email: "carlos.eduardo@nexa.com",
                        foto: null,
                        roleAtual: "colaborador",
                        permissoesPadrao: { controlAcess: false, announcement: true, idtVisual: false, dashboardGestor: false, isAdmin: false }
                    },
                    {
                        id: "u2",
                        nome: "Mariana Costa",
                        email: "mariana.costa@nexa.com",
                        foto: "https://images.unsplash.com/photo-1534528741775-53994a69daeb?q=80&w=150",
                        roleAtual: "gestor",
                        permissoesPadrao: { controlAcess: true, announcement: true, idtVisual: true, dashboardGestor: true, isAdmin: true }
                    },
                    {
                        id: "u3",
                        nome: "Roberto Alves",
                        email: "roberto.alves@nexa.com",
                        foto: "https://images.unsplash.com/photo-1507003211169-0a1dd7228f2d?q=80&w=150",
                        roleAtual: "colaborador",
                        permissoesPadrao: { controlAcess: false, announcement: false, idtVisual: false, dashboardGestor: false, isAdmin: false }
                    }
                ];

                const usuariosProcessados: UsuarioAcesso[] = listaBase.map(u => {
                    const salvas = localStorage.getItem(`permissoes_${u.id}`);
                    const roleSalvo = localStorage.getItem(`user_role_${u.id}`);
                    return {
                        id: u.id,
                        nome: u.nome,
                        email: u.email,
                        foto: u.foto,
                        roleAtual: (roleSalvo as 'gestor' | 'colaborador') || u.roleAtual,
                        permissoes: salvas ? JSON.parse(salvas) : u.permissoesPadrao
                    };
                });

                setUsuarios(usuariosProcessados);
            } catch (error) {
                console.error("Erro ao carregar controle de acessos:", error);
            } finally {
                setIsLoading(false);
            }
        };

        carregarUsuarios();
    }, []);

    const alternarPermissao = useCallback((usuarioId: string, chavePermissao: keyof PermissoesUsuario) => {
        setUsuarios(prev => prev.map(usuario => {
            if (usuario.id !== usuarioId) return usuario;

            const novasPermissoes = { ...usuario.permissoes };

            if (chavePermissao === 'isAdmin') {
                const novoValorAdmin = !novasPermissoes.isAdmin;
                novasPermissoes.isAdmin = novoValorAdmin;
                novasPermissoes.controlAcess = novoValorAdmin;
                novasPermissoes.announcement = novoValorAdmin;
                novasPermissoes.idtVisual = novoValorAdmin;
                novasPermissoes.dashboardGestor = novoValorAdmin;
            } else {
                novasPermissoes[chavePermissao] = !novasPermissoes[chavePermissao];
                if (!novasPermissoes[chavePermissao]) {
                    novasPermissoes.isAdmin = false;
                }
            }

            const novoRole = novasPermissoes.isAdmin ? 'gestor' : 'colaborador';

            return {
                ...usuario,
                roleAtual: novoRole,
                permissoes: novasPermissoes
            };
        }));
    }, []);

    const salvarAcessoUsuario = async (usuarioId: string) => {
        const usuarioAlvo = usuarios.find(u => u.id === usuarioId);
        if (!usuarioAlvo) return;

        try {
            localStorage.setItem(`permissoes_${usuarioId}`, JSON.stringify(usuarioAlvo.permissoes));
            localStorage.setItem(`user_role_${usuarioId}`, usuarioAlvo.roleAtual);

            const storedUser = localStorage.getItem('user_data');
            if (storedUser) {
                const userObj = JSON.parse(storedUser);
                if (userObj.id === usuarioId) {
                    userObj.roleAtual = usuarioAlvo.roleAtual;
                    localStorage.setItem('user_data', JSON.stringify(userObj));
                }
            }

            alert(`Permissões de ${usuarioAlvo.nome} aplicadas com sucesso no ecossistema Nexa!`);
        } catch {
            alert("Erro ao salvar alterações no servidor.");
        }
    };

    const usuariosFiltrados = usuarios.filter(u =>
        u.nome.toLowerCase().includes(busca.toLowerCase()) ||
        u.email.toLowerCase().includes(busca.toLowerCase())
    );

    return {
        usuarios: usuariosFiltrados,
        busca,
        setBusca,
        isLoading,
        alternarPermissao,
        salvarAcessoUsuario
    };
};