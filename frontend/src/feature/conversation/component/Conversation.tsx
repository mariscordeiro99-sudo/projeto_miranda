import React, { useRef } from 'react';
import { User, Send, MessageSquare, Mic, MicOff, Paperclip, Camera, FileText } from 'lucide-react';
import { useConversas } from '../hooks/useConversation';
import '../style/conversation.css';

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
        currentUserId,
        isGravandoAudio,
        iniciarGravacaoAudio,
        pararGravacaoAudio,
        enviarArquivoAnexo,
        capturarFotoCamera
    } = useConversas();

    const fileInputRef = useRef<HTMLInputElement>(null);

    const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
        const file = e.target.files?.[0];
        if (file) {
            enviarArquivoAnexo(file);
        }
    };

    const dispararSeletorArquivo = () => {
        fileInputRef.current?.click();
    };

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

                                            {msg.tipo === 'texto' && (
                                                <p className="message-text">{msg.texto}</p>
                                            )}

                                            {msg.tipo === 'imagem' && msg.midiaUrl && (
                                                <img src={msg.midiaUrl} alt="Imagem enviada" className="chat-media-preview image" />
                                            )}

                                            {msg.tipo === 'video' && msg.midiaUrl && (
                                                <video src={msg.midiaUrl} controls className="chat-media-preview video" />
                                            )}

                                            {msg.tipo === 'audio' && msg.midiaUrl && (
                                                <audio src={msg.midiaUrl} controls className="chat-media-player audio" />
                                            )}

                                            {msg.tipo === 'documento' && msg.midiaUrl && (
                                                <a href={msg.midiaUrl} target="_blank" rel="noopener noreferrer" className="chat-document-link">
                                                    <FileText size={24} />
                                                    <span className="doc-name">{msg.nomeArquivo || 'Visualizar PDF / Documento'}</span>
                                                </a>
                                            )}

                                            <span className="message-time">{msg.timestamp}</span>
                                        </div>
                                    </div>
                                );
                            })}
                        </div>

                        <footer className="chat-input-footer-container">
                            <form className="chat-input-footer" onSubmit={enviarMensagem}>

                                <input
                                    type="file"
                                    ref={fileInputRef}
                                    onChange={handleFileChange}
                                    accept=".mp4,.mp3,.png,.jpg,.jpeg,.pdf"
                                    className="hidden-file-input"
                                    style={{ display: 'none' }}
                                />

                                <div className="chat-action-buttons">
                                    <button type="button" className="chat-media-btn" onClick={dispararSeletorArquivo} title="Anexar Arquivo (Max 50MB)">
                                        <Paperclip size={20} />
                                    </button>
                                    <button type="button" className="chat-media-btn" onClick={capturarFotoCamera} title="Tirar Foto com a Câmera">
                                        <Camera size={20} />
                                    </button>

                                    <button
                                        type="button"
                                        className={`chat-media-btn btn-audio-recorder ${isGravandoAudio ? 'recording' : ''}`}
                                        onClick={isGravandoAudio ? pararGravacaoAudio : iniciarGravacaoAudio}
                                        title={isGravandoAudio ? "Parar e Enviar" : "Gravar Áudio"}
                                    >
                                        {isGravandoAudio ? <MicOff size={20} color="#ef4444" /> : <Mic size={20} />}
                                    </button>
                                </div>

                                <input
                                    type="text"
                                    placeholder={isGravandoAudio ? "Gravando áudio... clique no microfone para parar e enviar" : "Digite sua mensagem..."}
                                    value={mensagemInput}
                                    onChange={(e) => setMensagemInput(e.target.value)}
                                    disabled={isGravandoAudio}
                                />

                                <button type="submit" className="send-msg-btn" aria-label="Enviar mensagem" disabled={isGravandoAudio || !mensagemInput.trim()}>
                                    <Send size={18} />
                                </button>
                            </form>
                        </footer>
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