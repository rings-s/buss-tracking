<script lang="ts">
	let {
		position,
		driverName,
		busName
	}: {
		position: { lat: number; lng: number };
		driverName: string;
		busName: string;
	} = $props();
</script>

<div 
	data-lat={position.lat} 
	data-lng={position.lng}
	class="relative flex flex-col items-center justify-center transform -translate-x-1/2 -translate-y-full"
>
	<div class="relative z-10 p-1 bg-white rounded-full shadow-lg border-2 border-brand-500">
		<div class="w-8 h-8 rounded-full bg-brand-100 flex items-center justify-center text-brand-700 font-bold text-xs">
			<svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5" viewBox="0 0 20 20" fill="currentColor">
				<path d="M8 16.5a1.5 1.5 0 11-3 0 1.5 1.5 0 013 0zM15 16.5a1.5 1.5 0 11-3 0 1.5 1.5 0 013 0z" />
				<path d="M3 4a1 1 0 00-1 1v10a1 1 0 001 1h1.05a2.5 2.5 0 014.9 0H10a1 1 0 001-1V5a1 1 0 00-1-1H3zM14 7a1 1 0 00-1 1v6.05A2.5 2.5 0 0115.95 16H17a1 1 0 001-1v-5a1 1 0 00-.293-.707l-2-2A1 1 0 0015 7h-1z" />
			</svg>
		</div>
	</div>
	<div class="w-0.5 h-3 bg-brand-500 -mt-1 relative z-0"></div>
	
	<div class="absolute -bottom-8 bg-white/90 backdrop-blur-sm px-2 py-1 rounded-md shadow-sm border border-gray-200 whitespace-nowrap text-xs font-bold text-gray-800 pointer-events-none">
		{busName}
	</div>
</div>
