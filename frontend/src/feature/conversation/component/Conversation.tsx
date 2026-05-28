import React from 'react';
import { User, Send, MessageSquare } from 'lucide-react';
import { useConversas } from '../hooks/useConversation';
import '../style/conversas.css';

export const ConversasPage: React.FC = () => {
  const {
    contatos,
    contatoAtivo,
    setContatoAtivo,
    mensagens,
    mensagemInput,
    setMensagemInput,
    enviarMensagem,
    isLoading,
    currentUserId
  } = useConversas();

  return (
    <main className="chat-container">
      <section className="chat-sidebar">
        <div className="sidebar-chat-header">
          <h3>Mensagens</h3>
        </div>

        <div className="contacts-list">
          {isLoading ? (
            <div className="chat-sidebar-loading">Carregando contatos...</div>
          ) : (
            contatos.map((contato) => (
              <div
                key={contato.id}
                className={`contact-item ${contatoAtivo?.id === contato.id ? 'is-active' : ''}`}
                onClick={() => setContatoAtivo(contato)}
              >
                <div className="contact-avatar-wrapper">
                  {contato.foto ? (
                    <img src={contato.foto} alt={contato.nome} className="contact-avatar" />
                  ) : (
                    <div className="contact-avatar-placeholder">
                      <User size={20} color="#4169E1" />
                    </div>
                  )}
                  {contato.naoLidas > 0 && (
                    <span className="unread-badge">{contato.naoLidas}</span>
                  )}
                </div>

                <div className="contact-info-preview">
                  <div className="contact-name-row">
                    <span className="contact-name">{contato.nome}</span>
                    <span className="contact-time">{contato.timestampUltima}</span>
                  </div>
                  <p className="contact-last-msg">{contato.ultimaMensagem || "Nenhuma mensagem"}</p>
                </div>
              </div>
            ))
          )}
        </div>
      </section>

      <section className="chat-window">
        {contatoAtivo ? (
          <>
            <div className="chat-window-header">
              <div className="active-contact-profile">
                {contatoAtivo.foto ? (
                  <img src={contatoAtivo.foto} alt={contatoAtivo.nome} className="contact-avatar" />
                ) : (
                  <div className="contact-avatar-placeholder">
                    <User size={18} color="#4169E1" />
                  </div>
                )}
                <div>
                  <h4>{contatoAtivo.nome}</h4>
                  <small className="active-contact-role">{contatoAtivo.role}</small>
                </div>
              </div>
            </div>

            <div className="chat-messages-body">
              {mensagens.map((msg) => {
                const isMe = msg.senderId === currentUserId;
                return (
                  <div key={msg.id} className={`message-row ${isMe ? 'is-me' : 'is-other'}`}>
                    <div className="message-bubble">
                      <p className="message-text">{msg.texto}</p>
                      <span className="message-time">{msg.timestamp}</span>
                    </div>
                  </div>
                );
              })}
            </div>

            <form className="chat-input-footer" onSubmit={enviarMensagem}>
              <input
                type="text"
                placeholder="Digite sua mensagem..."
                value={mensagemInput}
                onChange={(e) => setMensagemInput(e.target.value)}
              />
              <button type="submit" className="send-msg-btn" aria-label="Enviar mensagem">
                <Send size={18} />
              </button>
            </form>
          </>
        ) : (
          <div className="chat-empty-state">
            <MessageSquare size={48} color="#cbd5e1" />
            <h3>Nenhuma conversa selecionada</h3>
            <p>Escolha um contato na barra lateral para começar a conversar.</p>
          </div>
        )}
      </section>
    </main>
  );
};