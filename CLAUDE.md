# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Bus tracking system with NFC-based employee attendance. Django REST API backend with JWT authentication, designed for a SvelteKit frontend.

**User Roles:**
- Admin: Full system management, create drivers/admins
- Driver: Start/end trips, send GPS location, scan NFC
- Employee: View own boarding history only

## Development Commands

### Backend (Django)

```bash
cd back
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

# Reset database (dev only)
rm db.sqlite3 && python manage.py migrate && python manage.py createsuperuser
```

### Frontend (SvelteKit)

```bash
cd front
npm install
npm run dev              # Start dev server (localhost:5173)
npm run check            # Type checking
npm run check -- --watch # Type checking in watch mode
npm run lint             # Lint code
npm run format           # Format code
npm run build            # Production build
npm run test:e2e         # E2E tests



You are able to use the Svelte MCP server, where you have access to comprehensive Svelte 5 and SvelteKit documentation. Here's how to use the available tools effectively:

## Available MCP Tools:

### 1. list-sections

Use this FIRST to discover all available documentation sections. Returns a structured list with titles, use_cases, and paths.
When asked about Svelte or SvelteKit topics, ALWAYS use this tool at the start of the chat to find relevant sections.

### 2. get-documentation

Retrieves full documentation content for specific sections. Accepts single or multiple sections.
After calling the list-sections tool, you MUST analyze the returned documentation sections (especially the use_cases field) and then use the get-documentation tool to fetch ALL documentation sections that are relevant for the user's task.

### 3. svelte-autofixer

Analyzes Svelte code and returns issues and suggestions.
You MUST use this tool whenever writing Svelte code before sending it to the user. Keep calling it until no issues or suggestions are returned.

### 4. playground-link

Generates a Svelte Playground link with the provided code.
After completing the code, ask the user if they want a playground link. Only call this tool after user confirmation and NEVER if code was written to files in their project.
```


Always use context7 when I need code generation, setup or configuration steps, or
library/API documentation. This means you should automatically use the Context7 MCP
tools to resolve library id and get library docs without me having to explicitly ask.



### Run Both (separate terminals)

```bash
# Terminal 1 - Backend
cd back && source ../venv/bin/activate && python manage.py runserver

# Terminal 2 - Frontend
cd front && npm run dev
```

## Environment Setup

Copy `.env.example` to `.env` and configure:
- `SECRET_KEY` - Django secret key
- `DEBUG` - Set to False in production
- `GOOGLE_CLIENT_ID/SECRET` - For Google OAuth

Frontend `.env.local`:
```
VITE_API_BASE_URL=http://localhost:8000
```

## Architecture

### Backend Django Apps

- **accounts**: Custom User model with roles, JWT auth, permission classes
- **base**: Business logic - Bus, Route, Trip, BusLocation, EmployeeBoarding models
- **back**: Project settings, URL routing, CORS configuration

### Permission System (accounts/permissions.py)

Role-based permission classes control access:
- `IsAdmin` - Admin only
- `IsDriver` - Driver only
- `IsEmployee` - Employee only
- `IsAdminOrDriver` - Admin or driver
- `IsAdminOrReadOnly` - Admin writes, authenticated reads
- `IsOwnerOrAdmin` - Object owner or admin
- `CanStartTrip` - Driver can start trips
- `CanManageBus` - Admin manages all, driver views assigned

### Critical Backend Patterns

**ViewSets with role-based querysets (used throughout):**
```python
def get_queryset(self):
    queryset = super().get_queryset()
    user = self.request.user

    if user.role == 'admin':
        return queryset  # See everything
    elif user.role == 'driver':
        return queryset.filter(driver=user)  # Own trips only
    elif user.role == 'employee':
        return queryset.filter(employeeboarding__employee=user).distinct()

    return queryset.none()
```

**Dynamic serializer selection:**
```python
def get_serializer_class(self):
    if self.action == 'retrieve':
        return TripDetailSerializer  # Nested data with locations
    return TripSerializer  # List view
```

**Action-based permissions:**
```python
def get_permissions(self):
    if self.action in ['create', 'start']:
        return [IsAdminOrDriver()]
    if self.action in ['update', 'partial_update', 'destroy']:
        return [IsAdmin()]
    return [IsAuthenticated()]
```

**JWT tokens with custom claims:**
```python
refresh['role'] = user.role
refresh['email'] = user.email
```

### Custom User Model

**User Roles:** `admin`, `driver`, `employee`

**Key fields:**
- `email` - Primary authentication (USERNAME_FIELD)
- `full_name` - Display name
- `role` - User role (default: 'employee')
- `nfc_uid` - NFC card identifier (nullable, unique)
- `phone_number` - Contact info

**Registration endpoints:**
- `/api/auth/register/` - Self-registration (employee role only)
- `/api/auth/admin/register/` - Admin-only (can create any role)

### API Structure

See `back/API_ENDPOINTS.md` for complete endpoint documentation.

**Key endpoints:**
- `/api/auth/` - Authentication (login, register, profile, Google OAuth)
- `/api/buses/` - Bus CRUD
- `/api/routes/` - Route CRUD
- `/api/trips/` - Trip management with start/end actions
- `/api/boardings/` - Employee boarding records
- `/api/dashboard/` - Role-based dashboard data
- `/api/live-tracking/` - Active trip tracking with GPS breadcrumb trails
- `/api/checkin/` - NFC check-in
- `/api/gps-update/` - GPS location updates (every 5s from driver)

### Data Flow Patterns

**NFC Check-in:**
```
NFC Card → Tablet → POST /api/checkin/ → EmployeeBoarding record created
```

**GPS Tracking:**
```
Driver starts trip → GPS updates every 5s → POST /api/gps-update/ →
BusLocation records → Admin views on Leaflet map with breadcrumb trail
```

**Registration:**
- Self-register: `/api/auth/register/` → Employee role only
- Admin register: `/api/auth/admin/register/` → Can create any role

## Frontend (SvelteKit)

### Tech Stack

- **SvelteKit 2.x** with Svelte 5 runes (`$state`, `$derived`, `$derived.by()`, `$effect`, `$props`)
- **TypeScript** (strict mode)
- **Tailwind CSS 4** with forms/typography plugins
- **Vite** build tool
- **Zod** for runtime validation
- **Leaflet.js** for interactive maps

### Architecture

```
front/src/lib/
├── schemas/index.ts           # Zod schemas (source of truth for types)
├── types/index.ts             # TypeScript types inferred from schemas
├── services/
│   ├── api-client.ts          # Base fetch wrapper with JWT auto-refresh
│   ├── auth.ts                # Auth service with Zod validation
│   ├── bus.ts                 # Bus & route services
│   ├── trip.ts                # Trip, boarding, dashboard services
│   └── nfc.ts                 # NFC card operations
├── stores/
│   └── auth.svelte.ts         # Auth state with Svelte 5 runes
└── components/                # UI components organized by domain
```

**Routes** (see `front/sitemap.md` for complete structure):
- `/` - Landing/home
- `/dashboard` - Role-based dashboard
- `/buses`, `/routes`, `/trips` - Resource management
- `/driver/start-trip`, `/driver/active-trip` - Driver workflows
- `/attendance`, `/my-attendance` - Attendance views
- `/live-tracking` - Real-time GPS tracking with Leaflet map
- `/checkin` - NFC scanner interface
- `/absence-reports` - Absence reporting

### Critical Frontend Patterns

**Zod Schema → Type Flow (NEVER manually define types that have schemas):**
```typescript
// 1. Define Zod schemas in lib/schemas/index.ts (source of truth)
export const busSchema = z.object({ id: z.number(), ... });
export const busCreateSchema = z.object({ name: z.string(), ... });

// 2. Infer TypeScript types in lib/types/index.ts
export type Bus = z.infer<typeof busSchema>;
export type BusCreateData = z.infer<typeof busCreateSchema>;

// 3. Services validate input/output in lib/services/
async create(data: BusCreateData): Promise<Bus> {
  const validatedData = busCreateSchema.parse(data);  // Validate input
  const response = await apiClient.post('/api/buses/', validatedData);
  return busSchema.parse(response);  // Validate output
}
```

**Auth Store (Svelte 5 Runes):**
```typescript
import { auth } from '$lib/stores/auth.svelte';

// Reactive getters
auth.user          // Current user or null
auth.isAuthenticated
auth.isAdmin / auth.isDriver / auth.isEmployee

// Actions
await auth.login(credentials)
await auth.logout()
auth.getRedirectPath(user)  // Role-based redirect
```

**Auth Guard Pattern:**
```typescript
// In +page.ts or +layout.ts
import { auth } from '$lib/stores/auth.svelte';

if (!auth.isAuthenticated) {
  redirect(302, '/auth/login');
}

if (!auth.isAdmin) {
  redirect(302, auth.getRedirectPath());
}
```

**Svelte 5 Runes Patterns:**
```typescript
// Simple state
let count = $state(0);

// Derived state (simple - no function wrapper needed)
const doubled = $derived(count * 2);

// Derived state (complex logic - use $derived.by)
const filteredItems = $derived.by(() => {
  return items.filter(item => item.active).sort((a, b) => a.name.localeCompare(b.name));
});

// Effects for side effects
$effect(() => {
  console.log('Count changed:', count);
});

// Props in components
let { prop1, prop2 = 'default' } = $props();
```

**API Client Error Handling:**
```typescript
import { apiClient, ApiClientError } from '$lib/services/api-client';

try {
  const data = await apiClient.get('/endpoint');
} catch (error) {
  if (error instanceof ApiClientError) {
    console.error(`API Error ${error.status}:`, error.data);
    // error.data contains structured error response
  }
}
```

### PWA Configuration

Progressive Web App with offline support:
- **Service Worker**: Caches map tiles (OSM), API responses
- **Cache Strategy**:
  - Map tiles: CacheFirst (30 days)
  - API calls: NetworkFirst (5 minutes)
- **Icons**: PWA icons in `front/static/` (192x192, 512x512, maskable variants)

### Map Integration (Leaflet.js)

**GPS Breadcrumb Trail Pattern:**
```typescript
// Direct GPS coordinate rendering (no OSRM road-snapping for live tracking)
const mapPaths = $derived(
  trips
    .filter(trip => trip.locations && trip.locations.length >= 2)
    .map(trip => {
      const sortedLocations = trip.locations!
        .slice()
        .sort((a, b) => new Date(a.timestamp).getTime() - new Date(b.timestamp).getTime());

      return {
        coordinates: sortedLocations.map(loc => [loc.latitude, loc.longitude]),
        color: selectedTrip?.id === trip.id ? '#10b981' : '#3b82f6',
        weight: selectedTrip?.id === trip.id ? 5 : 3
      };
    })
);
```

**Start/End Markers:**
```typescript
const mapMarkers = $derived.by(() => {
  const markers = [];

  trips.forEach(trip => {
    // Vehicle marker (current location)
    if (trip.current_location) {
      markers.push({ /* vehicle marker */ });
    }

    // Start/end markers
    if (trip.locations && trip.locations.length > 0) {
      const sorted = trip.locations.slice().sort(/* by timestamp */);
      markers.push({ /* start marker */ });
      markers.push({ /* end marker */ });
    }
  });

  return markers;
});
```

### NFC Integration

Web NFC API for employee check-in (requires HTTPS):
```typescript
import { nfcService } from '$lib/services/nfc';

// Scan NFC card
const uid = await nfcService.scan();

// Check in employee
await tripService.checkIn({
  nfc_uid: uid,
  trip_id: activeTripId,
  latitude: gpsCoords.lat,
  longitude: gpsCoords.lng
});
```

## Important Development Notes

**Type Safety:**
- All types flow from Zod schemas → TypeScript types
- Never manually define types that have Zod schemas
- Services validate both request and response data

**Database Migrations:**
- Migration files are gitignored except `__init__.py`
- Always run `makemigrations` and `migrate` after model changes
- Use `python manage.py migrate --fake-initial` for conflicts

**CORS:**
- Backend allows `localhost:5173` in development
- Update `CORS_ALLOWED_ORIGINS` for production
- Credentials allowed for cookie-based auth

**Accessibility:**
- Add `aria-label` to icon-only buttons
- Associate `<label>` with form controls using `for` and `id` attributes
- Modal dialogs need `role="dialog"`, `aria-modal="true"`, `tabindex="-1"`
- Keyboard handlers for Escape key on modals

**Component Organization:**
- Group by feature domain, not by type
- Shared components in `lib/components/shared/`
- Domain components in respective folders

**Configuration:**
- SQLite (dev), PostgreSQL (production - uncomment psycopg2-binary)
- REST Framework: JWT authentication with SimpleJWT
- Custom permission classes in `accounts/permissions.py`
