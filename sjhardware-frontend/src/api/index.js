import axios from 'axios';

const api = axios.create({
  baseURL: 'http://127.0.0.1:5000/api', // Flask backend URL
  headers: {
    'Content-Type': 'application/json',
  },
});

// Intercept requests (for adding tokens later)
api.interceptors.request.use(config => {
  // Example: add authentication token
  // const token = localStorage.getItem('token');
  // if (token) config.headers.Authorization = `Bearer ${token}`;
  return config;
});

export default api;
