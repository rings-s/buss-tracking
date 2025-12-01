<script lang="ts">
	import { page } from '$app/stores';
	import { tripService } from '$lib/services/trip';
	import { auth } from '$lib/stores/auth.svelte';
	import { ActiveTrip, LoadingSpinner, ErrorMessage } from '$lib/components';

	let tripId = $state<number | null>(null);
	let error = $state('');
	let isLoading = $state(true);

	$effect(() => {
		const urlTripId = $page.url.searchParams.get('tripId');

		if (urlTripId) {
			tripId = Number(urlTripId);
			isLoading = false;
		} else if (auth.user) {
			tripService.list({ driver_id: auth.user.id, is_active: true })
				.then((trips) => {
					if (trips.length > 0) {
						tripId = trips[0].id;
					}
				})
				.catch((err) => {
					error = err instanceof Error ? err.message : 'Failed to load active trip';
				})
				.finally(() => {
					isLoading = false;
				});
		}
	});
</script>

<div class="max-w-4xl mx-auto px-4 py-8">
	{#if isLoading}
		<LoadingSpinner message="Loading active trip..." />
	{:else if error}
		<ErrorMessage message={error} />
	{:else if tripId}
		<ActiveTrip {tripId} />
	{:else}
		<div class="glass-card p-12 text-center">
			<div class="w-20 h-20 mx-auto rounded-full bg-gray-50 flex items-center justify-center text-gray-300 mb-6">
				<svg xmlns="http://www.w3.org/2000/svg" class="h-10 w-10" fill="none" viewBox="0 0 24 24" stroke="currentColor">
					<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 20l-5.447-2.724A1 1 0 013 16.382V5.618a1 1 0 011.447-.894L9 7m0 13l6-3m-6 3V7m6 10l4.553 2.276A1 1 0 0021 18.382V7.618a1 1 0 00-.553-.894L15 4m0 13V4m0 0L9 7" />
				</svg>
			</div>
			<h2 class="text-2xl font-black text-gray-900 mb-4">No Active Trip</h2>
			<p class="text-gray-500 mb-8">You don't have an active trip right now.</p>
			<a href="/driver/start-trip" class="btn-primary inline-block">Start New Trip</a>
		</div>
	{/if}
</div>
