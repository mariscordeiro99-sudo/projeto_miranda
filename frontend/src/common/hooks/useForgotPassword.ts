import { useState } from 'react';
import type { ChangeEvent, FormEvent } from 'react';
import type { ForgotPasswordStep, NewPasswordData, PasswordRules } from '../types/forgotPassword';
import api from '../services/api';
import type { ApiError } from '../types/apiError';

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

    const rules: PasswordRules = {
        length: passwordData.novaSenha.length >= 6 && passwordData.novaSenha.length <= 15,
        upper: /[A-Z]/.test(passwordData.novaSenha),
        lower: /[a-z]/.test(passwordData.novaSenha),
        number: /[0-9]/.test(passwordData.novaSenha),
        special: /[^A-Za-z0-9]/.test(passwordData.novaSenha)
    };

    const isPasswordValid = Object.values(rules).every(Boolean);
    const isConfirmationValid = passwordData.confirmarNovaSenha.length > 0 && passwordData.novaSenha === passwordData.confirmarNovaSenha;

    const handlePasswordChange = (e: ChangeEvent<HTMLInputElement>) => {
        const { name, value } = e.target;
        setPasswordData((prev) => ({ ...prev, [name]: value }));
    };

    const resetForm = () => {
        setEmail('');
        setCodigoVerificacao('');
        setPasswordData({ novaSenha: '', confirmarNovaSenha: '' });
        setStep('FORMULARIO_EMAIL');
    };

    const enviarEmailRecuperacao = async (e: FormEvent) => {
        e.preventDefault();
        const emailLimpo = email.trim();
        if (!emailLimpo) return alert('Por favor, insira o seu e-mail.');

        setIsLoading(true);
        try {
            await api.post('/auth/forgot-password/request', { email: emailLimpo });

            alert(`Código de verificação enviado com sucesso para o e-mail corporativo.`);
            setStep('VERIFICACAO_CODIGO');
        } catch (error) {
            const apiError = error as ApiError;
            alert(apiError.response?.data?.detail || 'E-mail não encontrado ou erro na operação.');
        } finally {
            setIsLoading(false);
        }
    };

    const validarCodigoSeguranca = async (e: FormEvent) => {
        e.preventDefault();
        const token = codigoVerificacao.trim();
        if (token.length !== 6) return alert('O código precisa ter exatamente 6 dígitos.');

        setIsLoading(true);
        try {
            await api.post('/auth/forgot-password/validate-token', {
                email: email.trim(),
                token
            });

            setStep('NOVA_SENHA');
        } catch (error) {
            const apiError = error as ApiError;
            alert(apiError.response?.data?.detail || 'Código inválido ou expirado.');
        } finally {
            setIsLoading(false);
        }
    };

    const atualizarNovaSenha = async (e: FormEvent) => {
        e.preventDefault();

        if (!isPasswordValid || !isConfirmationValid) {
            return alert('Verifique os requisitos da senha antes de prosseguir.');
        }

        setIsLoading(true);
        try {
            await api.post('/auth/forgot-password/reset', {
                email: email.trim(),
                token: codigoVerificacao.trim(),
                nova_senha: passwordData.novaSenha
            });

            alert('Senha redefinida com sucesso! Você já pode entrar com suas novas credenciais.');
            resetForm();
            onSuccess();
        } catch (error) {
            const apiError = error as ApiError;
            alert(apiError.response?.data?.detail || 'Erro ao tentar redefinir a sua senha.');
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
        rules,
        isPasswordValid,
        isConfirmationValid,
        handlePasswordChange,
        enviarEmailRecuperacao,
        validarCodigoSeguranca,
        atualizarNovaSenha,
        voltarPasso,
    };
};