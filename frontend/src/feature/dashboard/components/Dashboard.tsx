import React from 'react';
import NavBar from '../../../common/components/NavBar';
import { Users, MessageSquare, Eye } from 'lucide-react';
import '../styles/dash.css';

const Dashboard: React.FC = () => {
  const metrics = {
    usuariosAtivos: 0,
    mensagensEnviadas: 0,
    taxaVisualizacao: "0%"
  };

  return (
    <div className="dashboard-layout">
      <header>
        <NavBar />
      </header>

      <main className="dashboard-container">
        <div className="dashboard-grid">

          <div className="metric-card card-usuarios">
            <div className="card-icon-wrapper">
              <Users size={32} />
            </div>
            <div className="card-info">
              <h3>Usuários Ativos</h3>
              <p className="card-value">{metrics.usuariosAtivos}</p>
            </div>
          </div>

          <div className="metric-card card-mensagens">
            <div className="card-icon-wrapper">
              <MessageSquare size={32} />
            </div>
            <div className="card-info">
              <h3>Mensagens Enviadas</h3>
              <p className="card-value">{metrics.mensagensEnviadas}</p>
            </div>
          </div>

          <div className="metric-card card-visualizacao">
            <div className="card-icon-wrapper">
              <Eye size={40} /> 
            </div>
            <div className="card-info">
              <h3>Taxa de Visualização</h3>
              <p className="card-value value-large">{metrics.taxaVisualizacao}</p>
            </div>
          </div>

        </div>
      </main>
    </div>
  );
};

export default Dashboard;