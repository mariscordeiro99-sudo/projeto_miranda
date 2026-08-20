import axios from 'axios';

const configuredBaseUrl = import.meta.env.VITE_API_URL;
const configuredApiBaseUrl = import.meta.env.VITE_API_BASE_URL;
const baseURL = configuredBaseUrl
  || configuredApiBaseUrl?.replace(/\/api\/?$/, '')
  || 'http://localhost:8000';

const api = axios.create({
  baseURL,
  timeout: 30000,
  headers: {
    'Content-Type': 'application/json',
  },
});

api.interceptors.request.use((config) => {
  const token = localStorage.getItem('auth_token') || localStorage.getItem('token');
  if (token && config.headers) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

export default api;
export { api };
