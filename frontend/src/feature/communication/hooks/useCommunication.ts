import { useState, useEffect } from 'react';
import type { Comunicado } from '../types/communication';
import type { ComunicadoAdmin } from '../../announcementsEdition/types/announEdt'; 

export const useComunicados = () => {
  const [comunicados, setComunicados] = useState<Comunicado[]>([]);
  const [isLoading, setIsLoading] = useState<boolean>(true);

  useEffect(() => {
    let isMounted = true; 

    const carregarComunicados = async () => {
      try {
        await new Promise((resolve) => setTimeout(resolve, 300));

        const bancoLocal = localStorage.getItem('nexa_comunicados_db');
        
        if (bancoLocal && isMounted) {
          const dadosAdmin: ComunicadoAdmin[] = JSON.parse(bancoLocal);

          const dadosAdaptados: Comunicado[] = dadosAdmin
            .filter((item) => item.status === 'ativo')
            .map((item) => {
              const imagemAnexo = item.anexos?.find(anexo => anexo.tipo === 'image');

              const idTratado = isNaN(Number(item.id)) 
                ? item.id 
                : Number(item.id);

              return {
                id: idTratado as Comunicado['id'], 
                titulo: item.titulo,
                conteudo: item.texto,   
                data: item.dataCriacao,
                autor: "Comunicação Nexa", 
                imagemUrl: imagemAnexo ? imagemAnexo.url : undefined,
                fixado: false 
              };
            });

          setComunicados(dadosAdaptados);
        } else if (isMounted) {
          setComunicados([]);
        }

        if (isMounted) {
          setIsLoading(false);
        }
      } catch (error) {
        console.error("Erro ao carregar e mapear comunicados:", error);
        if (isMounted) {
          setIsLoading(false);
        }
      }
    };

    carregarComunicados();

    return () => {
      isMounted = false;
    };
  }, []);

  return {
    comunicados,
    isLoading
  };
};