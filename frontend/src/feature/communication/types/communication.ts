export interface AnexoComunicado {
  id: string;
  nome: string;
  arquivoUrl: string;
  tamanho?: string;
}

export interface Comunicado {
  id: number;
  titulo: string;
  conteudo: string;
  data: string;
  autor: string;
  imagemUrl?: string;
  fixado: boolean;
  anexos?: AnexoComunicado[];
}