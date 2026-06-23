import { useState, useRef } from 'react';
import type { ChangeEvent } from 'react';
import type { UserProfileData, PasswordChangeState, ProfileStep, PasswordRules } from '../types/profileEdit';
import type { ApiError } from '../types/apiError';
import api from '../services/api';

interface UseProfileEditProps {
  isOpen: boolean;
  onClose: () => void;
  initialData: { email: string; fotoUrl: string };
}

export const useProfileEdit = ({ isOpen, onClose, initialData }: UseProfileEditProps) => {
  const fileInputRef = useRef<HTMLInputElement>(null);

  const [profileData, setProfileData] = useState<UserProfileData>({
    email: initialData.email,
    fotoUrl: initialData.fotoUrl,
  });

  const [passwordData, setPasswordData] = useState<PasswordChangeState>({
    senhaAtual: '',
    novaSenha: '',
    confirmarNovaSenha: '',
    codigoVerificacao: '',
  });

  const [step, setStep] = useState<ProfileStep>('FORMULARIO');
  const [isLoading, setIsLoading] = useState<boolean>(false);

  const rules: PasswordRules = {
    length: passwordData.novaSenha.length >= 6 && passwordData.novaSenha.length <= 15,
    upper: /[A-Z]/.test(passwordData.novaSenha),
    lower: /[a-z]/.test(passwordData.novaSenha),
    number: /[0-9]/.test(passwordData.novaSenha),
    special: /[^A-Za-z0-9]/.test(passwordData.novaSenha),
  };

  const isPasswordValid = Object.values(rules).every(Boolean);

  const handleProfileChange = (e: ChangeEvent<HTMLInputElement>) => {
    const { name, value } = e.target;
    setProfileData((prev) => ({ ...prev, [name]: value }));
  };

  const handlePasswordChange = (e: ChangeEvent<HTMLInputElement>) => {
    const { name, value } = e.target;
    setPasswordData((prev) => ({ ...prev, [name]: value }));
  };

  const dispararSeletorFoto = () => fileInputRef.current?.click();

  const handleMudarFoto = (e: ChangeEvent<HTMLInputElement>) => {
    const arquivos = e.target.files;
    if (!arquivos || arquivos.length === 0) return;

    const arquivoSelecionado = arquivos[0];
    setProfileData((prev) => ({
      ...prev,
      fotoUrl: URL.createObjectURL(arquivoSelecionado),
      fotoFile: arquivoSelecionado,
    }));
  };

  const iniciarTrocaSenha = async () => {
    if (!passwordData.senhaAtual || !passwordData.novaSenha || !passwordData.confirmarNovaSenha) {
      alert('Por favor, preencha todos os campos de senha.');
      return;
    }

    if (!isPasswordValid) {
      alert('A nova senha não atende aos requisitos.');
      return;
    }

    if (passwordData.novaSenha !== passwordData.confirmarNovaSenha) {
      alert('A nova senha e a confirmação não coincidem.');
      return;
    }

    setIsLoading(true);
    try {
      await api.post(`/usuarios/solicitar-codigo-senha`, {
        senhaAtual: passwordData.senhaAtual,
        novaSenha: passwordData.novaSenha,
      });

      setStep('VERIFICACAO_CODIGO');
      alert(`Código de verificação enviado para o e-mail: ${profileData.email}`);
    } catch (error) {
      console.error('Erro ao solicitar troca de senha:', error);
      const apiError = error as ApiError;
      const mensagemErro = apiError.response?.data?.detail || 'Erro ao enviar código de verificação.';
      alert(mensagemErro);
    } finally {
      setIsLoading(false);
    }
  };

  const salvarAlteracoesPerfil = async (e: React.FormEvent) => {
    e.preventDefault();
    setIsLoading(true);

    try {
      const formData = new FormData();
      formData.append('email', profileData.email);

      if (profileData.fotoFile) {
        formData.append('foto', profileData.fotoFile);
      }

      if (step === 'VERIFICACAO_CODIGO') {
        formData.append('senhaAtual', passwordData.senhaAtual);
        formData.append('novaSenha', passwordData.novaSenha);
        formData.append('codigoVerificacao', passwordData.codigoVerificacao);
      }

      await api.put(`/usuarios/perfil/atualizar`, formData, {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
      });

      alert('Perfil updated com sucesso!');
      setStep('FORMULARIO');
      setPasswordData({ senhaAtual: '', novaSenha: '', confirmarNovaSenha: '', codigoVerificacao: '' });
      onClose();
    } catch (error) {
      console.error('Erro ao atualizar perfil:', error);
      const apiError = error as ApiError;
      const mensagemErro = apiError.response?.data?.detail || 'Erro ao salvar as alterações do perfil.';
      alert(mensagemErro);
    } finally {
      setIsLoading(false);
    }
  };

  const voltarParaFormulario = () => setStep('FORMULARIO');

  return {
    isOpen,
    profileData,
    passwordData,
    step,
    isLoading,
    fileInputRef,
    rules,
    isPasswordValid,
    handleProfileChange,
    handlePasswordChange,
    dispararSeletorFoto,
    handleMudarFoto,
    iniciarTrocaSenha,
    salvarAlteracoesPerfil,
    voltarParaFormulario,
  };
};