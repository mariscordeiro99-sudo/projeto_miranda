import { useState, useEffect } from 'react';
import type { Comunicado } from '../types/communication';

export const useComunicados = () => {
  const [comunicados, setComunicados] = useState<Comunicado[]>([]);
  const [isLoading, setIsLoading] = useState<boolean>(true);

  useEffect(() => {
    // Simulando uma requisição de API do Django com dados mockados
    const carregarComunicados = () => {
      const dadosProvisorios: Comunicado[] = [
        {
          id: 1,
          titulo: "Manutenção Preventiva do Sistema",
          conteudo: "Informamos que no próximo domingo, entre as 02:00 e 05:00 da manhã, nosso sistema passará por uma atualização programada. Durante este período, o painel do gestor e as ferramentas de conversas poderão apresentar instabilidades momentâneas. Contamos com a compreensão de todos.",
          data: "19 Mai 2026",
          autor: "Suporte Técnico",
          fixado: true
        },
        {
          id: 2,
          titulo: "Nova Funcionalidade: Identidade Visual Flexível",
          conteudo: "Agora os gestores podem configurar as cores da instituição diretamente pelo painel de controle. A alteração reflete instantaneamente nos crachás virtuais e nas barras de navegação de todos os colaboradores associados.",
          data: "18 Mai 2026",
          autor: "Comunicação Interna",
          imagemUrl: "https://images.unsplash.com/photo-1618005182384-a83a8bd57fbe?q=80&w=600&auto=format&fit=crop",
          fixado: false
        }
      ];

      setComunicados(dadosProvisorios);
      setIsLoading(false);
    };

    carregarComunicados();
  }, []);

  return {
    comunicados,
    isLoading
  };
};