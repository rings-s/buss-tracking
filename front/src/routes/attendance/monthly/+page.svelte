<script lang="ts">
	import { MonthlyReport } from '$lib/components';

	const now = new Date();
	let month = $state(now.getMonth() + 1);
	let year = $state(now.getFullYear());
</script>

<div>
	<h1>Monthly Attendance Report</h1>
	
	<div>
		<label>
			Month:
			<select bind:value={month}>
				{#each Array(12) as _, i}
					<option value={i + 1}>
						{new Date(2000, i).toLocaleString('default', { month: 'long' })}
					</option>
				{/each}
			</select>
		</label>
		<label>
			Year:
			<input type="number" bind:value={year} min="2020" max="2030" />
		</label>
	</div>

	<MonthlyReport {month} {year} />
</div>
