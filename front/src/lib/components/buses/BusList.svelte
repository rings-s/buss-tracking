<script lang="ts">
	import { busService } from '$lib/services/bus';
	import type { Bus } from '$lib/types';

	let {
		onEdit,
		onCreate
	}: {
		onEdit?: (bus: Bus) => void;
		onCreate?: () => void;
	} = $props();

	let buses = $state<Bus[]>([]);
	let error = $state('');
	let isLoading = $state(true);

	async function loadBuses() {
		isLoading = true;
		try {
			buses = await busService.list();
		} catch (err) {
			error = err instanceof Error ? err.message : 'Failed to load buses';
		} finally {
			isLoading = false;
		}
	}

	async function handleDelete(id: number) {
		if (!confirm('Are you sure you want to delete this bus?')) return;
		
		try {
			await busService.delete(id);
			buses = buses.filter(b => b.id !== id);
		} catch (err) {
			error = err instanceof Error ? err.message : 'Failed to delete bus';
		}
	}

	$effect(() => {
		loadBuses();
	});
</script>

<div>
	<div>
		<h2>Buses</h2>
		{#if onCreate}
			<button type="button" onclick={onCreate}>Add Bus</button>
		{/if}
	</div>

	{#if isLoading}
		<p>Loading...</p>
	{:else if error}
		<p>{error}</p>
	{:else if buses.length === 0}
		<p>No buses found</p>
	{:else}
		<table>
			<thead>
				<tr>
					<th>Name</th>
					<th>Plate Number</th>
					<th>Capacity</th>
					<th>Driver</th>
					<th>Status</th>
					<th>Actions</th>
				</tr>
			</thead>
			<tbody>
				{#each buses as bus}
					<tr>
						<td>{bus.name}</td>
						<td>{bus.plate_number}</td>
						<td>{bus.capacity}</td>
						<td>{bus.driver?.full_name || 'Unassigned'}</td>
						<td>{bus.active ? 'Active' : 'Inactive'}</td>
						<td>
							{#if onEdit}
								<button type="button" onclick={() => onEdit(bus)}>Edit</button>
							{/if}
							<button type="button" onclick={() => handleDelete(bus.id)}>Delete</button>
						</td>
					</tr>
				{/each}
			</tbody>
		</table>
	{/if}
</div>
