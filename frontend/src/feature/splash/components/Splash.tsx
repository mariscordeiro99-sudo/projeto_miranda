import React from 'react';
import { useSplash } from '../hooks/useSplash';
import '../style/splash.css';

// Você pode substituir por um arquivo local importando: import logoImg from '../assets/logo.png'
const LOGO_PLACEHOLDER = "https://cdn-icons-png.flaticon.com/512/5968/5968282.png"; 

const SplashPage: React.FC = () => {
  const { seconds } = useSplash();

  return (
    <div className="splash-container">
      <div className="splash-logo-wrapper">
        <div className="splash-loader-ring"></div>
        <img 
          src={LOGO_PLACEHOLDER} 
          alt="Logo Animada" 
          className="splash-logo" 
        />
      </div>
      
      <h1 className="splash-text">Iniciando Sistema</h1>
      <p className="splash-timer">Aguarde... {seconds}s</p>
    </div>
  );
};

export default SplashPage;