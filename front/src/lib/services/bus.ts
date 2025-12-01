import { z } from 'zod';
import { apiClient } from './api-client';
import {
  busSchema,
  busCreateSchema,
  busLocationSchema,
  gpsUpdateSchema,
  routeSchema,
  routeCreateSchema,
} from '$lib/schemas';
import type {
  Bus,
  BusCreateData,
  BusUpdateData,
  BusLocation,
  GPSUpdateData,
  Route,
  RouteCreateData,
  PaginatedResponse,
} from '$lib/types';

export const busService = {
  // ==========================================================================
  // BUS CRUD
  // ==========================================================================

  /**
   * Get all buses
   */
  async list(params?: { active?: boolean }): Promise<Bus[]> {
    const response = await apiClient.get<Bus[]>('/api/buses/', { params });
    return z.array(busSchema).parse(response);
  },

  /**
   * Get paginated buses
   */
  async listPaginated(params?: {
    page?: number;
    active?: boolean;
  }): Promise<PaginatedResponse<Bus>> {
    const response = await apiClient.get<PaginatedResponse<Bus>>('/api/buses/', {
      params,
    });
    return {
      ...response,
      results: z.array(busSchema).parse(response.results),
    };
  },

  /**
   * Get single bus by ID
   */
  async get(id: number): Promise<Bus> {
    const response = await apiClient.get<Bus>(`/api/buses/${id}/`);
    return busSchema.parse(response);
  },

  /**
   * Create new bus
   */
  async create(data: BusCreateData): Promise<Bus> {
    const validatedData = busCreateSchema.parse(data);
    const response = await apiClient.post<Bus>('/api/buses/', validatedData);
    return busSchema.parse(response);
  },

  /**
   * Update bus
   */
  async update(id: number, data: BusUpdateData): Promise<Bus> {
    const response = await apiClient.patch<Bus>(`/api/buses/${id}/`, data);
    return busSchema.parse(response);
  },

  /**
   * Delete bus
   */
  async delete(id: number): Promise<void> {
    await apiClient.delete(`/api/buses/${id}/`);
  },

  // ==========================================================================
  // GPS LOCATION
  // ==========================================================================

  /**
   * Update GPS location for a bus
   */
  async updateGPS(data: GPSUpdateData): Promise<BusLocation> {
    const validatedData = gpsUpdateSchema.parse(data);
    const response = await apiClient.post<BusLocation>(
      '/api/gps-update/',
      validatedData
    );
    return busLocationSchema.parse(response);
  },

  /**
   * Get location history for a bus
   */
  async getLocationHistory(busId: number, limit = 50): Promise<BusLocation[]> {
    const response = await apiClient.get<BusLocation[]>(
      `/api/buses/${busId}/locations/`,
      { params: { limit } }
    );
    return z.array(busLocationSchema).parse(response);
  },
};

export const routeService = {
  // ==========================================================================
  // ROUTE CRUD
  // ==========================================================================

  /**
   * Get all routes
   */
  async list(): Promise<Route[]> {
    const response = await apiClient.get<Route[]>('/api/routes/');
    return z.array(routeSchema).parse(response);
  },

  /**
   * Get single route by ID
   */
  async get(id: number): Promise<Route> {
    const response = await apiClient.get<Route>(`/api/routes/${id}/`);
    return routeSchema.parse(response);
  },

  /**
   * Create new route
   */
  async create(data: RouteCreateData): Promise<Route> {
    const validatedData = routeCreateSchema.parse(data);
    const response = await apiClient.post<Route>('/api/routes/', validatedData);
    return routeSchema.parse(response);
  },

  /**
   * Update route
   */
  async update(id: number, data: Partial<RouteCreateData>): Promise<Route> {
    const response = await apiClient.patch<Route>(`/api/routes/${id}/`, data);
    return routeSchema.parse(response);
  },

  /**
   * Delete route
   */
  async delete(id: number): Promise<void> {
    await apiClient.delete(`/api/routes/${id}/`);
  },
};

export default { busService, routeService };
