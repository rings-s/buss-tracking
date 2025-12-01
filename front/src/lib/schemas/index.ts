import { z } from 'zod';

// =============================================================================
// USER SCHEMAS
// =============================================================================

export const userRoleSchema = z.enum(['admin', 'driver', 'employee']);

export const userMinimalSchema = z.object({
  id: z.number(),
  email: z.string().email(),
  full_name: z.string(),
  role: userRoleSchema,
});

export const userSchema = z.object({
  id: z.number().int().positive(),
  email: z.string().email('Invalid email format'),
  full_name: z.string().min(1, 'Full name is required').trim(),
  phone_number: z.string().trim(),
  role: userRoleSchema,
  is_active: z.boolean(),
  nfc_uid: z.string().nullish(),
  created_at: z.string().datetime(),
});

export const driverSchema = z.object({
  id: z.number().int().positive(),
  email: z.string().email('Invalid email format'),
  full_name: z.string().min(1).trim(),
  phone_number: z.string().trim(),
  is_active: z.boolean(),
});

export const employeeSchema = z.object({
  id: z.number().int().positive(),
  email: z.string().email('Invalid email format'),
  full_name: z.string().min(1).trim(),
  phone_number: z.string().trim(),
  nfc_uid: z.string().nullish(),
  is_active: z.boolean(),
});

// =============================================================================
// AUTH SCHEMAS
// =============================================================================

export const loginCredentialsSchema = z.object({
  email: z.string().email('Invalid email address'),
  password: z.string().min(1, 'Password is required'),
});

const baseRegisterSchema = z.object({
  email: z.string().email('Invalid email address'),
  password: z.string().min(8, 'Password must be at least 8 characters'),
  password_confirm: z.string(),
  full_name: z.string().min(1, 'Full name is required'),
  phone_number: z.string().optional(),
});

export const registerDataSchema = baseRegisterSchema.refine((data) => data.password === data.password_confirm, {
  message: "Passwords don't match",
  path: ['password_confirm'],
});

export const adminRegisterDataSchema = baseRegisterSchema.extend({
  role: userRoleSchema,
  nfc_uid: z.string().optional(),
}).refine((data) => data.password === data.password_confirm, {
  message: "Passwords don't match",
  path: ['password_confirm'],
});

export const authTokensSchema = z.object({
  access: z.string(),
  refresh: z.string(),
});

export const loginResponseSchema = z.object({
  access: z.string(),
  refresh: z.string(),
  user: userSchema,
});

// =============================================================================
// PROFILE SCHEMAS
// =============================================================================

// Legacy profile update schema - deprecated
export const profileUpdateSchema = z.object({
  full_name: z.string().min(1, 'Full name is required').trim(),
  phone_number: z.string().trim().optional(),
  nfc_uid: z.string().nullish(),
});

// Employee profile update schema (with NFC card)
export const employeeProfileUpdateSchema = z.object({
  full_name: z.string().min(1, 'Full name is required').trim(),
  phone_number: z.string().trim().optional(),
  nfc_uid: z.string().trim().optional().nullable(),
});

// Non-employee profile update schema (without NFC card)
export const nonEmployeeProfileUpdateSchema = z.object({
  full_name: z.string().min(1, 'Full name is required').trim(),
  phone_number: z.string().trim().optional(),
});

export const profileUpdateResponseSchema = z.object({
  user: userSchema,
  message: z.string(),
});

export const changePasswordSchema = z.object({
  old_password: z.string().min(1, 'Current password is required'),
  new_password: z.string().min(8, 'New password must be at least 8 characters'),
  new_password_confirm: z.string(),
}).refine((data) => data.new_password === data.new_password_confirm, {
  message: "Passwords don't match",
  path: ['new_password_confirm'],
});

export const changePasswordResponseSchema = z.object({
  message: z.string(),
});

// =============================================================================
// ROUTE SCHEMAS
// =============================================================================

export const routeSchema = z.object({
  id: z.number().int().positive(),
  name: z.string().min(1).trim(),
  start_point: z.string().min(1).trim(),
  end_point: z.string().min(1).trim(),
});

export const routeCreateSchema = z.object({
  name: z.string().min(1, 'Route name is required').trim(),
  start_point: z.string().min(1, 'Start point is required').trim(),
  end_point: z.string().min(1, 'End point is required').trim(),
});

// =============================================================================
// BUS SCHEMAS
// =============================================================================

export const busSchema = z.object({
  id: z.number().int().positive(),
  name: z.string().min(1).trim(),
  plate_number: z.string().min(1).trim().toUpperCase(),
  capacity: z.number().int().positive(),
  driver: driverSchema.nullable(),
  active: z.boolean(),
});

export const busCreateSchema = z.object({
  name: z.string().min(1, 'Bus name is required').trim(),
  plate_number: z.string().min(1, 'Plate number is required').trim().toUpperCase(),
  capacity: z.number().int().positive('Capacity must be at least 1'),
  driver: z.number().int().positive().nullish(),
  active: z.boolean().default(true),
});

export const busUpdateSchema = busCreateSchema.partial();

// =============================================================================
// BUS LOCATION SCHEMAS
// =============================================================================

export const busLocationSchema = z.object({
  id: z.number().int().positive(),
  bus: z.number().int().positive(),
  latitude: z.number().min(-90, 'Invalid latitude').max(90, 'Invalid latitude'),
  longitude: z.number().min(-180, 'Invalid longitude').max(180, 'Invalid longitude'),
  timestamp: z.string().datetime(),
});

export const gpsUpdateSchema = z.object({
  bus_id: z.number().int().positive(),
  latitude: z.number().min(-90, 'Invalid latitude').max(90, 'Invalid latitude'),
  longitude: z.number().min(-180, 'Invalid longitude').max(180, 'Invalid longitude'),
});

// =============================================================================
// EMPLOYEE BOARDING SCHEMAS
// =============================================================================

export const employeeBoardingSchema = z.object({
  id: z.number().int().positive(),
  trip: z.number().int().positive(),
  employee: employeeSchema,
  boarded_at: z.string().datetime(),
  // Location from tablet GPS at check-in
  latitude: z.number().min(-90).max(90).nullish(),
  longitude: z.number().min(-180).max(180).nullish(),
});

export const checkInDataSchema = z.object({
  nfc_uid: z.string().min(1, 'NFC UID is required').trim(),
  trip_id: z.number().int().positive(),
  // Tablet GPS location (optional but recommended)
  latitude: z.number().min(-90).max(90).nullish(),
  longitude: z.number().min(-180).max(180).nullish(),
});

export const checkInResponseSchema = z.object({
  success: z.boolean(),
  message: z.string(),
  boarding: employeeBoardingSchema,
});

// =============================================================================
// TRIP SCHEMAS
// =============================================================================

export const tripSchema = z.object({
  id: z.number().int().positive(),
  bus: busSchema,
  driver: driverSchema,
  route: routeSchema.nullable(),
  start_time: z.string().datetime(),
  end_time: z.string().datetime().nullable(),
  is_active: z.boolean(),
  boardings: z.array(employeeBoardingSchema).optional(),
  boarding_count: z.number().int().nonnegative().optional(),
  duration: z.number().nonnegative().nullish(),
});

export const tripCreateSchema = z.object({
  bus_id: z.number().int().positive(),
  driver_id: z.number().int().positive(),
  route_id: z.number().int().positive().nullish(),
});

export const tripDetailSchema = tripSchema.extend({
  locations: z.array(busLocationSchema).optional(),
  latest_location: busLocationSchema.nullish(),
});

// =============================================================================
// DASHBOARD SCHEMAS
// =============================================================================

export const dashboardBusSchema = busSchema.extend({
  active_trip: z.object({
    id: z.number().int().positive(),
    route: z.string().nullable(),
    start_time: z.string().datetime(),
    boarding_count: z.number().int().nonnegative(),
  }).nullable(),
  latest_location: z.object({
    latitude: z.number().min(-90).max(90),
    longitude: z.number().min(-180).max(180),
    timestamp: z.string().datetime(),
  }).nullable(),
});

// Admin dashboard response
export const adminDashboardSchema = z.object({
  buses: z.array(dashboardBusSchema),
  summary: z.object({
    total_buses: z.number().int().nonnegative(),
    buses_on_route: z.number().int().nonnegative(),
    buses_idle: z.number().int().nonnegative(),
    active_trips: z.number().int().nonnegative(),
    today_boardings: z.number().int().nonnegative(),
    today_trips: z.number().int().nonnegative(),
  }),
});

// Driver dashboard response
export const driverDashboardSchema = z.object({
  bus: dashboardBusSchema.nullable(),
  active_trip: tripSchema.nullable(),
  summary: z.object({
    today_trips: z.number().int().nonnegative(),
    today_boardings: z.number().int().nonnegative(),
    total_trips: z.number().int().nonnegative(),
  }),
});

// Employee dashboard response
export const employeeDashboardSchema = z.object({
  summary: z.object({
    today_boardings: z.number().int().nonnegative(),
    total_boardings: z.number().int().nonnegative(),
  }),
  recent_boardings: z.array(employeeBoardingSchema),
});

// Union type for all dashboard responses
export const dashboardDataSchema = z.union([
  adminDashboardSchema,
  driverDashboardSchema,
  employeeDashboardSchema,
]);

// =============================================================================
// LIVE TRACKING SCHEMAS
// =============================================================================

export const liveTrackingSchema = z.object({
  id: z.number().int().positive(),
  bus: busSchema,
  driver: driverSchema,
  route: routeSchema.nullable(),
  start_time: z.string().datetime(),
  is_active: z.boolean(),
  current_location: z.object({
    latitude: z.number().min(-90).max(90),
    longitude: z.number().min(-180).max(180),
    timestamp: z.string().datetime(),
    speed: z.number().nonnegative().optional(),
    heading: z.number().min(0).max(360).optional(),
  }).nullable(),
  locations: z.array(z.object({
    latitude: z.number().min(-90).max(90),
    longitude: z.number().min(-180).max(180),
    timestamp: z.string().datetime(),
  })).optional(),
  recent_boardings: z.array(employeeBoardingSchema),
  boarding_count: z.number().int().nonnegative(),
});

// =============================================================================
// BUS ATTENDANCE SCHEMAS
// =============================================================================

export const busAttendanceSchema = z.object({
  id: z.number().int().positive(),
  employee: employeeSchema,
  bus: busSchema,
  check_in_time: z.string().datetime(),
  bus_location_at_checkin: z.record(z.string(), z.unknown()),
});

// =============================================================================
// API RESPONSE SCHEMAS
// =============================================================================

export const apiErrorSchema = z.object({
  detail: z.string().optional(),
  message: z.string().optional(),
}).catchall(z.unknown());

export const paginatedResponseSchema = <T extends z.ZodTypeAny>(itemSchema: T) =>
  z.object({
    count: z.number(),
    next: z.string().nullable(),
    previous: z.string().nullable(),
    results: z.array(itemSchema),
  });

// =============================================================================
// ABSENCE REPORT SCHEMAS
// =============================================================================

export const absenceReportSchema = z.object({
  date: z.string().date(),
  absent_employees: z.array(userSchema),
  total_absent: z.number().int().nonnegative(),
});
