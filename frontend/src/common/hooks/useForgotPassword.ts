import { useState } from 'react';
import type { ChangeEvent, FormEvent } from 'react';
import type { ForgotPasswordStep, NewPasswordData } from '../types/forgotPassword';

interface UseForgotPasswordProps {
    onSuccess: () => void;
}

export const useForgotPassword = ({ onSuccess }: UseForgotPasswordProps) => {
    const [step, setStep] = useState<ForgotPasswordStep>('FORMULARIO_EMAIL');
    const [email, setEmail] = useState<string>('');
    const [codigoVerificacao, setCodigoVerificacao] = useState<string>('');
    const [passwordData, setPasswordData] = useState<NewPasswordData>({
        novaSenha: '',
        confirmarNovaSenha: '',
    });
    const [isLoading, setIsLoading] = useState<boolean>(false);

    const handlePasswordChange = (e: ChangeEvent<HTMLInputElement>) => {
        const { name, value } = e.target;
        setPasswordData((prev) => ({ ...prev, [name]: value }));
    };

    const enviarEmailRecuperacao = async (e: FormEvent) => {
        e.preventDefault();
        if (!email) {
            alert('Por favor, insira o seu e-mail.');
            return;
        }

        setIsLoading(true);
        try {
            await new Promise((resolve) => setTimeout(resolve, 1000));

            alert(`Código enviado com sucesso para: ${email}`);
            setStep('VERIFICACAO_CODIGO');
        } catch (error) {
            console.error('Erro ao enviar e-mail:', error);
            alert('Erro ao processar a solicitação.');
        } finally {
            setIsLoading(false);
        }
    };

    const validarCodigoSeguranca = async (e: FormEvent) => {
        e.preventDefault();
        if (codigoVerificacao.length !== 6) {
            alert('O código precisa ter exatamente 6 dígitos.');
            return;
        }

        setIsLoading(true);
        try {
            await new Promise((resolve) => setTimeout(resolve, 1000));

            if (codigoVerificacao !== '123456') {
                alert('Código inválido. Digite "123456" para testar no front.');
                setIsLoading(false);
                return;
            }

            setStep('NOVA_SENHA');
        } catch (error) {
            console.error('Erro ao validar código:', error);
            alert('Erro ao validar o código.');
        } finally {
            setIsLoading(false);
        }
    };

    const atualizarNovaSenha = async (e: FormEvent) => {
        e.preventDefault();
        if (!passwordData.novaSenha || !passwordData.confirmarNovaSenha) {
            alert('Por favor, preencha ambos os campos.');
            return;
        }

        if (passwordData.novaSenha.length < 6) {
            alert('A nova senha deve ter no mínimo 6 caracteres.');
            return;
        }

        if (passwordData.novaSenha !== passwordData.confirmarNovaSenha) {
            alert('As senhas digitadas não coincidem.');
            return;
        }

        setIsLoading(true);
        try {
            await new Promise((resolve) => setTimeout(resolve, 1200));

            alert('Senha redefinida com sucesso! Você já pode fazer login.');

            setStep('FORMULARIO_EMAIL');
            setEmail('');
            setCodigoVerificacao('');
            setPasswordData({ novaSenha: '', confirmarNovaSenha: '' });

            onSuccess();
        } catch (error) {
            console.error('Erro ao atualizar senha:', error);
            alert('Erro ao salvar nova senha.');
        } finally {
            setIsLoading(false);
        }
    };

    const voltarPasso = () => {
        if (step === 'VERIFICACAO_CODIGO') setStep('FORMULARIO_EMAIL');
        if (step === 'NOVA_SENHA') setStep('VERIFICACAO_CODIGO');
    };

    return {
        step,
        email,
        setEmail,
        codigoVerificacao,
        setCodigoVerificacao,
        passwordData,
        isLoading,
        handlePasswordChange,
        enviarEmailRecuperacao,
        validarCodigoSeguranca,
        atualizarNovaSenha,
        voltarPasso,
    };
};