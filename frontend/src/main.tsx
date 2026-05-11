import React from 'react';
import ReactDOM from 'react-dom/client';
import { AppRouter } from './routes';
import { AuthProvider } from './feature/auth/hooks/AuthProvider'; 

// Mantemos esta linha comentada para o Vite não travar no erro do CSS
// import "./index.css"; 

ReactDOM.createRoot(document.getElementById('root')!).render(
  <React.StrictMode>
    <AuthProvider>
      <AppRouter />
    </AuthProvider>
  </React.StrictMode>
);