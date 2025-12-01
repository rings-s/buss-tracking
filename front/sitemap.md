# Frontend Sitemap - Bus Tracking System

## Overview
- **Leaflet** for real-time map visualization
- **NFC Cards** for employee attendance (no phone required)
- Admin monitors drivers, trips, and attendance reports

---


## Public Routes
- `/` - Landing page
- `/auth/login` - User login
- `/auth/register` - Employee self-registration
- `/auth/google/callback` - Google OAuth callback

---

## Admin Routes

### Dashboard & Monitoring
- `/dashboard` - Overview with stats (buses, trips, attendance)
- `/live-tracking` - **Leaflet map** showing all active drivers and their routes in real-time


### Fleet Management
- `/buses` - Bus fleet CRUD
- `/routes` - Route management CRUD
- `/drivers` - Driver management

### Trip Management
- `/trips` - All trips (active/completed)
- `/trips/:id` - Trip details with route on map

### Attendance & Reports
- `/attendance` - Employee attendance records
- `/attendance/daily` - Daily attendance report
- `/attendance/monthly` - Monthly attendance report
- `/absence-reports` - Employee absence reports by day/month

---

## Driver Routes

### Trip Operations
- `/driver` - Driver dashboard (my trips)
- `/driver/start-trip` - Start a new trip (select bus, route)
- `/driver/active-trip` - Current active trip with GPS tracking

### NFC Check-in (Tablet Interface)
- `/checkin` - NFC scanner interface for employee check-in
  - Scans NFC card → Records boarding → Shows confirmation

---

## Employee Routes
- `/my-boardings` - Personal boarding history
- `/my-attendance` - Attendance summary (days present/absent)

*Note: Employees use NFC cards for attendance - no phone needed during trips*

---

## Components Structure

### Layout (`lib/components/layout/`)
- `Navbar.svelte`
- `Footer.svelte`

### Auth (`lib/components/auth/`)
- `Login.svelte`
- `Register.svelte`
- `GoogleLogin.svelte`
- `OAuthCallback.svelte`
- `AuthGuard.svelte`

### Dashboard (`lib/components/dashboard/`)
- `AdminDashboard.svelte` - Stats overview
- `DriverDashboard.svelte` - Driver's trips
- `StatsCards.svelte` - Stat display cards

### Map & Tracking (`lib/components/tracking/`)
- `LiveMap.svelte` - Leaflet map with active drivers
- `DriverMarker.svelte` - Driver position marker
- `RoutePolyline.svelte` - Route visualization
- `GPSUpdater.svelte` - Send GPS position (driver)

### Bus Management (`lib/components/buses/`)
- `BusList.svelte`
- `BusForm.svelte`

### Route Management (`lib/components/routes/`)
- `RouteList.svelte`
- `RouteForm.svelte`

### Trip Management (`lib/components/trips/`)
- `TripList.svelte`
- `TripForm.svelte`
- `TripDetail.svelte`
- `ActiveTrip.svelte`

### NFC Check-in (`lib/components/checkin/`)
- `NFCScanner.svelte` - Scan interface
- `CheckinConfirmation.svelte` - Success/error display
- `RecentCheckins.svelte` - Recent check-ins list

### Attendance & Reports (`lib/components/attendance/`)
- `AttendanceTable.svelte` - Attendance records
- `DailyReport.svelte` - Daily attendance
- `MonthlyReport.svelte` - Monthly summary
- `AbsenceReport.svelte` - Absence tracking
- `AttendanceCalendar.svelte` - Calendar view

### Boarding (`lib/components/boardings/`)
- `BoardingList.svelte`
- `BoardingDetail.svelte`

### Shared (`lib/components/shared/`)
- `LoadingSpinner.svelte`
- `ErrorMessage.svelte`
- `Pagination.svelte`
- `DatePicker.svelte`
- `DataTable.svelte`

---

## Data Flow

### NFC Check-in Flow
```
Employee boards bus → Driver scans NFC card →
POST /api/checkin/ → EmployeeBoarding created →
Confirmation shown
```

### GPS Tracking Flow
```
Driver starts trip → GPS updates every 5s →
POST /api/gps-update/ → BusLocation saved →
Admin sees live position on Leaflet map
```

### Attendance Reporting
```
Admin selects date range →
GET /api/attendance/report/ →
Shows present/absent employees with stats
```
