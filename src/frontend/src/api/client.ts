import axios, { AxiosError, AxiosInstance } from 'axios';

// Default service URLs from environment variables or fallback to localhost
const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';
const EXPLORER_URL = import.meta.env.VITE_EXPLORER_URL || 'http://localhost:8001';
const NODE_URL = import.meta.env.VITE_NODE_URL || 'http://localhost:5001';
const API_KEY = import.meta.env.VITE_API_KEY;

console.log('API URLs:', {
  API_URL,
  EXPLORER_URL,
  NODE_URL,
  API_KEY: API_KEY ? '[REDACTED]' : 'Not set'
});

export interface ApiError {
  message: string;
  code?: string;
  details?: Record<string, any>;
}

export class ApiRequestError extends Error {
  constructor(
    message: string,
    public statusCode: number,
    public error: ApiError
  ) {
    super(message);
    this.name = 'ApiRequestError';
  }
}

// Create axios instances for different services
export const createClient = (baseURL: string): AxiosInstance => {
  const instance = axios.create({
    baseURL,
    headers: {
      'X-API-Key': API_KEY,
      'Content-Type': 'application/json',
    },
    timeout: 30000, // 30 second timeout
  });

  // Response interceptor for error handling
  instance.interceptors.response.use(
    (response) => {
      console.log(`Response from ${baseURL}:`, {
        status: response.status,
        url: response.config.url,
        method: response.config.method
      });
      return response.data;
    },
    (error: AxiosError) => {
      console.error(`Error from ${baseURL}:`, {
        url: error.config?.url,
        method: error.config?.method,
        status: error.response?.status,
        data: error.response?.data,
        message: error.message
      });
      
      const statusCode = error.response?.status || 500;
      const errorData = error.response?.data as ApiError || {
        message: error.message || 'An unexpected error occurred',
      };
      
      throw new ApiRequestError(
        errorData.message,
        statusCode,
        errorData
      );
    }
  );

  // Request interceptor for authentication
  instance.interceptors.request.use((config) => {
    const token = localStorage.getItem('auth_token');
    if (token) {
      config.headers['Authorization'] = `Bearer ${token}`;
    }
    console.log(`Request to ${baseURL}:`, {
      url: config.url,
      method: config.method,
      hasToken: !!token
    });
    return config;
  });

  return instance;
};

// Create instances for different services
export const apiClient = createClient(API_URL);
export const explorerClient = createClient(EXPLORER_URL);
export const nodeClient = createClient(NODE_URL);

// Test connections to all services
const testConnections = async () => {
  try {
    await apiClient.get('/health');
    console.log('API service is connected');
  } catch (error) {
    console.error('API service connection failed:', error);
  }

  try {
    await explorerClient.get('/health');
    console.log('Explorer service is connected');
  } catch (error) {
    console.error('Explorer service connection failed:', error);
  }

  try {
    await nodeClient.get('/health');
    console.log('Node service is connected');
  } catch (error) {
    console.error('Node service connection failed:', error);
  }
};

// Run connection test when the client is initialized
testConnections();

export const setAuthToken = (token: string | null) => {
  if (token) {
    localStorage.setItem('auth_token', token);
  } else {
    localStorage.removeItem('auth_token');
  }
}; 