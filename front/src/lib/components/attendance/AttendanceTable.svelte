<script lang="ts">
	import type { EmployeeBoarding } from '$lib/types';

	let {
		boardings,
		showTrip = true
	}: {
		boardings: EmployeeBoarding[];
		showTrip?: boolean;
	} = $props();
</script>

<div class="glass-card p-6 overflow-hidden">
	{#if boardings.length === 0}
		<div class="text-center py-8 text-gray-500">
			<p class="text-lg font-medium">No attendance records found</p>
		</div>
	{:else}
		<div class="overflow-x-auto">
			<table class="w-full text-left border-collapse">
				<thead>
					<tr class="border-b border-gray-200/50 text-sm uppercase tracking-wider text-gray-500">
						<th class="py-4 px-4 font-bold">Employee</th>
						<th class="py-4 px-4 font-bold">Email</th>
						<th class="py-4 px-4 font-bold">Date/Time</th>
						{#if showTrip}
							<th class="py-4 px-4 font-bold">Trip ID</th>
						{/if}
					</tr>
				</thead>
				<tbody class="text-gray-700">
					{#each boardings as boarding}
						<tr class="border-b border-gray-100/50 hover:bg-brand-50/50 transition-colors duration-200">
							<td class="py-4 px-4 font-medium text-gray-900">{boarding.employee.full_name}</td>
							<td class="py-4 px-4 text-gray-600">{boarding.employee.email}</td>
							<td class="py-4 px-4 font-mono text-sm text-brand-600">{new Date(boarding.boarded_at).toLocaleString()}</td>
							{#if showTrip}
								<td class="py-4 px-4">
									<span class="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-brand-100 text-brand-800">
										#{boarding.trip}
									</span>
								</td>
							{/if}
						</tr>
					{/each}
				</tbody>
			</table>
		</div>
	{/if}
</div>
