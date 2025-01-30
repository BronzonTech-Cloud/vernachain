import { apiClient, setAuthToken } from './client';

export interface User {
  id: string;
  email: string;
  two_factor_enabled: boolean;
  created_at: string;
  last_login?: string;
}

export interface LoginRequest {
  email: string;
  password: string;
  two_factor_code?: string;
}

export interface RegisterRequest {
  email: string;
  password: string;
  confirm_password: string;
}

export interface PasswordResetRequest {
  email: string;
}

export interface PasswordResetConfirmRequest {
  token: string;
  new_password: string;
  confirm_password: string;
}

export interface Enable2FARequest {
  password: string;
}

export interface Verify2FARequest {
  code: string;
}

export interface AuthResponse {
  user: User;
  token: string;
}

// Authentication API calls
export const login = async (request: LoginRequest): Promise<AuthResponse> => {
  const response = await apiClient.post<AuthResponse>('/api/v1/auth/login', request);
  if (response.data && 'token' in response.data) {
    setAuthToken(response.data.token);
    return response.data;
  }
  throw new Error('Invalid response format from login');
};

export const register = async (request: RegisterRequest): Promise<AuthResponse> => {
  const response = await apiClient.post<AuthResponse>('/api/v1/auth/register', request);
  if (response.data && 'token' in response.data) {
    setAuthToken(response.data.token);
    return response.data;
  }
  throw new Error('Invalid response format from register');
};

export const logout = async (): Promise<void> => {
  await apiClient.post('/api/v1/auth/logout');
  setAuthToken(null);
};

export const requestPasswordReset = async (request: PasswordResetRequest): Promise<void> => {
  return apiClient.post('/api/v1/auth/reset-password', request);
};

export const confirmPasswordReset = async (request: PasswordResetConfirmRequest): Promise<void> => {
  return apiClient.post('/api/v1/auth/reset-password/confirm', request);
};

export const enable2FA = async (request: Enable2FARequest): Promise<{
  qr_code: string;
  secret: string;
}> => {
  return apiClient.post('/api/v1/auth/enable-2fa', request);
};

export const verify2FA = async (request: Verify2FARequest): Promise<void> => {
  return apiClient.post('/api/v1/auth/verify-2fa', request);
};

export const disable2FA = async (request: Enable2FARequest): Promise<void> => {
  return apiClient.post('/api/v1/auth/disable-2fa', request);
}; 