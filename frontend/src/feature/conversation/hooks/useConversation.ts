import { useState, useEffect } from 'react';
import type { ChatContato, Mensagem } from '../types/conversation';

export const useConversas = () => {
  const [contatos, setContatos] = useState<ChatContato[]>([]);
  const [contatoAtivo, setContatoAtivo] = useState<ChatContato | null>(null);
  const [mensagens, setMensagens] = useState<Mensagem[]>([]);
  const [mensagemInput, setMensagemInput] = useState<string>('');
  const [isLoading, setIsLoading] = useState<boolean>(true);

  // Recupera o ID do usuário logado para simular o remetente
  const currentUserId = "user-logado-123";

  useEffect(() => {
    // Simula carga inicial de contatos do sistema Nexa
    const carregarContatos = async () => {
      setIsLoading(true);
      try {
        await new Promise((resolve) => setTimeout(resolve, 800)); // Delay artificial
        
        const mockContatos: ChatContato[] = [
          {
            id: "1",
            nome: "Mariana Costa (Gestão)",
            foto: "https://images.unsplash.com/photo-1534528741775-53994a69daeb?q=80&w=150",
            role: "gestor",
            ultimaMensagem: "Pode me enviar o relatório de acessos atualizado?",
            timestampUltima: "10:42",
            naoLidas: 2
          },
          {
            id: "2",
            nome: "Roberto Alves",
            foto: null,
            role: "colaborador",
            ultimaMensagem: "Entendido, vou checar o mural.",
            timestampUltima: "Ontem",
            naoLidas: 0
          }
        ];
        
        setContatos(mockContatos);
      } catch (error) {
        console.error("Erro ao carregar contatos:", error);
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

    const carregarHistorico = () => {
      setContatos(prev => prev.map(c => c.id === contatoAtivo.id ? { ...c, naoLidas: 0 } : c));

      const historicoMock: Mensagem[] = [
        {
          id: "m1",
          senderId: contatoAtivo.id,
          texto: `Olá! Sou o ${contatoAtivo.nome}. Como posso te ajudar com os comunicados hoje?`,
          timestamp: "10:30"
        },
        {
          id: "m2",
          senderId: currentUserId,
          texto: "Oi! Tudo bem? Estou verificando as permissões do painel.",
          timestamp: "10:35"
        }
      ];

      if (contatoAtivo.ultimaMensagem && contatoAtivo.id === "1") {
        historicoMock.push({
          id: "m3",
          senderId: contatoAtivo.id,
          texto: contatoAtivo.ultimaMensagem,
          timestamp: "10:42"
        });
      }

      setMensagens(historicoMock);
    };

    carregarHistorico();
  }, [contatoAtivo]);

  const enviarMensagem = (e: React.FormEvent) => {
    e.preventDefault();
    if (!mensagemInput.trim() || !contatoAtivo) return;

    const novaMsg: Mensagem = {
      id: `msg-${Date.now()}`,
      senderId: currentUserId,
      texto: mensagemInput.trim(),
      timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
    };

    setMensagens(prev => [...prev, novaMsg]);
    
    setContatos(prev => prev.map(c => 
      c.id === contatoAtivo.id 
        ? { ...c, ultimaMensagem: novaMsg.texto, timestampUltima: novaMsg.timestamp } 
        : c
    ));

    setMensagemInput('');
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
    currentUserId
  };
};