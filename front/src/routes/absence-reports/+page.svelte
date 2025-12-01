<script lang="ts">
	import { AbsenceReport, DatePicker } from '$lib/components';

	let date = $state(new Date().toISOString().split('T')[0]);

	function handleDateChange(value: string) {
		date = value;
	}
</script>

<div>
	<h1>Absence Reports</h1>

	<DatePicker
		value={date}
		onChange={handleDateChange}
		label="Select Date"
	/>

	<AbsenceReport {date} />
</div>
