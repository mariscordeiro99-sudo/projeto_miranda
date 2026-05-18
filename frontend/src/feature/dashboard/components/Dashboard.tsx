import React from 'react';
import NavBar from '../../../common/components/NavBar';
import { Construction } from 'lucide-react';
import '../styles/dash.css';

const Dashboard: React.FC = () => {
  return (
    <div className="dashboard-layout">
      <header>
        <NavBar />
      </header>

      <main className="dashboard-content">
        <div className="placeholder-card">
          <Construction size={64} color="#4169E1" strokeWidth={1.5} />
          <h2>Painel do Gestor</h2>
          <p>Esta funcionalidade está em <strong>desenvolvimento</strong>.</p>
          <div className="status-badge">EM BREVE</div>
        </div>
      </main>
    </div>
  );
};

export default Dashboard;