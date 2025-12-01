<script lang="ts">
	import { onMount, onDestroy } from 'svelte';
	import { tripService } from '$lib/services/trip';
	import LeafletMap from '$lib/components/tracking/LeafletMap.svelte';
	import GPSUpdater from '$lib/components/tracking/GPSUpdater.svelte';
	import type { TripDetail } from '$lib/types';

	let { tripId }: { tripId: number } = $props();

	let trip = $state<TripDetail | null>(null);
	let error = $state('');
	let isLoading = $state(true);
	let refreshInterval: ReturnType<typeof setInterval>;

	// Convert trip data to map markers
	const mapMarkers = $derived(() => {
		if (!trip?.latest_location) return [];
		return [{
			id: 'current',
			lat: trip.latest_location.latitude,
			lng: trip.latest_location.longitude,
			label: 'Current Location',
			color: '#10b981',
			popup: `<strong>Current Position</strong><br/>Updated: ${new Date(trip.latest_location.timestamp).toLocaleTimeString()}`
		}];
	});

	const mapPath = $derived(() => {
		if (!trip?.locations || trip.locations.length < 2) return [];
		return [{
			coordinates: trip.locations
				.sort((a, b) => new Date(a.timestamp).getTime() - new Date(b.timestamp).getTime())
				.map(loc => [loc.latitude, loc.longitude] as [number, number]),
			color: '#3b82f6'
		}];
	});

	const defaultCenter: [number, number] = [24.7136, 46.6753];

	async function loadTrip() {
		try {
			trip = await tripService.get(tripId);
			error = '';
		} catch (err) {
			error = err instanceof Error ? err.message : 'Failed to load trip';
		} finally {
			isLoading = false;
		}
	}

	async function endTrip() {
		if (!confirm('Are you sure you want to end this trip?')) return;

		try {
			await tripService.end(tripId);
			window.location.href = '/dashboard';
		} catch (err) {
			error = err instanceof Error ? err.message : 'Failed to end trip';
		}
	}

	onMount(() => {
		loadTrip();
		// Refresh every 10 seconds to get updated location data
		refreshInterval = setInterval(loadTrip, 10000);
	});

	onDestroy(() => {
		if (refreshInterval) {
			clearInterval(refreshInterval);
		}
	});
</script>

<div class="space-y-6 animate-fade-in">
	{#if isLoading}
		<div class="flex justify-center py-12">
			<div class="animate-spin rounded-full h-10 w-10 border-b-2 border-brand-500"></div>
		</div>
	{:else if error}
		<div class="p-4 rounded-xl bg-red-50 text-red-600 border border-red-100 flex items-center gap-3">
			<svg xmlns="http://www.w3.org/2000/svg" class="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
				<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
			</svg>
			<span class="font-medium">{error}</span>
		</div>
	{:else if trip}
		<!-- Header -->
		<div class="flex items-center justify-between">
			<div>
				<h1 class="text-3xl font-black text-gray-900 tracking-tight">Active Trip</h1>
				<p class="text-gray-500">Trip #{trip.id} - {trip.bus.name}</p>
			</div>
			<button type="button" class="px-4 py-2 rounded-xl bg-red-50 text-red-600 font-bold hover:bg-red-100 transition-colors border border-red-100" onclick={endTrip}>
				End Trip
			</button>
		</div>

		<!-- Map -->
		<div class="glass-card p-4">
			<h3 class="text-lg font-bold mb-3 text-gray-900">Live Location</h3>
			<LeafletMap
				markers={mapMarkers()}
				paths={mapPath()}
				center={trip.latest_location ? [trip.latest_location.latitude, trip.latest_location.longitude] : defaultCenter}
				zoom={15}
				height="350px"
				showUserLocation={true}
			/>
			{#if trip.latest_location}
				<p class="text-xs text-gray-500 mt-2">
					Last update: {new Date(trip.latest_location.timestamp).toLocaleString()}
				</p>
			{:else}
				<p class="text-xs text-gray-500 mt-2">
					No location data yet. Start GPS tracking to see your position.
				</p>
			{/if}
		</div>

		<!-- GPS Tracking -->
		<GPSUpdater busId={trip.bus.id} />

		<!-- Trip Info -->
		<div class="grid grid-cols-1 md:grid-cols-2 gap-4">
			<div class="glass-card p-6">
				<h3 class="text-lg font-bold mb-4 text-gray-900">Trip Details</h3>
				<dl class="space-y-3">
					<div class="flex justify-between">
						<dt class="text-sm text-gray-500">Bus</dt>
						<dd class="font-bold">{trip.bus.name} ({trip.bus.plate_number})</dd>
					</div>
					{#if trip.route}
						<div class="flex justify-between">
							<dt class="text-sm text-gray-500">Route</dt>
							<dd class="font-bold">{trip.route.name}</dd>
						</div>
					{/if}
					<div class="flex justify-between">
						<dt class="text-sm text-gray-500">Started</dt>
						<dd class="font-mono text-sm">{new Date(trip.start_time).toLocaleString()}</dd>
					</div>
					<div class="flex justify-between">
						<dt class="text-sm text-gray-500">Location Points</dt>
						<dd class="font-bold">{trip.locations?.length || 0}</dd>
					</div>
				</dl>
			</div>

			<div class="glass-card p-6">
				<h3 class="text-lg font-bold mb-4 text-gray-900">
					Boardings <span class="text-brand-600">({trip.boardings?.length || 0})</span>
				</h3>
				{#if trip.boardings && trip.boardings.length > 0}
					<div class="overflow-y-auto max-h-[200px] space-y-2">
						{#each trip.boardings as boarding}
							<div class="p-2 rounded-lg bg-gray-50 flex justify-between items-center text-sm">
								<span class="font-medium">{boarding.employee.full_name}</span>
								<span class="text-xs text-gray-500">{new Date(boarding.boarded_at).toLocaleTimeString()}</span>
							</div>
						{/each}
					</div>
				{:else}
					<p class="text-gray-500 text-sm italic">No boardings yet</p>
				{/if}
			</div>
		</div>
	{/if}
</div>
