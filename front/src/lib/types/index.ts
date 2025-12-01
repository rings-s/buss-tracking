import { z } from 'zod';
import {
  userRoleSchema,
  userMinimalSchema,
  userSchema,
  driverSchema,
  employeeSchema,
  loginCredentialsSchema,
  registerDataSchema,
  adminRegisterDataSchema,
  authTokensSchema,
  loginResponseSchema,
  profileUpdateSchema,
  employeeProfileUpdateSchema,
  nonEmployeeProfileUpdateSchema,
  profileUpdateResponseSchema,
  changePasswordSchema,
  changePasswordResponseSchema,
  routeSchema,
  routeCreateSchema,
  busSchema,
  busCreateSchema,
  busUpdateSchema,
  busLocationSchema,
  gpsUpdateSchema,
  employeeBoardingSchema,
  checkInDataSchema,
  checkInResponseSchema,
  tripSchema,
  tripCreateSchema,
  tripDetailSchema,
  dashboardBusSchema,
  dashboardDataSchema,
  adminDashboardSchema,
  driverDashboardSchema,
  employeeDashboardSchema,
  liveTrackingSchema,
  busAttendanceSchema,
  apiErrorSchema,
  paginatedResponseSchema,
  absenceReportSchema,
} from '$lib/schemas';

// =============================================================================
// USER TYPES
// =============================================================================

export type UserRole = z.infer<typeof userRoleSchema>;
export type UserMinimal = z.infer<typeof userMinimalSchema>;
export type User = z.infer<typeof userSchema>;
export type Driver = z.infer<typeof driverSchema>;
export type Employee = z.infer<typeof employeeSchema>;

// =============================================================================
// AUTH TYPES
// =============================================================================

export type LoginCredentials = z.infer<typeof loginCredentialsSchema>;
export type RegisterData = z.infer<typeof registerDataSchema>;
export type AdminRegisterData = z.infer<typeof adminRegisterDataSchema>;
export type AuthTokens = z.infer<typeof authTokensSchema>;
export type LoginResponse = z.infer<typeof loginResponseSchema>;
export type ProfileUpdateData = z.infer<typeof profileUpdateSchema>;
export type EmployeeProfileUpdateData = z.infer<typeof employeeProfileUpdateSchema>;
export type NonEmployeeProfileUpdateData = z.infer<typeof nonEmployeeProfileUpdateSchema>;
export type ProfileUpdateResponse = z.infer<typeof profileUpdateResponseSchema>;
export type ChangePasswordData = z.infer<typeof changePasswordSchema>;
export type ChangePasswordResponse = z.infer<typeof changePasswordResponseSchema>;

// =============================================================================
// ROUTE TYPES
// =============================================================================

export type Route = z.infer<typeof routeSchema>;
export type RouteCreateData = z.infer<typeof routeCreateSchema>;

// =============================================================================
// BUS TYPES
// =============================================================================

export type Bus = z.infer<typeof busSchema>;
export type BusCreateData = z.infer<typeof busCreateSchema>;
export type BusUpdateData = z.infer<typeof busUpdateSchema>;

// =============================================================================
// BUS LOCATION TYPES
// =============================================================================

export type BusLocation = z.infer<typeof busLocationSchema>;
export type GPSUpdateData = z.infer<typeof gpsUpdateSchema>;

// =============================================================================
// EMPLOYEE BOARDING TYPES
// =============================================================================

export type EmployeeBoarding = z.infer<typeof employeeBoardingSchema>;
export type CheckInData = z.infer<typeof checkInDataSchema>;
export type CheckInResponse = z.infer<typeof checkInResponseSchema>;

// =============================================================================
// TRIP TYPES
// =============================================================================

export type Trip = z.infer<typeof tripSchema>;
export type TripCreateData = z.infer<typeof tripCreateSchema>;
export type TripDetail = z.infer<typeof tripDetailSchema>;

// =============================================================================
// DASHBOARD TYPES
// =============================================================================

export type DashboardBus = z.infer<typeof dashboardBusSchema>;
export type DashboardData = z.infer<typeof dashboardDataSchema>;
export type AdminDashboard = z.infer<typeof adminDashboardSchema>;
export type DriverDashboard = z.infer<typeof driverDashboardSchema>;
export type EmployeeDashboard = z.infer<typeof employeeDashboardSchema>;

// =============================================================================
// LIVE TRACKING TYPES
// =============================================================================

export type LiveTracking = z.infer<typeof liveTrackingSchema>;

// =============================================================================
// BUS ATTENDANCE TYPES
// =============================================================================

export type BusAttendance = z.infer<typeof busAttendanceSchema>;

// =============================================================================
// API RESPONSE TYPES
// =============================================================================

export type ApiError = z.infer<typeof apiErrorSchema>;
export type PaginatedResponse<T> = {
  count: number;
  next: string | null;
  previous: string | null;
  results: T[];
};

// =============================================================================
// ABSENCE REPORT TYPES
// =============================================================================

export type AbsenceReport = z.infer<typeof absenceReportSchema>;

// =============================================================================
// LEGACY COMPATIBILITY TYPES (for gradual migration)
// =============================================================================

// Active trip type for live tracking page
export interface ActiveTrip {
  id: number;
  bus: Bus;
  driver: Driver;
  route: Route | null;
  start_time: string;
  latest_location: BusLocation | null;
}
