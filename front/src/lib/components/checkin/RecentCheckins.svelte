<script lang="ts">
	import { tripService } from '$lib/services/trip';
	import type { EmployeeBoarding } from '$lib/types';

	let { tripId }: { tripId: number } = $props();

	let boardings = $state<EmployeeBoarding[]>([]);
	let error = $state('');
	let isLoading = $state(true);

	async function loadBoardings() {
		try {
			boardings = await tripService.listBoardings({ trip_id: tripId });
		} catch (err) {
			error = err instanceof Error ? err.message : 'Failed to load boardings';
		} finally {
			isLoading = false;
		}
	}

	$effect(() => {
		loadBoardings();
		
		const interval = setInterval(loadBoardings, 10000);
		return () => clearInterval(interval);
	});
</script>

<div class="glass-card p-6 h-full">
	<h3 class="text-xl font-black mb-4 text-gray-900 flex items-center gap-2">
		<span class="w-2 h-2 rounded-full bg-green-500 animate-pulse"></span>
		Recent Activity
	</h3>

	{#if isLoading}
		<div class="flex justify-center py-8">
			<div class="animate-spin rounded-full h-6 w-6 border-b-2 border-brand-500"></div>
		</div>
	{:else if error}
		<div class="p-3 rounded-lg bg-red-50 text-red-600 text-sm border border-red-100">
			{error}
		</div>
	{:else if boardings.length === 0}
		<div class="text-center py-8 text-gray-400 italic text-sm">
			No check-ins recorded yet
		</div>
	{:else}
		<ul class="space-y-3 max-h-[400px] overflow-y-auto pr-2">
			{#each boardings as boarding}
				<li class="p-3 rounded-xl bg-white/50 border border-gray-100 hover:bg-white hover:shadow-sm transition-all duration-200 flex justify-between items-center group">
					<div class="flex items-center gap-3">
						<div class="w-8 h-8 rounded-full bg-brand-100 text-brand-600 flex items-center justify-center text-xs font-bold">
							{boarding.employee.full_name.charAt(0)}
						</div>
						<span class="font-bold text-gray-800 text-sm">{boarding.employee.full_name}</span>
					</div>
					<span class="text-xs font-mono text-brand-500 bg-brand-50 px-2 py-1 rounded-md group-hover:bg-brand-100 transition-colors">
						{new Date(boarding.boarded_at).toLocaleTimeString([], {hour: '2-digit', minute:'2-digit'})}
					</span>
				</li>
			{/each}
		</ul>
	{/if}
</div>
