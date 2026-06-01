import axios from 'axios';
import { getToken, clearToken } from './auth';

// Dev: Vite proxy forwards '/api/v1' → localhost backend
// Production (Vercel): no proxy exists, must call Render backend directly
const baseURL = import.meta.env.PROD && import.meta.env.VITE_API_BASE_URL
  ? `${import.meta.env.VITE_API_BASE_URL}/api/v1`
  : '/api/v1';

const api = axios.create({ baseURL });

api.interceptors.request.use((config) => {
  const token = getToken();
  if (token) config.headers.Authorization = `Bearer ${token}`;
  return config;
});

api.interceptors.response.use(
  (res) => res,
  (err) => {
    if (err.response?.status === 401) {
      clearToken();
      window.location.href = '/login';
    }
    return Promise.reject(err);
  }
);

export default api;
