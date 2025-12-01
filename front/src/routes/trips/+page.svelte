<script lang="ts">
  import { onMount, onDestroy } from 'svelte';
  import { tripService } from '$lib/services/trip';
  import { auth } from '$lib/stores/auth.svelte';
  import LeafletMap from '$lib/components/tracking/LeafletMap.svelte';
  import type { LiveTracking } from '$lib/types';
  import { t } from '$lib/i18n';

  // State
  let trips = $state<LiveTracking[]>([]);
  let loading = $state(true);
  let error = $state('');
  let authError = $state(false);
  let selectedTrip = $state<LiveTracking | null>(null);
  let showModal = $state(false);
  let pollingInterval: ReturnType<typeof setInterval> | null = null;
  let lastUpdate = $state<Date | null>(null);

  // Filters
  let filterStatus = $state<'all' | 'active' | 'completed'>('all');
  let searchQuery = $state('');

  // Computed
  const filteredTrips = $derived.by(() => {
    let result = trips;

    // Status filter
    if (filterStatus === 'active') {
      result = result.filter(t => t.is_active);
    } else if (filterStatus === 'completed') {
      result = result.filter(t => !t.is_active);
    }

    // Search filter
    if (searchQuery.trim()) {
      const query = searchQuery.toLowerCase();
      result = result.filter(t =>
        t.bus.name.toLowerCase().includes(query) ||
        t.bus.plate_number.toLowerCase().includes(query) ||
        t.driver.full_name.toLowerCase().includes(query) ||
        t.route?.name.toLowerCase().includes(query)
      );
    }

    return result;
  });

  const stats = $derived.by(() => ({
    total: trips.length,
    active: trips.filter(t => t.is_active).length,
    completed: trips.filter(t => !t.is_active).length,
    totalBoardings: trips.reduce((sum, t) => sum + (t.boarding_count || 0), 0)
  }));

  // Map markers for active trips with GPS data
  const mapMarkers = $derived.by(() =>
    filteredTrips
      .filter(trip => trip.is_active && trip.current_location)
      .map(trip => ({
        id: trip.id,
        lat: trip.current_location!.latitude,
        lng: trip.current_location!.longitude,
        label: trip.bus.name,
        color: '#3b82f6',
        popup: `
          <strong>${trip.bus.name}</strong><br/>
          Driver: ${trip.driver.full_name}<br/>
          ${trip.route ? `Route: ${trip.route.name}` : 'No route assigned'}<br/>
          ${trip.current_location?.speed ? `Speed: ${Math.round(trip.current_location.speed * 3.6)} km/h<br/>` : ''}
          <small>Updated: ${new Date(trip.current_location!.timestamp).toLocaleTimeString()}</small>
        `
      }))
  );

  const defaultCenter: [number, number] = [24.7136, 46.6753];

  async function loadTrips() {
    try {
      trips = await tripService.getLiveTracking();
      lastUpdate = new Date();
      error = '';
      authError = false;
    } catch (e: any) {
      const message = e.message || 'Failed to load trips';
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

  // Start polling for real-time GPS updates
  function startPolling() {
    // Initial load
    loadTrips();

    // Poll every 5 seconds for GPS updates
    pollingInterval = setInterval(() => {
      loadTrips();
    }, 5000);
  }

  // Stop polling
  function stopPolling() {
    if (pollingInterval) {
      clearInterval(pollingInterval);
      pollingInterval = null;
    }
  }

  function openTripDetails(trip: LiveTracking) {
    selectedTrip = trip;
    showModal = true;
  }

  function closeModal() {
    showModal = false;
    selectedTrip = null;
  }

  function formatDateTime(dateString: string): string {
    return new Date(dateString).toLocaleString();
  }

  function formatDuration(minutes: number | null | undefined): string {
    if (!minutes) return '-';
    const hours = Math.floor(minutes / 60);
    const mins = minutes % 60;
    return hours > 0 ? `${hours}h ${mins}m` : `${mins}m`;
  }

  function handleMarkerClick(marker: any) {
    const trip = trips.find(t => t.id === marker.id);
    if (trip) openTripDetails(trip);
  }

  // Lifecycle: Start polling on mount, cleanup on destroy
  onMount(() => {
    startPolling();

    // Pause polling when tab is hidden to save resources
    const handleVisibilityChange = () => {
      if (document.hidden) {
        stopPolling();
      } else {
        startPolling();
      }
    };

    document.addEventListener('visibilitychange', handleVisibilityChange);

    return () => {
      document.removeEventListener('visibilitychange', handleVisibilityChange);
    };
  });

  onDestroy(() => {
    stopPolling();
  });
</script>

<div class="page">
  <header class="page-header">
    <div class="header-content">
      <h1>{$t('trips.title')}</h1>
      <p class="subtitle">{$t('trips.subtitle')}</p>
    </div>
  </header>

  {#if loading}
    <div class="loading-container">
      <div class="spinner"></div>
      <p>{$t('trips.loadingTrips')}</p>
    </div>
  {:else if authError}
    <div class="auth-message">
      <div class="auth-icon">
        <svg xmlns="http://www.w3.org/2000/svg" width="48" height="48" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
          <rect x="3" y="11" width="18" height="11" rx="2" ry="2"></rect>
          <path d="M7 11V7a5 5 0 0 1 10 0v4"></path>
        </svg>
      </div>
      <h2>{$t('trips.signInRequired')}</h2>
      <p>{$t('trips.signInMessage')}</p>
      <a href="/login" class="login-link">{$t('trips.signIn')}</a>
    </div>
  {:else if error}
    <div class="error-container">
      <p class="error">{$t('trips.error')}: {error}</p>
      <button onclick={loadTrips} class="retry-btn">{$t('trips.tryAgain')}</button>
    </div>
  {:else}
    <!-- Stats Cards -->
    <div class="stats-grid">
      <div class="stat-card">
        <span class="stat-value">{stats.total}</span>
        <span class="stat-label">{$t('trips.stats.totalTrips')}</span>
      </div>
      <div class="stat-card active">
        <span class="stat-value">{stats.active}</span>
        <span class="stat-label">{$t('trips.stats.active')}</span>
      </div>
      <div class="stat-card completed">
        <span class="stat-value">{stats.completed}</span>
        <span class="stat-label">{$t('trips.stats.completed')}</span>
      </div>
      <div class="stat-card boardings">
        <span class="stat-value">{stats.totalBoardings}</span>
        <span class="stat-label">{$t('trips.stats.boardings')}</span>
      </div>
    </div>

    <!-- Map Section -->
    {#if stats.active > 0}
      <section class="map-section">
        <div class="map-header">
          <h2>{$t('trips.map.title')}</h2>
          {#if lastUpdate}
            <span class="last-update">
              <svg xmlns="http://www.w3.org/2000/svg" width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <circle cx="12" cy="12" r="10"></circle>
                <polyline points="12 6 12 12 16 14"></polyline>
              </svg>
              {$t('trips.map.updated')}: {lastUpdate.toLocaleTimeString()}
            </span>
          {/if}
        </div>

        {#if mapMarkers.length > 0}
          <div class="map-container">
            <LeafletMap
              markers={mapMarkers}
              center={defaultCenter}
              zoom={11}
              height="100%"
              onMarkerClick={handleMarkerClick}
            />
          </div>
        {:else}
          <div class="map-placeholder">
            <svg xmlns="http://www.w3.org/2000/svg" width="48" height="48" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <path d="M21 10c0 7-9 13-9 13s-9-6-9-13a9 9 0 0 1 18 0z"></path>
              <circle cx="12" cy="10" r="3"></circle>
            </svg>
            <p>{$t('trips.map.noGPSData')}</p>
            <small>{$t('trips.map.gpsWillAppear')}</small>
          </div>
        {/if}
      </section>
    {/if}

    <!-- Filters -->
    <div class="filters">
      <div class="search-box">
        <svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
          <circle cx="11" cy="11" r="8"></circle>
          <path d="m21 21-4.3-4.3"></path>
        </svg>
        <input
          type="text"
          placeholder={$t('trips.filters.searchPlaceholder')}
          bind:value={searchQuery}
        />
      </div>
      <div class="filter-tabs">
        <button
          class:active={filterStatus === 'all'}
          onclick={() => filterStatus = 'all'}
        >{$t('trips.filters.all')} ({trips.length})</button>
        <button
          class:active={filterStatus === 'active'}
          onclick={() => filterStatus = 'active'}
        >{$t('trips.filters.active')} ({stats.active})</button>
        <button
          class:active={filterStatus === 'completed'}
          onclick={() => filterStatus = 'completed'}
        >{$t('trips.filters.completed')} ({stats.completed})</button>
      </div>
    </div>

    <!-- Trips Grid -->
    {#if filteredTrips.length === 0}
      <div class="empty-state">
        <svg xmlns="http://www.w3.org/2000/svg" width="48" height="48" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5">
          <path d="M8 6v6M8 16v.01M12 6v6m0 4v.01M16 6v6m0 4v.01"></path>
        </svg>
        <p>{$t('trips.noTripsFound')}</p>
        {#if searchQuery || filterStatus !== 'all'}
          <button onclick={() => { searchQuery = ''; filterStatus = 'all'; }}>{$t('trips.clearFilters')}</button>
        {/if}
      </div>
    {:else}
      <div class="trips-grid">
        {#each filteredTrips as trip (trip.id)}
          <button class="trip-card" class:active={trip.is_active} onclick={() => openTripDetails(trip)}>
            <div class="trip-header">
              <h3>{$t('trips.card.tripId', { id: trip.id })}</h3>
              <span class="status" class:active={trip.is_active}>
                {trip.is_active ? $t('trips.card.active') : $t('trips.card.completed')}
              </span>
            </div>

            <div class="trip-body">
              <div class="info-row">
                <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                  <path d="M8 6v6M8 18h.01M12 6v6m0 6h.01M16 6v6m0 6h.01"></path>
                </svg>
                <span>{trip.bus.name} ({trip.bus.plate_number})</span>
              </div>

              <div class="info-row">
                <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                  <path d="M19 21v-2a4 4 0 0 0-4-4H9a4 4 0 0 0-4 4v2"></path>
                  <circle cx="12" cy="7" r="4"></circle>
                </svg>
                <span>{trip.driver.full_name}</span>
              </div>

              {#if trip.route}
                <div class="info-row">
                  <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                    <circle cx="12" cy="12" r="10"></circle>
                    <polyline points="12 6 12 12 16 14"></polyline>
                  </svg>
                  <span>{trip.route.name}</span>
                </div>
              {/if}

              <div class="info-row">
                <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                  <rect x="3" y="4" width="18" height="18" rx="2" ry="2"></rect>
                  <line x1="16" y1="2" x2="16" y2="6"></line>
                  <line x1="8" y1="2" x2="8" y2="6"></line>
                  <line x1="3" y1="10" x2="21" y2="10"></line>
                </svg>
                <span>{formatDateTime(trip.start_time)}</span>
              </div>
            </div>

            <div class="trip-footer">
              <div class="metric">
                <span class="metric-value">{trip.boarding_count || 0}</span>
                <span class="metric-label">{$t('trips.card.boardings')}</span>
              </div>
              {#if trip.duration}
                <div class="metric">
                  <span class="metric-value">{formatDuration(trip.duration)}</span>
                  <span class="metric-label">{$t('trips.card.duration')}</span>
                </div>
              {/if}
            </div>
          </button>
        {/each}
      </div>
    {/if}
  {/if}
</div>

<!-- Trip Details Modal -->
{#if showModal && selectedTrip}
  <div class="modal-overlay" onclick={closeModal} onkeydown={(e) => e.key === 'Escape' && closeModal()} role="button" tabindex="0">
    <div class="modal" onclick={(e) => e.stopPropagation()}>
      <header class="modal-header">
        <h2>{$t('trips.modal.title', { id: selectedTrip.id })}</h2>
        <button class="close-btn" onclick={closeModal} aria-label={$t('trips.modal.closeModal')}>
          <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <line x1="18" y1="6" x2="6" y2="18"></line>
            <line x1="6" y1="6" x2="18" y2="18"></line>
          </svg>
        </button>
      </header>

      <div class="modal-body">
        <div class="detail-section">
          <h3>{$t('trips.modal.tripInformation')}</h3>
          <dl class="detail-list">
            <dt>{$t('trips.modal.status')}</dt>
            <dd>
              <span class="status-badge" class:active={selectedTrip.is_active}>
                {selectedTrip.is_active ? $t('trips.card.active') : $t('trips.card.completed')}
              </span>
            </dd>
            <dt>{$t('trips.modal.startTime')}</dt>
            <dd>{formatDateTime(selectedTrip.start_time)}</dd>
            {#if selectedTrip.end_time}
              <dt>{$t('trips.modal.endTime')}</dt>
              <dd>{formatDateTime(selectedTrip.end_time)}</dd>
            {/if}
            {#if selectedTrip.duration}
              <dt>{$t('trips.modal.duration')}</dt>
              <dd>{formatDuration(selectedTrip.duration)}</dd>
            {/if}
            <dt>{$t('trips.modal.boardings')}</dt>
            <dd>{selectedTrip.boarding_count || 0}</dd>
          </dl>
        </div>

        <div class="detail-section">
          <h3>{$t('trips.modal.bus')}</h3>
          <dl class="detail-list">
            <dt>{$t('trips.modal.name')}</dt>
            <dd>{selectedTrip.bus.name}</dd>
            <dt>{$t('trips.modal.plate')}</dt>
            <dd>{selectedTrip.bus.plate_number}</dd>
            <dt>{$t('trips.modal.capacity')}</dt>
            <dd>{selectedTrip.bus.capacity}</dd>
          </dl>
        </div>

        <div class="detail-section">
          <h3>{$t('trips.modal.driver')}</h3>
          <dl class="detail-list">
            <dt>{$t('trips.modal.name')}</dt>
            <dd>{selectedTrip.driver.full_name}</dd>
            <dt>{$t('trips.modal.email')}</dt>
            <dd>{selectedTrip.driver.email}</dd>
            <dt>{$t('trips.modal.phone')}</dt>
            <dd>{selectedTrip.driver.phone_number || '-'}</dd>
          </dl>
        </div>

        {#if selectedTrip.route}
          <div class="detail-section">
            <h3>{$t('trips.modal.route')}</h3>
            <dl class="detail-list">
              <dt>{$t('trips.modal.name')}</dt>
              <dd>{selectedTrip.route.name}</dd>
              <dt>{$t('trips.modal.from')}</dt>
              <dd>{selectedTrip.route.start_point}</dd>
              <dt>{$t('trips.modal.to')}</dt>
              <dd>{selectedTrip.route.end_point}</dd>
            </dl>
          </div>
        {/if}
      </div>

      <footer class="modal-footer">
        <a href="/trips/{selectedTrip.id}" class="btn-primary">{$t('trips.modal.viewFullDetails')}</a>
        <button class="btn-secondary" onclick={closeModal}>{$t('trips.modal.close')}</button>
      </footer>
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
    margin-bottom: 2rem;
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

  /* Stats Grid */
  .stats-grid {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(140px, 1fr));
    gap: 1rem;
    margin-bottom: 2rem;
  }

  .stat-card {
    background: white;
    border: 1px solid #e5e7eb;
    border-radius: 12px;
    padding: 1.25rem;
    text-align: center;
  }

  .stat-value {
    display: block;
    font-size: 2rem;
    font-weight: 700;
    color: #111827;
  }

  .stat-label {
    font-size: 0.875rem;
    color: #6b7280;
  }

  .stat-card.active .stat-value { color: #10b981; }
  .stat-card.completed .stat-value { color: #6b7280; }
  .stat-card.boardings .stat-value { color: #3b82f6; }

  /* Map Section */
  .map-section {
    margin-bottom: 2rem;
  }

  .map-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 1rem;
    flex-wrap: wrap;
    gap: 0.5rem;
  }

  .map-header h2 {
    font-size: 1.25rem;
    margin: 0;
    color: #374151;
  }

  .last-update {
    display: flex;
    align-items: center;
    gap: 0.25rem;
    font-size: 0.875rem;
    color: #6b7280;
  }

  .last-update svg {
    color: #10b981;
  }

  .map-container {
    border-radius: 12px;
    overflow: hidden;
    border: 1px solid #e5e7eb;
    /* Responsive height using viewport units */
    height: 50vh;
    min-height: 400px;
    max-height: 600px;
  }

  .map-placeholder {
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    padding: 3rem 2rem;
    background: #f9fafb;
    border-radius: 12px;
    border: 2px dashed #e5e7eb;
    text-align: center;
    min-height: 300px;
  }

  .map-placeholder svg {
    color: #9ca3af;
    margin-bottom: 1rem;
  }

  .map-placeholder p {
    margin: 0.5rem 0;
    color: #374151;
    font-weight: 500;
  }

  .map-placeholder small {
    color: #6b7280;
  }

  /* Filters */
  .filters {
    display: flex;
    flex-wrap: wrap;
    gap: 1rem;
    margin-bottom: 1.5rem;
    align-items: center;
  }

  .search-box {
    display: flex;
    align-items: center;
    gap: 0.5rem;
    flex: 1;
    min-width: 200px;
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

  .filter-tabs {
    display: flex;
    gap: 0.25rem;
    background: #f3f4f6;
    padding: 0.25rem;
    border-radius: 8px;
  }

  .filter-tabs button {
    padding: 0.5rem 1rem;
    border: none;
    background: transparent;
    border-radius: 6px;
    font-size: 0.875rem;
    cursor: pointer;
    color: #6b7280;
    transition: all 0.2s;
  }

  .filter-tabs button.active {
    background: white;
    color: #111827;
    box-shadow: 0 1px 2px rgba(0, 0, 0, 0.05);
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
    background: #f3f4f6;
    border: 1px solid #d1d5db;
    border-radius: 6px;
    cursor: pointer;
  }

  /* Trips Grid */
  .trips-grid {
    display: grid;
    grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
    gap: 1rem;
  }

  .trip-card {
    width: 100%;
    text-align: left;
    background: white;
    border: 1px solid #e5e7eb;
    border-radius: 12px;
    padding: 1.25rem;
    cursor: pointer;
    transition: all 0.2s;
  }

  .trip-card:hover {
    border-color: #3b82f6;
    box-shadow: 0 4px 12px rgba(59, 130, 246, 0.1);
  }

  .trip-card.active {
    border-left: 4px solid #10b981;
  }

  .trip-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 1rem;
  }

  .trip-header h3 {
    margin: 0;
    font-size: 1.125rem;
    font-weight: 600;
  }

  .status {
    padding: 0.25rem 0.75rem;
    border-radius: 9999px;
    font-size: 0.75rem;
    font-weight: 500;
    background: #f3f4f6;
    color: #6b7280;
  }

  .status.active {
    background: #d1fae5;
    color: #065f46;
  }

  .trip-body {
    display: flex;
    flex-direction: column;
    gap: 0.5rem;
    margin-bottom: 1rem;
  }

  .info-row {
    display: flex;
    align-items: center;
    gap: 0.5rem;
    font-size: 0.875rem;
    color: #4b5563;
  }

  .info-row svg {
    color: #9ca3af;
    flex-shrink: 0;
  }

  .trip-footer {
    display: flex;
    gap: 1.5rem;
    padding-top: 1rem;
    border-top: 1px solid #f3f4f6;
  }

  .metric {
    display: flex;
    flex-direction: column;
  }

  .metric-value {
    font-size: 1.25rem;
    font-weight: 600;
    color: #111827;
  }

  .metric-label {
    font-size: 0.75rem;
    color: #6b7280;
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
    max-width: 600px;
    max-height: 90vh;
    overflow: hidden;
    display: flex;
    flex-direction: column;
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
    overflow-y: auto;
  }

  .detail-section {
    margin-bottom: 1.5rem;
  }

  .detail-section:last-child {
    margin-bottom: 0;
  }

  .detail-section h3 {
    margin: 0 0 0.75rem;
    font-size: 0.875rem;
    font-weight: 600;
    color: #6b7280;
    text-transform: uppercase;
    letter-spacing: 0.05em;
  }

  .detail-list {
    display: grid;
    grid-template-columns: 100px 1fr;
    gap: 0.5rem;
    margin: 0;
  }

  .detail-list dt {
    color: #6b7280;
    font-size: 0.875rem;
  }

  .detail-list dd {
    margin: 0;
    font-size: 0.875rem;
    color: #111827;
  }

  .status-badge {
    display: inline-block;
    padding: 0.25rem 0.5rem;
    border-radius: 4px;
    font-size: 0.75rem;
    font-weight: 500;
    background: #f3f4f6;
    color: #6b7280;
  }

  .status-badge.active {
    background: #d1fae5;
    color: #065f46;
  }

  .modal-footer {
    display: flex;
    gap: 0.75rem;
    padding: 1.25rem 1.5rem;
    border-top: 1px solid #e5e7eb;
    justify-content: flex-end;
  }

  .btn-primary {
    padding: 0.625rem 1.25rem;
    background: #3b82f6;
    color: white;
    border: none;
    border-radius: 8px;
    font-weight: 500;
    text-decoration: none;
    cursor: pointer;
  }

  .btn-primary:hover {
    background: #2563eb;
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

  /* Responsive */
  /* Tablet and below (768px) */
  @media (max-width: 768px) {
    .map-container {
      height: 45vh;
      min-height: 350px;
      max-height: 500px;
    }

    .map-header {
      flex-direction: column;
      align-items: flex-start;
    }

    .stats-grid {
      grid-template-columns: repeat(2, 1fr);
    }
  }

  /* Mobile (640px) */
  @media (max-width: 640px) {
    .map-container {
      height: 40vh;
      min-height: 300px;
      max-height: 400px;
    }

    .filters {
      flex-direction: column;
    }

    .search-box {
      width: 100%;
    }

    .filter-tabs {
      width: 100%;
      justify-content: center;
    }

    .trips-grid {
      grid-template-columns: 1fr;
    }

    .detail-list {
      grid-template-columns: 1fr;
    }

    .detail-list dt {
      font-weight: 600;
      color: #374151;
    }

    .stats-grid {
      grid-template-columns: 1fr;
    }
  }

  /* Small mobile (480px) */
  @media (max-width: 480px) {
    .map-container {
      height: 35vh;
      min-height: 250px;
      max-height: 350px;
    }

    .map-placeholder {
      min-height: 250px;
      padding: 2rem 1rem;
    }

    .map-placeholder svg {
      width: 36px;
      height: 36px;
    }

    .map-header h2 {
      font-size: 1.125rem;
    }

    .last-update {
      font-size: 0.75rem;
    }
  }

  /* Large screens (1024px+) */
  @media (min-width: 1024px) {
    .map-container {
      height: 55vh;
      min-height: 450px;
      max-height: 700px;
    }
  }
</style>
