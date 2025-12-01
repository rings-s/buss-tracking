<script lang="ts">
	import { onMount } from 'svelte';
	import { busService } from '$lib/services/bus';
	import { gpsUpdateSchema } from '$lib/schemas';

	let { busId }: { busId: number } = $props();

	let isTracking = $state(false);
	let error = $state('');
	let lastUpdate = $state<Date | null>(null);
	let watchId: number | null = null;
	let currentPosition = $state<GeolocationPosition | null>(null);
	let updateCount = $state(0);
	let permissionStatus = $state<'prompt' | 'granted' | 'denied'>('prompt');
	let isAcquiringLocation = $state(true);

	async function sendLocation(position: GeolocationPosition) {
		try {
			currentPosition = position;
			isAcquiringLocation = false; // Location acquired

			const data = {
				bus_id: busId,
				latitude: position.coords.latitude,
				longitude: position.coords.longitude
			};
			gpsUpdateSchema.parse(data);
			await busService.updateGPS(data);
			lastUpdate = new Date();
			updateCount++;
			error = '';
		} catch (err) {
			error = err instanceof Error ? err.message : 'Failed to update location';
		}
	}

	async function checkPermission() {
		if ('permissions' in navigator) {
			try {
				const result = await navigator.permissions.query({ name: 'geolocation' as PermissionName });
				permissionStatus = result.state as 'prompt' | 'granted' | 'denied';

				result.addEventListener('change', () => {
					permissionStatus = result.state as 'prompt' | 'granted' | 'denied';
				});
			} catch (e) {
				// Permissions API not supported, proceed anyway
			}
		}
	}

	function startTracking() {
		if (!navigator.geolocation) {
			error = 'Geolocation is not supported on this device';
			return;
		}

		isTracking = true;
		error = '';

		watchId = navigator.geolocation.watchPosition(
			sendLocation,
			(err) => {
				switch (err.code) {
					case err.PERMISSION_DENIED:
						error = 'GPS permission denied. Please enable location access in your browser settings.';
						permissionStatus = 'denied';
						break;
					case err.POSITION_UNAVAILABLE:
						error = 'GPS position unavailable. Make sure GPS is enabled on your device.';
						break;
					case err.TIMEOUT:
						error = 'GPS request timed out. Retrying... (GPS can take up to 60 seconds on first use)';
						// Don't stop tracking on timeout, let it retry
						break;
					default:
						error = err.message || 'Unknown GPS error';
				}
				// Only stop tracking if permission denied
				if (err.code === err.PERMISSION_DENIED) {
					isTracking = false;
				}
			},
			{
				enableHighAccuracy: true,
				maximumAge: 0,        // Always get fresh location (best for real-time tracking)
				timeout: 15000        // 15 seconds (GPS can take up to 60s on cold start)
			}
		);
	}

	function stopTracking() {
		if (watchId !== null) {
			navigator.geolocation.clearWatch(watchId);
			watchId = null;
		}
		isTracking = false;
	}

	// Auto-start GPS tracking when component mounts
	onMount(() => {
		checkPermission();
		startTracking();
	});

	$effect(() => {
		return () => {
			if (watchId !== null) {
				navigator.geolocation.clearWatch(watchId);
			}
		};
	});
</script>

<div class="glass-card p-6 animate-fade-in">
	<div class="flex items-center justify-between mb-4">
		<h3 class="text-xl font-black text-gray-900 flex items-center gap-2">
			<svg xmlns="http://www.w3.org/2000/svg" class="h-6 w-6 text-brand-500" fill="none" viewBox="0 0 24 24" stroke="currentColor">
				<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M17.657 16.657L13.414 20.9a1.998 1.998 0 01-2.827 0l-4.244-4.243a8 8 0 1111.314 0z" />
				<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 11a3 3 0 11-6 0 3 3 0 016 0z" />
			</svg>
			GPS Tracking
		</h3>
		{#if isTracking}
			<span class="relative flex h-3 w-3">
			  <span class="animate-ping absolute inline-flex h-full w-full rounded-full bg-green-400 opacity-75"></span>
			  <span class="relative inline-flex rounded-full h-3 w-3 bg-green-500"></span>
			</span>
		{:else}
			<span class="h-3 w-3 rounded-full bg-gray-300"></span>
		{/if}
	</div>
	
	{#if error}
		<div class="mb-4 p-3 rounded-xl bg-red-50 text-red-600 border border-red-100 text-sm flex items-start gap-2">
			<svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5 flex-shrink-0" fill="none" viewBox="0 0 24 24" stroke="currentColor">
				<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
			</svg>
			<span>{error}</span>
		</div>
	{/if}

	<div class="space-y-4">
		{#if isTracking}
			<div class="p-4 rounded-xl bg-brand-50 border border-brand-100 space-y-3">
				<div class="flex items-center justify-between">
					<p class="text-sm font-bold text-brand-700">Status: Active</p>
					<span class="text-xs font-mono bg-brand-100 px-2 py-1 rounded text-brand-700">
						{updateCount} updates sent
					</span>
				</div>

				{#if isAcquiringLocation}
					<p class="text-xs font-mono text-brand-600 animate-pulse flex items-center gap-2">
						<svg class="animate-spin h-3 w-3" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
							<circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
							<path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
						</svg>
						Acquiring GPS fix... (may take up to 60 seconds)
					</p>
				{:else if lastUpdate}
					<p class="text-xs font-mono text-brand-600">
						Last update: {lastUpdate.toLocaleTimeString()}
					</p>
				{:else}
					<p class="text-xs font-mono text-brand-600 animate-pulse">
						Waiting for location...
					</p>
				{/if}

				{#if currentPosition}
					<div class="pt-2 border-t border-brand-100">
						<p class="text-xs font-bold text-brand-700 mb-2">Current Location</p>
						<div class="grid grid-cols-2 gap-2 text-xs">
							<div>
								<span class="text-brand-600">Lat:</span>
								<span class="font-mono text-brand-700 ml-1">
									{currentPosition.coords.latitude.toFixed(6)}
								</span>
							</div>
							<div>
								<span class="text-brand-600">Lng:</span>
								<span class="font-mono text-brand-700 ml-1">
									{currentPosition.coords.longitude.toFixed(6)}
								</span>
							</div>
							<div>
								<span class="text-brand-600">Accuracy:</span>
								<span class="font-mono ml-1 font-bold"
									class:text-green-600={currentPosition.coords.accuracy < 50}
									class:text-yellow-600={currentPosition.coords.accuracy >= 50 && currentPosition.coords.accuracy < 100}
									class:text-red-600={currentPosition.coords.accuracy >= 100}>
									±{Math.round(currentPosition.coords.accuracy)}m
								</span>
							</div>
							{#if currentPosition.coords.speed !== null}
								<div>
									<span class="text-brand-600">Speed:</span>
									<span class="font-mono text-brand-700 ml-1">
										{Math.round((currentPosition.coords.speed || 0) * 3.6)} km/h
									</span>
								</div>
							{/if}
						</div>
					</div>
				{/if}
			</div>
			<button type="button" class="w-full px-4 py-2 rounded-xl bg-red-50 text-red-600 font-bold hover:bg-red-100 transition-colors border border-red-100" onclick={stopTracking}>
				Stop Tracking
			</button>
		{:else}
			<div class="p-4 rounded-xl bg-gray-50 border border-gray-100">
				<p class="text-sm font-bold text-gray-500">Status: Inactive</p>
				<p class="text-xs text-gray-400">Start tracking to share your location</p>
				{#if permissionStatus === 'denied'}
					<p class="text-xs text-red-600 mt-2 flex items-center gap-1">
						<svg xmlns="http://www.w3.org/2000/svg" class="h-3 w-3" fill="none" viewBox="0 0 24 24" stroke="currentColor">
							<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
						</svg>
						Location permission required
					</p>
				{/if}
			</div>
			<button type="button" class="btn-primary w-full" onclick={startTracking}>
				Start Tracking
			</button>
		{/if}
	</div>
</div>
