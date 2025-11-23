# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Bus tracking system with NFC-based employee attendance. Django REST API backend with JWT authentication, designed for a SvelteKit frontend.

**User Roles:**
- Admin: Full system management, create drivers/admins
- Driver: Start/end trips, send GPS location, scan NFC
- Employee: View own boarding history only

## Development Commands

```bash
# Navigate to Django project
cd back

# Activate virtual environment
source ../venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Run development server
python manage.py runserver

# Database migrations
python manage.py makemigrations
python manage.py migrate

# Create superuser
python manage.py createsuperuser

# Run tests
python manage.py test
python manage.py test accounts  # Single app
python manage.py test base.tests.TestClassName.test_method  # Single test
```

## Environment Setup

Copy `.env.example` to `.env` and configure:
- `SECRET_KEY` - Django secret key
- `DEBUG` - Set to False in production
- `GOOGLE_CLIENT_ID/SECRET` - For Google OAuth

## Architecture

### Apps

- **accounts**: Custom User model with roles, JWT auth, permissions
- **base**: Business logic - Bus, Route, Trip, BusLocation, EmployeeBoarding
- **back**: Project settings, URL routing

### Permission System (accounts/permissions.py)

Role-based permission classes control access:
- `IsAdmin` - Admin only
- `IsDriver` - Driver only
- `IsAdminOrDriver` - Admin or driver
- `IsAdminOrReadOnly` - Admin for writes, authenticated for reads

### Key Patterns

**ViewSets with role-based querysets:**
```python
def get_queryset(self):
    if user.role == 'driver':
        return queryset.filter(driver=user)
    elif user.role == 'employee':
        return queryset.filter(employeeboarding__employee=user)
```

**JWT tokens with custom claims:**
```python
refresh['role'] = user.role
refresh['email'] = user.email
```

### API Structure

- `/api/auth/` - Authentication (login, register, profile)
- `/api/buses/` - Bus CRUD
- `/api/routes/` - Route CRUD
- `/api/trips/` - Trip management with start/end actions
- `/api/boardings/` - Employee boarding records
- `/api/dashboard/` - Role-based dashboard data
- `/api/live-tracking/` - Active trip tracking
- `/api/checkin/` - NFC check-in
- `/api/gps-update/` - GPS location updates

See `back/API_ENDPOINTS.md` for complete endpoint documentation.

### Data Flow

**NFC Check-in:** `NFC Card → Android Tablet → POST /api/checkin/ → EmployeeBoarding record`

**GPS Tracking:** `Driver app → POST /api/gps-update/ (every 5s) → BusLocation record`

**Registration:**
- Self-register at `/api/auth/register/` → Employee role only
- Admin register at `/api/auth/admin/register/` → Can create any role

## Configuration Notes

- SQLite (dev), PostgreSQL (production)
- CORS: `localhost:5173` (SvelteKit)
- Google OAuth callback: `http://localhost:5173/auth/callback`

---

## Frontend (SvelteKit)

### Development Commands

```bash
cd front

# Install dependencies
npm install

# Start dev server (localhost:5173)
npm run dev

# Type checking
npm run check

# Build for production
npm run build

# E2E tests
npm run test:e2e
```

### Tech Stack

- **SvelteKit 2.x** with Svelte 5 runes (`$state`, `$derived`, `$props`)
- **TypeScript** (strict mode)
- **Tailwind CSS 4** with forms/typography plugins
- **Vite** build tool

### Recommended Architecture

```
front/src/
├── routes/                    # Pages (file-based routing)
│   ├── +layout.svelte         # Root layout with nav
│   ├── auth/
│   │   ├── login/+page.svelte
│   │   └── register/+page.svelte
│   ├── dashboard/+page.svelte
│   ├── (protected)/           # Route group with auth guard
│   │   └── +layout.server.ts  # Auth middleware
│   └── ...
├── lib/
│   ├── components/            # Reusable UI components
│   ├── services/              # API client modules
│   │   ├── api-client.ts      # Base fetch wrapper with JWT
│   │   ├── auth.ts
│   │   ├── bus.ts
│   │   └── trip.ts
│   ├── stores/                # Svelte stores
│   │   └── auth.ts            # User state, token management
│   └── types/                 # TypeScript interfaces
│       └── index.ts
```

### Auth Integration Pattern

```typescript
// JWT stored in HTTP-only cookies by backend
// Frontend tracks auth state, backend handles token security

// API client pattern
async function fetchWithAuth(url: string, options?: RequestInit) {
  const response = await fetch(`${API_BASE}${url}`, {
    ...options,
    credentials: 'include', // Send cookies
    headers: {
      'Content-Type': 'application/json',
      ...options?.headers
    }
  });

  if (response.status === 401) {
    // Attempt token refresh
    await refreshToken();
    return fetch(`${API_BASE}${url}`, { ...options, credentials: 'include' });
  }

  return response;
}
```

### TypeScript Types (match backend models)

```typescript
interface User {
  id: number;
  email: string;
  full_name: string;
  phone_number: string;
  role: 'admin' | 'driver' | 'employee';
  nfc_uid?: string;
}

interface Bus {
  id: number;
  name: string;
  plate_number: string;
  capacity: number;
  driver: User | null;
  active: boolean;
}

interface Trip {
  id: number;
  bus: Bus;
  driver: User;
  route: Route | null;
  start_time: string;
  end_time: string | null;
  is_active: boolean;
}

interface EmployeeBoarding {
  id: number;
  trip: Trip;
  employee: User;
  boarded_at: string;
}
```

### Key Pages to Implement

| Route | Purpose | Roles |
|-------|---------|-------|
| `/auth/login` | JWT login | All |
| `/auth/register` | Employee self-registration | Public |
| `/dashboard` | Role-based overview | All authenticated |
| `/buses` | Bus fleet management | Admin |
| `/routes` | Route CRUD | Admin |
| `/trips` | Trip management | Admin, Driver |
| `/live-tracking` | Real-time GPS map | Admin, Driver |
| `/checkin` | NFC tablet interface | Driver |
| `/boardings` | Boarding history | All (filtered by role) |

### Environment Variables

Create `front/.env.local`:
```
VITE_API_BASE_URL=http://localhost:8000
```

Access in code: `import.meta.env.VITE_API_BASE_URL`
