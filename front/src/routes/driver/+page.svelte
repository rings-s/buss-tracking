<script lang="ts">
  import { onMount } from 'svelte';
  import { goto } from '$app/navigation';
  import { tripService } from '$lib/services/trip';
  import { auth } from '$lib/stores/auth.svelte';
  import type { Trip } from '$lib/types';

  let trips = $state<Trip[]>([]);
  let activeTrip = $state<Trip | null>(null);
  let loading = $state(true);
  let error = $state('');
  let starting = $state(false);
  let ending = $state(false);

  onMount(async () => {
    if (!auth.isAuthenticated || auth.user?.role !== 'driver') {
      goto('/auth/login');
      return;
    }
    await loadTrips();
  });

  async function loadTrips() {
    try {
      const allTrips = await tripService.list();
      trips = allTrips;
      activeTrip = allTrips.find(t => t.is_active) || null;
    } catch (e: any) {
      error = e.message || 'Failed to load trips';
    } finally {
      loading = false;
    }
  }

  async function startTrip() {
    starting = true;
    error = '';
    try {
      // Driver starts trip - backend auto-assigns bus and driver
      const baseUrl = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000';
      const response = await fetch(`${baseUrl}/api/trips/start/`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${localStorage.getItem('access_token')}`
        },
        body: JSON.stringify({})
      });

      if (!response.ok) {
        const data = await response.json();
        throw new Error(data.error || 'Failed to start trip');
      }

      await loadTrips();
    } catch (e: any) {
      error = e.message || 'Failed to start trip';
    } finally {
      starting = false;
    }
  }

  async function endTrip() {
    if (!activeTrip) return;
    ending = true;
    error = '';
    try {
      await tripService.end(activeTrip.id);
      await loadTrips();
    } catch (e: any) {
      error = e.message || 'Failed to end trip';
    } finally {
      ending = false;
    }
  }

  function formatTime(dateString: string): string {
    return new Date(dateString).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
  }

  function formatDate(dateString: string): string {
    return new Date(dateString).toLocaleDateString([], { month: 'short', day: 'numeric' });
  }

  function formatDuration(minutes: number | null | undefined): string {
    if (!minutes) return '-';
    const hrs = Math.floor(minutes / 60);
    const mins = minutes % 60;
    return hrs > 0 ? `${hrs}h ${mins}m` : `${mins}m`;
  }
</script>

<div class="min-h-screen bg-gray-50 relative overflow-hidden">
  <!-- Background Elements -->
  <div class="hero-dots fixed inset-0 opacity-30 pointer-events-none"></div>
  <div class="fixed top-0 left-0 w-full h-96 bg-gradient-to-b from-brand-50/80 to-transparent pointer-events-none"></div>

  <div class="relative z-10 p-4 md:p-8 max-w-4xl mx-auto">
    <!-- Header -->
    <div class="mb-8">
      <h1 class="text-3xl font-black text-gray-900">My Trips</h1>
      <p class="text-gray-500 mt-1">Manage your bus trips and check-ins</p>
    </div>

    {#if loading}
      <div class="flex items-center justify-center py-12">
        <div class="animate-spin rounded-full h-12 w-12 border-b-2 border-brand-500"></div>
      </div>
    {:else}
      {#if error}
        <div class="mb-6 p-4 rounded-xl bg-red-50 border border-red-200 text-red-600 font-medium">
          {error}
        </div>
      {/if}

      <!-- Active Trip Card -->
      <div class="mb-8">
        {#if activeTrip}
          <div class="glass-card p-6 border-l-4 border-green-500">
            <div class="flex items-start justify-between mb-4">
              <div>
                <div class="flex items-center gap-2 mb-2">
                  <span class="relative flex h-3 w-3">
                    <span class="animate-ping absolute inline-flex h-full w-full rounded-full bg-green-400 opacity-75"></span>
                    <span class="relative inline-flex rounded-full h-3 w-3 bg-green-500"></span>
                  </span>
                  <span class="text-sm font-bold text-green-600 uppercase tracking-wider">Active Trip</span>
                </div>
                <h2 class="text-2xl font-black text-gray-900">Trip #{activeTrip.id}</h2>
              </div>
              <button
                onclick={endTrip}
                disabled={ending}
                class="px-4 py-2 bg-red-500 text-white rounded-lg font-bold hover:bg-red-600 disabled:opacity-50 transition-colors"
              >
                {ending ? 'Ending...' : 'End Trip'}
              </button>
            </div>

            <div class="grid grid-cols-2 md:grid-cols-4 gap-4 mb-4">
              <div class="bg-white/50 rounded-lg p-3">
                <p class="text-xs text-gray-500 font-bold uppercase">Bus</p>
                <p class="font-bold text-gray-900">{activeTrip.bus.name}</p>
              </div>
              <div class="bg-white/50 rounded-lg p-3">
                <p class="text-xs text-gray-500 font-bold uppercase">Started</p>
                <p class="font-mono text-gray-900">{formatTime(activeTrip.start_time)}</p>
              </div>
              <div class="bg-white/50 rounded-lg p-3">
                <p class="text-xs text-gray-500 font-bold uppercase">Duration</p>
                <p class="font-mono text-gray-900">{formatDuration(activeTrip.duration)}</p>
              </div>
              <div class="bg-white/50 rounded-lg p-3">
                <p class="text-xs text-gray-500 font-bold uppercase">Boardings</p>
                <p class="font-bold text-gray-900">{activeTrip.boarding_count || 0}</p>
              </div>
            </div>

            {#if activeTrip.route}
              <div class="bg-white/50 rounded-lg p-3">
                <p class="text-xs text-gray-500 font-bold uppercase">Route</p>
                <p class="font-bold text-gray-900">{activeTrip.route.name}</p>
                <p class="text-sm text-gray-600">{activeTrip.route.start_point} → {activeTrip.route.end_point}</p>
              </div>
            {/if}

            <div class="mt-4 flex gap-3">
              <a href="/checkin" class="flex-1 btn-primary text-center">
                Open Check-in
              </a>
              <a href="/live-tracking" class="flex-1 btn-secondary text-center">
                View on Map
              </a>
            </div>
          </div>
        {:else}
          <div class="glass-card p-8 text-center">
            <div class="w-16 h-16 mx-auto rounded-full bg-gray-100 flex items-center justify-center text-gray-400 mb-4">
              <svg xmlns="http://www.w3.org/2000/svg" class="h-8 w-8" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8 7h12m0 0l-4-4m4 4l-4 4m0 6H4m0 0l4 4m-4-4l4-4" />
              </svg>
            </div>
            <h2 class="text-xl font-bold text-gray-900 mb-2">No Active Trip</h2>
            <p class="text-gray-500 mb-6">Start a trip to begin tracking and accepting check-ins</p>
            <button
              onclick={startTrip}
              disabled={starting}
              class="btn-primary px-8 py-3 text-lg"
            >
              {starting ? 'Starting...' : 'Start New Trip'}
            </button>
          </div>
        {/if}
      </div>

      <!-- Trip History -->
      <div>
        <h2 class="text-xl font-bold text-gray-900 mb-4">Trip History</h2>

        {#if trips.filter(t => !t.is_active).length === 0}
          <div class="glass-card p-6 text-center text-gray-500">
            No completed trips yet
          </div>
        {:else}
          <div class="space-y-3">
            {#each trips.filter(t => !t.is_active) as trip}
              <div class="glass-card p-4 hover:shadow-md transition-shadow">
                <div class="flex items-center justify-between">
                  <div>
                    <div class="flex items-center gap-3">
                      <span class="font-bold text-gray-900">Trip #{trip.id}</span>
                      <span class="text-xs px-2 py-0.5 rounded-full bg-gray-100 text-gray-600 font-bold">
                        {formatDate(trip.start_time)}
                      </span>
                    </div>
                    <p class="text-sm text-gray-500 mt-1">
                      {trip.bus.name}
                      {#if trip.route} • {trip.route.name}{/if}
                    </p>
                  </div>
                  <div class="text-right">
                    <p class="font-mono text-sm text-gray-600">
                      {formatTime(trip.start_time)} - {trip.end_time ? formatTime(trip.end_time) : '-'}
                    </p>
                    <p class="text-sm text-gray-500">
                      {trip.boarding_count || 0} boardings • {formatDuration(trip.duration)}
                    </p>
                  </div>
                </div>
              </div>
            {/each}
          </div>
        {/if}
      </div>
    {/if}
  </div>
</div>

<style>
  .glass-card {
    background: rgba(255, 255, 255, 0.9);
    backdrop-filter: blur(12px);
    border: 1px solid rgba(229, 231, 235, 0.8);
    border-radius: 1rem;
    box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.05);
  }

  .btn-primary {
    display: inline-flex;
    align-items: center;
    justify-content: center;
    padding: 0.75rem 1.5rem;
    background: linear-gradient(135deg, #3b82f6 0%, #2563eb 100%);
    color: white;
    border: none;
    border-radius: 0.75rem;
    font-weight: 600;
    cursor: pointer;
    transition: all 0.2s;
  }

  .btn-primary:hover:not(:disabled) {
    transform: translateY(-1px);
    box-shadow: 0 4px 12px rgba(59, 130, 246, 0.4);
  }

  .btn-primary:disabled {
    opacity: 0.5;
    cursor: not-allowed;
  }

  .btn-secondary {
    display: inline-flex;
    align-items: center;
    justify-content: center;
    padding: 0.75rem 1.5rem;
    background: white;
    color: #374151;
    border: 1px solid #e5e7eb;
    border-radius: 0.75rem;
    font-weight: 600;
    cursor: pointer;
    transition: all 0.2s;
  }

  .btn-secondary:hover {
    background: #f9fafb;
    border-color: #d1d5db;
  }

  .hero-dots {
    background-image: radial-gradient(#d1d5db 1px, transparent 1px);
    background-size: 20px 20px;
  }
</style>
