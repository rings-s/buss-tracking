<script lang="ts">
	import { busCreateSchema } from '$lib/schemas';
	import type { Bus, BusCreateData } from '$lib/types';

	let {
		bus,
		onSubmit,
		onCancel
	}: {
		bus?: Bus;
		onSubmit: (data: BusCreateData) => void;
		onCancel: () => void;
	} = $props();

	let name = $state(bus?.name || '');
	let plate_number = $state(bus?.plate_number || '');
	let capacity = $state(bus?.capacity || 1);
	let driver = $state<number | null>(bus?.driver?.id || null);
	let active = $state(bus?.active ?? true);
	let error = $state('');

	function handleSubmit(e: Event) {
		e.preventDefault();
		error = '';

		try {
			const data: BusCreateData = {
				name,
				plate_number,
				capacity,
				driver,
				active
			};
			busCreateSchema.parse(data);
			onSubmit(data);
		} catch (err) {
			if (err instanceof Error) {
				error = err.message;
			}
		}
	}
</script>

<form onsubmit={handleSubmit}>
	<h3>{bus ? 'Edit Bus' : 'Add Bus'}</h3>

	{#if error}
		<div role="alert">{error}</div>
	{/if}

	<div>
		<label>
			Name
			<input type="text" bind:value={name} required />
		</label>
	</div>

	<div>
		<label>
			Plate Number
			<input type="text" bind:value={plate_number} required />
		</label>
	</div>

	<div>
		<label>
			Capacity
			<input type="number" bind:value={capacity} min="1" required />
		</label>
	</div>

	<div>
		<label>
			<input type="checkbox" bind:checked={active} />
			Active
		</label>
	</div>

	<div>
		<button type="submit">{bus ? 'Update' : 'Create'}</button>
		<button type="button" onclick={onCancel}>Cancel</button>
	</div>
</form>
