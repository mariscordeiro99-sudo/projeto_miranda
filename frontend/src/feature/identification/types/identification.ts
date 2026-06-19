export interface BrasaoMidia {
  id: string;
  nome: string;
  url: string;
  file?: File;
}

export interface FormIdentidadeState {
  brasaoAtual: BrasaoMidia | null;
  isAlterado: boolean;
}