# SvelteKit + Django Data Loading Mentor Guide

Complete guide to data loading patterns with type-safe validation using Zod.

---

## Table of Contents
- [Overview](#overview)
- [Django Data Loading](#django-data-loading)
- [SvelteKit Data Loading](#sveltekit-data-loading)
- [Zod Validation Layer](#zod-validation-layer)
- [Complete Data Flow](#complete-data-flow)
- [Common Patterns](#common-patterns)
- [Best Practices](#best-practices)

---

## Overview

**Architecture**: Django REST API (backend) → API Client (fetch) → Zod Validation → SvelteKit (frontend)

**Key Concept**: Data flows from Django through 3 validation layers:
1. **Django Serializers** - Backend validation
2. **Zod Schemas** - Runtime type validation
3. **TypeScript Types** - Compile-time type checking

---

## Django Data Loading

### 1. Model → Serializer → ViewSet

**Django Flow**: Database → Model → Serializer → ViewSet → JSON Response

#### Example: Bus Data Loading

```python
# models.py - Database schema
class Bus(models.Model):
    name = models.CharField(max_length=100)
    plate_number = models.CharField(max_length=20)
    capacity = models.IntegerField()
    driver = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    active = models.BooleanField(default=True)

# serializers.py - Data transformation
class BusSerializer(serializers.ModelSerializer):
    # Read: Returns full driver object with nested fields
    driver = DriverSerializer(read_only=True)

    # Write: Accepts driver ID only
    driver_id = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.filter(role='driver'),
        source='driver',
        write_only=True,
        required=False,
        allow_null=True
    )

    class Meta:
        model = Bus
        fields = ['id', 'name', 'plate_number', 'capacity', 'driver', 'driver_id', 'active']
        read_only_fields = ['id']

# views.py - API endpoints
class BusViewSet(viewsets.ModelViewSet):
    serializer_class = BusSerializer
    permission_classes = [IsAuthenticated, IsAdminOrReadOnly]

    def get_queryset(self):
        # Role-based filtering
        queryset = Bus.objects.select_related('driver').all()

        if self.request.user.role == 'driver':
            # Drivers see only their assigned bus
            return queryset.filter(driver=self.request.user)

        return queryset  # Admins see all
```

**What Happens**:
1. Client requests `/api/buses/`
2. Django checks permissions
3. `get_queryset()` filters data by role
4. `BusSerializer` transforms Model → JSON
5. Returns: `[{ id: 1, name: "Bus A", driver: { id: 2, name: "John" }, ... }]`

---

### 2. Dynamic Serializers (List vs Detail)

```python
class TripViewSet(viewsets.ModelViewSet):
    def get_serializer_class(self):
        # Different serializers for different actions
        if self.action == 'retrieve':
            return TripDetailSerializer  # Includes locations, boardings
        return TripSerializer  # Basic info only

# TripSerializer - List view (lightweight)
class TripSerializer(serializers.ModelSerializer):
    class Meta:
        model = Trip
        fields = ['id', 'bus', 'driver', 'route', 'start_time', 'is_active']

# TripDetailSerializer - Detail view (heavyweight)
class TripDetailSerializer(TripSerializer):
    locations = BusLocationSerializer(many=True, read_only=True)
    boardings = EmployeeBoardingSerializer(many=True, read_only=True)

    class Meta(TripSerializer.Meta):
        fields = TripSerializer.Meta.fields + ['locations', 'boardings', 'latest_location']
```

**Why**: List endpoints need speed, detail endpoints need completeness.

---

## SvelteKit Data Loading

### 1. Load Functions (+page.ts)

**Purpose**: Fetch data BEFORE page renders (runs on server OR client)

```typescript
// routes/buses/+page.ts
import type { PageLoad } from './$types';
import { busService } from '$lib/services/bus';

export const load: PageLoad = async ({ fetch, parent }) => {
  // Wait for parent layout data (auth check)
  await parent();

  // Fetch buses (uses Zod validation internally)
  const buses = await busService.getAll();

  // Return data to component
  return {
    buses
  };
};
```

**Flow**:
1. User navigates to `/buses`
2. `load()` runs BEFORE component mounts
3. Data is fetched and validated
4. Component receives validated data via `data` prop

---

### 2. Using Loaded Data in Components

```svelte
<!-- routes/buses/+page.svelte -->
<script lang="ts">
  import type { PageData } from './$types';

  // Data prop contains everything returned from load()
  let { data }: { data: PageData } = $props();

  // Access loaded data
  const buses = data.buses;
</script>

<div>
  {#each buses as bus}
    <div>{bus.name} - {bus.plate_number}</div>
  {/each}
</div>
```

---

### 3. Server-Only Loads (+page.server.ts)

**Purpose**: Load data on SERVER only (never exposes API keys to client)

```typescript
// routes/admin/users/+page.server.ts
import type { PageServerLoad } from './$types';
import { ADMIN_SECRET_KEY } from '$env/static/private';

export const load: PageServerLoad = async ({ fetch, locals }) => {
  // This code NEVER runs in browser
  const response = await fetch('/api/admin/users', {
    headers: { 'X-Admin-Key': ADMIN_SECRET_KEY }
  });

  const users = await response.json();

  return { users };
};
```

**Difference**:
- `+page.ts` - Runs on server AND client
- `+page.server.ts` - Runs on server ONLY (secure)

---

### 4. Layout Loads (+layout.ts)

**Purpose**: Load data shared across multiple pages

```typescript
// routes/+layout.ts
import type { LayoutLoad } from './$types';
import { auth } from '$lib/stores/auth.svelte';

export const load: LayoutLoad = async () => {
  // Check if user is authenticated
  if (auth.isAuthenticated) {
    // Return user data available to ALL child pages
    return {
      user: auth.user
    };
  }

  return {};
};
```

**Inheritance**:
```
+layout.ts (user data)
  ├─ routes/dashboard/+page.ts (merges with user data)
  ├─ routes/profile/+page.ts (merges with user data)
  └─ routes/buses/+page.ts (merges with user data)
```

---

## Zod Validation Layer

### 1. Schema Definition (Source of Truth)

**Location**: `lib/schemas/index.ts`

```typescript
import { z } from 'zod';

// 1. Define Zod schema (SINGLE SOURCE OF TRUTH)
export const busSchema = z.object({
  id: z.number().int().positive(),
  name: z.string().min(1).trim(),
  plate_number: z.string().min(1).trim().toUpperCase(),
  capacity: z.number().int().positive(),
  driver: driverSchema.nullable(),
  active: z.boolean(),
});

// 2. Create schema for API input (what we SEND)
export const busCreateSchema = z.object({
  name: z.string().min(1, 'Bus name is required').trim(),
  plate_number: z.string().min(1, 'Plate number is required').trim().toUpperCase(),
  capacity: z.number().int().positive('Capacity must be at least 1'),
  driver: z.number().int().positive().nullish(),  // Send driver ID, not object
  active: z.boolean().default(true),
});
```

---

### 2. Type Inference (TypeScript Types)

**Location**: `lib/types/index.ts`

```typescript
import { z } from 'zod';
import { busSchema, busCreateSchema } from '$lib/schemas';

// NEVER manually write these types - always infer from Zod
export type Bus = z.infer<typeof busSchema>;
export type BusCreateData = z.infer<typeof busCreateSchema>;

// TypeScript now knows:
// Bus = { id: number, name: string, plate_number: string, ... }
// BusCreateData = { name: string, plate_number: string, capacity: number, ... }
```

**Why Infer?**
- ✅ Single source of truth (schema)
- ✅ Types automatically update when schema changes
- ✅ Runtime validation + compile-time checking
- ❌ Don't manually define types that have schemas

---

### 3. Service Layer Validation

**Location**: `lib/services/bus.ts`

```typescript
import { apiClient } from './api-client';
import { busSchema, busCreateSchema } from '$lib/schemas';
import type { Bus, BusCreateData } from '$lib/types';

export const busService = {
  // GET /api/buses/ - Validate response
  async getAll(): Promise<Bus[]> {
    const response = await apiClient.get('/api/buses/');

    // Validate EVERY item in array
    return z.array(busSchema).parse(response);
  },

  // GET /api/buses/:id - Validate single item
  async getById(id: number): Promise<Bus> {
    const response = await apiClient.get(`/api/buses/${id}/`);

    // Validate single object
    return busSchema.parse(response);
  },

  // POST /api/buses/ - Validate input AND output
  async create(data: BusCreateData): Promise<Bus> {
    // 1. Validate input before sending
    const validatedInput = busCreateSchema.parse(data);

    // 2. Send to API
    const response = await apiClient.post('/api/buses/', validatedInput);

    // 3. Validate response before returning
    return busSchema.parse(response);
  },

  // PATCH /api/buses/:id - Partial update
  async update(id: number, data: Partial<BusCreateData>): Promise<Bus> {
    // Use .partial() for optional fields
    const validatedInput = busCreateSchema.partial().parse(data);

    const response = await apiClient.patch(`/api/buses/${id}/`, validatedInput);

    return busSchema.parse(response);
  }
};
```

**What Happens**:
1. **Input Validation**: `busCreateSchema.parse(data)` - Throws error if invalid
2. **API Call**: Send validated data to Django
3. **Output Validation**: `busSchema.parse(response)` - Ensures API returned correct shape
4. **Type Safety**: TypeScript knows return type is `Bus`

---

### 4. Form Validation

```svelte
<script lang="ts">
  import { busCreateSchema } from '$lib/schemas';
  import type { BusCreateData } from '$lib/types';
  import { z } from 'zod';

  let formData = $state<BusCreateData>({
    name: '',
    plate_number: '',
    capacity: 0,
    driver: null,
    active: true
  });

  let errors = $state<Record<string, string>>({});

  async function handleSubmit() {
    errors = {};

    try {
      // Validate form data
      const validatedData = busCreateSchema.parse(formData);

      // Send to API
      await busService.create(validatedData);

    } catch (e) {
      if (e instanceof z.ZodError) {
        // Extract validation errors
        e.issues.forEach((issue) => {
          if (issue.path[0]) {
            errors[issue.path[0] as string] = issue.message;
          }
        });
      }
    }
  }
</script>

<form onsubmit={(e) => { e.preventDefault(); handleSubmit(); }}>
  <input
    type="text"
    bind:value={formData.name}
    class={errors.name ? 'border-red-500' : ''}
  />
  {#if errors.name}
    <p class="text-red-500">{errors.name}</p>
  {/if}
</form>
```

---

## Complete Data Flow

### Example: Loading Trips Page

**Step-by-Step Flow**:

```
User navigates to /trips
    ↓
1. SvelteKit runs +page.ts load()
    ↓
2. load() calls tripService.getAll()
    ↓
3. tripService.getAll() calls apiClient.get('/api/trips/')
    ↓
4. apiClient adds JWT token to request
    ↓
5. Django receives request at TripViewSet
    ↓
6. Django checks permissions (IsAuthenticated)
    ↓
7. Django filters queryset by role (get_queryset)
    ↓
8. Django serializes data with TripSerializer
    ↓
9. Django returns JSON: [{ id: 1, bus: {...}, driver: {...}, ... }]
    ↓
10. apiClient receives response
    ↓
11. tripService validates with z.array(tripSchema).parse()
    ↓
12. Zod checks EVERY field matches schema
    ↓
13. If valid: Returns Trip[] to load()
    ↓
14. load() returns { trips } to component
    ↓
15. Component receives data prop with trips
    ↓
16. Page renders with validated data
```

---

## Common Patterns

### 1. Dependent Data Loading

```typescript
// routes/trips/[id]/+page.ts
export const load: PageLoad = async ({ params, fetch }) => {
  const tripId = parseInt(params.id);

  // Load trip first
  const trip = await tripService.getById(tripId);

  // Then load related data
  const [boardings, locations] = await Promise.all([
    boardingService.getByTripId(tripId),
    locationService.getByTripId(tripId)
  ]);

  return {
    trip,
    boardings,
    locations
  };
};
```

---

### 2. Authenticated Data Loading

```typescript
// routes/profile/+page.ts
import { redirect } from '@sveltejs/kit';
import { auth } from '$lib/stores/auth.svelte';

export const load: PageLoad = async () => {
  // Guard: Redirect if not authenticated
  if (!auth.isAuthenticated) {
    throw redirect(302, '/auth/login');
  }

  // Load user profile
  const user = await authService.getProfile();

  return { user };
};
```

---

### 3. Real-Time Data (No Load Function)

```svelte
<script lang="ts">
  import { onMount } from 'svelte';
  import { liveTrackingSchema } from '$lib/schemas';
  import type { LiveTracking } from '$lib/types';

  let trips = $state<LiveTracking[]>([]);
  let loading = $state(true);

  async function loadLiveTracking() {
    try {
      const response = await apiClient.get('/api/live-tracking/');

      // Validate real-time data
      trips = z.array(liveTrackingSchema).parse(response);

    } catch (e) {
      console.error('Failed to load tracking data', e);
    } finally {
      loading = false;
    }
  }

  onMount(() => {
    loadLiveTracking();

    // Poll every 10 seconds
    const interval = setInterval(loadLiveTracking, 10000);

    return () => clearInterval(interval);
  });
</script>
```

---

### 4. Nested Schema Validation

```typescript
// Schema with nested objects
export const tripDetailSchema = z.object({
  id: z.number(),
  bus: busSchema,  // Nested bus object
  driver: driverSchema,  // Nested driver object
  route: routeSchema.nullable(),
  locations: z.array(busLocationSchema).optional(),  // Array of locations
  boardings: z.array(employeeBoardingSchema).optional()  // Array of boardings
});

// Service validates entire nested structure
async getById(id: number): Promise<TripDetail> {
  const response = await apiClient.get(`/api/trips/${id}/`);

  // Validates trip AND all nested objects
  return tripDetailSchema.parse(response);
}
```

---

## Best Practices

### ✅ DO

1. **Always validate at boundaries**
   ```typescript
   // Good: Validate API responses
   const users = z.array(userSchema).parse(await apiClient.get('/api/users/'));
   ```

2. **Use schema inference for types**
   ```typescript
   // Good: Single source of truth
   export type User = z.infer<typeof userSchema>;
   ```

3. **Validate form input before submission**
   ```typescript
   // Good: Catch errors early
   const validatedData = busCreateSchema.parse(formData);
   await busService.create(validatedData);
   ```

4. **Use load() for initial data**
   ```typescript
   // Good: Data ready before page renders
   export const load = async () => {
     return { buses: await busService.getAll() };
   };
   ```

5. **Keep schemas close to types**
   ```
   lib/schemas/index.ts  ← Zod schemas
   lib/types/index.ts    ← Type inference
   lib/services/*.ts     ← Validation usage
   ```

---

### ❌ DON'T

1. **Don't manually define types that have schemas**
   ```typescript
   // Bad: Out of sync with schema
   export type User = {
     id: number;
     name: string;
   };

   // Good: Always infer
   export type User = z.infer<typeof userSchema>;
   ```

2. **Don't skip validation**
   ```typescript
   // Bad: No validation
   const response = await fetch('/api/buses/');
   return await response.json();  // Could be anything!

   // Good: Validate
   const response = await apiClient.get('/api/buses/');
   return z.array(busSchema).parse(response);
   ```

3. **Don't load data in onMount when load() works**
   ```typescript
   // Bad: Delay before data shows
   onMount(async () => {
     buses = await busService.getAll();
   });

   // Good: Data ready immediately
   export const load = async () => ({ buses: await busService.getAll() });
   ```

4. **Don't expose secrets in client-side load()**
   ```typescript
   // Bad: API key exposed to client
   const data = await fetch('/api/admin', {
     headers: { 'X-Secret': ADMIN_KEY }
   });

   // Good: Use +page.server.ts
   export const load: PageServerLoad = async () => { ... };
   ```

---

## Quick Reference

### When to Use Each Load Type

| Type | File | Runs On | Use When |
|------|------|---------|----------|
| Page Load | `+page.ts` | Server + Client | Public data, client-side navigation |
| Server Load | `+page.server.ts` | Server Only | Secrets, server-only APIs |
| Layout Load | `+layout.ts` | Server + Client | Shared data across pages |
| Layout Server | `+layout.server.ts` | Server Only | Auth checks, session data |

---

### Zod Schema Cheatsheet

```typescript
// Basic types
z.string()
z.number()
z.boolean()
z.date()

// Constraints
z.string().min(1, 'Required')
z.number().positive()
z.string().email('Invalid email')
z.string().trim()

// Optional/Nullable
z.string().optional()          // string | undefined
z.string().nullable()          // string | null
z.string().nullish()           // string | null | undefined

// Objects
z.object({
  name: z.string(),
  age: z.number()
})

// Arrays
z.array(z.string())
z.array(userSchema)

// Nested
z.object({
  user: userSchema,
  posts: z.array(postSchema)
})

// Transformations
z.string().transform(s => s.toLowerCase())
z.string().toUpperCase()  // Built-in transform

// Enums
z.enum(['admin', 'driver', 'employee'])

// Union
z.union([z.string(), z.number()])

// Partial (all fields optional)
userSchema.partial()

// Pick specific fields
userSchema.pick({ name: true, email: true })

// Omit specific fields
userSchema.omit({ password: true })
```

---

## Summary

**Data Loading Flow**:
```
Django Model → Serializer → JSON Response
    ↓
API Client (fetch with JWT)
    ↓
Zod Schema Validation
    ↓
TypeScript Type Safety
    ↓
SvelteKit Load Function
    ↓
Component Renders
```

**Key Principles**:
1. **Django** - Database to JSON with serializers
2. **Zod** - Runtime validation at API boundaries
3. **TypeScript** - Compile-time type checking
4. **SvelteKit** - Load data before rendering

**Remember**:
- Schemas are the single source of truth
- Validate at EVERY boundary (API responses, form inputs)
- Use load() for initial data, onMount() for real-time updates
- Keep validation logic in services, not components
