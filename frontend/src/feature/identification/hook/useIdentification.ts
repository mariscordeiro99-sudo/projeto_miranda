import { useState, useRef, useEffect } from 'react';
import type { ChangeEvent } from 'react';
import type { FormIdentidadeState } from '../types/identification';
import api from '../../../common/services/api'; 
import BRASAO_PADRAO_SISTEMA from '../../../assets/images/logo-sBg.png';

export const useIdentidade = () => {
    const fileInputRef = useRef<HTMLInputElement>(null);
    const [isSaving, setIsSaving] = useState<boolean>(false);

    const [state, setState] = useState<FormIdentidadeState>({
        brasaoAtual: {
            id: 'b1',
            nome: 'brasao_padrao.png',
            url: BRASAO_PADRAO_SISTEMA
        },
        isAlterado: false
    });

    useEffect(() => {
        const carregarBrasaoServidor = async () => {
            try {
                const response = await api.get('/instituicao/identidade-visual/');
                
                if (response.data && response.data.brasao_url) {
                    setState({
                        brasaoAtual: {
                            id: response.data.id || 'b1',
                            nome: response.data.nome_arquivo || 'brasao_institucional.png',
                            url: response.data.brasao_url
                        },
                        isAlterado: false
                    });
                    
                    localStorage.setItem('instituicao_brasao', response.data.brasao_url);
                }
            } catch (error) {
                console.error("Erro ao buscar identidade visual do servidor:", error);
                const brasaoSalvo = localStorage.getItem('instituicao_brasao');
                if (brasaoSalvo) {
                    setState({
                        brasaoAtual: {
                            id: 'b1',
                            nome: 'brasao_customizado.png',
                            url: brasaoSalvo
                        },
                        isAlterado: false
                    });
                }
            }
        };

        carregarBrasaoServidor();
    }, []);

    const dispararSeletorArquivo = () => {
        fileInputRef.current?.click();
    };

    const handleMudarArquivo = (e: ChangeEvent<HTMLInputElement>) => {
        const arquivos = e.target.files;
        if (!arquivos || arquivos.length === 0) return;

        const arquivoSelecionado = arquivos[0];
        const urlTemporaria = URL.createObjectURL(arquivoSelecionado);

        setState({
            brasaoAtual: {
                id: crypto.randomUUID ? crypto.randomUUID() : Math.random().toString(),
                nome: arquivoSelecionado.name,
                url: urlTemporaria,
                file: arquivoSelecionado 
            },
            isAlterado: true
        });
    };

    const salvarIdentidadeVisual = async () => {
        if (!state.isAlterado || !state.brasaoAtual) return;

        setIsSaving(true);
        try {
            const formData = new FormData();
            
            if (state.brasaoAtual.file) {
                formData.append('brasao', state.brasaoAtual.file, state.brasaoAtual.nome);
            }

            const response = await api.put('/instituicao/identidade-visual/atualizar/', formData, {
                headers: {
                    'Content-Type': 'multipart/form-data',
                },
            });

            const urlFinalSalva = response.data?.brasao_url || state.brasaoAtual.url;

            localStorage.setItem('instituicao_brasao', urlFinalSalva);

            window.dispatchEvent(new CustomEvent('nexa_brasao_updated', {
                detail: urlFinalSalva
            }));

            setState(prev => ({
                ...prev,
                brasaoAtual: prev.brasaoAtual ? { ...prev.brasaoAtual, url: urlFinalSalva } : null,
                isAlterado: false
            }));

            alert("Identidade visual atualizada com sucesso no servidor!");
        } catch (error) {
            console.error("Erro ao enviar arquivo para o servidor:", error);
            alert("Erro ao salvar o novo brasão no banco de dados.");
        } finally {
            setIsSaving(false);
        }
    };

    return {
        brasao: state.brasaoAtual,
        isAlterado: state.isAlterado,
        isSaving,
        fileInputRef,
        dispararSeletorArquivo,
        handleMudarArquivo,
        salvarIdentidadeVisual
    };
};