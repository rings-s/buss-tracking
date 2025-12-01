<script lang="ts">
	import { tripService } from '$lib/services/trip';
	import type { EmployeeBoarding } from '$lib/types';

	let {
		employeeId,
		month,
		year,
		onDateSelect
	}: {
		employeeId?: number;
		month: number;
		year: number;
		onDateSelect?: (date: string) => void;
	} = $props();

	let boardings = $state<EmployeeBoarding[]>([]);
	let error = $state('');
	let isLoading = $state(true);

	const daysInMonth = $derived(new Date(year, month, 0).getDate());
	const firstDayOfWeek = $derived(new Date(year, month - 1, 1).getDay());

	const attendanceDays = $derived(() => {
		const days = new Set<number>();
		boardings.forEach(b => {
			const d = new Date(b.boarded_at);
			if (d.getMonth() + 1 === month && d.getFullYear() === year) {
				days.add(d.getDate());
			}
		});
		return days;
	});

	$effect(() => {
		isLoading = true;
		const params = employeeId ? { employee_id: employeeId } : {};
		tripService.listBoardings(params)
			.then((result) => {
				boardings = result;
			})
			.catch((err) => {
				error = err instanceof Error ? err.message : 'Failed to load data';
			})
			.finally(() => {
				isLoading = false;
			});
	});

	function handleDayClick(day: number) {
		if (onDateSelect) {
			const m = month < 10 ? '0' + month : month;
			const d = day < 10 ? '0' + day : day;
			onDateSelect(year + '-' + m + '-' + d);
		}
	}
</script>

<div>
	<h3>
		{new Date(year, month - 1).toLocaleString('default', { month: 'long' })} {year}
	</h3>

	{#if isLoading}
		<p>Loading...</p>
	{:else if error}
		<p>{error}</p>
	{:else}
		<table>
			<thead>
				<tr>
					<th>Sun</th>
					<th>Mon</th>
					<th>Tue</th>
					<th>Wed</th>
					<th>Thu</th>
					<th>Fri</th>
					<th>Sat</th>
				</tr>
			</thead>
			<tbody>
				{#each Array(Math.ceil((daysInMonth + firstDayOfWeek) / 7)) as _, weekIndex}
					<tr>
						{#each Array(7) as _, dayIndex}
							{@const day = weekIndex * 7 + dayIndex - firstDayOfWeek + 1}
							<td>
								{#if day > 0 && day <= daysInMonth}
									<button 
										type="button"
										onclick={() => handleDayClick(day)}
										disabled={!onDateSelect}
									>
										{day}
										{#if attendanceDays().has(day)}
											<span>✓</span>
										{/if}
									</button>
								{/if}
							</td>
						{/each}
					</tr>
				{/each}
			</tbody>
		</table>
	{/if}
</div>
