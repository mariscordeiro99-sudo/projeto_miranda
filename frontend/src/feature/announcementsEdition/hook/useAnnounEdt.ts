import { useState, useEffect, useCallback } from 'react';
import api from '../../../common/services/api';
import type { ComunicadoAdmin, AnexoComunicado } from '../types/announEdt';
import type { ApiError } from '../../../common/types/apiError';

export const useComunicadosAdmin = () => {
    const [comunicados, setComunicados] = useState<ComunicadoAdmin[]>([]);
    const [isLoading, setIsLoading] = useState<boolean>(true);
    const [error, setError] = useState<string | null>(null);

    const [isModalOpen, setIsModalOpen] = useState<boolean>(false);
    const [isPreviewOpen, setIsPreviewOpen] = useState<boolean>(false);
    const [comunicadoEdicao, setComunicadoEdicao] = useState<ComunicadoAdmin | null>(null);

    const [titulo, setTitulo] = useState('');
    const [resumo, setResumo] = useState('');
    const [texto, setTexto] = useState('');
    const [anexos, setAnexos] = useState<AnexoComunicado[]>([]);
    const [erroUpload, setErroUpload] = useState<string | null>(null);

    const carregarComunicados = useCallback(async () => {
        try {
            setIsLoading(true);
            setError(null);
            const response = await api.get<ComunicadoAdmin[]>('/admin/announcements/');
            setComunicados(response.data);
        } catch (err: unknown) {
            console.error("Erro ao buscar comunicados:", err);
            const apiError = err as ApiError;
            setError(apiError.response?.data?.detail || "Erro ao carregar os comunicados do sistema.");
        } finally {
            setIsLoading(false);
        }
    }, []);

    useEffect(() => {
        carregarComunicados();
    }, [carregarComunicados]);

    const abrirCriacao = useCallback(() => {
        setComunicadoEdicao(null);
        setTitulo('');
        setResumo('');
        setTexto('');
        setAnexos([]);
        setErroUpload(null);
        setIsModalOpen(true);
    }, []);

    const abrirEdicao = useCallback((comunicado: ComunicadoAdmin) => {
        setComunicadoEdicao(comunicado);
        setTitulo(comunicado.titulo);
        setResumo(comunicado.resumo);
        setTexto(comunicado.texto);
        setAnexos(comunicado.anexos);
        setErroUpload(null);
        setIsModalOpen(true);
    }, []);

    const lidarComUploadArquivo = (e: React.ChangeEvent<HTMLInputElement>) => {
        setErroUpload(null);
        const files = e.target.files;
        if (!files || files.length === 0) return;

        const arquivo = files[0];
        const extensao = arquivo.name.split('.').pop()?.toLowerCase();

        const extensoesImagens = ['png', 'jpeg', 'jpg'];
        const extensoesVideo = ['mp4'];
        const extensoesPdf = ['pdf'];

        let tipoDefinido: 'image' | 'video' | 'pdf' | null = null;
        if (extensoesImagens.includes(extensao || '')) tipoDefinido = 'image';
        if (extensoesVideo.includes(extensao || '')) tipoDefinido = 'video';
        if (extensoesPdf.includes(extensao || '')) tipoDefinido = 'pdf';

        if (!tipoDefinido) {
            setErroUpload("Formato inválido. Apenas MP4, JPEG, PNG ou PDF são permitidos.");
            return;
        }

        const limiteTamanho = tipoDefinido === 'video' ? 50 * 1024 * 1024 : 10 * 1024 * 1024;
        if (arquivo.size > limiteTamanho) {
            setErroUpload(`Arquivo muito grande. Limite: ${tipoDefinido === 'video' ? '50MB' : '10MB'}.`);
            return;
        }

        const novoAnexo: AnexoComunicado = {
            id: `temp-${Date.now()}`,
            nome: arquivo.name,
            tipo: tipoDefinido,
            url: URL.createObjectURL(arquivo),
            file: arquivo
        };

        setAnexos(prev => [...prev, novoAnexo]);
        e.target.value = '';
    };

    const removerAnexo = useCallback((id: string) => {
        setAnexos(prev => {
            const filtrados = prev.filter(anexo => anexo.id !== id);
            const removido = prev.find(anexo => anexo.id === id);
            if (removido && removido.url.startsWith('blob:')) {
                URL.revokeObjectURL(removido.url);
            }
            return filtrados;
        });
    }, []);

    const salvarComunicado = async (e: React.FormEvent) => {
        e.preventDefault();
        if (!titulo.trim() || !resumo.trim() || !texto.trim()) return;

        try {
            setIsLoading(true);
            const formData = new FormData();
            formData.append('titulo', titulo);
            formData.append('resumo', resumo);
            formData.append('texto', texto);

            anexos.forEach((anexo) => {
                if (anexo.file) {
                    formData.append('arquivos', anexo.file);
                }
            });

            if (comunicadoEdicao) {
                await api.put(`/admin/announcements/${comunicadoEdicao.id}/`, formData, {
                    headers: { 'Content-Type': 'multipart/form-data' }
                });
            } else {
                await api.post('/admin/announcements/', formData, {
                    headers: { 'Content-Type': 'multipart/form-data' }
                });
            }

            setIsModalOpen(false);
            carregarComunicados();
        } catch (err: unknown) {
            console.error("Erro ao salvar comunicado:", err);
            const apiError = err as ApiError;
            alert(apiError.response?.data?.detail || "Erro ao salvar comunicado.");
        } finally {
            setIsLoading(false);
        }
    };

    const alternarStatus = useCallback(async (id: string) => {
        try {
            const comunicadoAlvo = comunicados.find(c => c.id === id);
            if (!comunicadoAlvo) return;

            const novoStatus = comunicadoAlvo.status === 'ativo' ? 'inativo' : 'ativo';

            await api.patch(`/admin/announcements/${id}/`, { status: novoStatus });

            setComunicados(prev => prev.map(c => c.id === id ? { ...c, status: novoStatus } : c));
        } catch (err: unknown) {
            console.error("Erro ao alternar status:", err);
            const apiError = err as ApiError;
            alert(apiError.response?.data?.detail || "Não foi possível alterar o status.");
        }
    }, [comunicados]);

    const apagarComunicado = useCallback(async (id: string) => {
        if (!window.confirm("Deseja realmente excluir permanentemente este comunicado?")) return;

        try {
            await api.delete(`/admin/announcements/${id}/`);
            setComunicados(prev => prev.filter(c => c.id !== id));
        } catch (err: unknown) {
            console.error("Erro ao apagar comunicado:", err);
            const apiError = err as ApiError;
            alert(apiError.response?.data?.detail || "Erro ao excluir comunicado.");
        }
    }, []);

    return {
        comunicados,
        isModalOpen,
        setIsModalOpen,
        isPreviewOpen,
        setIsPreviewOpen,
        comunicadoEdicao,
        titulo,
        setTitulo,
        resumo,
        setResumo,
        texto,
        setTexto,
        anexos,
        erroUpload,
        abrirCriacao,
        abrirEdicao,
        lidarComUploadArquivo,
        removerAnexo,
        salvarComunicado,
        alternarStatus,
        apagarComunicado,
        isLoading,
        error
    };
};