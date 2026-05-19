export interface Comunicado {
  id: number;
  titulo: string;
  conteudo: string;
  data: string;
  autor: string;
  imagemUrl?: string;
  fixado: boolean;
}