<script lang="ts">
	import { DailyReport, DatePicker } from '$lib/components';

	let date = $state(new Date().toISOString().split('T')[0]);

	function handleDateChange(value: string) {
		date = value;
	}
</script>

<div>
	<h1>Daily Attendance Report</h1>

	<DatePicker
		value={date}
		onChange={handleDateChange}
		label="Select Date"
	/>

	<DailyReport {date} />
</div>
