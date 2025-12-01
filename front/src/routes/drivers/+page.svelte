<script lang="ts">
	import { apiClient } from '$lib/services/api-client';
	import { LoadingSpinner, ErrorMessage, DataTable } from '$lib/components';
	import type { User } from '$lib/types';

	let drivers = $state<User[]>([]);
	let error = $state('');
	let isLoading = $state(true);

	const columns = [
		{ key: 'full_name', label: 'Name' },
		{ key: 'email', label: 'Email' },
		{ key: 'phone_number', label: 'Phone' },
		{ key: 'is_active', label: 'Status', render: (d: User) => d.is_active ? 'Active' : 'Inactive' }
	];

	$effect(() => {
		apiClient.get<User[]>('/api/auth/users/', { params: { role: 'driver' } })
			.then((result) => {
				drivers = result;
			})
			.catch((err) => {
				error = err instanceof Error ? err.message : 'Failed to load drivers';
			})
			.finally(() => {
				isLoading = false;
			});
	});
</script>

<div>
	<h1>Drivers</h1>

	{#if isLoading}
		<LoadingSpinner message="Loading drivers..." />
	{:else if error}
		<ErrorMessage message={error} />
	{:else if drivers.length === 0}
		<p>No drivers found</p>
	{:else}
		<DataTable {columns} data={drivers} />
	{/if}
</div>
