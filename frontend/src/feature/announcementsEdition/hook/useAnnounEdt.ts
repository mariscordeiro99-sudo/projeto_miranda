import { useState, useCallback } from 'react';
import type { ComunicadoAdmin, AnexoComunicado } from '../types/announEdt';

export const useComunicadosAdmin = () => {
    const [comunicados, setComunicados] = useState<ComunicadoAdmin[]>(() => {
        const localDados = localStorage.getItem('nexa_comunicados_db');
        if (localDados) {
            return JSON.parse(localDados);
        }

        const mockDados: ComunicadoAdmin[] = [
            {
                id: "c1",
                titulo: "Nova Diretriz de Segurança de Dados",
                resumo: "Atualização importante sobre o uso de credenciais e acessos ao painel corporativo.",
                texto: "Prezados colaboradores, a partir desta semana iniciamos a migração para autenticação baseada em tokens com expiração de 12 horas...",
                status: "ativo",
                dataCriacao: "28/05/2026",
                anexos: [{ id: "a1", nome: "manual_seguranca.pdf", tipo: "pdf", url: "#" }]
            }
        ];
        localStorage.setItem('nexa_comunicados_db', JSON.stringify(mockDados));
        return mockDados;
    });

    const [isModalOpen, setIsModalOpen] = useState<boolean>(false);
    const [isPreviewOpen, setIsPreviewOpen] = useState<boolean>(false);
    const [comunicadoEdicao, setComunicadoEdicao] = useState<ComunicadoAdmin | null>(null);

    const [titulo, setTitulo] = useState('');
    const [resumo, setResumo] = useState('');
    const [texto, setTexto] = useState('');
    const [anexos, setAnexos] = useState<AnexoComunicado[]>([]);
    const [erroUpload, setErroUpload] = useState<string | null>(null);

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

    const salvarComunicado = (e: React.FormEvent) => {
        e.preventDefault();
        if (!titulo.trim() || !resumo.trim() || !texto.trim()) return;

        let listaAtualizada: ComunicadoAdmin[] = [];

        if (comunicadoEdicao) {
            listaAtualizada = comunicados.map(c => c.id === comunicadoEdicao.id ? {
                ...c, titulo, resumo, texto, anexos
            } : c);
        } else {
            const novo: ComunicadoAdmin = {
                id: `comunicado-${Date.now()}`,
                titulo,
                resumo,
                texto,
                status: 'ativo',
                dataCriacao: new Date().toLocaleDateString('pt-BR'),
                anexos
            };
            listaAtualizada = [novo, ...comunicados];
        }

        setComunicados(listaAtualizada);
        localStorage.setItem('nexa_comunicados_db', JSON.stringify(listaAtualizada));
        setIsModalOpen(false);
    };

    const alternarStatus = useCallback((id: string) => {
        setComunicados(prev => {
            const listaAtualizada = prev.map(c => c.id === id ? {
                ...c,
                status: (c.status === 'ativo' ? 'inativo' : 'ativo') as "ativo" | "inativo" // 🎯 Correção aqui
            } : c);
            localStorage.setItem('nexa_comunicados_db', JSON.stringify(listaAtualizada));
            return listaAtualizada;
        });
    }, []);

    const apagarComunicado = useCallback((id: string) => {
        if (window.confirm("Deseja realmente excluir permanentemente este comunicado?")) {
            setComunicados(prev => {
                const listaAtualizada = prev.filter(c => c.id !== id);
                localStorage.setItem('nexa_comunicados_db', JSON.stringify(listaAtualizada));
                return listaAtualizada;
            });
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
        apagarComunicado
    };
};