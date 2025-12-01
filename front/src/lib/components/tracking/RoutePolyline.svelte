<script lang="ts">
	import type { BusLocation } from '$lib/types';

	let { locations }: { locations: BusLocation[] } = $props();

	const coordinates = $derived(
		locations.map(loc => ({ lat: loc.latitude, lng: loc.longitude }))
	);
</script>

<div 
	data-coordinates={JSON.stringify(coordinates)}
	data-color="#a2d2ff"
	class="hidden"
>
	Route path with {locations.length} points
</div>
