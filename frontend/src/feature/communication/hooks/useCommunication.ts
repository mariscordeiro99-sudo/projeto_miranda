import { useState, useEffect } from 'react';
import api from '../../../common/services/api';
import type { Comunicado } from '../types/communication';
import type { ApiError } from '../../../common/types/apiError';

export const useComunicados = () => {
  const [comunicados, setComunicados] = useState<Comunicado[]>([]);
  const [comunicadoAtivo, setComunicadoAtivo] = useState<Comunicado | null>(null);
  const [isLoading, setIsLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);

  const carregarComunicados = async (isMounted: boolean) => {
    try {
      if (isMounted) {
        setIsLoading(true);
        setError(null);
      }

      const response = await api.get<Comunicado[]>('/announcements/');

      if (isMounted) {
        setComunicados(response.data);
      }
    } catch (err: unknown) {
      console.error("Erro ao carregar comunicados da API:", err);

      if (isMounted) {
        const apiError = err as ApiError;
        setError(apiError.response?.data?.detail || 'Não foi possível carregar o mural de comunicados.');
      }
    } finally {
      if (isMounted) {
        setIsLoading(false);
      }
    }
  };

  useEffect(() => {
    let isMounted = true;

    carregarComunicados(isMounted);

    return () => {
      isMounted = false;
    };
  }, []);

  const abrirComunicado = (comunicado: Comunicado) => {
    setComunicadoAtivo(comunicado);
  };

  const fecharComunicado = () => {
    setComunicadoAtivo(null);
  };

  return {
    comunicados,
    comunicadoAtivo,
    abrirComunicado,
    fecharComunicado,
    isLoading,
    error,
    refetch: () => carregarComunicados(true) 
  };
};