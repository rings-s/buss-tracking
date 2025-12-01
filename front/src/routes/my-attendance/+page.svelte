<script lang="ts">
	import { auth } from '$lib/stores/auth.svelte';
	import { AttendanceCalendar, LoadingSpinner } from '$lib/components';

	const now = new Date();
	let month = $state(now.getMonth() + 1);
	let year = $state(now.getFullYear());

	function handleDateSelect(date: string) {
		console.log('Selected date:', date);
	}
</script>

<div>
	<h1>My Attendance</h1>

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

	{#if auth.isLoading}
		<LoadingSpinner message="Loading..." />
	{:else if auth.user}
		<AttendanceCalendar
			employeeId={auth.user.id}
			{month}
			{year}
			onDateSelect={handleDateSelect}
		/>
	{:else}
		<p>Please log in to view your attendance</p>
	{/if}
</div>
