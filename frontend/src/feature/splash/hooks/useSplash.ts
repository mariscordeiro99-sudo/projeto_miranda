import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { AppRoutes } from '../../../routes/types/loginReg';
import { SPLASH_CONFIG } from '../types/splashConfig';

export const useSplash = () => {
  const [seconds, setSeconds] = useState(SPLASH_CONFIG.DURATION_MS / 1000);
  const navigate = useNavigate();

  useEffect(() => {
    const timer = setInterval(() => {
      setSeconds((prev) => (prev > 0 ? prev - 1 : 0));
    }, SPLASH_CONFIG.TICK_INTERVAL_MS);

    const redirect = setTimeout(() => {
      navigate(AppRoutes.LOGIN);
    }, SPLASH_CONFIG.DURATION_MS);

    return () => {
      clearInterval(timer);
      clearTimeout(redirect);
    };
  }, [navigate]);

  return { seconds };
};