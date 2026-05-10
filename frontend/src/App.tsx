import React from 'react';
import { AppRouter } from './routes/index';
import './common/styles/global.css';

const App: React.FC = () => {
  return (
    <div className="app-wrapper">
      <AppRouter />
    </div>
  )
};

export default App;