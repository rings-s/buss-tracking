<script lang="ts">
	import { tripService } from '$lib/services/trip';
	import type { EmployeeBoarding } from '$lib/types';
	import AttendanceTable from './AttendanceTable.svelte';

	let { date }: { date: string } = $props();

	let boardings = $state<EmployeeBoarding[]>([]);
	let error = $state('');
	let isLoading = $state(true);

	$effect(() => {
		isLoading = true;
		tripService.listBoardings()
			.then((result) => {
				boardings = result.filter(b => 
					b.boarded_at.startsWith(date)
				);
			})
			.catch((err) => {
				error = err instanceof Error ? err.message : 'Failed to load report';
			})
			.finally(() => {
				isLoading = false;
			});
	});

	const uniqueEmployees = $derived(
		new Set(boardings.map(b => b.employee.id)).size
	);
</script>

<div>
	<h2>Daily Report - {date}</h2>

	{#if isLoading}
		<p>Loading...</p>
	{:else if error}
		<p>{error}</p>
	{:else}
		<div>
			<p>Total Present: {uniqueEmployees}</p>
			<p>Total Boardings: {boardings.length}</p>
		</div>

		<AttendanceTable {boardings} />
	{/if}
</div>
