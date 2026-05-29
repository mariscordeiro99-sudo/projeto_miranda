export interface AnexoComunicado {
    id: string;
    nome: string;
    tipo: 'image' | 'video' | 'pdf';
    url: string;
    file?: File;
}

export interface ComunicadoAdmin {
    id: string;
    titulo: string;
    resumo: string;
    texto: string;
    status: 'ativo' | 'inativo';
    dataCriacao: string;
    anexos: AnexoComunicado[];
}

export interface FormComunicadoState {
    titulo: string;
    resumo: string;
    texto: string;
    anexos: AnexoComunicado[];
}