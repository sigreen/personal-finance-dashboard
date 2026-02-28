import axios from 'axios';
import type {
  Account,
  Transaction,
  ImportLog,
  UploadResponse,
  CSVPreview,
  ImportRequest,
  ImportResult,
  Category
} from '../types';

const API_BASE_URL = import.meta.env.VITE_API_URL || '/api';

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Accounts
export const getAccounts = async (): Promise<Account[]> => {
  const response = await api.get('/accounts');
  return response.data;
};

export const getAccount = async (id: string): Promise<Account> => {
  const response = await api.get(`/accounts/${id}`);
  return response.data;
};

export const createAccount = async (account: Partial<Account>): Promise<Account> => {
  const response = await api.post('/accounts', account);
  return response.data;
};

// Transactions
export const getTransactions = async (params?: {
  account_id?: string;
  limit?: number;
  offset?: number;
}): Promise<Transaction[]> => {
  const response = await api.get('/transactions', { params });
  return response.data;
};

// CSV Import
export const uploadCSV = async (file: File): Promise<UploadResponse> => {
  const formData = new FormData();
  formData.append('file', file);

  const response = await api.post('/upload', formData, {
    headers: {
      'Content-Type': 'multipart/form-data',
    },
  });
  return response.data;
};

export const previewCSV = async (importId: string): Promise<CSVPreview> => {
  const response = await api.get(`/upload/${importId}/preview`);
  return response.data;
};

export const processImport = async (
  importId: string,
  request: ImportRequest
): Promise<ImportResult> => {
  const response = await api.post(`/import/${importId}/process`, request);
  return response.data;
};

export const getImportStatus = async (importId: string): Promise<ImportLog> => {
  const response = await api.get(`/import/${importId}/status`);
  return response.data;
};

export const getImportHistory = async (): Promise<ImportLog[]> => {
  const response = await api.get('/imports');
  return response.data;
};

// Categories
export const getCategories = async (): Promise<Category[]> => {
  const response = await api.get('/categories');
  return response.data;
};

export const updateTransactionCategory = async (
  transactionId: string,
  categoryId: string | null
): Promise<{ message: string; transaction_id: string }> => {
  const response = await api.patch(`/transactions/${transactionId}/category`, null, {
    params: { category_id: categoryId }
  });
  return response.data;
};

// Health check
export const healthCheck = async (): Promise<{ status: string; service: string }> => {
  const response = await api.get('/health');
  return response.data;
};

export default api;
