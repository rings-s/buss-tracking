<script lang="ts">
	let { stats }: { stats: { label: string; value: number; icon?: string; color?: string }[] } = $props();

	const getIcon = (label: string) => {
		const l = label.toLowerCase();
		if (l.includes('bus')) return 'M8 7h12m0 0l-4-4m4 4l-4 4m0 6H4m0 0l4 4m-4-4l4-4'; // Swap/Bus icon
		if (l.includes('trip')) return 'M9 20l-5.447-2.724A1 1 0 013 16.382V5.618a1 1 0 011.447-.894L9 7m0 13l6-3m-6 3V7m6 10l4.553 2.276A1 1 0 0021 18.382V7.618a1 1 0 00-.553-.894L15 4m0 13V4'; // Map
		if (l.includes('boarding')) return 'M17 20h5v-2a3 3 0 00-5.356-1.857M17 20H7m10 0v-2c0-.656-.126-1.283-.356-1.857M7 20H2v-2a3 3 0 015.356-1.857M7 20v-2c0-.656.126-1.283.356-1.857m0 0a5.002 5.002 0 019.288 0M15 7a3 3 0 11-6 0 3 3 0 016 0zm6 3a2 2 0 11-4 0 2 2 0 014 0zM7 10a2 2 0 11-4 0 2 2 0 014 0z'; // Users
		if (l.includes('idle')) return 'M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z'; // Clock
		return 'M13 10V3L4 14h7v7l9-11h-7z'; // Lightning/Default
	};

	const getGradient = (index: number) => {
		const gradients = [
			'from-brand-400/20 to-brand-600/20 border-brand-200/50 text-brand-700',
			'from-purple-400/20 to-purple-600/20 border-purple-200/50 text-purple-700',
			'from-emerald-400/20 to-emerald-600/20 border-emerald-200/50 text-emerald-700',
			'from-amber-400/20 to-amber-600/20 border-amber-200/50 text-amber-700',
			'from-rose-400/20 to-rose-600/20 border-rose-200/50 text-rose-700',
			'from-cyan-400/20 to-cyan-600/20 border-cyan-200/50 text-cyan-700',
		];
		return gradients[index % gradients.length];
	};
</script>

<div class="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-6 gap-4">
	{#each stats as stat, i}
		<div 
			class="relative overflow-hidden rounded-2xl border bg-white/60 backdrop-blur-sm p-4 transition-all duration-300 hover:-translate-y-1 hover:shadow-lg group {getGradient(i)}"
			style="animation: slide-up 0.5s ease-out forwards {i * 100}ms; opacity: 0;"
		>
			<!-- Decorative Background Blob -->
			<div class="absolute -right-4 -top-4 h-24 w-24 rounded-full bg-current opacity-5 blur-2xl transition-all duration-500 group-hover:scale-150"></div>

			<div class="relative z-10 flex flex-col h-full justify-between">
				<div class="mb-3 flex items-center justify-between">
					<div class="rounded-lg bg-white/50 p-2 shadow-sm ring-1 ring-black/5">
						<svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
							<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d={getIcon(stat.label)} />
						</svg>
					</div>
					<!-- Trend indicator placeholder (optional) -->
					<!-- <span class="text-[10px] font-bold text-green-600 bg-green-100 px-1.5 py-0.5 rounded-full">+5%</span> -->
				</div>
				
				<div>
					<p class="text-3xl font-black tracking-tight text-gray-900 group-hover:scale-105 transition-transform origin-left duration-200">
						{stat.value}
					</p>
					<p class="text-xs font-bold uppercase tracking-wider opacity-70 mt-1 truncate" title={stat.label}>
						{stat.label}
					</p>
				</div>
			</div>
		</div>
	{/each}
</div>
