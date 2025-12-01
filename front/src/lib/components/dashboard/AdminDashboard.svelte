<script lang="ts">
	import { tripService } from '$lib/services/trip';
	import type { AdminDashboard } from '$lib/types';
	import StatsCards from './StatsCards.svelte';

	let data = $state<AdminDashboard | null>(null);
	let error = $state('');
	let isLoading = $state(true);

	$effect(() => {
		tripService.getDashboard()
			.then((result) => {
				data = result as AdminDashboard;
			})
			.catch((err) => {
				error = err instanceof Error ? err.message : 'Failed to load dashboard';
			})
			.finally(() => {
				isLoading = false;
			});
	});

	const stats = $derived(data ? [
		{ label: 'Total Buses', value: data.summary.total_buses },
		{ label: 'Buses on Route', value: data.summary.buses_on_route },
		{ label: 'Buses Idle', value: data.summary.buses_idle },
		{ label: 'Active Trips', value: data.summary.active_trips },
		{ label: "Today's Trips", value: data.summary.today_trips },
		{ label: "Today's Boardings", value: data.summary.today_boardings }
	] : []);
</script>

<div class="space-y-8">
	<div class="flex items-center justify-between">
		<div>
			<h1 class="text-3xl font-black text-gray-900 tracking-tight">Admin Overview</h1>
			<p class="text-gray-500 mt-1">Monitor fleet status and daily performance.</p>
		</div>
		<div class="flex gap-3">
			<button class="btn-secondary !py-2 !px-4 text-sm flex items-center gap-2">
				<svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
					<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-4l-4 4m0 0l-4-4m4 4V4" />
				</svg>
				Export Report
			</button>
			<button class="btn-primary !py-2 !px-4 text-sm flex items-center gap-2">
				<svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
					<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 6v6m0 0v6m0-6h6m-6 0H6" />
				</svg>
				Add Bus
			</button>
		</div>
	</div>

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
	{:else if data}
		<StatsCards {stats} />

		<section class="space-y-6">
			<div class="flex items-center justify-between">
				<h2 class="text-xl font-black text-gray-900 flex items-center gap-2">
					<span class="w-2 h-8 rounded-full bg-brand-500"></span>
					Fleet Status
				</h2>
				<div class="flex gap-2">
					<span class="px-3 py-1 rounded-full bg-green-100 text-green-700 text-xs font-bold uppercase tracking-wider">
						{data.summary.buses_on_route} Active
					</span>
					<span class="px-3 py-1 rounded-full bg-gray-100 text-gray-600 text-xs font-bold uppercase tracking-wider">
						{data.summary.buses_idle} Idle
					</span>
				</div>
			</div>

			{#if data.buses.length === 0}
				<div class="glass-card p-12 text-center">
					<div class="w-16 h-16 mx-auto rounded-full bg-gray-100 flex items-center justify-center text-gray-400 mb-4">
						<svg xmlns="http://www.w3.org/2000/svg" class="h-8 w-8" fill="none" viewBox="0 0 24 24" stroke="currentColor">
							<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8 7h12m0 0l-4-4m4 4l-4 4m0 6H4m0 0l4 4m-4-4l4-4" />
						</svg>
					</div>
					<p class="text-gray-500 font-medium">No buses registered in the system.</p>
				</div>
			{:else}
				<div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
					{#each data.buses as bus}
						<div class="glass-card p-6 group hover:border-brand-200 transition-all duration-300">
							<div class="flex justify-between items-start mb-4">
								<div class="flex items-center gap-3">
									<div class="w-10 h-10 rounded-full flex items-center justify-center {bus.active_trip ? 'bg-green-100 text-green-600' : 'bg-gray-100 text-gray-500'}">
										<svg xmlns="http://www.w3.org/2000/svg" class="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
											<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8 7h12m0 0l-4-4m4 4l-4 4m0 6H4m0 0l4 4m-4-4l4-4" />
										</svg>
									</div>
									<div>
										<h3 class="font-bold text-gray-900">{bus.name}</h3>
										<p class="text-xs font-mono text-gray-500 bg-gray-100 px-1.5 py-0.5 rounded inline-block">{bus.plate_number}</p>
									</div>
								</div>
								<span class={`w-3 h-3 rounded-full ${bus.active_trip ? 'bg-green-500 animate-pulse' : 'bg-gray-300'}`} title={bus.active_trip ? 'Active' : 'Idle'}></span>
							</div>

							<div class="space-y-3">
								<div class="flex items-center gap-2 text-sm text-gray-600">
									<svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4 text-gray-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
										<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z" />
									</svg>
									<span class="truncate">{bus.driver?.full_name || 'No driver assigned'}</span>
								</div>

								{#if bus.active_trip}
									<div class="p-3 rounded-lg bg-green-50 border border-green-100">
										<p class="text-xs font-bold text-green-700 uppercase tracking-wider mb-1">Current Trip</p>
										<div class="flex items-center justify-between">
											<span class="text-sm font-bold text-gray-900">Trip #{bus.active_trip.id}</span>
											<a href="/trips/{bus.active_trip.id}" class="text-xs font-bold text-brand-600 hover:text-brand-800 hover:underline">View</a>
										</div>
									</div>
								{:else}
									<div class="p-3 rounded-lg bg-gray-50 border border-gray-100">
										<p class="text-xs font-bold text-gray-500 uppercase tracking-wider">Status</p>
										<p class="text-sm font-medium text-gray-700">Parked / Idle</p>
									</div>
								{/if}
							</div>
						</div>
					{/each}
				</div>
			{/if}
		</section>
	{/if}
</div>
