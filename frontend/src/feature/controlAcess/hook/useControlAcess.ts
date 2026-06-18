import { useState, useEffect, useCallback } from 'react';
import api from '../../../common/services/api';
import type { UsuarioAcesso, PermissoesUsuario } from '../types/typeAcess';
import type { ApiError } from '../../../common/types/apiError';

export const useControleAcesso = () => {
    const [usuarios, setUsuarios] = useState<UsuarioAcesso[]>([]);
    const [isLoading, setIsLoading] = useState<boolean>(true);
    const [busca, setBusca] = useState<string>('');

    useEffect(() => {
        let isMounted = true;

        const carregarUsuarios = async () => {
            try {
                if (isMounted) setIsLoading(true);
                
                const response = await api.get<UsuarioAcesso[]>('/admin/users-permissions/');
                
                if (isMounted) {
                    setUsuarios(response.data);
                }
            } catch (error: unknown) {
                console.error("Erro ao carregar controle de acessos:", error);
            } finally {
                if (isMounted) setIsLoading(false);
            }
        };

        carregarUsuarios();

        return () => {
            isMounted = false;
        };
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
            await api.put(`/admin/users-permissions/${usuarioId}/`, {
                roleAtual: usuarioAlvo.roleAtual,
                permissoes: usuarioAlvo.permissoes
            });

            alert(`Permissões de ${usuarioAlvo.nome} aplicadas com sucesso no ecossistema Nexa!`);
        } catch (err: unknown) {
            console.error("Erro ao salvar permissões no servidor:", err);
            const apiError = err as ApiError;
            alert(apiError.response?.data?.detail || "Erro ao salvar alterações no servidor.");
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