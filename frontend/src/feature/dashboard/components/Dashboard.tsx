import React from 'react';
import { Users, MessageSquare, Eye, RefreshCw, AlertCircle } from 'lucide-react';
import { useDashboard } from '../hook/useDashboard';
import '../styles/dash.css';

const Dashboard: React.FC = () => {
  const { metrics, isLoading, error, refetch } = useDashboard();

  if (isLoading) {
    return (
      <main className="dashboard-container state-centered">
        <div className="loading-wrapper">
          <RefreshCw className="spinner" size={40} />
          <p>Carregando métricas do painel...</p>
        </div>
      </main>
    );
  }

  if (error) {
    return (
      <main className="dashboard-container state-centered">
        <div className="error-card">
          <AlertCircle size={48} color="#dc2626" />
          <h3>Ops! Algo deu errado</h3>
          <p>{error}</p>
          <button onClick={refetch} className="btn-retry">
            Tentar novamente
          </button>
        </div>
      </main>
    );
  }

  return (
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
  );
};

export default Dashboard;