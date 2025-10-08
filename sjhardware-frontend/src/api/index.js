// src/api.js
import axios from 'axios';
import router from '../router';

const api = axios.create({
  baseURL: 'http://127.0.0.1:5000/api',
  headers: { 'Content-Type': 'application/json' },
});

// Attach token automatically
api.interceptors.request.use(config => {
  const token = localStorage.getItem('token');

  if (token) {
    // Check client-side token expiration
    const payload = JSON.parse(atob(token.split('.')[1]));
    if (payload.exp * 1000 < Date.now()) {
      // Token expired → logout
      localStorage.removeItem('token');
      localStorage.removeItem('user');
      delete api.defaults.headers.common['Authorization'];
      router.push('/login');
      throw new axios.Cancel('Token expired');
    }

    config.headers.Authorization = `Bearer ${token}`;
  }

  return config;
});

// Handle 401 from backend
api.interceptors.response.use(
  res => res,
  err => {
    if (err.response && err.response.status === 401) {
      localStorage.removeItem('token');
      localStorage.removeItem('user');
      delete api.defaults.headers.common['Authorization'];
      router.push('/login');
      alert('Session expired. Please login again.');
    }
    return Promise.reject(err);
  }
);

export default api;
