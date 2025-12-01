import { z } from 'zod';
import { apiClient } from './api-client';
import {
  tripSchema,
  tripDetailSchema,
  tripCreateSchema,
  employeeBoardingSchema,
  checkInDataSchema,
  checkInResponseSchema,
  liveTrackingSchema,
  dashboardDataSchema,
} from '$lib/schemas';
import type {
  Trip,
  TripDetail,
  TripCreateData,
  EmployeeBoarding,
  CheckInData,
  CheckInResponse,
  LiveTracking,
  DashboardData,
  PaginatedResponse,
} from '$lib/types';

export const tripService = {
  // ==========================================================================
  // TRIP CRUD
  // ==========================================================================

  /**
   * Get all trips
   */
  async list(params?: {
    is_active?: boolean;
    driver_id?: number;
    bus_id?: number;
  }): Promise<Trip[]> {
    const response = await apiClient.get<any>('/api/trips/', { params });
    // Handle paginated, non-paginated, or other response formats
    let results: Trip[];
    if (Array.isArray(response)) {
      results = response;
    } else if (response?.results) {
      results = response.results;
    } else {
      results = [];
    }
    return z.array(tripSchema).parse(results);
  },

  /**
   * Get paginated trips
   */
  async listPaginated(params?: {
    page?: number;
    is_active?: boolean;
  }): Promise<PaginatedResponse<Trip>> {
    const response = await apiClient.get<PaginatedResponse<Trip>>('/api/trips/', {
      params,
    });
    return {
      ...response,
      results: z.array(tripSchema).parse(response.results),
    };
  },

  /**
   * Get single trip with details
   */
  async get(id: number): Promise<TripDetail> {
    const response = await apiClient.get<TripDetail>(`/api/trips/${id}/`);
    return tripDetailSchema.parse(response);
  },

  /**
   * Create/start new trip
   */
  async create(data: TripCreateData): Promise<Trip> {
    const validatedData = tripCreateSchema.parse(data);
    const response = await apiClient.post<Trip>('/api/trips/', validatedData);
    return tripSchema.parse(response);
  },

  /**
   * Start a trip (action endpoint)
   */
  async start(id: number): Promise<Trip> {
    const response = await apiClient.post<Trip>(`/api/trips/${id}/start/`);
    return tripSchema.parse(response);
  },

  /**
   * End a trip
   */
  async end(id: number): Promise<Trip> {
    const response = await apiClient.post<Trip>(`/api/trips/${id}/end/`);
    return tripSchema.parse(response);
  },

  /**
   * Delete trip
   */
  async delete(id: number): Promise<void> {
    await apiClient.delete(`/api/trips/${id}/`);
  },

  // ==========================================================================
  // BOARDINGS
  // ==========================================================================

  /**
   * Get all boardings
   */
  async listBoardings(params?: {
    trip_id?: number;
    employee_id?: number;
  }): Promise<EmployeeBoarding[]> {
    const response = await apiClient.get<any>('/api/boardings/', { params });
    // Handle paginated, non-paginated, or other response formats
    let results: EmployeeBoarding[];
    if (Array.isArray(response)) {
      results = response;
    } else if (response?.results) {
      results = response.results;
    } else {
      results = [];
    }
    return z.array(employeeBoardingSchema).parse(results);
  },

  /**
   * NFC check-in
   */
  async checkIn(data: CheckInData): Promise<CheckInResponse> {
    const validatedData = checkInDataSchema.parse(data);
    const response = await apiClient.post<CheckInResponse>(
      '/api/checkin/',
      validatedData
    );
    return checkInResponseSchema.parse(response);
  },

  // ==========================================================================
  // LIVE TRACKING
  // ==========================================================================

  /**
   * Get active trips for live tracking
   */
  async getLiveTracking(): Promise<LiveTracking[]> {
    const response = await apiClient.get<any>('/api/live-tracking/');
    // Handle paginated, non-paginated, or other response formats
    let results: LiveTracking[];
    if (Array.isArray(response)) {
      results = response;
    } else if (response?.active_trips) {
      // Backend returns { active_trips: [...], total_active: n }
      results = response.active_trips;
    } else if (response?.results) {
      results = response.results;
    } else {
      results = [];
    }
    return z.array(liveTrackingSchema).parse(results);
  },

  /**
   * Get live tracking for specific trip
   */
  async getLiveTrackingById(id: number): Promise<LiveTracking> {
    const response = await apiClient.get<LiveTracking>(`/api/live-tracking/${id}/`);
    return liveTrackingSchema.parse(response);
  },

  // ==========================================================================
  // DASHBOARD
  // ==========================================================================

  /**
   * Get dashboard data (response varies by user role)
   */
  async getDashboard(): Promise<DashboardData> {
    // Don't validate here - response structure varies by user role
    return apiClient.get<DashboardData>('/api/dashboard/');
  },
};

export default tripService;
