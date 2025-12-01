<script lang="ts">
	import type { EmployeeBoarding } from '$lib/types';

	let { boarding }: { boarding: EmployeeBoarding } = $props();
</script>

<div>
	<h2>Boarding Details</h2>
	
	<dl>
		<dt>Employee</dt>
		<dd>{boarding.employee.full_name}</dd>
		
		<dt>Email</dt>
		<dd>{boarding.employee.email}</dd>
		
		<dt>Phone</dt>
		<dd>{boarding.employee.phone_number}</dd>
		
		<dt>Trip ID</dt>
		<dd>{boarding.trip}</dd>
		
		<dt>Boarded At</dt>
		<dd>{new Date(boarding.boarded_at).toLocaleString()}</dd>
	</dl>
</div>
