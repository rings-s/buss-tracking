<script lang="ts">
	import { tripService } from '$lib/services/trip';
	import type { EmployeeBoarding } from '$lib/types';

	let {
		month,
		year
	}: {
		month: number;
		year: number;
	} = $props();

	let boardings = $state<EmployeeBoarding[]>([]);
	let error = $state('');
	let isLoading = $state(true);

	const monthName = $derived(
		new Date(year, month - 1).toLocaleString('default', { month: 'long' })
	);

	$effect(() => {
		isLoading = true;
		tripService.listBoardings()
			.then((result) => {
				boardings = result.filter(b => {
					const d = new Date(b.boarded_at);
					return d.getMonth() + 1 === month && d.getFullYear() === year;
				});
			})
			.catch((err) => {
				error = err instanceof Error ? err.message : 'Failed to load report';
			})
			.finally(() => {
				isLoading = false;
			});
	});

	const dailySummary = $derived(() => {
		const summary = new Map<string, number>();
		boardings.forEach(b => {
			const day = b.boarded_at.split('T')[0];
			summary.set(day, (summary.get(day) || 0) + 1);
		});
		return Array.from(summary.entries()).sort();
	});

	const uniqueEmployees = $derived(
		new Set(boardings.map(b => b.employee.id)).size
	);
</script>

<div>
	<h2>Monthly Report - {monthName} {year}</h2>

	{#if isLoading}
		<p>Loading...</p>
	{:else if error}
		<p>{error}</p>
	{:else}
		<div>
			<p>Total Unique Employees: {uniqueEmployees}</p>
			<p>Total Boardings: {boardings.length}</p>
		</div>

		<h3>Daily Breakdown</h3>
		{#if dailySummary().length === 0}
			<p>No data for this month</p>
		{:else}
			<table>
				<thead>
					<tr>
						<th>Date</th>
						<th>Boardings</th>
					</tr>
				</thead>
				<tbody>
					{#each dailySummary() as [day, count]}
						<tr>
							<td>{day}</td>
							<td>{count}</td>
						</tr>
					{/each}
				</tbody>
			</table>
		{/if}
	{/if}
</div>
