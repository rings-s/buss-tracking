<script lang="ts">
  import { onMount, onDestroy } from 'svelte';
  import { tripService } from '$lib/services/trip';
  import { nfcService, type NFCReadResult } from '$lib/services/nfc';
  import { auth } from '$lib/stores/auth.svelte';
  import type { Trip, CheckInResponse } from '$lib/types';
  import { t } from '$lib/i18n';

  let activeTrips = $state<Trip[]>([]);
  let selectedTripId = $state<number | null>(null);
  let nfcUid = $state('');
  let loading = $state(true);
  let submitting = $state(false);
  let error = $state('');
  let success = $state<CheckInResponse | null>(null);

  // Tablet GPS location
  let latitude = $state<number | null>(null);
  let longitude = $state<number | null>(null);
  let locationStatus = $state<'pending' | 'active' | 'error'>('pending');
  let locationError = $state('');
  let watchId: number | null = null;

  // Web NFC state
  let nfcSupported = $state(false);
  let nfcScanning = $state(false);
  let nfcError = $state('');

  onMount(async () => {
    // Check NFC support
    nfcSupported = nfcService.isSupported();

    // Start GPS tracking for tablet location
    startLocationTracking();

    // Only load active trips if user is authenticated (driver/admin with permissions)
    // Unauthenticated users can still check in if they have a trip ID
    if (auth.isAuthenticated && (auth.isDriver || auth.isAdmin)) {
      try {
        const trips = await tripService.list({ is_active: true });
        activeTrips = trips;
        if (trips.length === 1) {
          selectedTripId = trips[0].id;
        }
      } catch (e: any) {
        // Silently fail - user can still manually enter trip ID if needed
        console.error('Failed to load active trips:', e);
      }
    }

    loading = false;
  });

  onDestroy(() => {
    // Clean up GPS watch
    if (watchId !== null && navigator.geolocation) {
      navigator.geolocation.clearWatch(watchId);
    }

    // Stop NFC scanning
    if (nfcScanning) {
      nfcService.stopScan();
    }
  });

  function startLocationTracking() {
    if (!navigator.geolocation) {
      locationStatus = 'error';
      locationError = $t('checkin.gps.notSupported');
      return;
    }

    watchId = navigator.geolocation.watchPosition(
      (position) => {
        latitude = position.coords.latitude;
        longitude = position.coords.longitude;
        locationStatus = 'active';
        locationError = '';
      },
      (err) => {
        switch (err.code) {
          case err.PERMISSION_DENIED:
            locationStatus = 'error';
            locationError = $t('checkin.gps.permissionDenied');
            break;
          case err.POSITION_UNAVAILABLE:
            locationStatus = 'error';
            locationError = $t('checkin.gps.unavailable');
            break;
          case err.TIMEOUT:
            // Don't mark as error on timeout, keep trying (GPS can take up to 60s)
            locationError = $t('checkin.gps.timeout');
            break;
          default:
            locationStatus = 'error';
            locationError = $t('checkin.gps.unableToGet');
        }
      },
      {
        enableHighAccuracy: true,
        maximumAge: 0,        // Always get fresh location (best for check-in accuracy)
        timeout: 15000        // 15 seconds (GPS can take up to 60s on cold start)
      }
    );
  }

  async function handleCheckIn() {
    if (!selectedTripId || !nfcUid.trim()) {
      error = $t('checkin.form.validationError');
      return;
    }

    submitting = true;
    error = '';
    success = null;

    try {
      const response = await tripService.checkIn({
        nfc_uid: nfcUid.trim(),
        trip_id: selectedTripId,
        latitude: latitude,
        longitude: longitude
      });
      success = response;
      nfcUid = ''; // Clear for next scan

      // Auto-reset after 3 seconds for continuous scanning
      setTimeout(() => {
        if (success) {
          resetForm();
        }
      }, 3000);
    } catch (e: any) {
      error = e.message || 'Check-in failed';
    } finally {
      submitting = false;
    }
  }

  function resetForm() {
    success = null;
    error = '';
    nfcUid = '';
  }

  async function startNFCScan() {
    if (!nfcSupported) {
      nfcError = $t('checkin.nfc.notSupported');
      return;
    }

    if (!selectedTripId) {
      nfcError = $t('checkin.nfc.selectTripFirst');
      return;
    }

    try {
      nfcScanning = true;
      nfcError = '';
      error = '';

      await nfcService.startScan(
        (result: NFCReadResult) => {
          // Use serial number as UID
          nfcUid = result.serialNumber;

          // Auto-submit check-in
          handleCheckIn();
        },
        (err: Error) => {
          nfcError = err.message;
          nfcScanning = false;
        }
      );
    } catch (err: any) {
      nfcError = err.message || 'Failed to start NFC scanning';
      nfcScanning = false;
    }
  }

  function stopNFCScan() {
    nfcService.stopScan();
    nfcScanning = false;
    nfcError = '';
  }

  function formatTime(dateString: string): string {
    return new Date(dateString).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
  }
</script>

<div class="min-h-screen bg-gray-50 relative overflow-hidden">
  <!-- Background Elements -->
  <div class="hero-dots fixed inset-0 opacity-30 pointer-events-none"></div>
  <div class="fixed top-0 left-0 w-full h-96 bg-gradient-to-b from-brand-50/80 to-transparent pointer-events-none"></div>

  <div class="relative z-10 p-4 md:p-8 max-w-2xl mx-auto">
    <!-- Header -->
    <div class="text-center mb-8">
      <div class="w-16 h-16 mx-auto rounded-full bg-brand-100 flex items-center justify-center text-brand-600 mb-4">
        <svg xmlns="http://www.w3.org/2000/svg" class="h-8 w-8" fill="none" viewBox="0 0 24 24" stroke="currentColor">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 9h3.75M15 12h3.75M15 15h3.75M4.5 19.5h15a2.25 2.25 0 002.25-2.25V6.75A2.25 2.25 0 0019.5 4.5h-15a2.25 2.25 0 00-2.25 2.25v10.5A2.25 2.25 0 004.5 19.5zm6-10.125a1.875 1.875 0 11-3.75 0 1.875 1.875 0 013.75 0zm1.294 6.336a6.721 6.721 0 01-3.17.789 6.721 6.721 0 01-3.168-.789 3.376 3.376 0 016.338 0z" />
        </svg>
      </div>
      <h1 class="text-3xl font-black text-gray-900">{$t('checkin.title')}</h1>
      <p class="text-gray-500 mt-2">{$t('checkin.subtitle')}</p>
    </div>

    <!-- GPS Status -->
    <div class="mb-6 glass-card p-4">
      <div class="flex items-center justify-between mb-2">
        <div class="flex items-center gap-3">
          <div class={`w-3 h-3 rounded-full ${
            locationStatus === 'active' ? 'bg-green-500 animate-pulse' :
            locationStatus === 'pending' ? 'bg-yellow-500 animate-pulse' :
            'bg-red-500'
          }`}></div>
          <span class="text-sm font-bold text-gray-700">
            {#if locationStatus === 'active'}
              {$t('checkin.gps.active')}
            {:else if locationStatus === 'pending'}
              {$t('checkin.gps.acquiring')}
            {:else}
              {$t('checkin.gps.error')}
            {/if}
          </span>
        </div>
        {#if locationStatus === 'active'}
          <span class="text-xs bg-green-50 text-green-700 px-2 py-1 rounded font-medium">
            {$t('checkin.gps.ready')}
          </span>
        {/if}
      </div>

      {#if locationStatus === 'active' && latitude && longitude}
        <div class="mt-3 pt-3 border-t border-gray-100">
          <div class="grid grid-cols-2 gap-2 text-xs">
            <div>
              <span class="text-gray-500">{$t('checkin.gps.latitude')}</span>
              <span class="font-mono text-gray-700 ml-1 font-medium">
                {latitude.toFixed(6)}
              </span>
            </div>
            <div>
              <span class="text-gray-500">{$t('checkin.gps.longitude')}</span>
              <span class="font-mono text-gray-700 ml-1 font-medium">
                {longitude.toFixed(6)}
              </span>
            </div>
          </div>
          <p class="text-xs text-gray-500 mt-2 flex items-center gap-1">
            <svg xmlns="http://www.w3.org/2000/svg" class="h-3 w-3" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
            </svg>
            {$t('checkin.gps.locationRecorded')}
          </p>
        </div>
      {:else if locationStatus === 'pending'}
        <p class="text-xs text-yellow-700 mt-2 flex items-center gap-1">
          <svg class="animate-spin h-3 w-3" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
            <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
            <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
          </svg>
          {$t('checkin.gps.pleaseWait')}
        </p>
      {/if}

      {#if locationError}
        <div class="mt-2 p-2 rounded-lg bg-red-50 border border-red-100">
          <p class="text-xs text-red-600 flex items-start gap-1">
            <svg xmlns="http://www.w3.org/2000/svg" class="h-3 w-3 mt-0.5 flex-shrink-0" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
            </svg>
            <span>{locationError}</span>
          </p>
        </div>
      {/if}
    </div>

    {#if loading}
      <div class="flex items-center justify-center py-12">
        <div class="animate-spin rounded-full h-12 w-12 border-b-2 border-brand-500"></div>
      </div>
    {:else if activeTrips.length === 0}
      <div class="glass-card p-8">
        <div class="text-center mb-6">
          <div class="w-16 h-16 mx-auto rounded-full bg-blue-100 flex items-center justify-center text-blue-600 mb-4">
            <svg xmlns="http://www.w3.org/2000/svg" class="h-8 w-8" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
            </svg>
          </div>
          <h2 class="text-xl font-bold text-gray-900 mb-2">Check-in Available</h2>
          <p class="text-gray-500 mb-4">
            {#if auth.isAuthenticated}
              No active trips found. Enter trip ID manually or ask the driver to start a trip.
            {:else}
              Ask the driver for the trip ID to check in.
            {/if}
          </p>
        </div>

        <form onsubmit={(e) => { e.preventDefault(); handleCheckIn(); }} class="space-y-4">
          <!-- Manual Trip ID Input -->
          <div>
            <label for="manual-trip" class="block text-sm font-bold text-gray-700 mb-2">Trip ID</label>
            <input
              type="number"
              id="manual-trip"
              bind:value={selectedTripId}
              placeholder="Enter trip ID..."
              required
              class="w-full px-4 py-3 rounded-xl border border-gray-200 bg-white focus:ring-2 focus:ring-brand-500 focus:border-transparent transition-all text-lg"
            />
            <p class="text-xs text-gray-500 mt-2">
              The driver will provide you with the trip ID
            </p>
          </div>

          <!-- NFC Input -->
          <div>
            <label for="nfc-manual" class="block text-sm font-bold text-gray-700 mb-2">NFC Card UID</label>
            <input
              type="text"
              id="nfc-manual"
              bind:value={nfcUid}
              placeholder="Scan NFC card..."
              required
              class="w-full px-4 py-4 rounded-xl border border-gray-200 bg-white focus:ring-2 focus:ring-brand-500 focus:border-transparent transition-all text-xl font-mono tracking-wider"
            />
            <p class="text-xs text-gray-500 mt-2">
              <svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4 inline mr-1" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
              </svg>
              NFC reader will automatically input the card UID
            </p>
          </div>

          {#if error}
            <div class="p-4 rounded-xl bg-red-50 border border-red-200 flex items-start gap-3">
              <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5 text-red-500 flex-shrink-0 mt-0.5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
              </svg>
              <span class="text-red-600 font-medium">{error}</span>
            </div>
          {/if}

          <button
            type="submit"
            disabled={submitting || !selectedTripId || !nfcUid.trim()}
            class="w-full btn-primary py-4 text-lg font-bold disabled:opacity-50 disabled:cursor-not-allowed"
          >
            {#if submitting}
              <span class="flex items-center justify-center gap-2">
                <svg class="animate-spin h-5 w-5" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                  <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
                  <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                </svg>
                Processing...
              </span>
            {:else}
              Check In Employee
            {/if}
          </button>
        </form>
      </div>
    {:else if success}
      <div class="glass-card p-8 text-center bg-green-50/50 border-green-200 animate-fade-in">
        <div class="w-20 h-20 mx-auto rounded-full bg-green-100 flex items-center justify-center text-green-600 mb-4">
          <svg xmlns="http://www.w3.org/2000/svg" class="h-10 w-10" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7" />
          </svg>
        </div>
        <h2 class="text-2xl font-black text-green-700 mb-2">Check-in Successful!</h2>
        <p class="text-green-600 font-medium mb-6">{success.message}</p>

        <div class="bg-white rounded-xl p-4 text-left space-y-3 mb-6">
          <div class="flex justify-between items-center">
            <span class="text-gray-500 text-sm">Employee</span>
            <span class="font-bold text-gray-900">{success.boarding.employee.full_name}</span>
          </div>
          <div class="flex justify-between items-center">
            <span class="text-gray-500 text-sm">Email</span>
            <span class="text-gray-700">{success.boarding.employee.email}</span>
          </div>
          <div class="flex justify-between items-center">
            <span class="text-gray-500 text-sm">Time</span>
            <span class="font-mono text-gray-700">{formatTime(success.boarding.boarded_at)}</span>
          </div>
          {#if success.boarding.latitude && success.boarding.longitude}
            <div class="flex justify-between items-center">
              <span class="text-gray-500 text-sm">Location</span>
              <span class="font-mono text-xs text-gray-500">
                {success.boarding.latitude.toFixed(4)}, {success.boarding.longitude.toFixed(4)}
              </span>
            </div>
          {/if}
        </div>

        <p class="text-sm text-gray-500 mb-4">Auto-resetting in 3 seconds...</p>
        <button type="button" onclick={resetForm} class="btn-primary">
          Scan Next Card
        </button>
      </div>
    {:else}
      <form onsubmit={(e) => { e.preventDefault(); handleCheckIn(); }} class="glass-card p-6 space-y-6">
        <!-- Trip Selection -->
        <div>
          <label for="trip" class="block text-sm font-bold text-gray-700 mb-2">Select Trip</label>
          <select
            id="trip"
            bind:value={selectedTripId}
            required
            class="w-full px-4 py-3 rounded-xl border border-gray-200 bg-white focus:ring-2 focus:ring-brand-500 focus:border-transparent transition-all text-lg"
          >
            <option value={null}>-- Select active trip --</option>
            {#each activeTrips as trip}
              <option value={trip.id}>
                Trip #{trip.id} - {trip.bus.name} ({trip.driver.full_name})
                {#if trip.route} - {trip.route.name}{/if}
              </option>
            {/each}
          </select>
        </div>

        <!-- Web NFC Scanner -->
        {#if nfcSupported}
          <div>
            <div class="flex items-center justify-between mb-2">
              <span class="block text-sm font-bold text-gray-700">Web NFC Scanner</span>
              <div class="flex items-center gap-2">
                <div class={`w-2 h-2 rounded-full ${nfcScanning ? 'bg-green-500 animate-pulse' : 'bg-gray-300'}`}></div>
                <span class="text-xs text-gray-500">{nfcScanning ? 'Scanning...' : 'Inactive'}</span>
              </div>
            </div>

            {#if !nfcScanning}
              <button
                type="button"
                onclick={startNFCScan}
                disabled={!selectedTripId}
                class="w-full btn-secondary py-3 disabled:opacity-50 disabled:cursor-not-allowed"
              >
                <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5 inline mr-2" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 18h.01M7 21h10a2 2 0 002-2V5a2 2 0 00-2-2H7a2 2 0 00-2 2v14a2 2 0 002 2z" />
                </svg>
                Enable NFC Scanning
              </button>
            {:else}
              <button
                type="button"
                onclick={stopNFCScan}
                class="w-full py-3 rounded-xl bg-red-50 text-red-600 border-2 border-red-200 hover:bg-red-100 font-bold transition-all"
              >
                <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5 inline mr-2" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
                </svg>
                Stop NFC Scanning
              </button>
              <div class="mt-3 p-3 rounded-lg bg-blue-50 border border-blue-200">
                <p class="text-sm text-blue-600 flex items-center gap-2">
                  <svg class="animate-pulse h-4 w-4" fill="currentColor" viewBox="0 0 20 20">
                    <circle cx="10" cy="10" r="3"/>
                  </svg>
                  Ready to scan - tap NFC card on device
                </p>
              </div>
            {/if}

            {#if nfcError}
              <div class="mt-3 p-3 rounded-lg bg-yellow-50 border border-yellow-200">
                <p class="text-sm text-yellow-800 flex items-start gap-2">
                  <svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4 flex-shrink-0 mt-0.5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
                  </svg>
                  {nfcError}
                </p>
              </div>
            {/if}
          </div>

          <!-- Divider -->
          <div class="relative my-6">
            <div class="absolute inset-0 flex items-center">
              <div class="w-full border-t border-gray-200"></div>
            </div>
            <div class="relative flex justify-center text-sm">
              <span class="px-4 bg-white text-gray-500 font-medium">OR use manual input</span>
            </div>
          </div>
        {/if}

        <!-- NFC Input -->
        <div>
          <label for="nfc" class="block text-sm font-bold text-gray-700 mb-2">NFC Card UID {nfcSupported ? '(Manual)' : ''}</label>
          <input
            type="text"
            id="nfc"
            bind:value={nfcUid}
            placeholder="Scan NFC card..."
            required
            class="w-full px-4 py-4 rounded-xl border border-gray-200 bg-white focus:ring-2 focus:ring-brand-500 focus:border-transparent transition-all text-xl font-mono tracking-wider"
          />
          <p class="text-xs text-gray-500 mt-2">
            <svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4 inline mr-1" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
            </svg>
            {nfcSupported ? 'NFC reader or Web NFC will input the card UID' : 'NFC reader will automatically input the card UID'}
          </p>
        </div>

        {#if error}
          <div class="p-4 rounded-xl bg-red-50 border border-red-200 flex items-start gap-3">
            <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5 text-red-500 flex-shrink-0 mt-0.5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
            </svg>
            <span class="text-red-600 font-medium">{error}</span>
          </div>
        {/if}

        <button
          type="submit"
          disabled={submitting || !selectedTripId || !nfcUid.trim()}
          class="w-full btn-primary py-4 text-lg font-bold disabled:opacity-50 disabled:cursor-not-allowed"
        >
          {#if submitting}
            <span class="flex items-center justify-center gap-2">
              <svg class="animate-spin h-5 w-5" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
                <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
              </svg>
              Processing...
            </span>
          {:else}
            Check In Employee
          {/if}
        </button>
      </form>
    {/if}

    <!-- Info Card -->
    <div class="mt-8 p-4 rounded-xl bg-blue-50 border border-blue-100">
      <h3 class="font-bold text-blue-900 mb-2 flex items-center gap-2">
        <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
        </svg>
        How NFC Check-in Works
      </h3>
      <ul class="text-sm text-blue-800 space-y-1">
        <li>• Employee taps their NFC card on the tablet</li>
        <li>• System automatically records employee, time & location</li>
        <li>• No employee login required after initial registration</li>
        <li>• Card is linked directly to employee profile</li>
      </ul>
    </div>
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

  .btn-secondary {
    display: inline-flex;
    align-items: center;
    justify-content: center;
    padding: 0.75rem 1.5rem;
    background: white;
    color: #3b82f6;
    border: 2px solid #3b82f6;
    border-radius: 0.75rem;
    font-weight: 600;
    cursor: pointer;
    transition: all 0.2s;
  }

  .btn-secondary:hover:not(:disabled) {
    background: #eff6ff;
    transform: translateY(-1px);
  }

  .hero-dots {
    background-image: radial-gradient(#d1d5db 1px, transparent 1px);
    background-size: 20px 20px;
  }

  .animate-fade-in {
    animation: fadeIn 0.3s ease-out;
  }

  @keyframes fadeIn {
    from {
      opacity: 0;
      transform: translateY(10px);
    }
    to {
      opacity: 1;
      transform: translateY(0);
    }
  }
</style>
