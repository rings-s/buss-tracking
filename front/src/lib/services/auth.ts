import { apiClient } from './api-client';
import {
  loginCredentialsSchema,
  registerDataSchema,
  adminRegisterDataSchema,
  loginResponseSchema,
  userSchema,
  profileUpdateSchema,
  profileUpdateResponseSchema,
  changePasswordSchema,
  changePasswordResponseSchema,
} from '$lib/schemas';
import type {
  LoginCredentials,
  RegisterData,
  AdminRegisterData,
  LoginResponse,
  User,
  ProfileUpdateData,
  ProfileUpdateResponse,
  ChangePasswordData,
  ChangePasswordResponse,
} from '$lib/types';

// Google OAuth config
const GOOGLE_CLIENT_ID = import.meta.env.VITE_GOOGLE_CLIENT_ID || '';
const GOOGLE_REDIRECT_URI = import.meta.env.VITE_GOOGLE_REDIRECT_URI || 'http://localhost:5173/auth/callback';

export const authService = {
  /**
   * Login with email and password
   */
  async login(credentials: LoginCredentials): Promise<LoginResponse> {
    // Validate input
    const validatedCredentials = loginCredentialsSchema.parse(credentials);

    const response = await apiClient.post<LoginResponse>(
      '/api/auth/login/',
      validatedCredentials
    );

    // Validate response
    return loginResponseSchema.parse(response);
  },

  /**
   * Register a new employee (self-registration)
   */
  async register(data: RegisterData): Promise<User> {
    // Validate input
    const validatedData = registerDataSchema.parse(data);

    const response = await apiClient.post<User>(
      '/api/auth/register/',
      validatedData
    );

    // Validate response
    return userSchema.parse(response);
  },

  /**
   * Admin register - create user with any role
   */
  async adminRegister(data: AdminRegisterData): Promise<User> {
    // Validate input
    const validatedData = adminRegisterDataSchema.parse(data);

    const response = await apiClient.post<User>(
      '/api/auth/admin/register/',
      validatedData
    );

    // Validate response
    return userSchema.parse(response);
  },

  /**
   * Get current user profile
   */
  async getProfile(): Promise<User> {
    const response = await apiClient.get<User>('/api/auth/user/');
    return userSchema.parse(response);
  },

  /**
   * Update current user profile
   */
  async updateProfile(data: ProfileUpdateData): Promise<ProfileUpdateResponse> {
    // Validate input
    const validatedData = profileUpdateSchema.parse(data);

    const response = await apiClient.patch<ProfileUpdateResponse>(
      '/api/auth/user/',
      validatedData
    );

    return profileUpdateResponseSchema.parse(response);
  },

  /**
   * Change password
   */
  async changePassword(data: ChangePasswordData): Promise<ChangePasswordResponse> {
    // Validate input
    const validatedData = changePasswordSchema.parse(data);

    const response = await apiClient.post<ChangePasswordResponse>(
      '/api/auth/password/change/',
      validatedData
    );

    return changePasswordResponseSchema.parse(response);
  },

  /**
   * Refresh access token
   */
  async refreshToken(refreshToken: string): Promise<{ access: string }> {
    return apiClient.post<{ access: string }>('/api/auth/token/refresh/', {
      refresh: refreshToken,
    });
  },

  /**
   * Logout (invalidate tokens on server if supported)
   */
  async logout(): Promise<void> {
    try {
      await apiClient.post('/api/auth/logout/');
    } catch {
      // Ignore errors on logout
    }
  },

  /**
   * Verify token validity
   */
  async verifyToken(token: string): Promise<boolean> {
    try {
      await apiClient.post('/api/auth/token/verify/', { token });
      return true;
    } catch {
      return false;
    }
  },

  // ===========================================================================
  // GOOGLE OAUTH
  // ===========================================================================

  /**
   * Get Google OAuth URL to redirect user
   */
  getGoogleAuthUrl(): string {
    const params = new URLSearchParams({
      client_id: GOOGLE_CLIENT_ID,
      redirect_uri: GOOGLE_REDIRECT_URI,
      response_type: 'code',
      scope: 'openid email profile',
      access_type: 'offline',
      prompt: 'consent',
    });

    return `https://accounts.google.com/o/oauth2/v2/auth?${params.toString()}`;
  },

  /**
   * Login with Google OAuth code
   */
  async googleLogin(code: string): Promise<LoginResponse> {
    const response = await apiClient.post<LoginResponse>('/api/auth/google/', {
      code,
    });

    return loginResponseSchema.parse(response);
  },
};

export default authService;
