import axios, { AxiosInstance, AxiosResponse, AxiosError } from 'axios';

// API response types
export interface APIResponse<T = any> {
  success: boolean;
  data?: T;
  error?: string;
  message?: string;
  timestamp: string;
}

export interface PaginatedResponse<T = any> {
  items: T[];
  total: number;
  page: number;
  page_size: number;
  total_pages: number;
  has_next: boolean;
  has_prev: boolean;
}

// API client class
class APIClient {
  private client: AxiosInstance;
  private baseURL: string;

  constructor() {
    this.baseURL = import.meta.env.VITE_API_URL || 'http://localhost:8000';
    this.client = axios.create({
      baseURL: this.baseURL,
      timeout: 10000,
      headers: {
        'Content-Type': 'application/json',
      },
    });

    // Add request interceptor
    this.client.interceptors.request.use(
      (config) => {
        const token = localStorage.getItem('token');
        if (token) {
          config.headers.Authorization = `Bearer ${token}`;
        }
        return config;
      },
      (error) => Promise.reject(error)
    );

    // Add response interceptor
    this.client.interceptors.response.use(
      (response) => response,
      this.handleError
    );
  }

  private handleError(error: AxiosError): Promise<never> {
    if (error.response?.status === 401) {
      // Handle unauthorized access
      localStorage.removeItem('token');
      window.location.href = '/login';
    }
    return Promise.reject(error);
  }

  // Generic request method
  private async request<T>(
    method: string,
    endpoint: string,
    data?: any,
    config?: any
  ): Promise<APIResponse<T>> {
    try {
      const response: AxiosResponse<APIResponse<T>> = await this.client.request({
        method,
        url: endpoint,
        data,
        ...config,
      });
      return response.data;
    } catch (error) {
      if (axios.isAxiosError(error)) {
        throw new Error(error.response?.data?.error || error.message);
      }
      throw error;
    }
  }

  // HTTP methods
  async get<T>(endpoint: string, params?: any): Promise<APIResponse<T>> {
    return this.request<T>('GET', endpoint, undefined, { params });
  }

  async post<T>(endpoint: string, data?: any): Promise<APIResponse<T>> {
    return this.request<T>('POST', endpoint, data);
  }

  async put<T>(endpoint: string, data?: any): Promise<APIResponse<T>> {
    return this.request<T>('PUT', endpoint, data);
  }

  async delete<T>(endpoint: string): Promise<APIResponse<T>> {
    return this.request<T>('DELETE', endpoint);
  }

  // Pagination helper
  async getPaginated<T>(
    endpoint: string,
    page = 1,
    pageSize = 10,
    sortBy?: string,
    sortDesc = false
  ): Promise<PaginatedResponse<T>> {
    const params = {
      page,
      page_size: pageSize,
      sort_by: sortBy,
      sort_desc: sortDesc,
    };
    const response = await this.get<PaginatedResponse<T>>(endpoint, params);
    return response.data!;
  }

  // WebSocket connection
  connectWebSocket(): WebSocket {
    const ws = new WebSocket(`ws://${this.baseURL.replace(/^http(s)?:\/\//, '')}/ws`);
    
    ws.onopen = () => {
      console.log('WebSocket connected');
    };

    ws.onerror = (error) => {
      console.error('WebSocket error:', error);
    };

    ws.onclose = () => {
      console.log('WebSocket disconnected');
      // Implement reconnection logic if needed
    };

    return ws;
  }

  // Authentication methods
  async login(email: string, password: string): Promise<void> {
    const response = await this.post<{ token: string }>('/api/auth/login', {
      email,
      password,
    });
    if (response.success && response.data?.token) {
      localStorage.setItem('token', response.data.token);
    }
  }

  async logout(): Promise<void> {
    await this.post('/api/auth/logout');
    localStorage.removeItem('token');
  }

  // Blockchain methods
  async getWalletBalance(address: string): Promise<string> {
    const response = await this.get<{ balance: string }>(
      `/api/blockchain/balance/${address}`
    );
    return response.data?.balance || '0';
  }

  async sendTransaction(to: string, amount: string): Promise<string> {
    const response = await this.post<{ hash: string }>('/api/blockchain/transfer', {
      to,
      amount,
    });
    return response.data?.hash || '';
  }
}

// Create and export singleton instance
export const api = new APIClient();

// Export type utilities
export type { AxiosError }; 