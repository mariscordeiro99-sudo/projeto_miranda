import React from 'react';
import { Plus, Edit2, Trash2, Eye, EyeOff, FileText, Image as ImageIcon, Video, X } from 'lucide-react';
import { useComunicadosAdmin } from '../hook/useAnnounEdt';
import '../styles/layoutAnnounEdt.css';
import '../styles/modalAnnounEdt.css';
import '../styles/previewAnnounEdt.css';


export const ComunicadosAdminPage: React.FC = () => {
    const {
        comunicados,
        isModalOpen,
        setIsModalOpen,
        isPreviewOpen,
        setIsPreviewOpen,
        comunicadoEdicao,
        titulo,
        setTitulo,
        resumo,
        setResumo,
        texto,
        setTexto,
        anexos,
        erroUpload,
        abrirCriacao,
        abrirEdicao,
        lidarComUploadArquivo,
        removerAnexo,
        salvarComunicado,
        alternarStatus,
        apagarComunicado
    } = useComunicadosAdmin();

    return (
        <main className="admin-container">
            {/* Cabeçalho de Controle */}
            <header className="admin-header-row">
                <button className="create-comunicado-btn" onClick={abrirCriacao} aria-label="Criar novo comunicado">
                    <Plus size={20} />
                    <span>Novo Comunicado</span>
                </button>
                <h2>Gerenciamento de Comunicados</h2>
            </header>

            {/* Lista de Comunicados para Gestão */}
            <section className="admin-list-grid">
                {comunicados.length === 0 ? (
                    <div className="empty-admin-state">Nenhum comunicado cadastrado no sistema.</div>
                ) : (
                    comunicados.map((comunicado) => (
                        <article key={comunicado.id} className={`admin-card ${comunicado.status === 'inativo' ? 'is-disabled' : ''}`}>
                            <div className="admin-card-content">
                                <span className="card-date">{comunicado.dataCriacao}</span>
                                <h3>{comunicado.titulo}</h3>
                                <p>{comunicado.resumo}</p>

                                {comunicado.anexos.length > 0 && (
                                    <div className="card-attachment-badge">
                                        <FileText size={14} />
                                        <span>{comunicado.anexos.length} anexo(s)</span>
                                    </div>
                                )}
                            </div>

                            {/* Barra de Ações Rápidas */}
                            <div className="admin-card-actions">
                                <button
                                    className="action-btn edit"
                                    onClick={() => abrirEdicao(comunicado)}
                                    title="Editar Comunicado"
                                >
                                    <Edit2 size={16} />
                                </button>

                                <button
                                    className={`action-btn toggle ${comunicado.status === 'ativo' ? 'active' : ''}`}
                                    onClick={() => alternarStatus(comunicado.id)}
                                    title={comunicado.status === 'ativo' ? "Desativar" : "Ativar"}
                                >
                                    {comunicado.status === 'ativo' ? <Eye size={16} /> : <EyeOff size={16} />}
                                </button>

                                <button
                                    className="action-btn delete"
                                    onClick={() => apagarComunicado(comunicado.id)}
                                    title="Apagar permanentemente"
                                >
                                    <Trash2 size={16} />
                                </button>
                            </div>
                        </article>
                    ))
                )}
            </section>

            {/* MODAL DE CADASTRO / EDIÇÃO */}
            {isModalOpen && (
                <div className="admin-modal-overlay">
                    <div className="admin-modal-box">
                        <header className="modal-box-header">
                            <h3>{comunicadoEdicao ? 'Editar Comunicado' : 'Cadastrar Comunicado'}</h3>
                            <button className="close-modal-btn" onClick={() => setIsModalOpen(false)}>
                                <X size={20} />
                            </button>
                        </header>

                        <form onSubmit={salvarComunicado} className="modal-form-body">
                            <label>
                                <span>Título do Comunicado</span>
                                <input type="text" value={titulo} onChange={(e) => setTitulo(e.target.value)} required max={100} />
                            </label>

                            <label>
                                <span>Resumo (Aparece no card do mural)</span>
                                <input type="text" value={resumo} onChange={(e) => setResumo(e.target.value)} required max={250} />
                            </label>

                            <label>
                                <span>Texto Completo</span>
                                <textarea value={texto} onChange={(e) => setTexto(e.target.value)} required rows={6} />
                            </label>

                            {/* Dropzone de Upload Segura */}
                            <div className="upload-section-wrapper">
                                <span>Anexos (MP4, JPEG, PNG ou PDF)</span>
                                <label className="custom-file-upload">
                                    <input type="file" accept=".mp4,.jpeg,.jpg,.png,.pdf" onChange={lidarComUploadArquivo} />
                                    <Plus size={16} /> Adicionar Arquivo
                                </label>

                                {erroUpload && <p className="upload-error-message">{erroUpload}</p>}

                                {/* Lista de Arquivos Pré-carregados */}
                                <div className="uploaded-files-list">
                                    {anexos.map((anexo) => (
                                        <div key={anexo.id} className="uploaded-file-row">
                                            <div className="file-meta">
                                                {anexo.tipo === 'image' && <ImageIcon size={16} color="#4169E1" />}
                                                {anexo.tipo === 'video' && <Video size={16} color="#7f00ff" />}
                                                {anexo.tipo === 'pdf' && <FileText size={16} color="#ef4444" />}
                                                <span className="file-name-txt">{anexo.nome}</span>
                                            </div>
                                            <button type="button" className="remove-file-btn" onClick={() => removerAnexo(anexo.id)}>
                                                <X size={14} />
                                            </button>
                                        </div>
                                    ))}
                                </div>
                            </div>

                            {/* Botões do Rodapé do Formulário */}
                            <footer className="modal-form-footer">
                                <button type="button" className="preview-btn" onClick={() => setIsPreviewOpen(true)}>
                                    Visualizar Modo Mural (Preview)
                                </button>
                                <div className="action-submit-group">
                                    <button type="button" className="cancel-form-btn" onClick={() => setIsModalOpen(false)}>Cancelar</button>
                                    <button type="submit" className="submit-form-btn">Salvar Alterações</button>
                                </div>
                            </footer>
                        </form>
                    </div>
                </div>
            )}

            {/* MODAL SEPARADO DE PREVIEW REALISTA (Como vai se comportar no mural) */}
            {isPreviewOpen && (
                <div className="admin-modal-overlay preview-layer">
                    <div className="preview-modal-box">
                        <header className="modal-box-header border-none">
                            <h3>Modo de Visualização Prévia</h3>
                            <button className="close-modal-btn" onClick={() => setIsPreviewOpen(false)}>
                                <X size={20} />
                            </button>
                        </header>

                        <div className="preview-mural-card">
                            <span className="preview-badge-live">Novo</span>
                            <h2>{titulo || "Título não preenchido"}</h2>
                            <p className="preview-text-body">{texto || "Nenhum texto completo digitado até o momento."}</p>

                            {/* Renderização condicional e segura de arquivos de mídia */}
                            {anexos.length > 0 && (
                                <div className="preview-media-container">
                                    {anexos.map((anexo) => (
                                        <div key={anexo.id} className="preview-media-item">
                                            {anexo.tipo === 'image' && (
                                                <img src={anexo.url} alt="Preview do anexo de imagem" className="secure-image-render" />
                                            )}
                                            {anexo.tipo === 'video' && (
                                                <video src={anexo.url} controls className="secure-video-render">
                                                    Seu navegador não suporta a execução deste vídeo.
                                                </video>
                                            )}
                                            {anexo.tipo === 'pdf' && (
                                                <a href={anexo.url} target="_blank" rel="noopener noreferrer" className="secure-pdf-download-anchor">
                                                    <FileText size={18} />
                                                    <span>Visualizar documento PDF associado ({anexo.nome})</span>
                                                </a>
                                            )}
                                        </div>
                                    ))}
                                </div>
                            )}
                        </div>
                    </div>
                </div>
            )}
        </main>
    );
};