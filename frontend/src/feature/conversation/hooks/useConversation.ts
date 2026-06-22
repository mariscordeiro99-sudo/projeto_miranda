import { useState, useEffect, useRef } from 'react';
import type { ChatContato, Mensagem, TipoMidia } from '../types/conversation';
import api from '../../../common/services/api';
import type { ApiError } from '../../../common/types/apiError';

export const useConversas = () => {
  const [contatos, setContatos] = useState<ChatContato[]>([]);
  const [contatoAtivo, setContatoAtivo] = useState<ChatContato | null>(null);
  const [mensagens, setMensagens] = useState<Mensagem[]>([]);
  const [mensagemInput, setMensagemInput] = useState<string>('');
  const [isLoading, setIsLoading] = useState<boolean>(true);

  const [isGravandoAudio, setIsGravandoAudio] = useState<boolean>(false);
  const mediaRecorderRef = useRef<MediaRecorder | null>(null);
  const audioChunksRef = useRef<Blob[]>([]);

  const currentUserId = "user-logado-123";

  const MAX_FILE_SIZE = 50 * 1024 * 1024;
  const FORMATOS_PERMITIDOS = ['video/mp4', 'audio/mp3', 'audio/mpeg', 'image/png', 'image/jpeg', 'image/jpg', 'application/pdf'];

  useEffect(() => {
    const carregarContatos = async () => {
      setIsLoading(true);
      try {
        const response = await api.get('/chat/contatos');
        setContatos(response.data);
      } catch (error) {
        const apiError = error as ApiError;
        console.error("Erro ao carregar contatos via API:", apiError.response?.data?.detail || error);
      } finally {
        setIsLoading(false);
      }
    };
    carregarContatos();
  }, []);

  useEffect(() => {
    if (!contatoAtivo) {
      setMensagens([]);
      return;
    }
    const carregarHistorico = async () => {
      try {
        await api.post(`/chat/contatos/${contatoAtivo.id}/ler`);
        setContatos(prev => prev.map(c => c.id === contatoAtivo.id ? { ...c, naoLidas: 0 } : c));

        const response = await api.get(`/chat/mensagens/${contatoAtivo.id}`);
        setMensagens(response.data);
      } catch (error) {
        const apiError = error as ApiError;
        console.error("Erro ao carregar histórico via API:", apiError.response?.data?.detail || error);
      }
    };
    carregarHistorico();
  }, [contatoAtivo]);

  const anexarNovaMensagemLocal = (novaMsg: Mensagem) => {
    setMensagens(prev => [...prev, novaMsg]);
    setContatos(prev => prev.map(c =>
      c.id === contatoAtivo?.id
        ? { ...c, ultimaMensagem: novaMsg.texto || `[${novaMsg.tipo}]`, timestampUltima: novaMsg.timestamp }
        : c
    ));
  };

  const enviarMensagem = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!mensagemInput.trim() || !contatoAtivo) return;

    const payload = {
      receiverId: contatoAtivo.id,
      texto: mensagemInput.trim(),
      tipo: 'texto'
    };

    try {
      const response = await api.post('/chat/enviar', payload);
      anexarNovaMensagemLocal(response.data);
      setMensagemInput('');
    } catch (error) {
      const apiError = error as ApiError;
      console.error("Detalhes do erro:", apiError);
      alert(apiError.response?.data?.detail || 'Erro ao enviar mensagem de texto.');
    }
  };

  const validarArquivo = (file: File): boolean => {
    if (file.size > MAX_FILE_SIZE) {
      alert('O arquivo excede o limite máximo de 50MB corporativo.');
      return false;
    }
    if (!FORMATOS_PERMITIDOS.includes(file.type)) {
      alert('Formato não suportado. Envie MP4, MP3, PNG, JPG ou PDF.');
      return false;
    }
    return true;
  };

  const extrairTipoMidia = (mimeType: string): TipoMidia => {
    if (mimeType.startsWith('image/')) return 'imagem';
    if (mimeType.startsWith('video/')) return 'video';
    if (mimeType.startsWith('audio/')) return 'audio';
    return 'documento';
  };

  const enviarArquivoAnexo = async (file: File) => {
    if (!contatoAtivo || !validarArquivo(file)) return;

    const formData = new FormData();
    formData.append('file', file);
    formData.append('receiverId', contatoAtivo.id);
    formData.append('tipo', extrairTipoMidia(file.type));

    try {
      const response = await api.post('/chat/upload', formData, {
        headers: { 'Content-Type': 'multipart/form-data' }
      });
      anexarNovaMensagemLocal(response.data);
    } catch (error) {
      const apiError = error as ApiError;
      console.error("Detalhes do erro:", apiError);
      alert(apiError.response?.data?.detail || 'Falha ao enviar o arquivo anexo.');
    }
  };

  const iniciarGravacaoAudio = async () => {
    try {
      const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
      const mediaRecorder = new MediaRecorder(stream);
      mediaRecorderRef.current = mediaRecorder;
      audioChunksRef.current = [];

      mediaRecorder.ondataavailable = (event) => {
        if (event.data.size > 0) audioChunksRef.current.push(event.data);
      };

      mediaRecorder.onstop = async () => {
        const audioBlob = new Blob(audioChunksRef.current, { type: 'audio/mp3' });
        const audioFile = new File([audioBlob], `audio-${Date.now()}.mp3`, { type: 'audio/mp3' });
        await enviarArquivoAnexo(audioFile);
        stream.getTracks().forEach(track => track.stop());
      };

      mediaRecorder.start();
      setIsGravandoAudio(true);
    } catch (err) {
      const apiError = err as ApiError;
      console.error("Detalhes do erro:", apiError);
      alert(apiError.response?.data?.detail || 'Permissão de microfone não concedida.');
    }
  };

  const pararGravacaoAudio = () => {
    if (mediaRecorderRef.current && isGravandoAudio) {
      mediaRecorderRef.current.stop();
      setIsGravandoAudio(false);
    }
  };

  const capturarFotoCamera = async () => {
    if (!contatoAtivo) return;

    const video = document.createElement('video');
    try {
      const stream = await navigator.mediaDevices.getUserMedia({ video: true });
      video.srcObject = stream;
      video.play();

      await new Promise((resolve) => setTimeout(resolve, 500));

      const canvas = document.createElement('canvas');
      canvas.width = video.videoWidth || 640;
      canvas.height = video.videoHeight || 480;

      const context = canvas.getContext('2d');
      context?.drawImage(video, 0, 0, canvas.width, canvas.height);

      canvas.toBlob(async (blob) => {
        if (blob) {
          const fotoFile = new File([blob], `screenshot-${Date.now()}.jpg`, { type: 'image/jpeg' });
          await enviarArquivoAnexo(fotoFile);
        }
        stream.getTracks().forEach(track => track.stop());
      }, 'image/jpeg');

    } catch (err) {
      const apiError = err as ApiError;
      console.error("Detalhes do erro:", apiError);
      alert(apiError.response?.data?.detail || 'Câmera indisponível ou permissão negada.');
    }
  };

  return {
    contatos,
    contatoAtivo,
    setContatoAtivo,
    mensagens,
    mensagemInput,
    setMensagemInput,
    enviarMensagem,
    isLoading,
    currentUserId,
    isGravandoAudio,
    iniciarGravacaoAudio,
    pararGravacaoAudio,
    enviarArquivoAnexo,
    capturarFotoCamera
  };
};