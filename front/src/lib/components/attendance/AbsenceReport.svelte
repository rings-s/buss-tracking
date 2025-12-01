<script lang="ts">
	import { apiClient } from '$lib/services/api-client';
	import type { AbsenceReport } from '$lib/types';

	let { date }: { date: string } = $props();

	let report = $state<AbsenceReport | null>(null);
	let error = $state('');
	let isLoading = $state(true);

	$effect(() => {
		isLoading = true;
		apiClient.get<AbsenceReport>('/api/admin/absence-report/', { params: { date } })
			.then((result) => {
				report = result;
			})
			.catch((err) => {
				error = err instanceof Error ? err.message : 'Failed to load report';
			})
			.finally(() => {
				isLoading = false;
			});
	});
</script>

<div class="glass-card p-8">
	<h2 class="text-2xl font-black mb-6 text-gray-900">Absence Report <span class="text-brand-500">— {date}</span></h2>

	{#if isLoading}
		<div class="flex justify-center py-12">
			<div class="animate-spin rounded-full h-8 w-8 border-b-2 border-brand-500"></div>
		</div>
	{:else if error}
		<div class="p-4 rounded-xl bg-red-50 text-red-600 border border-red-100">
			<p class="font-bold">Error</p>
			<p>{error}</p>
		</div>
	{:else if report}
		<div class="mb-8 p-4 rounded-xl bg-brand-50/50 border border-brand-100/50 inline-block">
			<p class="text-sm font-bold text-brand-800 uppercase tracking-wide">Total Absent</p>
			<p class="text-3xl font-black text-brand-600">{report.total_absent}</p>
		</div>

		{#if report.absent_employees.length === 0}
			<div class="text-center py-8 text-gray-500 bg-gray-50/50 rounded-xl border border-gray-100">
				<p class="text-lg font-medium">No absences recorded</p>
				<p class="text-sm">Everyone is present today!</p>
			</div>
		{:else}
			<div class="overflow-x-auto rounded-xl border border-gray-200/50">
				<table class="w-full text-left border-collapse">
					<thead class="bg-gray-50/80">
						<tr class="border-b border-gray-200/50 text-xs uppercase tracking-wider text-gray-500">
							<th class="py-3 px-4 font-bold">Name</th>
							<th class="py-3 px-4 font-bold">Email</th>
							<th class="py-3 px-4 font-bold">Phone</th>
						</tr>
					</thead>
					<tbody class="bg-white/50">
						{#each report.absent_employees as employee}
							<tr class="border-b border-gray-100/50 hover:bg-red-50/30 transition-colors duration-200">
								<td class="py-3 px-4 font-bold text-gray-900">{employee.full_name}</td>
								<td class="py-3 px-4 text-gray-600">{employee.email}</td>
								<td class="py-3 px-4 font-mono text-sm text-gray-500">{employee.phone_number}</td>
							</tr>
						{/each}
					</tbody>
				</table>
			</div>
		{/if}
	{/if}
</div>
