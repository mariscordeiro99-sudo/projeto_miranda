export interface Mensagem {
  id: string;
  senderId: string;
  texto: string;
  timestamp: string;
}

export interface ChatContato {
  id: string;
  nome: string;
  foto: string | null;
  role: 'gestor' | 'colaborador';
  ultimaMensagem?: string;
  timestampUltima?: string;
  naoLidas: number;
}

export interface ConversasState {
  contatos: ChatContato[];
  contatoAtivo: ChatContato | null;
  mensagens: Mensagem[];
  mensagemInput: string;
  isLoading: boolean;
}