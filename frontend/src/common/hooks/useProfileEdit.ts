import { useState, useRef } from 'react';
import type { ChangeEvent } from 'react';
import type { UserProfileData, PasswordChangeState, ProfileStep } from '../types/profileEdit';

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

    if (passwordData.novaSenha !== passwordData.confirmarNovaSenha) {
      alert('A nova senha e a confirmação não coincidem.');
      return;
    }

    setIsLoading(true);
    try {
      await new Promise((resolve) => setTimeout(resolve, 1000));
      setStep('VERIFICACAO_CODIGO');
      alert(`Código de verificação enviado para o e-mail: ${profileData.email}`);
    } catch (error) {
      console.error('Erro ao solicitar troca de senha:', error);
      alert('Erro ao enviar código de verificação.');
    } finally {
      setIsLoading(false);
    }
  };

  const salvarAlteracoesPerfil = async (e: React.FormEvent) => {
    e.preventDefault();
    setIsLoading(true);

    try {
      await new Promise((resolve) => setTimeout(resolve, 1200));

      if (step === 'VERIFICACAO_CODIGO' && passwordData.codigoVerificacao !== '123456') {
        alert('Código de verificação incorreto! Use "123456" para testar no front.');
        setIsLoading(false);
        return;
      }

      alert('Perfil atualizado com sucesso!');

      setStep('FORMULARIO');
      setPasswordData({ senhaAtual: '', novaSenha: '', confirmarNovaSenha: '', codigoVerificacao: '' });
      onClose();
    } catch (error) {
      console.error('Erro ao solicitar troca de senha:', error);
      alert('Erro ao enviar código de verificação.');
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
    handleProfileChange,
    handlePasswordChange,
    dispararSeletorFoto,
    handleMudarFoto,
    iniciarTrocaSenha,
    salvarAlteracoesPerfil,
    voltarParaFormulario,
  };
};