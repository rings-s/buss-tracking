<script lang="ts">
	import { tripService } from '$lib/services/trip';
	import { auth } from '$lib/stores/auth.svelte';
	import type { Trip } from '$lib/types';

	let trips = $state<Trip[]>([]);
	let error = $state('');
	let isLoading = $state(true);

	const activeTrip = $derived(trips.find(t => t.is_active));

	$effect(() => {
		if (!auth.user) return;
		
		tripService.list({ driver_id: auth.user.id })
			.then((result) => {
				trips = result;
			})
			.catch((err) => {
				error = err instanceof Error ? err.message : 'Failed to load trips';
			})
			.finally(() => {
				isLoading = false;
			});
	});
</script>

<div class="space-y-8 animate-fade-in">
	<h1 class="text-4xl font-black text-gray-900 tracking-tight">Driver Dashboard</h1>

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
	{:else}
		<div class="grid grid-cols-1 lg:grid-cols-2 gap-8">
			<section class="glass-card p-8 h-full flex flex-col relative overflow-hidden group">
				<!-- Decorative Background -->
				<div class="absolute top-0 right-0 w-64 h-64 bg-brand-400/10 rounded-full blur-3xl -translate-y-1/2 translate-x-1/2 group-hover:bg-brand-400/20 transition-all duration-500"></div>
				
				<h2 class="text-2xl font-black mb-6 text-gray-900 flex items-center gap-2 relative z-10">
					<span class="w-3 h-3 rounded-full bg-brand-500 animate-pulse"></span>
					Current Status
				</h2>
				
				{#if activeTrip}
					<div class="flex-1 flex flex-col justify-between relative z-10">
						<div class="space-y-6">
							<div class="p-6 rounded-2xl bg-gradient-to-br from-brand-50 to-white border border-brand-100 shadow-sm">
								<div class="flex items-center gap-4 mb-6">
									<div class="w-14 h-14 rounded-2xl bg-brand-100 text-brand-600 flex items-center justify-center shadow-inner">
										<svg xmlns="http://www.w3.org/2000/svg" class="h-8 w-8" fill="none" viewBox="0 0 24 24" stroke="currentColor">
											<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 10V3L4 14h7v7l9-11h-7z" />
										</svg>
									</div>
									<div>
										<p class="text-sm font-bold text-brand-600 uppercase tracking-wider">Trip in Progress</p>
										<p class="text-2xl font-black text-gray-900">{activeTrip.route?.name || 'No Route'}</p>
									</div>
								</div>
								
								<div class="grid grid-cols-2 gap-6">
									<div class="bg-white/60 p-3 rounded-xl border border-brand-50">
										<p class="text-xs font-bold text-gray-500 uppercase mb-1">Bus</p>
										<p class="font-bold text-gray-900 text-lg">{activeTrip.bus.name}</p>
									</div>
									<div class="bg-white/60 p-3 rounded-xl border border-brand-50">
										<p class="text-xs font-bold text-gray-500 uppercase mb-1">Boardings</p>
										<p class="font-bold text-gray-900 text-lg">{activeTrip.boarding_count || 0}</p>
									</div>
									<div class="col-span-2 bg-white/60 p-3 rounded-xl border border-brand-50">
										<p class="text-xs font-bold text-gray-500 uppercase mb-1">Started At</p>
										<p class="font-mono text-sm text-gray-700 font-medium">{new Date(activeTrip.start_time).toLocaleString()}</p>
									</div>
								</div>
							</div>
						</div>
						
						<div class="mt-8">
							<a href="/driver/active-trip" class="btn-primary flex justify-center items-center gap-2 group-hover:scale-[1.02] transition-transform">
								<span>Manage Active Trip</span>
								<svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5" viewBox="0 0 20 20" fill="currentColor">
									<path fill-rule="evenodd" d="M7.293 14.707a1 1 0 010-1.414L10.586 10 7.293 6.707a1 1 0 011.414-1.414l4 4a1 1 0 010 1.414l-4 4a1 1 0 01-1.414 0z" clip-rule="evenodd" />
								</svg>
							</a>
						</div>
					</div>
				{:else}
					<div class="flex-1 flex flex-col justify-center items-center text-center py-12 relative z-10">
						<div class="w-24 h-24 rounded-full bg-gray-50 border-4 border-white shadow-lg flex items-center justify-center text-gray-300 mb-6">
							<svg xmlns="http://www.w3.org/2000/svg" class="h-12 w-12" fill="none" viewBox="0 0 24 24" stroke="currentColor">
								<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 12h.01M12 12h.01M19 12h.01M6 12a1 1 0 11-2 0 1 1 0 012 0zm7 0a1 1 0 11-2 0 1 1 0 012 0zm7 0a1 1 0 11-2 0 1 1 0 012 0z" />
							</svg>
						</div>
						<h3 class="text-xl font-bold text-gray-900 mb-2">No Active Trip</h3>
						<p class="text-gray-500 mb-8 max-w-xs">You are currently not assigned to any active trip. Start a new trip to begin tracking.</p>
						<a href="/driver/start-trip" class="btn-primary shadow-xl shadow-brand-200/50">Start New Trip</a>
					</div>
				{/if}
			</section>

			<section class="glass-card p-8 h-full">
				<h2 class="text-2xl font-black mb-6 text-gray-900">Recent History</h2>
				{#if trips.length === 0}
					<div class="text-center py-12 text-gray-400 italic">No trip history found</div>
				{:else}
					<div class="overflow-y-auto max-h-[500px] pr-4 space-y-0 relative">
						<!-- Timeline Line -->
						<div class="absolute left-4 top-4 bottom-4 w-0.5 bg-gray-200"></div>

						{#each trips as trip}
							<div class="relative pl-10 py-3 group">
								<!-- Timeline Dot -->
								<div class={`absolute left-[11px] top-6 w-3 h-3 rounded-full border-2 border-white shadow-sm z-10 ${trip.is_active ? 'bg-green-500 ring-4 ring-green-100' : 'bg-gray-300 group-hover:bg-brand-400 transition-colors'}`}></div>

								<div class="p-4 rounded-2xl bg-white/50 border border-gray-100 hover:bg-white hover:shadow-md hover:border-brand-100 transition-all duration-200">
									<div class="flex justify-between items-start mb-2">
										<div>
											<p class="font-bold text-gray-900 text-lg">{trip.route?.name || 'No Route'}</p>
											<p class="text-xs text-gray-500 font-medium flex items-center gap-1">
												<svg xmlns="http://www.w3.org/2000/svg" class="h-3 w-3" fill="none" viewBox="0 0 24 24" stroke="currentColor">
													<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8 7h12m0 0l-4-4m4 4l-4 4m0 6H4m0 0l4 4m-4-4l4-4" />
												</svg>
												{trip.bus.name}
											</p>
										</div>
										<span class={`px-2.5 py-1 rounded-lg text-xs font-bold ${trip.is_active ? 'bg-green-100 text-green-700' : 'bg-gray-100 text-gray-600'}`}>
											{trip.is_active ? 'Active' : 'Completed'}
										</span>
									</div>
									<div class="flex justify-between items-end mt-3 pt-3 border-t border-gray-100/50">
										<p class="font-mono text-xs text-brand-600 font-medium bg-brand-50 px-2 py-1 rounded">{new Date(trip.start_time).toLocaleDateString()}</p>
										<div class="text-right flex items-center gap-1 text-gray-700">
											<svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4 text-gray-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
												<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M17 20h5v-2a3 3 0 00-5.356-1.857M17 20H7m10 0v-2c0-.656-.126-1.283-.356-1.857M7 20H2v-2a3 3 0 015.356-1.857M7 20v-2c0-.656.126-1.283.356-1.857m0 0a5.002 5.002 0 019.288 0M15 7a3 3 0 11-6 0 3 3 0 016 0zm6 3a2 2 0 11-4 0 2 2 0 014 0zM7 10a2 2 0 11-4 0 2 2 0 014 0z" />
											</svg>
											<span class="text-sm font-bold">{trip.boarding_count || 0}</span>
										</div>
									</div>
								</div>
							</div>
						{/each}
					</div>
				{/if}
			</section>
		</div>
	{/if}
</div>
