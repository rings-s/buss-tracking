<script lang="ts">
	import { page } from '$app/stores';
	import { TripDetail } from '$lib/components';

	const tripId = $derived(Number($page.params.id));
</script>

<TripDetail {tripId} />
