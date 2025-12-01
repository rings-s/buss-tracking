<script lang="ts">
	import { goto } from '$app/navigation';
	import { tripService } from '$lib/services/trip';
	import { TripForm, ErrorMessage } from '$lib/components';
	import type { TripCreateData } from '$lib/types';

	let error = $state('');

	async function handleSubmit(data: TripCreateData) {
		try {
			const trip = await tripService.create(data);
			goto('/driver/active-trip?tripId=' + trip.id);
		} catch (err) {
			error = err instanceof Error ? err.message : 'Failed to start trip';
		}
	}

	function handleCancel() {
		goto('/driver');
	}

	function dismissError() {
		error = '';
	}
</script>

<div>
	<h1>Start New Trip</h1>

	{#if error}
		<ErrorMessage message={error} onDismiss={dismissError} />
	{/if}

	<TripForm onSubmit={handleSubmit} onCancel={handleCancel} />
</div>
