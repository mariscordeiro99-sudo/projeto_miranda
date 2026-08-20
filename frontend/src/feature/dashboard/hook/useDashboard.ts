import { useState, useEffect } from 'react';
import api from '../../../common/services/api';
import type { DashboardMetrics } from '../types/dashboardMetrics';
import type {ApiError} from '../../../common/types/apiError';

export const useDashboard = () => {
  const [metrics, setMetrics] = useState<DashboardMetrics>({
    usuariosAtivos: 0,
    mensagensEnviadas: 0,
    taxaVisualizacao: '0%'
  });
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const fetchMetrics = async () => {
    try {
      setIsLoading(true);
      setError(null);
      
      const response = await api.get<DashboardMetrics>('/dashboard/metrics/');
      setMetrics(response.data);
    } catch (err: unknown) { 
      console.error('Erro ao buscar métricas do painel:', err);
      
      const apiError = err as ApiError;
      setError(apiError.response?.data?.detail || 'Não foi possível carregar os dados do painel.');
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    fetchMetrics();
  }, []);

  return {
    metrics,
    isLoading,
    error,
    refetch: fetchMetrics
  };
};