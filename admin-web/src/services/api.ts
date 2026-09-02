import axios from 'axios';
import { API_URL } from '../constants/api';
import { authStorage } from '../lib/authStorage';

const api = axios.create({
  baseURL: API_URL,
});

// Interceptor to add auth token
api.interceptors.request.use((config) => {
  const token = authStorage.getItem('token');
  if (token && config.headers) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

// Handle unauthorized responses
api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      authStorage.removeItem('token');
      authStorage.removeItem('role');
      window.location.href = '/login';
    }
    return Promise.reject(error);
  }
);

export const loginAdmin = async (credentials: { email: string; password: string }) => {
  const response = await api.post('/auth/admin-login', credentials);
  return response.data;
};

export const fetchDashboardMetrics = async () => {
  const response = await api.get('/admin/dashboard');
  return response.data;
};

export const createVoucher = async (code: string, discountAmount: number, pointsCost: number = 0) => {
  const response = await api.post('/points/vouchers/admin/create', {
    voucher_code: code,
    discount_type: 'fixed_amount',
    discount_amount: discountAmount,
    minimum_spend: 0,
    usage_limit: 1000,
    expires_in_days: 0, // 0 means no expiration
    points_cost: pointsCost
  });
  return response.data;
};

export const getVouchers = async () => {
  const response = await api.get('/admin/vouchers');
  return response.data;
};

export const deleteVoucher = async (id: number) => {
  const response = await api.delete(`/admin/vouchers/${id}`);
  return response.data;
};

export const fetchUsers = async (page: number = 1, limit: number = 50) => {
  const response = await api.get(`/admin/users?page=${page}&limit=${limit}`);
  return response.data;
};

export const triggerScraper = async (storeName: string) => {
  const response = await api.post(`/admin/trigger-scraper?store_name=${storeName}`);
  return response.data;
};
