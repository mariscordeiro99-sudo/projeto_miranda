export interface ApiError {
  response?: {
    data?: {
      detail?: string;
    };
  };
}