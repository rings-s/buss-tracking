<script lang="ts">
	import { tripService } from '$lib/services/trip';
	import LeafletMap from '$lib/components/tracking/LeafletMap.svelte';
	import type { TripDetail } from '$lib/types';

	let { tripId }: { tripId: number } = $props();

	let trip = $state<TripDetail | null>(null);
	let error = $state('');
	let isLoading = $state(true);

	// Convert trip locations to map data
	const mapMarkers = $derived(() => {
		if (!trip?.latest_location) return [];
		return [{
			id: 'current',
			lat: trip.latest_location.latitude,
			lng: trip.latest_location.longitude,
			label: 'Current Location',
			color: '#3b82f6',
			popup: `<strong>Current Location</strong><br/>${new Date(trip.latest_location.timestamp).toLocaleString()}`
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

	$effect(() => {
		tripService.get(tripId)
			.then((result) => {
				trip = result;
			})
			.catch((err) => {
				error = err instanceof Error ? err.message : 'Failed to load trip';
			})
			.finally(() => {
				isLoading = false;
			});
	});
</script>

<div class="space-y-8 animate-fade-in">
	{#if isLoading}
		<div class="flex justify-center py-20">
			<div class="animate-spin rounded-full h-12 w-12 border-b-2 border-brand-500"></div>
		</div>
	{:else if error}
		<div class="p-4 rounded-xl bg-red-50 text-red-600 border border-red-100 flex items-center gap-3">
			<svg xmlns="http://www.w3.org/2000/svg" class="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
				<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
			</svg>
			<span class="font-medium">{error}</span>
		</div>
	{:else if trip}
		<div class="flex items-center justify-between">
			<h2 class="text-3xl font-black text-gray-900 tracking-tight">Trip Details</h2>
			<span class={`px-3 py-1 rounded-full text-sm font-bold uppercase tracking-wider ${trip.is_active ? 'bg-green-100 text-green-700' : 'bg-gray-100 text-gray-600'}`}>
				{trip.is_active ? 'Active' : 'Completed'}
			</span>
		</div>

		<!-- Map Section -->
		{#if trip.locations && trip.locations.length > 0}
			<section class="glass-card p-6 mb-8">
				<h3 class="text-xl font-black mb-4 text-gray-900 flex items-center gap-2">
					<svg xmlns="http://www.w3.org/2000/svg" class="h-6 w-6 text-brand-500" fill="none" viewBox="0 0 24 24" stroke="currentColor">
						<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 20l-5.447-2.724A1 1 0 013 16.382V5.618a1 1 0 011.447-.894L9 7m0 13l6-3m-6 3V7m6 10l4.553 2.276A1 1 0 0021 18.382V7.618a1 1 0 00-.553-.894L15 4m0 13V4m0 0L9 7" />
					</svg>
					Route Map
				</h3>
				<LeafletMap
					markers={mapMarkers()}
					paths={mapPath()}
					center={trip.latest_location ? [trip.latest_location.latitude, trip.latest_location.longitude] : defaultCenter}
					zoom={14}
					height="300px"
				/>
				<p class="text-xs text-gray-500 mt-2">{trip.locations.length} location points recorded</p>
			</section>
		{/if}

		<div class="grid grid-cols-1 md:grid-cols-2 gap-8">
			<section class="glass-card p-8 h-full">
				<h3 class="text-xl font-black mb-6 text-gray-900 flex items-center gap-2">
					<svg xmlns="http://www.w3.org/2000/svg" class="h-6 w-6 text-brand-500" fill="none" viewBox="0 0 24 24" stroke="currentColor">
						<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
					</svg>
					Trip Info
				</h3>
				<dl class="space-y-4">
					<div class="flex justify-between items-center p-3 rounded-lg bg-white/50">
						<dt class="text-sm font-bold text-gray-500">Bus</dt>
						<dd class="font-bold text-gray-900">{trip.bus.name} <span class="text-gray-400 text-xs ml-1">({trip.bus.plate_number})</span></dd>
					</div>
					
					<div class="flex justify-between items-center p-3 rounded-lg bg-white/50">
						<dt class="text-sm font-bold text-gray-500">Driver</dt>
						<dd class="font-bold text-gray-900">{trip.driver.full_name}</dd>
					</div>
					
					<div class="flex justify-between items-center p-3 rounded-lg bg-white/50">
						<dt class="text-sm font-bold text-gray-500">Route</dt>
						<dd class="font-bold text-gray-900">{trip.route?.name || 'No route'}</dd>
					</div>
					
					<div class="flex justify-between items-center p-3 rounded-lg bg-white/50">
						<dt class="text-sm font-bold text-gray-500">Start Time</dt>
						<dd class="font-mono text-sm text-gray-700">{new Date(trip.start_time).toLocaleString()}</dd>
					</div>
					
					<div class="flex justify-between items-center p-3 rounded-lg bg-white/50">
						<dt class="text-sm font-bold text-gray-500">End Time</dt>
						<dd class="font-mono text-sm text-gray-700">{trip.end_time ? new Date(trip.end_time).toLocaleString() : 'In progress'}</dd>
					</div>
				</dl>
			</section>

			<section class="glass-card p-8 h-full">
				<h3 class="text-xl font-black mb-6 text-gray-900 flex items-center gap-2">
					<svg xmlns="http://www.w3.org/2000/svg" class="h-6 w-6 text-brand-500" fill="none" viewBox="0 0 24 24" stroke="currentColor">
						<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M17 20h5v-2a3 3 0 00-5.356-1.857M17 20H7m10 0v-2c0-.656-.126-1.283-.356-1.857M7 20H2v-2a3 3 0 015.356-1.857M7 20v-2c0-.656.126-1.283.356-1.857m0 0a5.002 5.002 0 019.288 0M15 7a3 3 0 11-6 0 3 3 0 016 0zm6 3a2 2 0 11-4 0 2 2 0 014 0zM7 10a2 2 0 11-4 0 2 2 0 014 0z" />
					</svg>
					Boardings <span class="ml-2 px-2 py-0.5 rounded-full bg-brand-100 text-brand-700 text-xs">{trip.boardings?.length || 0}</span>
				</h3>
				{#if trip.boardings && trip.boardings.length > 0}
					<div class="overflow-y-auto max-h-[400px] pr-2 space-y-3">
						{#each trip.boardings as boarding}
							<div class="p-3 rounded-xl bg-white/50 border border-gray-100 hover:bg-white hover:shadow-sm transition-all duration-200 flex justify-between items-center group">
								<span class="font-bold text-gray-900">{boarding.employee.full_name}</span>
								<span class="text-xs font-mono text-gray-500 group-hover:text-brand-600 transition-colors">{new Date(boarding.boarded_at).toLocaleString()}</span>
							</div>
						{/each}
					</div>
				{:else}
					<div class="text-center py-12 text-gray-400 italic">No boardings recorded</div>
				{/if}
			</section>
		</div>
	{/if}
</div>
