<script lang="ts">
  import { onMount } from 'svelte';
  import { routeService } from '$lib/services/bus';
  import { auth } from '$lib/stores/auth.svelte';
  import LeafletMap from '$lib/components/tracking/LeafletMap.svelte';
  import type { Route, RouteCreateData } from '$lib/types';
  import { t } from '$lib/i18n';

  // Polyline decoder for OSRM responses
  function decodePolyline(encoded: string): [number, number][] {
    const points: [number, number][] = [];
    let index = 0, lat = 0, lng = 0;

    while (index < encoded.length) {
      let b, shift = 0, result = 0;
      do {
        b = encoded.charCodeAt(index++) - 63;
        result |= (b & 0x1f) << shift;
        shift += 5;
      } while (b >= 0x20);
      const dlat = ((result & 1) ? ~(result >> 1) : (result >> 1));
      lat += dlat;

      shift = 0;
      result = 0;
      do {
        b = encoded.charCodeAt(index++) - 63;
        result |= (b & 0x1f) << shift;
        shift += 5;
      } while (b >= 0x20);
      const dlng = ((result & 1) ? ~(result >> 1) : (result >> 1));
      lng += dlng;

      points.push([lat / 1e5, lng / 1e5]);
    }
    return points;
  }

  // Cache for road routes
  let roadRouteCache = $state<Map<string, [number, number][]>>(new Map());
  let loadingRoutes = $state(false);

  // Saudi Arabia cities with coordinates
  const saudiCities: Record<string, { lat: number; lng: number }> = {
    'Riyadh': { lat: 24.7136, lng: 46.6753 },
    'Jeddah': { lat: 21.4858, lng: 39.1925 },
    'Mecca': { lat: 21.3891, lng: 39.8579 },
    'Medina': { lat: 24.5247, lng: 39.5692 },
    'Dammam': { lat: 26.4207, lng: 50.0888 },
    'Khobar': { lat: 26.2172, lng: 50.1971 },
    'Dhahran': { lat: 26.2361, lng: 50.0393 },
    'Tabuk': { lat: 28.3838, lng: 36.5550 },
    'Abha': { lat: 18.2164, lng: 42.5053 },
    'Taif': { lat: 21.4373, lng: 40.5127 },
    'Buraidah': { lat: 26.3260, lng: 43.9750 },
    'Khamis Mushait': { lat: 18.3093, lng: 42.7450 },
    'Hail': { lat: 27.5114, lng: 41.7208 },
    'Najran': { lat: 17.4933, lng: 44.1277 },
    'Jubail': { lat: 27.0046, lng: 49.6225 },
    'Yanbu': { lat: 24.0895, lng: 38.0618 },
    'Al Ahsa': { lat: 25.3648, lng: 49.5855 },
    'Jizan': { lat: 16.8892, lng: 42.5511 },
    'Sakaka': { lat: 29.9697, lng: 40.2064 },
    'Arar': { lat: 30.9753, lng: 41.0381 },
    'Al Qatif': { lat: 26.5196, lng: 50.0115 },
    'Al Kharj': { lat: 24.1556, lng: 47.3126 },
    'Hafar Al Batin': { lat: 28.4328, lng: 45.9708 },
    'Al Mubarraz': { lat: 25.4084, lng: 49.5624 },
    'Qurayyat': { lat: 31.3316, lng: 37.3430 }
  };

  const cityNames = Object.keys(saudiCities).sort();

  // State
  let routes = $state<Route[]>([]);
  let loading = $state(true);
  let error = $state('');
  let authError = $state(false);
  let selectedRoute = $state<Route | null>(null);

  // Modal state
  let showModal = $state(false);
  let modalMode = $state<'create' | 'edit'>('create');
  let formData = $state<RouteCreateData>({
    name: '',
    start_point: '',
    end_point: ''
  });
  let formError = $state('');
  let saving = $state(false);

  // Delete confirmation
  let showDeleteConfirm = $state(false);
  let deleteTarget = $state<Route | null>(null);
  let deleting = $state(false);

  // Search
  let searchQuery = $state('');

  // Computed
  const filteredRoutes = $derived.by(() => {
    if (!searchQuery.trim()) return routes;
    const query = searchQuery.toLowerCase();
    return routes.filter(r =>
      r.name.toLowerCase().includes(query) ||
      r.start_point.toLowerCase().includes(query) ||
      r.end_point.toLowerCase().includes(query)
    );
  });

  // Helper to get city coordinates - case insensitive match
  function getCityCoords(cityName: string): { lat: number; lng: number } | null {
    // Direct match first
    if (saudiCities[cityName]) {
      return saudiCities[cityName];
    }
    // Case insensitive search
    const found = Object.entries(saudiCities).find(
      ([name]) => name.toLowerCase() === cityName.toLowerCase()
    );
    return found ? found[1] : null;
  }

  // Map markers - show start and end points using actual city coordinates
  const mapMarkers = $derived.by(() => {
    const routesToShow = selectedRoute ? [selectedRoute] : routes;
    const result: Array<{
      id: string;
      lat: number;
      lng: number;
      label: string;
      color: string;
      popup: string;
    }> = [];

    routesToShow.forEach(route => {
      const startCoords = getCityCoords(route.start_point);
      const endCoords = getCityCoords(route.end_point);

      if (startCoords) {
        result.push({
          id: `${route.id}-start`,
          lat: startCoords.lat,
          lng: startCoords.lng,
          label: route.start_point,
          color: '#22c55e',
          popup: `<div style="text-align:center"><strong>${route.name}</strong><br/><span style="color:#22c55e">● Start:</span> ${route.start_point}</div>`
        });
      }

      if (endCoords) {
        result.push({
          id: `${route.id}-end`,
          lat: endCoords.lat,
          lng: endCoords.lng,
          label: route.end_point,
          color: '#ef4444',
          popup: `<div style="text-align:center"><strong>${route.name}</strong><br/><span style="color:#ef4444">● End:</span> ${route.end_point}</div>`
        });
      }
    });

    return result;
  });

  // Fetch road route from OSRM
  async function fetchRoadRoute(
    start: { lat: number; lng: number },
    end: { lat: number; lng: number }
  ): Promise<[number, number][]> {
    const cacheKey = `${start.lat},${start.lng}-${end.lat},${end.lng}`;

    // Check cache first
    if (roadRouteCache.has(cacheKey)) {
      return roadRouteCache.get(cacheKey)!;
    }

    try {
      // Use OSRM demo server for routing
      const url = `https://router.project-osrm.org/route/v1/driving/${start.lng},${start.lat};${end.lng},${end.lat}?overview=full&geometries=polyline`;
      const response = await fetch(url);
      const data = await response.json();

      if (data.code === 'Ok' && data.routes?.[0]?.geometry) {
        const coordinates = decodePolyline(data.routes[0].geometry);
        // Update cache
        roadRouteCache = new Map(roadRouteCache).set(cacheKey, coordinates);
        return coordinates;
      }
    } catch (error) {
      console.error('Failed to fetch road route:', error);
    }

    // Fallback to straight line
    return [[start.lat, start.lng], [end.lat, end.lng]];
  }

  // Load road routes for all routes
  async function loadRoadRoutes() {
    loadingRoutes = true;
    const routesToLoad = selectedRoute ? [selectedRoute] : routes;

    for (const route of routesToLoad) {
      const startCoords = getCityCoords(route.start_point);
      const endCoords = getCityCoords(route.end_point);

      if (startCoords && endCoords) {
        const cacheKey = `${startCoords.lat},${startCoords.lng}-${endCoords.lat},${endCoords.lng}`;
        if (!roadRouteCache.has(cacheKey)) {
          await fetchRoadRoute(startCoords, endCoords);
        }
      }
    }
    loadingRoutes = false;
  }

  // Map paths - draw lines following roads
  const mapPaths = $derived.by(() => {
    const routesToShow = selectedRoute ? [selectedRoute] : routes;
    const result: Array<{
      coordinates: [number, number][];
      color: string;
      weight: number;
    }> = [];

    routesToShow.forEach(route => {
      const startCoords = getCityCoords(route.start_point);
      const endCoords = getCityCoords(route.end_point);

      if (startCoords && endCoords) {
        const cacheKey = `${startCoords.lat},${startCoords.lng}-${endCoords.lat},${endCoords.lng}`;
        const roadCoordinates = roadRouteCache.get(cacheKey);

        result.push({
          coordinates: roadCoordinates || [
            [startCoords.lat, startCoords.lng],
            [endCoords.lat, endCoords.lng]
          ],
          color: selectedRoute?.id === route.id ? '#1d4ed8' : '#3b82f6',
          weight: selectedRoute?.id === route.id ? 6 : 4
        });
      }
    });

    return result;
  });

  // Center of Saudi Arabia
  const defaultCenter: [number, number] = [24.0, 45.0];

  async function loadRoutes() {
    try {
      routes = await routeService.list();
      error = '';
      authError = false;
      // Load road routes after getting route data
      if (routes.length > 0) {
        await loadRoadRoutes();
      }
    } catch (e: any) {
      const message = e.message || 'Failed to load routes';
      if (message.includes('credentials were not provided') || message.includes('Authentication')) {
        authError = true;
        error = '';
      } else {
        error = message;
        authError = false;
      }
    } finally {
      loading = false;
    }
  }

  // Reload road routes when selected route changes
  $effect(() => {
    if (selectedRoute && routes.length > 0) {
      loadRoadRoutes();
    }
  });

  function openCreateModal() {
    modalMode = 'create';
    formData = { name: '', start_point: '', end_point: '' };
    formError = '';
    showModal = true;
  }

  function openEditModal(route: Route) {
    modalMode = 'edit';
    formData = {
      name: route.name,
      start_point: route.start_point,
      end_point: route.end_point
    };
    selectedRoute = route;
    formError = '';
    showModal = true;
  }

  function closeModal() {
    showModal = false;
    formError = '';
  }

  async function handleSubmit() {
    if (!formData.name.trim() || !formData.start_point.trim() || !formData.end_point.trim()) {
      formError = 'All fields are required';
      return;
    }

    saving = true;
    formError = '';

    try {
      if (modalMode === 'create') {
        const newRoute = await routeService.create(formData);
        routes = [...routes, newRoute];
        // Load road route for the new route
        const startCoords = getCityCoords(newRoute.start_point);
        const endCoords = getCityCoords(newRoute.end_point);
        if (startCoords && endCoords) {
          await fetchRoadRoute(startCoords, endCoords);
        }
      } else if (selectedRoute) {
        const updatedRoute = await routeService.update(selectedRoute.id, formData);
        routes = routes.map(r => r.id === selectedRoute!.id ? updatedRoute : r);
        selectedRoute = updatedRoute;
        // Reload road route if cities changed
        const startCoords = getCityCoords(updatedRoute.start_point);
        const endCoords = getCityCoords(updatedRoute.end_point);
        if (startCoords && endCoords) {
          await fetchRoadRoute(startCoords, endCoords);
        }
      }
      closeModal();
    } catch (e: any) {
      formError = e.message || 'Failed to save route';
    } finally {
      saving = false;
    }
  }

  function confirmDelete(route: Route) {
    deleteTarget = route;
    showDeleteConfirm = true;
  }

  async function handleDelete() {
    if (!deleteTarget) return;

    deleting = true;
    try {
      await routeService.delete(deleteTarget.id);
      routes = routes.filter(r => r.id !== deleteTarget!.id);
      if (selectedRoute?.id === deleteTarget.id) {
        selectedRoute = null;
      }
      showDeleteConfirm = false;
      deleteTarget = null;
    } catch (e: any) {
      error = e.message || 'Failed to delete route';
    } finally {
      deleting = false;
    }
  }

  function selectRoute(route: Route) {
    selectedRoute = selectedRoute?.id === route.id ? null : route;
  }

  onMount(loadRoutes);
</script>

<div class="min-h-screen bg-gray-50 relative overflow-hidden flex flex-col">
  <!-- Background Elements -->
  <div class="hero-dots fixed inset-0 opacity-30 pointer-events-none"></div>
  <div class="fixed top-0 left-0 w-full h-96 bg-gradient-to-b from-brand-50/80 to-transparent pointer-events-none"></div>

  {#if loading}
    <div class="flex-1 flex items-center justify-center">
      <div class="animate-spin rounded-full h-12 w-12 border-b-2 border-brand-500"></div>
    </div>
  {:else if authError}
    <div class="flex-1 flex items-center justify-center p-4 animate-fade-in relative z-10">
      <div class="glass-card max-w-md w-full p-8 text-center relative overflow-hidden group">
        <!-- Decorative Background -->
        <div class="absolute top-0 right-0 w-40 h-40 bg-brand-400/10 rounded-full blur-3xl -translate-y-1/2 translate-x-1/2 group-hover:bg-brand-400/20 transition-all duration-500"></div>

        <div class="w-20 h-20 mx-auto rounded-full bg-brand-50 flex items-center justify-center text-brand-500 mb-6 shadow-sm relative z-10">
          <svg xmlns="http://www.w3.org/2000/svg" class="h-10 w-10" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 15v2m-6 4h12a2 2 0 002-2v-6a2 2 0 00-2-2H6a2 2 0 00-2 2v6a2 2 0 002 2zm10-10V7a4 4 0 00-8 0v4h8z" />
          </svg>
        </div>

        <h2 class="text-2xl font-black text-gray-900 mb-3 relative z-10">{$t('routes.authRequired')}</h2>
        <p class="text-gray-500 mb-8 relative z-10">{$t('routes.authMessage')}</p>

        <a href="/login" class="btn-primary w-full flex justify-center items-center gap-2 relative z-10 group-hover:scale-[1.02] transition-transform">
          <span>{$t('routes.signInToContinue')}</span>
          <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5" viewBox="0 0 20 20" fill="currentColor">
            <path fill-rule="evenodd" d="M7.293 14.707a1 1 0 010-1.414L10.586 10 7.293 6.707a1 1 0 011.414-1.414l4 4a1 1 0 010 1.414l-4 4a1 1 0 01-1.414 0z" clip-rule="evenodd" />
          </svg>
        </a>
      </div>
    </div>
  {:else if error}
    <div class="flex-1 flex items-center justify-center p-4">
      <div class="p-4 rounded-xl bg-red-50 text-red-600 border border-red-100 flex items-center gap-3">
        <svg xmlns="http://www.w3.org/2000/svg" class="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
        </svg>
        <span class="font-medium">{error}</span>
      </div>
    </div>
  {:else}
    <div class="flex-1 flex flex-col lg:flex-row h-[calc(100vh-64px)] overflow-hidden">
      <!-- Map Section -->
      <div class="flex-1 relative z-0">
        <LeafletMap
          markers={mapMarkers}
          paths={mapPaths}
          center={defaultCenter}
          zoom={6}
          height="100%"
        />
        
        <!-- Floating Header on Map -->
        <div class="absolute top-4 left-4 z-[400] glass-card p-4 shadow-lg max-w-xs animate-slide-down">
          <h1 class="text-xl font-black text-gray-900 flex items-center gap-2">
            <span class="relative flex h-3 w-3">
              <span class="relative inline-flex rounded-full h-3 w-3 bg-brand-500"></span>
            </span>
            {$t('routes.mapTitle')}
          </h1>
          {#if loadingRoutes}
            <p class="text-xs text-brand-600 mt-1 font-medium flex items-center gap-1">
              <span class="animate-spin h-3 w-3 border-2 border-brand-600 border-t-transparent rounded-full"></span>
              {$t('routes.calculatingPaths')}
            </p>
          {:else}
            <p class="text-xs text-gray-500 mt-1 font-medium">
              {$t('routes.mapLegend')}
            </p>
          {/if}
          {#if selectedRoute}
            <button
              class="mt-2 text-xs font-bold text-brand-600 hover:text-brand-800 hover:underline"
              onclick={() => selectedRoute = null}
            >
              {$t('routes.showAllRoutes')}
            </button>
          {/if}
        </div>
      </div>

      <!-- Sidebar / Route List -->
      <div class="w-full lg:w-96 bg-white/80 backdrop-blur-md border-l border-gray-200 flex flex-col z-10 shadow-xl">
        <div class="p-4 border-b border-gray-100 bg-white/50 space-y-4">
          <div class="flex items-center justify-between">
            <h2 class="font-bold text-gray-900 flex items-center gap-2">
              <span>{$t('routes.title')}</span>
              <span class="bg-brand-100 text-brand-700 px-2 py-0.5 rounded-full text-xs">{routes.length}</span>
            </h2>
            {#if auth.isAdmin}
              <button class="btn-primary !py-1.5 !px-3 !text-xs flex items-center gap-1" onclick={openCreateModal}>
                <svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4" viewBox="0 0 20 20" fill="currentColor">
                  <path fill-rule="evenodd" d="M10 3a1 1 0 011 1v5h5a1 1 0 110 2h-5v5a1 1 0 11-2 0v-5H4a1 1 0 110-2h5V4a1 1 0 011-1z" clip-rule="evenodd" />
                </svg>
                {$t('routes.addRoute')}
              </button>
            {/if}
          </div>

          <!-- Search -->
          <div class="relative">
            <svg xmlns="http://www.w3.org/2000/svg" class="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-gray-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
            </svg>
            <input
              type="text"
              placeholder={$t('routes.searchPlaceholder')}
              bind:value={searchQuery}
              class="w-full pl-9 pr-4 py-2 rounded-lg border border-gray-200 bg-white/50 focus:bg-white focus:border-brand-300 focus:ring-2 focus:ring-brand-100 outline-none transition-all text-sm"
            />
          </div>
        </div>

        <div class="flex-1 overflow-y-auto p-4 space-y-3 custom-scrollbar">
          {#if filteredRoutes.length === 0}
            <div class="text-center py-12 text-gray-400">
              <div class="w-16 h-16 mx-auto rounded-full bg-gray-50 flex items-center justify-center mb-3">
                <svg xmlns="http://www.w3.org/2000/svg" class="h-8 w-8" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 20l-5.447-2.724A1 1 0 0 1 3 16.382V5.618a1 1 0 0 1 1.447-.894L9 7m0 13l6-3m-6 3V7m6 10l4.553 2.276A1 1 0 0 0 21 18.382V7.618a1 1 0 0 0-.553-.894L15 4m0 13V4" />
                </svg>
              </div>
              <p class="text-sm font-medium">{searchQuery ? $t('routes.noRoutesMatch') : $t('routes.noRoutesYet')}</p>
            </div>
          {:else}
            {#each filteredRoutes as route (route.id)}
              <div
                class="w-full text-left p-4 rounded-xl border transition-all duration-200 group relative overflow-hidden cursor-pointer
                  {selectedRoute?.id === route.id 
                    ? 'bg-brand-50 border-brand-200 shadow-sm' 
                    : 'bg-white border-gray-100 hover:border-brand-200 hover:shadow-md'}"
                onclick={() => selectRoute(route)}
                role="button"
                tabindex="0"
                onkeydown={(e) => e.key === 'Enter' && selectRoute(route)}
              >
                <div class="flex justify-between items-start mb-3">
                  <h3 class="font-bold text-gray-900 text-sm">{route.name}</h3>
                  {#if auth.isAdmin}
                    <div class="flex gap-1 opacity-0 group-hover:opacity-100 transition-opacity">
                      <button
                        class="p-1 hover:bg-gray-100 rounded text-gray-500 hover:text-brand-600"
                        onclick={(e) => { e.stopPropagation(); openEditModal(route); }}
                        title="Edit"
                      >
                        <svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4" viewBox="0 0 20 20" fill="currentColor">
                          <path d="M13.586 3.586a2 2 0 112.828 2.828l-.793.793-2.828-2.828.793-.793zM11.379 5.793L3 14.172V17h2.828l8.38-8.379-2.83-2.828z" />
                        </svg>
                      </button>
                      <button
                        class="p-1 hover:bg-red-50 rounded text-gray-500 hover:text-red-600"
                        onclick={(e) => { e.stopPropagation(); confirmDelete(route); }}
                        title="Delete"
                      >
                        <svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4" viewBox="0 0 20 20" fill="currentColor">
                          <path fill-rule="evenodd" d="M9 2a1 1 0 00-.894.553L7.382 4H4a1 1 0 000 2v10a2 2 0 002 2h8a2 2 0 002-2V6a1 1 0 100-2h-3.382l-.724-1.447A1 1 0 0011 2H9zM7 8a1 1 0 012 0v6a1 1 0 11-2 0V8zm5-1a1 1 0 00-1 1v6a1 1 0 102 0V8a1 1 0 00-1-1z" clip-rule="evenodd" />
                        </svg>
                      </button>
                    </div>
                  {/if}
                </div>

                <div class="relative pl-4 space-y-4">
                  <!-- Connecting Line -->
                  <div class="absolute left-[5px] top-2 bottom-2 w-0.5 bg-gray-200"></div>

                  <div class="relative">
                    <div class="absolute -left-4 top-1.5 w-2.5 h-2.5 rounded-full border-2 border-green-500 bg-white z-10"></div>
                    <div class="text-xs">
                      <span class="text-gray-400 font-bold uppercase tracking-wider text-[10px] block mb-0.5">{$t('routes.start')}</span>
                      <span class="font-medium text-gray-900">{route.start_point}</span>
                    </div>
                  </div>

                  <div class="relative">
                    <div class="absolute -left-4 top-1.5 w-2.5 h-2.5 rounded-full border-2 border-red-500 bg-white z-10"></div>
                    <div class="text-xs">
                      <span class="text-gray-400 font-bold uppercase tracking-wider text-[10px] block mb-0.5">{$t('routes.end')}</span>
                      <span class="font-medium text-gray-900">{route.end_point}</span>
                    </div>
                  </div>
                </div>
              </div>
            {/each}
          {/if}
        </div>
      </div>
    </div>
  {/if}
</div>

<!-- Create/Edit Modal -->
{#if showModal}
  <div class="modal-overlay" onclick={closeModal}>
    <div class="modal" onclick={(e) => e.stopPropagation()}>
      <header class="modal-header">
        <h2>{modalMode === 'create' ? $t('routes.createRoute') : $t('routes.editRoute')}</h2>
        <button class="close-btn" onclick={closeModal}>
          <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <line x1="18" y1="6" x2="6" y2="18"></line>
            <line x1="6" y1="6" x2="18" y2="18"></line>
          </svg>
        </button>
      </header>

      <form class="modal-body" onsubmit={(e) => { e.preventDefault(); handleSubmit(); }}>
        {#if formError}
          <div class="form-error">{formError}</div>
        {/if}

        <div class="form-group">
          <label for="name">{$t('routes.routeName')}</label>
          <input
            id="name"
            type="text"
            bind:value={formData.name}
            placeholder={$t('routes.routeNamePlaceholder')}
            required
          />
        </div>

        <div class="form-group">
          <label for="start_point">{$t('routes.startPoint')}</label>
          <select
            id="start_point"
            bind:value={formData.start_point}
            required
          >
            <option value="">{$t('routes.selectCity')}</option>
            {#each cityNames as city}
              <option value={city}>{city}</option>
            {/each}
          </select>
        </div>

        <div class="form-group">
          <label for="end_point">{$t('routes.endPoint')}</label>
          <select
            id="end_point"
            bind:value={formData.end_point}
            required
          >
            <option value="">{$t('routes.selectCity')}</option>
            {#each cityNames as city}
              <option value={city}>{city}</option>
            {/each}
          </select>
        </div>

        <footer class="form-footer">
          <button type="button" class="btn-secondary" onclick={closeModal}>
            {$t('routes.cancel')}
          </button>
          <button type="submit" class="btn-primary" disabled={saving}>
            {saving ? $t('routes.saving') : (modalMode === 'create' ? $t('routes.createRoute') : $t('routes.saveChanges'))}
          </button>
        </footer>
      </form>
    </div>
  </div>
{/if}

<!-- Delete Confirmation Modal -->
{#if showDeleteConfirm && deleteTarget}
  <div class="modal-overlay" onclick={() => showDeleteConfirm = false}>
    <div class="modal confirm-modal" onclick={(e) => e.stopPropagation()}>
      <div class="confirm-icon">
        <svg xmlns="http://www.w3.org/2000/svg" width="48" height="48" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
          <path d="M10.29 3.86L1.82 18a2 2 0 0 0 1.71 3h16.94a2 2 0 0 0 1.71-3L13.71 3.86a2 2 0 0 0-3.42 0z"></path>
          <line x1="12" y1="9" x2="12" y2="13"></line>
          <line x1="12" y1="17" x2="12.01" y2="17"></line>
        </svg>
      </div>
      <h2>{$t('routes.deleteRouteTitle')}</h2>
      <p>{$t('routes.deleteRouteMessage', { name: deleteTarget.name })}</p>
      <div class="confirm-actions">
        <button class="btn-secondary" onclick={() => showDeleteConfirm = false}>
          {$t('routes.cancel')}
        </button>
        <button class="btn-danger" onclick={handleDelete} disabled={deleting}>
          {deleting ? $t('routes.deleting') : $t('routes.deleteRoute')}
        </button>
      </div>
    </div>
  </div>
{/if}

<style>
  .page {
    padding: 1.5rem;
    max-width: 1400px;
    margin: 0 auto;
  }

  .page-header {
    display: flex;
    justify-content: space-between;
    align-items: flex-start;
    margin-bottom: 2rem;
    gap: 1rem;
    flex-wrap: wrap;
  }

  .page-header h1 {
    margin: 0 0 0.25rem;
    font-size: 1.875rem;
    font-weight: 700;
    color: #111827;
  }

  .subtitle {
    margin: 0;
    color: #6b7280;
  }

  .btn-primary {
    display: inline-flex;
    align-items: center;
    gap: 0.5rem;
    padding: 0.625rem 1.25rem;
    background: #3b82f6;
    color: white;
    border: none;
    border-radius: 8px;
    font-weight: 500;
    cursor: pointer;
    transition: background 0.2s;
  }

  .btn-primary:hover {
    background: #2563eb;
  }

  .btn-primary:disabled {
    opacity: 0.6;
    cursor: not-allowed;
  }

  /* Loading & Error States */
  .loading-container {
    display: flex;
    flex-direction: column;
    align-items: center;
    padding: 4rem 2rem;
    color: #6b7280;
  }

  .spinner {
    width: 40px;
    height: 40px;
    border: 3px solid #e5e7eb;
    border-top-color: #3b82f6;
    border-radius: 50%;
    animation: spin 0.8s linear infinite;
    margin-bottom: 1rem;
  }

  @keyframes spin {
    to { transform: rotate(360deg); }
  }

  .auth-message {
    text-align: center;
    padding: 3rem 2rem;
    background: #f8fafc;
    border-radius: 12px;
    border: 1px solid #e2e8f0;
  }

  .auth-icon {
    color: #64748b;
    margin-bottom: 1rem;
  }

  .auth-message h2 {
    margin: 0 0 0.5rem;
    color: #1e293b;
  }

  .auth-message p {
    color: #64748b;
    margin: 0 0 1.5rem;
  }

  .login-link {
    display: inline-block;
    background: #3b82f6;
    color: white;
    padding: 0.75rem 2rem;
    border-radius: 8px;
    text-decoration: none;
    font-weight: 500;
  }

  .login-link:hover {
    background: #2563eb;
  }

  .error-container {
    text-align: center;
    padding: 2rem;
  }

  .error {
    color: #dc2626;
    margin-bottom: 1rem;
  }

  .retry-btn {
    padding: 0.5rem 1rem;
    background: #f3f4f6;
    border: 1px solid #d1d5db;
    border-radius: 6px;
    cursor: pointer;
  }

  /* Stats Bar */
  .stats-bar {
    display: flex;
    gap: 1.5rem;
    margin-bottom: 2rem;
  }

  .stat {
    display: flex;
    align-items: baseline;
    gap: 0.5rem;
  }

  .stat-value {
    font-size: 2rem;
    font-weight: 700;
    color: #111827;
  }

  .stat-label {
    color: #6b7280;
    font-size: 0.875rem;
  }

  /* Map Section */
  .map-section {
    margin-bottom: 2rem;
  }

  .section-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 1rem;
  }

  .section-header h2 {
    font-size: 1.25rem;
    margin: 0;
    color: #374151;
  }

  .clear-selection {
    background: none;
    border: none;
    color: #3b82f6;
    font-size: 0.875rem;
    cursor: pointer;
  }

  .clear-selection:hover {
    text-decoration: underline;
  }

  .map-container {
    border-radius: 12px;
    overflow: hidden;
    border: 1px solid #e5e7eb;
  }

  .map-info {
    margin-top: 0.75rem;
  }

  .map-note {
    display: flex;
    align-items: center;
    gap: 0.5rem;
    margin: 0;
    font-size: 0.75rem;
    color: #6b7280;
  }

  .loading-routes {
    display: flex;
    align-items: center;
    gap: 0.5rem;
    margin: 0;
    font-size: 0.75rem;
    color: #3b82f6;
  }

  .mini-spinner {
    width: 14px;
    height: 14px;
    border: 2px solid #e5e7eb;
    border-top-color: #3b82f6;
    border-radius: 50%;
    animation: spin 0.8s linear infinite;
  }

  /* Search */
  .search-container {
    margin-bottom: 1.5rem;
  }

  .search-box {
    display: flex;
    align-items: center;
    gap: 0.5rem;
    max-width: 400px;
    background: white;
    border: 1px solid #d1d5db;
    border-radius: 8px;
    padding: 0.5rem 0.75rem;
  }

  .search-box svg {
    color: #9ca3af;
  }

  .search-box input {
    flex: 1;
    border: none;
    outline: none;
    font-size: 0.875rem;
  }

  /* Empty State */
  .empty-state {
    text-align: center;
    padding: 3rem;
    color: #6b7280;
  }

  .empty-state svg {
    margin-bottom: 1rem;
    opacity: 0.5;
  }

  .empty-state button {
    margin-top: 1rem;
    padding: 0.5rem 1rem;
    background: #3b82f6;
    color: white;
    border: none;
    border-radius: 6px;
    cursor: pointer;
  }

  /* Routes Grid */
  .routes-grid {
    display: grid;
    grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
    gap: 1rem;
  }

  .route-card {
    background: white;
    border: 1px solid #e5e7eb;
    border-radius: 12px;
    padding: 1.25rem;
    cursor: pointer;
    transition: all 0.2s;
  }

  .route-card:hover {
    border-color: #3b82f6;
    box-shadow: 0 4px 12px rgba(59, 130, 246, 0.1);
  }

  .route-card.selected {
    border-color: #3b82f6;
    background: #eff6ff;
  }

  .route-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 1rem;
  }

  .route-header h3 {
    margin: 0;
    font-size: 1.125rem;
    font-weight: 600;
    color: #111827;
  }

  .actions {
    display: flex;
    gap: 0.25rem;
  }

  .action-btn {
    padding: 0.375rem;
    background: none;
    border: none;
    border-radius: 6px;
    cursor: pointer;
    color: #6b7280;
    transition: all 0.2s;
  }

  .action-btn:hover {
    background: #f3f4f6;
  }

  .action-btn.edit:hover {
    color: #3b82f6;
  }

  .action-btn.delete:hover {
    color: #dc2626;
  }

  .route-body {
    display: flex;
    flex-direction: column;
    gap: 0.5rem;
  }

  .route-point {
    display: flex;
    align-items: center;
    gap: 0.75rem;
  }

  .point-indicator {
    width: 12px;
    height: 12px;
    border-radius: 50%;
    flex-shrink: 0;
  }

  .point-indicator.start {
    background: #10b981;
  }

  .point-indicator.end {
    background: #ef4444;
  }

  .point-info {
    display: flex;
    flex-direction: column;
    min-width: 0;
  }

  .point-label {
    font-size: 0.75rem;
    color: #6b7280;
  }

  .point-value {
    font-size: 0.875rem;
    color: #374151;
    white-space: nowrap;
    overflow: hidden;
    text-overflow: ellipsis;
  }

  .route-line {
    width: 2px;
    height: 20px;
    background: #e5e7eb;
    margin-left: 5px;
  }

  /* Modal */
  .modal-overlay {
    position: fixed;
    inset: 0;
    background: rgba(0, 0, 0, 0.5);
    display: flex;
    align-items: center;
    justify-content: center;
    padding: 1rem;
    z-index: 1000;
  }

  .modal {
    background: white;
    border-radius: 16px;
    width: 100%;
    max-width: 480px;
    overflow: hidden;
  }

  .modal-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 1.25rem 1.5rem;
    border-bottom: 1px solid #e5e7eb;
  }

  .modal-header h2 {
    margin: 0;
    font-size: 1.25rem;
  }

  .close-btn {
    background: none;
    border: none;
    padding: 0.25rem;
    cursor: pointer;
    color: #6b7280;
  }

  .close-btn:hover {
    color: #111827;
  }

  .modal-body {
    padding: 1.5rem;
  }

  .form-error {
    background: #fef2f2;
    color: #dc2626;
    padding: 0.75rem 1rem;
    border-radius: 8px;
    margin-bottom: 1rem;
    font-size: 0.875rem;
  }

  .form-group {
    margin-bottom: 1rem;
  }

  .form-group label {
    display: block;
    font-size: 0.875rem;
    font-weight: 500;
    color: #374151;
    margin-bottom: 0.5rem;
  }

  .form-group input,
  .form-group select {
    width: 100%;
    padding: 0.625rem 0.875rem;
    border: 1px solid #d1d5db;
    border-radius: 8px;
    font-size: 0.875rem;
    transition: border-color 0.2s;
    background: white;
  }

  .form-group input:focus,
  .form-group select:focus {
    outline: none;
    border-color: #3b82f6;
    box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.1);
  }

  .form-group select {
    cursor: pointer;
    appearance: none;
    background-image: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='12' height='12' fill='%236b7280' viewBox='0 0 16 16'%3E%3Cpath d='M7.247 11.14L2.451 5.658C1.885 5.013 2.345 4 3.204 4h9.592a1 1 0 0 1 .753 1.659l-4.796 5.48a1 1 0 0 1-1.506 0z'/%3E%3C/svg%3E");
    background-repeat: no-repeat;
    background-position: right 0.75rem center;
    padding-right: 2.5rem;
  }

  .form-footer {
    display: flex;
    gap: 0.75rem;
    justify-content: flex-end;
    margin-top: 1.5rem;
  }

  .btn-secondary {
    padding: 0.625rem 1.25rem;
    background: white;
    color: #374151;
    border: 1px solid #d1d5db;
    border-radius: 8px;
    font-weight: 500;
    cursor: pointer;
  }

  .btn-secondary:hover {
    background: #f9fafb;
  }

  /* Delete Confirmation Modal */
  .confirm-modal {
    text-align: center;
    padding: 2rem;
  }

  .confirm-icon {
    color: #f59e0b;
    margin-bottom: 1rem;
  }

  .confirm-modal h2 {
    margin: 0 0 0.5rem;
    font-size: 1.25rem;
  }

  .confirm-modal p {
    color: #6b7280;
    margin: 0 0 1.5rem;
    font-size: 0.875rem;
  }

  .confirm-actions {
    display: flex;
    gap: 0.75rem;
    justify-content: center;
  }

  .btn-danger {
    padding: 0.625rem 1.25rem;
    background: #dc2626;
    color: white;
    border: none;
    border-radius: 8px;
    font-weight: 500;
    cursor: pointer;
  }

  .btn-danger:hover {
    background: #b91c1c;
  }

  .btn-danger:disabled {
    opacity: 0.6;
    cursor: not-allowed;
  }

  /* Responsive */
  @media (max-width: 640px) {
    .page-header {
      flex-direction: column;
      align-items: stretch;
    }

    .routes-grid {
      grid-template-columns: 1fr;
    }
  }
</style>
