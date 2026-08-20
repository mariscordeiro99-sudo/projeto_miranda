import React from 'react';
import { Palette, Upload, Save, Image as ImageIcon } from 'lucide-react';
import { useIdentidade } from '../hook/useIdentification';
import '../style/identification.css';

export const IdentityPage: React.FC = () => {
  const {
    brasao,
    isAlterado,
    isSaving,
    fileInputRef,
    dispararSeletorArquivo,
    handleMudarArquivo,
    salvarIdentidadeVisual
  } = useIdentidade();

  return (
    <main className="identity-container">
      <header className="identity-header">
        <div className="identity-title-wrapper">
          <Palette size={28} color="#4169E1" />
          <div>
            <h2>Identidade Visual</h2>
            <p>Personalize os elementos visuais da instituição dentro do ecossistema Nexa.</p>
          </div>
        </div>
      </header>

      <section className="identity-card-panel">
        <div className="identity-card">
          <h3 className="identity-card-title">Brasão da Instituição</h3>
          <p className="identity-card-description">
            Este logotipo será exibido na barra de navegação superior e nos relatórios gerados pelo sistema.
          </p>

          <div className="identity-form">
            <div className="identity-preview-group">
              <div className="identity-preview-box">
                {brasao?.url ? (
                  <img 
                    src={brasao.url} 
                    alt="Pré-visualização do Brasão" 
                    className="identity-preview-img" 
                  />
                ) : (
                  <div className="identity-preview-placeholder">
                    <ImageIcon size={48} color="#94a3b8" />
                  </div>
                )}
              </div>

              <input
                type="file"
                ref={fileInputRef}
                onChange={handleMudarArquivo}
                accept="image/*"
                style={{ display: 'none' }}
              />

              <button 
                type="button" 
                className="btn-upload-custom" 
                onClick={dispararSeletorArquivo}
              >
                <Upload size={16} />
                <span>Escolher Nova Imagem</span>
              </button>
            </div>

            <div className="identity-divider" />

            <div className="identity-actions">
              <button
                type="button"
                className="btn-submit-identity"
                disabled={!isAlterado || isSaving}
                onClick={salvarIdentidadeVisual}
              >
                <Save size={18} />
                <span>{isSaving ? 'Salvando...' : 'Salvar Alterações'}</span>
              </button>
            </div>
          </div>
        </div>
      </section>
    </main>
  );
};

export default IdentityPage;