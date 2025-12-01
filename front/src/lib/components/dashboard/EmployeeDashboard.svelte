<script lang="ts">
	import { tripService } from '$lib/services/trip';
	import type { EmployeeDashboard } from '$lib/types';

	let data = $state<EmployeeDashboard | null>(null);
	let error = $state('');
	let isLoading = $state(true);

	$effect(() => {
		tripService.getDashboard()
			.then((result) => {
				data = result as EmployeeDashboard;
			})
			.catch((err) => {
				error = err instanceof Error ? err.message : 'Failed to load dashboard';
			})
			.finally(() => {
				isLoading = false;
			});
	});
</script>

<section class="glass-card p-8 h-full animate-fade-in flex flex-col">
	<div class="flex items-center justify-between mb-8">
		<h2 class="text-2xl font-black text-gray-900 flex items-center gap-3">
			<span class="relative flex h-4 w-4">
			  <span class="animate-ping absolute inline-flex h-full w-full rounded-full bg-green-400 opacity-75"></span>
			  <span class="relative inline-flex rounded-full h-4 w-4 bg-green-500"></span>
			</span>
			My Activity
		</h2>
		{#if data}
			<div class="flex flex-col items-end">
				<span class="text-xs font-bold text-gray-500 uppercase tracking-wider mb-1">Total Boardings</span>
				<span class="px-3 py-1 rounded-full bg-brand-100 text-brand-700 text-sm font-black tracking-tight">
					{data.summary.total_boardings}
				</span>
			</div>
		{/if}
	</div>

	{#if isLoading}
		<div class="flex justify-center py-12">
			<div class="animate-spin rounded-full h-10 w-10 border-b-2 border-brand-500"></div>
		</div>
	{:else if error}
		<div class="p-4 rounded-xl bg-red-50 text-red-600 border border-red-100">
			<p class="font-medium">{error}</p>
		</div>
	{:else if data}
		<div class="mb-8 p-6 rounded-2xl bg-gradient-to-br from-brand-500 to-brand-700 text-white shadow-lg shadow-brand-500/30 relative overflow-hidden group">
			<!-- Decorative circles -->
			<div class="absolute -right-10 -top-10 w-40 h-40 rounded-full bg-white/10 blur-2xl group-hover:bg-white/20 transition-colors duration-500"></div>
			<div class="absolute -left-10 -bottom-10 w-32 h-32 rounded-full bg-black/10 blur-2xl"></div>

			<div class="relative z-10">
				<p class="text-sm font-bold text-brand-100 uppercase tracking-wide mb-2">Today's Boardings</p>
				<div class="flex items-baseline gap-2">
					<p class="text-5xl font-black tracking-tight">{data.summary.today_boardings}</p>
					<span class="text-brand-200 font-medium">trips</span>
				</div>
				<div class="mt-4 h-1.5 w-full bg-black/20 rounded-full overflow-hidden">
					<div class="h-full bg-white/90 rounded-full" style="width: {Math.min((data.summary.today_boardings / 4) * 100, 100)}%"></div>
				</div>
				<p class="text-xs text-brand-200 mt-2 font-medium">Daily goal progress</p>
			</div>
		</div>

		{#if data.recent_boardings.length === 0}
			<div class="flex flex-col items-center justify-center py-12 text-center flex-1">
				<div class="w-20 h-20 rounded-full bg-gray-50 flex items-center justify-center text-gray-300 mb-4">
					<svg xmlns="http://www.w3.org/2000/svg" class="h-10 w-10" fill="none" viewBox="0 0 24 24" stroke="currentColor">
						<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M17 20h5v-2a3 3 0 00-5.356-1.857M17 20H7m10 0v-2c0-.656-.126-1.283-.356-1.857M7 20H2v-2a3 3 0 015.356-1.857M7 20v-2c0-.656.126-1.283.356-1.857m0 0a5.002 5.002 0 019.288 0M15 7a3 3 0 11-6 0 3 3 0 016 0zm6 3a2 2 0 11-4 0 2 2 0 014 0zM7 10a2 2 0 11-4 0 2 2 0 014 0z" />
					</svg>
				</div>
				<p class="text-gray-500 font-medium">No recent boardings recorded</p>
			</div>
		{:else}
			<div class="flex-1 flex flex-col min-h-0">
				<h3 class="text-sm font-bold text-gray-500 mb-4 uppercase tracking-wider flex items-center gap-2">
					<svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
						<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" />
					</svg>
					Recent History
				</h3>
				<div class="overflow-y-auto pr-2 space-y-3 custom-scrollbar flex-1">
					{#each data.recent_boardings as boarding}
						<div class="p-4 rounded-xl bg-white/50 border border-gray-100 hover:bg-white hover:shadow-md hover:border-brand-100 transition-all duration-200 group flex items-center justify-between">
							<div class="flex items-center gap-4">
								<div class="w-10 h-10 rounded-full bg-brand-50 text-brand-600 flex items-center justify-center group-hover:bg-brand-100 group-hover:scale-110 transition-all duration-200">
									<svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
										<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 10V3L4 14h7v7l9-11h-7z" />
									</svg>
								</div>
								<div>
									<p class="font-bold text-gray-900">Trip #{boarding.trip}</p>
									<p class="text-xs text-gray-500 font-medium">Successfully boarded</p>
								</div>
							</div>
							<div class="text-right">
								<p class="text-sm font-mono font-bold text-gray-900">{new Date(boarding.boarded_at).toLocaleTimeString([], {hour: '2-digit', minute:'2-digit'})}</p>
								<p class="text-[10px] uppercase tracking-wider text-gray-400 font-bold">{new Date(boarding.boarded_at).toLocaleDateString()}</p>
							</div>
						</div>
					{/each}
				</div>
			</div>
		{/if}
	{/if}
</section>
