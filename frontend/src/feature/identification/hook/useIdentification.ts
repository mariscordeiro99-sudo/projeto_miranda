import { useState, useRef } from 'react';
import type { ChangeEvent } from 'react';
import type { FormIdentidadeState} from '../types/identification';
import BRASAO_PADRAO_SISTEMA from '../../../assets/images/logo-sBg.png';

export const useIdentidade = () => {
    const fileInputRef = useRef<HTMLInputElement>(null);

    const [state, setState] = useState<FormIdentidadeState>(() => {
        const brasaoSalvo = localStorage.getItem('instituicao_brasao');
        return {
            brasaoAtual: {
                id: 'b1',
                nome: brasaoSalvo ? 'brasao_customizado.png' : 'brasao_padrao.png',
                url: brasaoSalvo || BRASAO_PADRAO_SISTEMA
            },
            isAlterado: false
        };
    });

    const [isSaving, setIsSaving] = useState<boolean>(false);

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
            await new Promise(resolve => setTimeout(resolve, 600));

            localStorage.setItem('instituicao_brasao', state.brasaoAtual.url);

            window.dispatchEvent(new CustomEvent('nexa_brasao_updated', {
                detail: state.brasaoAtual.url
            }));

            setState(prev => ({ ...prev, isAlterado: false }));
            alert("Identidade visual atualizada com sucesso! O novo brasão já foi aplicado à barra de navegação.");
        } catch (error) {
            console.error("Erro ao salvar:", error);
            alert("Erro ao salvar o novo brasão.");
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