import React from 'react';
import NavBar from '../../../common/components/NavBar';
import { Calendar, User, Pin, Loader2 } from 'lucide-react';
import { useComunicados } from '../hooks/useCommunication';
import '../style/communication.css';

const Comunicados: React.FC = () => {
  const { comunicados, isLoading } = useComunicados();

  return (
    <div className="comunicados-layout">
      <header>
        <NavBar />
      </header>

      <main className="comunicados-container">
        <div className="comunicados-header">
          <h2>Mural de Comunicados</h2>
          <p>Fique por dentro das últimas atualizações e avisos importantes.</p>
        </div>

        {isLoading ? (
          <div className="comunicados-loading">
            <Loader2 className="animate-spin" size={40} color="#4169E1" />
            <p>Carregando mural...</p>
          </div>
        ) : (
          <div className="comunicados-list">
            {comunicados.map((comunicado) => (
              <article 
                key={comunicado.id} 
                className={`comunicado-card ${comunicado.fixado ? 'is-fixed' : ''}`}
              >
                {comunicado.fixado && (
                  <div className="pinned-badge">
                    <Pin size={14} /> <span>Fixado pelo Gestor</span>
                  </div>
                )}

                <div className="comunicado-meta">
                  <div className="meta-item">
                    <User size={14} />
                    <span>{comunicado.autor}</span>
                  </div>
                  <div className="meta-item">
                    <Calendar size={14} />
                    <span>{comunicado.data}</span>
                  </div>
                </div>

                <h3 className="comunicado-title">{comunicado.titulo}</h3>
                <p className="comunicado-body">{comunicado.conteudo}</p>

                {comunicado.imagemUrl && (
                  <div className="comunicado-image-wrapper">
                    <img src={comunicado.imagemUrl} alt={comunicado.titulo} className="comunicado-img" />
                  </div>
                )}
              </article>
            ))}
          </div>
        )}
      </main>
    </div>
  );
};

export default Comunicados;