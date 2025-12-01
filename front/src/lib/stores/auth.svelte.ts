import { browser } from '$app/environment';
import type { User, LoginCredentials, RegisterData, ProfileUpdateData } from '$lib/types';
import { authService } from '$lib/services/auth';

// Token storage keys
const ACCESS_TOKEN_KEY = 'access_token';
const REFRESH_TOKEN_KEY = 'refresh_token';

// Auth state using Svelte 5 runes
let user = $state<User | null>(null);
let isLoading = $state(true);
let isAuthenticated = $state(false);

// Token management
function getAccessToken(): string | null {
  if (!browser) return null;
  return localStorage.getItem(ACCESS_TOKEN_KEY);
}

function getRefreshToken(): string | null {
  if (!browser) return null;
  return localStorage.getItem(REFRESH_TOKEN_KEY);
}

function setTokens(access: string, refresh: string): void {
  if (!browser) return;
  localStorage.setItem(ACCESS_TOKEN_KEY, access);
  localStorage.setItem(REFRESH_TOKEN_KEY, refresh);
}

function clearTokens(): void {
  if (!browser) return;
  localStorage.removeItem(ACCESS_TOKEN_KEY);
  localStorage.removeItem(REFRESH_TOKEN_KEY);
}

// Auth actions
async function login(credentials: LoginCredentials): Promise<User> {
  const response = await authService.login(credentials);

  setTokens(response.access, response.refresh);
  user = response.user;
  isAuthenticated = true;

  return response.user;
}

async function googleLogin(code: string): Promise<User> {
  const response = await authService.googleLogin(code);

  setTokens(response.access, response.refresh);
  user = response.user;
  isAuthenticated = true;

  return response.user;
}

// Get redirect path based on user role
function getRedirectPath(currentUser?: User | null): string {
  const u = currentUser || user;
  if (!u) return '/auth/login';

  switch (u.role) {
    case 'admin':
      return '/dashboard';
    case 'driver':
      return '/driver';
    case 'employee':
      return '/my-boardings';
    default:
      return '/dashboard';
  }
}

function getGoogleAuthUrl(): string {
  return authService.getGoogleAuthUrl();
}

async function register(data: RegisterData): Promise<User> {
  const newUser = await authService.register(data);
  return newUser;
}

async function logout(): Promise<void> {
  try {
    await authService.logout();
  } finally {
    clearTokens();
    user = null;
    isAuthenticated = false;
  }
}

async function refreshAccessToken(): Promise<boolean> {
  const refreshToken = getRefreshToken();
  if (!refreshToken) return false;

  try {
    const response = await authService.refreshToken(refreshToken);
    if (browser) {
      localStorage.setItem(ACCESS_TOKEN_KEY, response.access);
    }
    return true;
  } catch {
    clearTokens();
    user = null;
    isAuthenticated = false;
    return false;
  }
}

async function loadUser(): Promise<void> {
  isLoading = true;

  try {
    const token = getAccessToken();
    if (!token) {
      isLoading = false;
      return;
    }

    // Try to get user profile
    const currentUser = await authService.getProfile();
    user = currentUser;
    isAuthenticated = true;
  } catch (error) {
    // Try to refresh token
    const refreshed = await refreshAccessToken();
    if (refreshed) {
      try {
        const currentUser = await authService.getProfile();
        user = currentUser;
        isAuthenticated = true;
      } catch {
        clearTokens();
        user = null;
        isAuthenticated = false;
      }
    }
  } finally {
    isLoading = false;
  }
}

async function updateProfile(data: ProfileUpdateData): Promise<User> {
  const response = await authService.updateProfile(data);
  user = response.user;
  return response.user;
}

// Initialize on browser
if (browser) {
  loadUser();
}

// Export auth store
export const auth = {
  get user() { return user; },
  get isLoading() { return isLoading; },
  get isAuthenticated() { return isAuthenticated; },
  get accessToken() { return getAccessToken(); },

  login,
  googleLogin,
  getGoogleAuthUrl,
  getRedirectPath,
  register,
  logout,
  loadUser,
  updateProfile,
  refreshAccessToken,

  // Role checks
  get isAdmin() { return user?.role === 'admin'; },
  get isDriver() { return user?.role === 'driver'; },
  get isEmployee() { return user?.role === 'employee'; },

  // Permission checks
  canManageBuses() { return user?.role === 'admin'; },
  canManageRoutes() { return user?.role === 'admin'; },
  canManageTrips() { return user?.role === 'admin' || user?.role === 'driver'; },
  canViewDashboard() { return !!user; },
  canPerformCheckIn() { return user?.role === 'driver'; },
};

export default auth;
