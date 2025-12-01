# Bus Tracking API Endpoints

Base URL: `http://localhost:8000`

---

## Authentication

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/auth/login/` | Login with email/password, returns JWT |
| POST | `/api/auth/logout/` | Logout (invalidate token) |
| POST | `/api/auth/register/` | Self-register (employee role only) |
| POST | `/api/auth/admin/register/` | Admin register user with any role |
| POST | `/api/auth/token/refresh/` | Refresh JWT token |
| GET | `/api/auth/verify/` | Verify token validity |
| GET | `/api/auth/user/` | Get current authenticated user |
| PUT/PATCH | `/api/auth/user/` | Update current user profile |
| POST | `/api/auth/password/change/` | Change password |
| POST | `/api/auth/google/` | Google OAuth login |
| GET | `/api/auth/users/` | Get users by role (?role=driver) |
| POST | `/api/auth/assign-nfc/` | Assign NFC UID to user |

---

## Buses

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/buses/` | List all buses |
| POST | `/api/buses/` | Create new bus |
| GET | `/api/buses/{id}/` | Get bus details |
| PUT | `/api/buses/{id}/` | Update bus |
| PATCH | `/api/buses/{id}/` | Partial update bus |
| DELETE | `/api/buses/{id}/` | Delete bus |
| GET | `/api/buses/{id}/locations/` | Get bus location history |

**Query Parameters:**
- `?active=true` - Filter by active status

---

## Routes

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/routes/` | List all routes |
| POST | `/api/routes/` | Create new route |
| GET | `/api/routes/{id}/` | Get route details |
| PUT | `/api/routes/{id}/` | Update route |
| PATCH | `/api/routes/{id}/` | Partial update route |
| DELETE | `/api/routes/{id}/` | Delete route |

---

## Trips

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/trips/` | List all trips |
| POST | `/api/trips/` | Create new trip |
| GET | `/api/trips/{id}/` | Get trip details (with locations) |
| PUT | `/api/trips/{id}/` | Update trip |
| PATCH | `/api/trips/{id}/` | Partial update trip |
| DELETE | `/api/trips/{id}/` | Delete trip |
| POST | `/api/trips/start/` | Start a new trip |
| POST | `/api/trips/{id}/end/` | End an active trip |
| GET | `/api/trips/active/` | Get all active trips |

**Query Parameters:**
- `?is_active=true` - Filter by active status
- `?driver_id=1` - Filter by driver

---

## Employee Boardings

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/boardings/` | List all boardings |
| POST | `/api/boardings/` | Create boarding record |
| GET | `/api/boardings/{id}/` | Get boarding details |
| PUT | `/api/boardings/{id}/` | Update boarding |
| DELETE | `/api/boardings/{id}/` | Delete boarding |

**Query Parameters:**
- `?trip_id=1` - Filter by trip

---

## Page Endpoints

### Dashboard (Page 1)

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/dashboard/` | Dashboard data with buses and stats |

**Response:**
```json
{
  "buses": [...],
  "summary": {
    "total_buses": 10,
    "buses_on_route": 3,
    "buses_idle": 7,
    "active_trips": 3,
    "today_boardings": 45,
    "today_trips": 5
  }
}
```

### Live Tracking (Page 2)

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/live-tracking/` | All active trips with real-time data |
| GET | `/api/live-tracking/{trip_id}/` | Single trip tracking detail |

**Response:**
```json
{
  "active_trips": [...],
  "total_active": 3
}
```

---

## Core API Endpoints

### NFC Check-in

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/checkin/` | Employee NFC check-in |

**Request:**
```json
{
  "nfc_uid": "ABC123XYZ",
  "trip_id": 1
}
```

**Response:**
```json
{
  "success": true,
  "message": "John Doe checked in successfully",
  "boarding": {...}
}
```

### GPS Update

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/gps-update/` | Update bus GPS location |

**Request:**
```json
{
  "bus_id": 1,
  "latitude": 40.7128,
  "longitude": -74.0060
}
```

**Response:**
```json
{
  "success": true,
  "location": {
    "id": 123,
    "bus": 1,
    "latitude": 40.7128,
    "longitude": -74.0060,
    "timestamp": "2025-01-15T10:30:00Z"
  }
}
```

---

## Legacy Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/location/update/` | Update bus location (driver only) |
| POST | `/api/trip/start/` | Start trip (driver only) |
| POST | `/api/trip/end/` | End trip (driver only) |
| POST | `/api/nfc/scan/` | NFC scan |
| GET | `/api/admin/dashboard/` | Admin dashboard (admin only) |
| GET | `/api/admin/absence-report/` | Employee absence report (admin only) |

### Absence Report Query Parameters:
- `?type=day&date=2025-01-15` - Daily report
- `?type=month&month=2025-01` - Monthly report
- `?type=range&start_date=2025-01-01&end_date=2025-01-31` - Date range
- `?employee_id=1` - Filter by specific employee

---

## Admin Panel

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/admin/` | Django admin interface |

---

## Authentication Notes

All endpoints (except `/api/auth/login/` and `/api/auth/register/`) require authentication.

**Headers:**
```
Authorization: Bearer <jwt_token>
```

Or use HTTP-only cookies (automatically set after login).

---

## Error Responses

**400 Bad Request:**
```json
{
  "field_name": ["Error message"]
}
```

**401 Unauthorized:**
```json
{
  "detail": "Authentication credentials were not provided."
}
```

**403 Forbidden:**
```json
{
  "detail": "You do not have permission to perform this action."
}
```

**404 Not Found:**
```json
{
  "error": "Resource not found"
}
```
