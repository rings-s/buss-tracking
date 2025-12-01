<script lang="ts">
  import { onMount, onDestroy } from 'svelte';
  import { tripService } from '$lib/services/trip';
  import LeafletMap from '$lib/components/tracking/LeafletMap.svelte';
  import type { LiveTracking } from '$lib/types';
  import { auth } from '$lib/stores/auth.svelte';
  import { t } from '$lib/i18n';

  let trips = $state<LiveTracking[]>([]);
  let loading = $state(true);
  let error = $state('');
  let authError = $state(false);
  let refreshInterval: ReturnType<typeof setInterval>;
  let selectedTrip = $state<LiveTracking | null>(null);
  let mapComponent = $state<LeafletMap>();

  // Convert trips to map markers with vehicle icons and start/end markers
  // Using Svelte 5 $derived with function for complex logic
  const mapMarkers = $derived.by(() => {
    const markers: any[] = [];

    for (const trip of trips) {
      // Vehicle marker (current location)
      if (trip.current_location) {
        markers.push({
          id: trip.id,
          lat: trip.current_location.latitude,
          lng: trip.current_location.longitude,
          label: `${trip.bus.name}`,
          color: selectedTrip?.id === trip.id ? '#10b981' : '#3b82f6',
          isVehicle: true,
          isSelected: selectedTrip?.id === trip.id,
          heading: trip.current_location.heading || 0,
          popup: `
            <strong>${trip.bus.name}</strong><br/>
            ${$t('tracking.tripInfo.driver')}: ${trip.driver.full_name}<br/>
            ${trip.route ? `${$t('tracking.tripInfo.route')}: ${trip.route.name}<br/>` : ''}
            ${$t('tracking.tripInfo.boardings')}: ${trip.boarding_count}<br/>
            ${$t('tracking.tripInfo.speed')}: ${trip.current_location.speed?.toFixed(1) || 0} ${$t('tracking.units.kmh')}
          `
        });
      }

      // Start/end markers for all trips with GPS data
      if (trip.locations && trip.locations.length > 0) {
        const sorted = trip.locations
          .slice()
          .sort((a, b) => new Date(a.timestamp).getTime() - new Date(b.timestamp).getTime());

        const isSelected = selectedTrip?.id === trip.id;

        // Start marker (green for selected, light green for others)
        markers.push({
          id: `trip-${trip.id}-start`,
          lat: sorted[0].latitude,
          lng: sorted[0].longitude,
          color: isSelected ? '#10b981' : '#86efac',
          label: $t('tracking.legend.startPoint'),
          popup: `<strong>${trip.bus.name} - ${$t('tracking.popup.tripStart')}</strong><br/>${formatTime(sorted[0].timestamp)}`
        });

        // End marker only if different from start (i.e., at least 2 GPS points)
        if (sorted.length >= 2) {
          const last = sorted[sorted.length - 1];
          // Only add end marker if it's different from start location
          if (last.latitude !== sorted[0].latitude || last.longitude !== sorted[0].longitude) {
            markers.push({
              id: `trip-${trip.id}-end`,
              lat: last.latitude,
              lng: last.longitude,
              color: isSelected ? '#ef4444' : '#fca5a5',
              label: $t('tracking.legend.endPoint'),
              popup: `<strong>${trip.bus.name} - ${$t('tracking.popup.latestGPS')}</strong><br/>${formatTime(last.timestamp)}`
            });
          }
        }
      }
    }

    return markers;
  });

  // Get paths for all trips with selected trip highlighted
  const mapPaths = $derived(
    trips
      .filter(trip => trip.locations && trip.locations.length >= 2)
      .map(trip => {
        const sortedLocations = trip.locations!
          .slice()
          .sort((a, b) => new Date(a.timestamp).getTime() - new Date(b.timestamp).getTime());

        return {
          coordinates: sortedLocations.map(loc => [loc.latitude, loc.longitude] as [number, number]),
          color: selectedTrip?.id === trip.id ? '#10b981' : '#3b82f6',
          weight: selectedTrip?.id === trip.id ? 5 : 3
        };
      })
  );

  // Default center (can be adjusted based on your region)
  const defaultCenter: [number, number] = [24.7136, 46.6753]; // Riyadh, Saudi Arabia

  async function loadLiveTracking() {
    try {
      const newTrips = await tripService.getLiveTracking();
      trips = newTrips;

      error = '';
      authError = false;
    } catch (e: any) {
      const message = e.message || 'Failed to load live tracking data';
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

  onMount(() => {
    loadLiveTracking();
    // Refresh every 10 seconds
    refreshInterval = setInterval(loadLiveTracking, 10000);
  });

  onDestroy(() => {
    if (refreshInterval) {
      clearInterval(refreshInterval);
    }
  });

  // Auto-center map when trips load
  $effect(() => {
    if (mapComponent && trips.length > 0 && !selectedTrip && !loading) {
      const allCoordinates: [number, number][] = [];

      trips.forEach(trip => {
        if (trip.locations && trip.locations.length > 0) {
          trip.locations.forEach(loc => {
            allCoordinates.push([loc.latitude, loc.longitude]);
          });
        } else if (trip.current_location) {
          allCoordinates.push([trip.current_location.latitude, trip.current_location.longitude]);
        }
      });

      if (allCoordinates.length > 0) {
        setTimeout(() => {
          mapComponent?.fitBoundsWithPadding(allCoordinates, 50, 13);
        }, 100);
      }
    }
  });

  function formatTime(dateString: string): string {
    return new Date(dateString).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
  }

  function handleMarkerClick(marker: any) {
    const trip = trips.find(t => t.id === marker.id);
    if (trip) {
      selectTrip(trip);
    }
  }

  function selectTrip(trip: LiveTracking) {
    selectedTrip = trip;

    // Fit bounds to show entire route
    if (trip.locations && trip.locations.length >= 2 && mapComponent) {
      const coordinates = trip.locations.map(loc => [loc.latitude, loc.longitude] as [number, number]);
      mapComponent.fitBoundsWithPadding(coordinates, 50, 15);
    } else if (trip.current_location && mapComponent) {
      mapComponent.flyTo(trip.current_location.latitude, trip.current_location.longitude, 15);
    }
  }
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
        
        <h2 class="text-2xl font-black text-gray-900 mb-3 relative z-10">{$t('tracking.authRequired')}</h2>
        <p class="text-gray-500 mb-8 relative z-10">{$t('tracking.authMessage')}</p>

        <a href="/login" class="btn-primary w-full flex justify-center items-center gap-2 relative z-10 group-hover:scale-[1.02] transition-transform">
          <span>{$t('tracking.signInToContinue')}</span>
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
      <div class="flex-1 relative z-0 min-h-[400px] lg:min-h-0">
        <LeafletMap
          bind:this={mapComponent}
          markers={mapMarkers}
          paths={mapPaths}
          center={defaultCenter}
          zoom={12}
          height="100%"
          onMarkerClick={handleMarkerClick}
        />
        
        <!-- Floating Header on Map -->
        <div class="absolute top-4 left-4 z-[400] glass-card p-4 shadow-lg max-w-xs animate-slide-down">
          <h1 class="text-xl font-black text-gray-900 flex items-center gap-2">
            <span class="relative flex h-3 w-3">
              <span class="animate-ping absolute inline-flex h-full w-full rounded-full bg-red-400 opacity-75"></span>
              <span class="relative inline-flex rounded-full h-3 w-3 bg-red-500"></span>
            </span>
            {$t('tracking.title')}
          </h1>
          <p class="text-xs text-gray-500 mt-1 font-medium">{$t('tracking.autoUpdating')}</p>
        </div>
      </div>

      <!-- Sidebar / Trip List -->
      <div class="w-full lg:w-96 bg-white/80 backdrop-blur-md border-l border-gray-200 flex flex-col z-10 shadow-xl">
        <div class="p-4 border-b border-gray-100 bg-white/50">
          <h2 class="font-bold text-gray-900 flex items-center justify-between">
            <span>{$t('tracking.activeTrips')}</span>
            <span class="bg-brand-100 text-brand-700 px-2 py-0.5 rounded-full text-xs">{trips.length}</span>
          </h2>
        </div>

        <div class="flex-1 overflow-y-auto p-4 space-y-3 custom-scrollbar">
          {#if trips.length === 0}
            <div class="text-center py-12 text-gray-400">
              <div class="w-16 h-16 mx-auto rounded-full bg-gray-50 flex items-center justify-center mb-3">
                <svg xmlns="http://www.w3.org/2000/svg" class="h-8 w-8" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 20l-5.447-2.724A1 1 0 013 16.382V5.618a1 1 0 011.447-.894L9 7m0 13l6-3m-6 3V7m6 10l4.553 2.276A1 1 0 0021 18.382V7.618a1 1 0 00-.553-.894L15 4m0 13V4" />
                </svg>
              </div>
              <p class="text-sm font-medium">{$t('tracking.noActiveTrips')}</p>
            </div>
          {:else}
            {#each trips as trip}
              <button
                class="w-full text-left p-4 rounded-xl border transition-all duration-200 group relative overflow-hidden
                  {selectedTrip?.id === trip.id
                    ? 'bg-brand-50 border-brand-200 shadow-sm'
                    : 'bg-white border-gray-100 hover:border-brand-200 hover:shadow-md'}"
                onclick={() => selectTrip(trip)}
              >
                <div class="flex justify-between items-start mb-2">
                  <div>
                    <h3 class="font-bold text-gray-900 text-sm">{$t('tracking.tripCard.tripId', { id: trip.id })}</h3>
                    <p class="text-xs text-gray-500 font-medium">{trip.bus.name}</p>
                  </div>
                  <span class="flex h-2 w-2 rounded-full bg-green-500"></span>
                </div>

                <div class="space-y-1.5">
                  <div class="flex items-center gap-2 text-xs text-gray-600">
                    <svg xmlns="http://www.w3.org/2000/svg" class="h-3.5 w-3.5 text-gray-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z" />
                    </svg>
                    <span class="truncate">{trip.driver.full_name}</span>
                  </div>
                  {#if trip.route}
                    <div class="flex items-center gap-2 text-xs text-gray-600">
                      <svg xmlns="http://www.w3.org/2000/svg" class="h-3.5 w-3.5 text-gray-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 20l-5.447-2.724A1 1 0 013 16.382V5.618a1 1 0 011.447-.894L9 7m0 13l6-3m-6 3V7m6 10l4.553 2.276A1 1 0 0021 18.382V7.618a1 1 0 00-.553-.894L15 4m0 13V4" />
                      </svg>
                      <span class="truncate">{trip.route.name}</span>
                    </div>
                  {/if}
                  <div class="flex items-center gap-2 text-xs">
                    <svg xmlns="http://www.w3.org/2000/svg" class="h-3.5 w-3.5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M17.657 16.657L13.414 20.9a1.998 1.998 0 01-2.827 0l-4.244-4.243a8 8 0 1111.314 0z" />
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 11a3 3 0 11-6 0 3 3 0 016 0z" />
                    </svg>
                    {#if trip.locations && trip.locations.length > 0}
                      <span class="text-green-600 font-medium">{trip.locations.length} {$t('tracking.tripCard.gpsPoints')}</span>
                    {:else}
                      <span class="text-yellow-600 font-medium">{$t('tracking.tripCard.noGPSData')}</span>
                    {/if}
                  </div>
                </div>
              </button>
            {/each}
          {/if}
        </div>

        {#if selectedTrip}
          <div class="p-4 bg-brand-50 border-t border-brand-100 animate-slide-up">
            <div class="flex justify-between items-start mb-3">
              <h3 class="font-bold text-brand-900 text-sm">{$t('tracking.details.title')}</h3>
              <button
                class="text-brand-600 hover:text-brand-800"
                onclick={() => selectedTrip = null}
                aria-label={$t('tracking.details.closeDetails')}
              >
                <svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4" viewBox="0 0 20 20" fill="currentColor">
                  <path fill-rule="evenodd" d="M4.293 4.293a1 1 0 011.414 0L10 8.586l4.293-4.293a1 1 0 111.414 1.414L11.414 10l4.293 4.293a1 1 0 01-1.414 1.414L10 11.414l-4.293 4.293a1 1 0 01-1.414-1.414L8.586 10 4.293 5.707a1 1 0 010-1.414z" clip-rule="evenodd" />
                </svg>
              </button>
            </div>
            <div class="grid grid-cols-2 gap-2 text-xs">
              <div class="bg-white p-2 rounded border border-brand-100">
                <p class="text-gray-500 uppercase text-[10px] font-bold">{$t('tracking.details.speed')}</p>
                <p class="font-mono font-bold text-gray-900">{selectedTrip.current_location?.speed?.toFixed(1) || 0} km/h</p>
              </div>
              <div class="bg-white p-2 rounded border border-brand-100">
                <p class="text-gray-500 uppercase text-[10px] font-bold">{$t('tracking.details.boardings')}</p>
                <p class="font-mono font-bold text-gray-900">{selectedTrip.boarding_count}</p>
              </div>
              <div class="col-span-2 bg-white p-2 rounded border border-brand-100">
                <p class="text-gray-500 uppercase text-[10px] font-bold">{$t('tracking.details.lastUpdate')}</p>
                <p class="font-mono text-gray-900">{selectedTrip.current_location ? formatTime(selectedTrip.current_location.timestamp) : 'N/A'}</p>
              </div>
              {#if selectedTrip.locations && selectedTrip.locations.length > 0}
                <div class="bg-white p-2 rounded border border-brand-100">
                  <p class="text-gray-500 uppercase text-[10px] font-bold">{$t('tracking.details.gpsPoints')}</p>
                  <p class="font-mono font-bold text-gray-900">{selectedTrip.locations.length}</p>
                </div>
                <div class="bg-white p-2 rounded border border-brand-100">
                  <p class="text-gray-500 uppercase text-[10px] font-bold">{$t('tracking.details.routeStatus')}</p>
                  <p class="text-[10px] text-gray-900">
                    {#if selectedTrip.locations.length === 1}
                      <span class="text-yellow-600">{$t('tracking.details.startOnly')}</span>
                    {:else}
                      <span class="text-green-600">{$t('tracking.details.moving', { points: selectedTrip.locations.length })}</span>
                    {/if}
                  </p>
                </div>
              {:else}
                <div class="col-span-2 bg-yellow-50 border border-yellow-200 rounded p-2">
                  <p class="text-yellow-700 text-[10px]">⚠️ {$t('tracking.details.noGPSWarning')}</p>
                </div>
              {/if}
            </div>
          </div>
        {/if}
      </div>
    </div>
  {/if}
</div>
