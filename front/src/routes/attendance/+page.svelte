<script lang="ts">
	import { onMount, onDestroy } from 'svelte';
	import { tripService } from '$lib/services/trip';
	import type { EmployeeBoarding } from '$lib/types';
	import { fade, fly, scale } from 'svelte/transition';
	import { cubicOut } from 'svelte/easing';

	// ============================================================================
	// STATE MANAGEMENT - Svelte 5 Runes
	// ============================================================================

	let boardings = $state<EmployeeBoarding[]>([]);
	let filteredBoardings = $state<EmployeeBoarding[]>([]);
	let error = $state('');
	let isLoading = $state(true);
	let refreshInterval: ReturnType<typeof setInterval> | null = null;

	// Advanced filter state
	let searchQuery = $state('');
	let selectedTripFilter = $state<number | 'all'>('all');
	let dateFilter = $state<'today' | 'week' | 'month' | 'all'>('all');
	let sortBy = $state<'date' | 'name' | 'trip'>('date');
	let sortOrder = $state<'asc' | 'desc'>('desc');
	let currentPage = $state(1);
	let itemsPerPage = $state(10);

	// UI state
	let showFilters = $state(false);
	let selectedBoarding = $state<EmployeeBoarding | null>(null);
	let viewMode = $state<'table' | 'cards'>('table');

	// ============================================================================
	// DERIVED STATE - Complex Computations
	// ============================================================================

	// Extract unique trips for filter dropdown
	const uniqueTrips = $derived.by(() => {
		const trips = new Set(boardings.map(b => b.trip));
		return Array.from(trips).sort((a, b) => a - b);
	});

	// Statistics
	const stats = $derived.by(() => {
		return {
			total: boardings.length,
			today: boardings.filter(b => {
				const boardingDate = new Date(b.boarded_at);
				const today = new Date();
				return boardingDate.toDateString() === today.toDateString();
			}).length,
			thisWeek: boardings.filter(b => {
				const boardingDate = new Date(b.boarded_at);
				const weekAgo = new Date();
				weekAgo.setDate(weekAgo.getDate() - 7);
				return boardingDate >= weekAgo;
			}).length,
			uniqueEmployees: new Set(boardings.map(b => b.employee.id)).size,
			uniqueTrips: uniqueTrips.length
		};
	});

	// Filtered and sorted data
	const processedBoardings = $derived.by(() => {
		let result = [...boardings];

		// Apply search filter
		if (searchQuery.trim()) {
			const query = searchQuery.toLowerCase();
			result = result.filter(b =>
				b.employee.full_name.toLowerCase().includes(query) ||
				b.employee.email.toLowerCase().includes(query) ||
				b.trip.toString().includes(query)
			);
		}

		// Apply trip filter
		if (selectedTripFilter !== 'all') {
			result = result.filter(b => b.trip === selectedTripFilter);
		}

		// Apply date filter
		const now = new Date();
		if (dateFilter === 'today') {
			result = result.filter(b => {
				const boardingDate = new Date(b.boarded_at);
				return boardingDate.toDateString() === now.toDateString();
			});
		} else if (dateFilter === 'week') {
			const weekAgo = new Date();
			weekAgo.setDate(weekAgo.getDate() - 7);
			result = result.filter(b => new Date(b.boarded_at) >= weekAgo);
		} else if (dateFilter === 'month') {
			const monthAgo = new Date();
			monthAgo.setMonth(monthAgo.getMonth() - 1);
			result = result.filter(b => new Date(b.boarded_at) >= monthAgo);
		}

		// Apply sorting
		result.sort((a, b) => {
			let comparison = 0;

			switch (sortBy) {
				case 'date':
					comparison = new Date(a.boarded_at).getTime() - new Date(b.boarded_at).getTime();
					break;
				case 'name':
					comparison = a.employee.full_name.localeCompare(b.employee.full_name);
					break;
				case 'trip':
					comparison = a.trip - b.trip;
					break;
			}

			return sortOrder === 'asc' ? comparison : -comparison;
		});

		return result;
	});

	// Pagination
	const paginatedBoardings = $derived.by(() => {
		const start = (currentPage - 1) * itemsPerPage;
		const end = start + itemsPerPage;
		return processedBoardings.slice(start, end);
	});

	const totalPages = $derived(Math.ceil(processedBoardings.length / itemsPerPage));

	// ============================================================================
	// DATA FETCHING
	// ============================================================================

	async function loadBoardings() {
		try {
			isLoading = true;
			const result = await tripService.listBoardings();
			boardings = result;
			error = '';
		} catch (err) {
			error = err instanceof Error ? err.message : 'Failed to load attendance records';
			console.error('Error loading boardings:', err);
		} finally {
			isLoading = false;
		}
	}

	// ============================================================================
	// ACTIONS
	// ============================================================================

	function toggleSort(field: typeof sortBy) {
		if (sortBy === field) {
			sortOrder = sortOrder === 'asc' ? 'desc' : 'asc';
		} else {
			sortBy = field;
			sortOrder = 'desc';
		}
	}

	function resetFilters() {
		searchQuery = '';
		selectedTripFilter = 'all';
		dateFilter = 'all';
		sortBy = 'date';
		sortOrder = 'desc';
		currentPage = 1;
	}

	function exportToCSV() {
		const headers = ['Employee Name', 'Email', 'Phone', 'Boarded At', 'Trip ID'];
		const rows = processedBoardings.map(b => [
			b.employee.full_name,
			b.employee.email,
			b.employee.phone_number || 'N/A',
			new Date(b.boarded_at).toLocaleString(),
			b.trip.toString()
		]);

		const csv = [
			headers.join(','),
			...rows.map(row => row.map(cell => `"${cell}"`).join(','))
		].join('\n');

		const blob = new Blob([csv], { type: 'text/csv' });
		const url = URL.createObjectURL(blob);
		const a = document.createElement('a');
		a.href = url;
		a.download = `attendance-${new Date().toISOString().split('T')[0]}.csv`;
		a.click();
		URL.revokeObjectURL(url);
	}

	// ============================================================================
	// LIFECYCLE
	// ============================================================================

	onMount(() => {
		loadBoardings();
		// Auto-refresh every 30 seconds
		refreshInterval = setInterval(loadBoardings, 30000);
	});

	onDestroy(() => {
		if (refreshInterval) {
			clearInterval(refreshInterval);
		}
	});

	// ============================================================================
	// HELPER FUNCTIONS
	// ============================================================================

	function formatDateTime(dateString: string): string {
		return new Date(dateString).toLocaleString('en-US', {
			year: 'numeric',
			month: 'short',
			day: 'numeric',
			hour: '2-digit',
			minute: '2-digit'
		});
	}

	function formatTime(dateString: string): string {
		return new Date(dateString).toLocaleTimeString('en-US', {
			hour: '2-digit',
			minute: '2-digit'
		});
	}

	function getRelativeTime(dateString: string): string {
		const date = new Date(dateString);
		const now = new Date();
		const diffMs = now.getTime() - date.getTime();
		const diffMins = Math.floor(diffMs / 60000);
		const diffHours = Math.floor(diffMins / 60);
		const diffDays = Math.floor(diffHours / 24);

		if (diffMins < 1) return 'Just now';
		if (diffMins < 60) return `${diffMins}m ago`;
		if (diffHours < 24) return `${diffHours}h ago`;
		if (diffDays < 7) return `${diffDays}d ago`;
		return formatDateTime(dateString);
	}
</script>

<!-- ============================================================================ -->
<!-- MAIN LAYOUT -->
<!-- ============================================================================ -->

<div class="min-h-screen bg-gradient-to-br from-gray-50 via-white to-gray-50">
	<!-- Header Section -->
	<div class="bg-white border-b border-gray-200 sticky top-0 z-30 backdrop-blur-lg bg-white/80">
		<div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6">
			<div class="flex items-center justify-between flex-wrap gap-4">
				<div>
					<h1 class="text-3xl font-black text-gray-900 tracking-tight">
						Employee Attendance
					</h1>
					<p class="mt-1 text-sm text-gray-500 font-medium">
						Real-time tracking and reporting
					</p>
				</div>

				<div class="flex items-center gap-3">
					<!-- View Mode Toggle -->
					<div class="inline-flex rounded-lg border border-gray-200 p-1 bg-gray-50">
						<button
							onclick={() => viewMode = 'table'}
					aria-label="Table view"
							class="px-3 py-1.5 text-sm font-medium rounded-md transition-all duration-200 {viewMode === 'table' ? 'bg-white text-brand-600 shadow-sm' : 'text-gray-600 hover:text-gray-900'}"
						>
							<svg class="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
								<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3 10h18M3 14h18m-9-4v8m-7 0h14a2 2 0 002-2V8a2 2 0 00-2-2H5a2 2 0 00-2 2v8a2 2 0 002 2z" />
							</svg>
						</button>
						<button
							onclick={() => viewMode = 'cards'}
					aria-label="Card view"
							class="px-3 py-1.5 text-sm font-medium rounded-md transition-all duration-200 {viewMode === 'cards' ? 'bg-white text-brand-600 shadow-sm' : 'text-gray-600 hover:text-gray-900'}"
						>
							<svg class="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
								<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 6a2 2 0 012-2h2a2 2 0 012 2v2a2 2 0 01-2 2H6a2 2 0 01-2-2V6zM14 6a2 2 0 012-2h2a2 2 0 012 2v2a2 2 0 01-2 2h-2a2 2 0 01-2-2V6zM4 16a2 2 0 012-2h2a2 2 0 012 2v2a2 2 0 01-2 2H6a2 2 0 01-2-2v-2zM14 16a2 2 0 012-2h2a2 2 0 012 2v2a2 2 0 01-2 2h-2a2 2 0 01-2-2v-2z" />
							</svg>
						</button>
					</div>

					<!-- Export Button -->
					<button
						onclick={exportToCSV}
						disabled={processedBoardings.length === 0}
						class="btn-secondary flex items-center gap-2 disabled:opacity-50 disabled:cursor-not-allowed"
					>
						<svg class="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
							<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 10v6m0 0l-3-3m3 3l3-3m2 8H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
						</svg>
						<span class="hidden sm:inline">Export CSV</span>
					</button>

					<!-- Refresh Button -->
					<button
						onclick={loadBoardings}
						disabled={isLoading}
						class="btn-primary flex items-center gap-2 disabled:opacity-50"
					>
						<svg
							class="w-4 h-4 {isLoading ? 'animate-spin' : ''}"
							fill="none"
							viewBox="0 0 24 24"
							stroke="currentColor"
						>
							<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
						</svg>
						<span class="hidden sm:inline">Refresh</span>
					</button>
				</div>
			</div>
		</div>
	</div>

	<div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
		<!-- Statistics Cards -->
		{#if !isLoading}
			<div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4 mb-8" in:fly={{ y: 20, duration: 400, delay: 100 }}>
				<!-- Total Boardings -->
				<div class="glass-card p-6 hover:shadow-lg transition-all duration-200 group">
					<div class="flex items-center justify-between">
						<div>
							<p class="text-sm font-medium text-gray-500 uppercase tracking-wide">Total Boardings</p>
							<p class="text-3xl font-black text-gray-900 mt-2 group-hover:text-brand-600 transition-colors">{stats.total}</p>
						</div>
						<div class="w-12 h-12 rounded-xl bg-brand-100 flex items-center justify-center group-hover:bg-brand-200 transition-colors">
							<svg class="w-6 h-6 text-brand-600" fill="none" viewBox="0 0 24 24" stroke="currentColor">
								<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M17 20h5v-2a3 3 0 00-5.356-1.857M17 20H7m10 0v-2c0-.656-.126-1.283-.356-1.857M7 20H2v-2a3 3 0 015.356-1.857M7 20v-2c0-.656.126-1.283.356-1.857m0 0a5.002 5.002 0 019.288 0M15 7a3 3 0 11-6 0 3 3 0 016 0zm6 3a2 2 0 11-4 0 2 2 0 014 0zM7 10a2 2 0 11-4 0 2 2 0 014 0z" />
							</svg>
						</div>
					</div>
				</div>

				<!-- Today's Boardings -->
				<div class="glass-card p-6 hover:shadow-lg transition-all duration-200 group">
					<div class="flex items-center justify-between">
						<div>
							<p class="text-sm font-medium text-gray-500 uppercase tracking-wide">Today</p>
							<p class="text-3xl font-black text-gray-900 mt-2 group-hover:text-green-600 transition-colors">{stats.today}</p>
						</div>
						<div class="w-12 h-12 rounded-xl bg-green-100 flex items-center justify-center group-hover:bg-green-200 transition-colors">
							<svg class="w-6 h-6 text-green-600" fill="none" viewBox="0 0 24 24" stroke="currentColor">
								<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" />
							</svg>
						</div>
					</div>
				</div>

				<!-- Unique Employees -->
				<div class="glass-card p-6 hover:shadow-lg transition-all duration-200 group">
					<div class="flex items-center justify-between">
						<div>
							<p class="text-sm font-medium text-gray-500 uppercase tracking-wide">Employees</p>
							<p class="text-3xl font-black text-gray-900 mt-2 group-hover:text-purple-600 transition-colors">{stats.uniqueEmployees}</p>
						</div>
						<div class="w-12 h-12 rounded-xl bg-purple-100 flex items-center justify-center group-hover:bg-purple-200 transition-colors">
							<svg class="w-6 h-6 text-purple-600" fill="none" viewBox="0 0 24 24" stroke="currentColor">
								<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z" />
							</svg>
						</div>
					</div>
				</div>

				<!-- Unique Trips -->
				<div class="glass-card p-6 hover:shadow-lg transition-all duration-200 group">
					<div class="flex items-center justify-between">
						<div>
							<p class="text-sm font-medium text-gray-500 uppercase tracking-wide">Active Trips</p>
							<p class="text-3xl font-black text-gray-900 mt-2 group-hover:text-blue-600 transition-colors">{stats.uniqueTrips}</p>
						</div>
						<div class="w-12 h-12 rounded-xl bg-blue-100 flex items-center justify-center group-hover:bg-blue-200 transition-colors">
							<svg class="w-6 h-6 text-blue-600" fill="none" viewBox="0 0 24 24" stroke="currentColor">
								<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 20l-5.447-2.724A1 1 0 013 16.382V5.618a1 1 0 011.447-.894L9 7m0 13l6-3m-6 3V7m6 10l4.553 2.276A1 1 0 0021 18.382V7.618a1 1 0 00-.553-.894L15 4m0 13V4" />
							</svg>
						</div>
					</div>
				</div>
			</div>
		{/if}

		<!-- Filters Section -->
		<div class="glass-card p-6 mb-6" in:fly={{ y: 20, duration: 400, delay: 200 }}>
			<div class="flex items-center justify-between mb-4">
				<h2 class="text-lg font-bold text-gray-900 flex items-center gap-2">
					<svg class="w-5 h-5 text-brand-600" fill="none" viewBox="0 0 24 24" stroke="currentColor">
						<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3 4a1 1 0 011-1h16a1 1 0 011 1v2.586a1 1 0 01-.293.707l-6.414 6.414a1 1 0 00-.293.707V17l-4 4v-6.586a1 1 0 00-.293-.707L3.293 7.293A1 1 0 013 6.586V4z" />
					</svg>
					Filters & Search
				</h2>
				<button
					onclick={() => showFilters = !showFilters}
					class="text-sm font-medium text-brand-600 hover:text-brand-700 flex items-center gap-1"
				>
					{showFilters ? 'Hide' : 'Show'}
					<svg class="w-4 h-4 transition-transform duration-200 {showFilters ? 'rotate-180' : ''}" fill="none" viewBox="0 0 24 24" stroke="currentColor">
						<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 9l-7 7-7-7" />
					</svg>
				</button>
			</div>

			{#if showFilters}
				<div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4" transition:fly={{ y: -10, duration: 300 }}>
					<!-- Search Input -->
					<div class="col-span-full">
						<label for="search-input" class="block text-sm font-medium text-gray-700 mb-2">Search</label>
						<div class="relative">
							<input
						id="search-input"
								type="text"
								bind:value={searchQuery}
								placeholder="Search by name, email, or trip..."
								class="input-field pl-10"
							/>
							<svg class="absolute left-3 top-1/2 -translate-y-1/2 w-5 h-5 text-gray-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
								<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
							</svg>
						</div>
					</div>

					<!-- Trip Filter -->
					<div>
						<label for="trip-filter" class="block text-sm font-medium text-gray-700 mb-2">Trip</label>
						<select id="trip-filter" bind:value={selectedTripFilter} class="input-field">
							<option value="all">All Trips</option>
							{#each uniqueTrips as tripId}
								<option value={tripId}>Trip #{tripId}</option>
							{/each}
						</select>
					</div>

					<!-- Date Filter -->
					<div>
						<label for="date-filter" class="block text-sm font-medium text-gray-700 mb-2">Time Period</label>
						<select id="date-filter" bind:value={dateFilter} class="input-field">
							<option value="all">All Time</option>
							<option value="today">Today</option>
							<option value="week">This Week</option>
							<option value="month">This Month</option>
						</select>
					</div>

					<!-- Sort By -->
					<div>
						<label for="sort-by" class="block text-sm font-medium text-gray-700 mb-2">Sort By</label>
						<select id="sort-by" bind:value={sortBy} class="input-field">
							<option value="date">Date & Time</option>
							<option value="name">Employee Name</option>
							<option value="trip">Trip ID</option>
						</select>
					</div>

					<!-- Items Per Page -->
					<div>
						<label for="per-page" class="block text-sm font-medium text-gray-700 mb-2">Per Page</label>
						<select id="per-page" bind:value={itemsPerPage} class="input-field">
							<option value={10}>10</option>
							<option value={25}>25</option>
							<option value={50}>50</option>
							<option value={100}>100</option>
						</select>
					</div>

					<!-- Reset Button -->
					<div class="col-span-full flex justify-end">
						<button onclick={resetFilters} class="btn-secondary flex items-center gap-2">
							<svg class="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
								<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
							</svg>
							Reset Filters
						</button>
					</div>
				</div>
			{/if}

			<!-- Active Filters Display -->
			{#if searchQuery || selectedTripFilter !== 'all' || dateFilter !== 'all'}
				<div class="mt-4 flex flex-wrap gap-2">
					{#if searchQuery}
						<span class="inline-flex items-center gap-1 px-3 py-1 rounded-full text-sm font-medium bg-brand-100 text-brand-700" transition:scale>
							Search: {searchQuery}
							<button onclick={() => searchQuery = ''} aria-label="Remove search filter" class="hover:text-brand-900">
								<svg class="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
									<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
								</svg>
							</button>
						</span>
					{/if}
					{#if selectedTripFilter !== 'all'}
						<span class="inline-flex items-center gap-1 px-3 py-1 rounded-full text-sm font-medium bg-blue-100 text-blue-700" transition:scale>
							Trip #{selectedTripFilter}
							<button onclick={() => selectedTripFilter = 'all'} aria-label="Remove trip filter" class="hover:text-blue-900">
								<svg class="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
									<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
								</svg>
							</button>
						</span>
					{/if}
					{#if dateFilter !== 'all'}
						<span class="inline-flex items-center gap-1 px-3 py-1 rounded-full text-sm font-medium bg-green-100 text-green-700" transition:scale>
							{dateFilter.charAt(0).toUpperCase() + dateFilter.slice(1)}
							<button onclick={() => dateFilter = 'all'} aria-label="Remove date filter" class="hover:text-green-900">
								<svg class="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
									<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
								</svg>
							</button>
						</span>
					{/if}
				</div>
			{/if}
		</div>

		<!-- Results Count -->
		<div class="mb-4 flex items-center justify-between">
			<p class="text-sm text-gray-600">
				Showing <span class="font-semibold text-gray-900">{paginatedBoardings.length}</span> of
				<span class="font-semibold text-gray-900">{processedBoardings.length}</span> results
			</p>
		</div>

		<!-- Main Content -->
		{#if isLoading}
			<!-- Loading State -->
			<div class="glass-card p-12 flex flex-col items-center justify-center" in:fade>
				<div class="animate-spin rounded-full h-12 w-12 border-4 border-brand-200 border-t-brand-600 mb-4"></div>
				<p class="text-gray-600 font-medium">Loading attendance records...</p>
			</div>
		{:else if error}
			<!-- Error State -->
			<div class="glass-card p-8" in:fade>
				<div class="flex items-center gap-3 text-red-600">
					<svg class="w-6 h-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
						<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
					</svg>
					<span class="font-medium">{error}</span>
				</div>
			</div>
		{:else if paginatedBoardings.length === 0}
			<!-- Empty State -->
			<div class="glass-card p-12 text-center" in:fade>
				<div class="w-20 h-20 mx-auto rounded-full bg-gray-100 flex items-center justify-center mb-4">
					<svg class="w-10 h-10 text-gray-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
						<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
					</svg>
				</div>
				<h3 class="text-lg font-bold text-gray-900 mb-2">No Records Found</h3>
				<p class="text-gray-600 mb-4">Try adjusting your filters or search query</p>
				{#if searchQuery || selectedTripFilter !== 'all' || dateFilter !== 'all'}
					<button onclick={resetFilters} class="btn-primary">
						Reset Filters
					</button>
				{/if}
			</div>
		{:else if viewMode === 'table'}
			<!-- Table View -->
			<div class="glass-card overflow-hidden" in:fly={{ y: 20, duration: 400 }}>
				<div class="overflow-x-auto">
					<table class="w-full">
						<thead class="bg-gray-50 border-b border-gray-200">
							<tr>
								<th class="px-6 py-4 text-left">
									<button
										onclick={() => toggleSort('name')}
										class="flex items-center gap-2 text-xs font-bold text-gray-700 uppercase tracking-wider hover:text-brand-600"
									>
										Employee
										{#if sortBy === 'name'}
											<svg class="w-4 h-4 {sortOrder === 'asc' ? '' : 'rotate-180'}" fill="none" viewBox="0 0 24 24" stroke="currentColor">
												<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 15l7-7 7 7" />
											</svg>
										{/if}
									</button>
								</th>
								<th class="px-6 py-4 text-left text-xs font-bold text-gray-700 uppercase tracking-wider">
									Contact
								</th>
								<th class="px-6 py-4 text-left">
									<button
										onclick={() => toggleSort('date')}
										class="flex items-center gap-2 text-xs font-bold text-gray-700 uppercase tracking-wider hover:text-brand-600"
									>
										Boarded At
										{#if sortBy === 'date'}
											<svg class="w-4 h-4 {sortOrder === 'asc' ? '' : 'rotate-180'}" fill="none" viewBox="0 0 24 24" stroke="currentColor">
												<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 15l7-7 7 7" />
											</svg>
										{/if}
									</button>
								</th>
								<th class="px-6 py-4 text-left">
									<button
										onclick={() => toggleSort('trip')}
										class="flex items-center gap-2 text-xs font-bold text-gray-700 uppercase tracking-wider hover:text-brand-600"
									>
										Trip
										{#if sortBy === 'trip'}
											<svg class="w-4 h-4 {sortOrder === 'asc' ? '' : 'rotate-180'}" fill="none" viewBox="0 0 24 24" stroke="currentColor">
												<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 15l7-7 7 7" />
											</svg>
										{/if}
									</button>
								</th>
								<th class="px-6 py-4 text-right text-xs font-bold text-gray-700 uppercase tracking-wider">
									Actions
								</th>
							</tr>
						</thead>
						<tbody class="divide-y divide-gray-100">
							{#each paginatedBoardings as boarding, i (boarding.id)}
								<tr
									class="hover:bg-brand-50/30 transition-colors cursor-pointer"
									onclick={() => selectedBoarding = boarding}
									in:fly={{ y: 20, duration: 300, delay: i * 50 }}
								>
									<td class="px-6 py-4">
										<div class="flex items-center gap-3">
											<div class="w-10 h-10 rounded-full bg-brand-100 flex items-center justify-center">
												<span class="text-brand-700 font-bold text-sm">
													{boarding.employee.full_name.split(' ').map(n => n[0]).join('').toUpperCase().slice(0, 2)}
												</span>
											</div>
											<div>
												<p class="font-semibold text-gray-900">{boarding.employee.full_name}</p>
												<p class="text-xs text-gray-500">ID: {boarding.employee.id}</p>
											</div>
										</div>
									</td>
									<td class="px-6 py-4">
										<p class="text-sm text-gray-900">{boarding.employee.email}</p>
										<p class="text-xs text-gray-500">{boarding.employee.phone_number || 'N/A'}</p>
									</td>
									<td class="px-6 py-4">
										<p class="text-sm font-medium text-gray-900">{formatDateTime(boarding.boarded_at)}</p>
										<p class="text-xs text-gray-500">{getRelativeTime(boarding.boarded_at)}</p>
									</td>
									<td class="px-6 py-4">
										<span class="inline-flex items-center px-3 py-1 rounded-full text-xs font-semibold bg-brand-100 text-brand-800">
											Trip #{boarding.trip}
										</span>
									</td>
									<td class="px-6 py-4 text-right">
										<button
											onclick={(e) => { e.stopPropagation(); selectedBoarding = boarding; }}
											class="text-brand-600 hover:text-brand-700 font-medium text-sm"
										>
											View Details
										</button>
									</td>
								</tr>
							{/each}
						</tbody>
					</table>
				</div>
			</div>
		{:else}
			<!-- Card View -->
			<div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
				{#each paginatedBoardings as boarding, i (boarding.id)}
					<button
						onclick={() => selectedBoarding = boarding}
						class="glass-card p-6 hover:shadow-lg transition-all duration-200 text-left group"
						in:scale={{ duration: 300, delay: i * 50, start: 0.9 }}
					>
						<div class="flex items-start justify-between mb-4">
							<div class="w-12 h-12 rounded-full bg-brand-100 flex items-center justify-center group-hover:bg-brand-200 transition-colors">
								<span class="text-brand-700 font-bold">
									{boarding.employee.full_name.split(' ').map(n => n[0]).join('').toUpperCase().slice(0, 2)}
								</span>
							</div>
							<span class="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-semibold bg-brand-100 text-brand-800">
								Trip #{boarding.trip}
							</span>
						</div>

						<h3 class="font-bold text-gray-900 mb-1 group-hover:text-brand-600 transition-colors">
							{boarding.employee.full_name}
						</h3>
						<p class="text-sm text-gray-600 mb-3">{boarding.employee.email}</p>

						<div class="space-y-2 text-sm">
							<div class="flex items-center gap-2 text-gray-600">
								<svg class="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
									<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" />
								</svg>
								<span>{formatDateTime(boarding.boarded_at)}</span>
							</div>
							<p class="text-xs text-gray-500 ml-6">{getRelativeTime(boarding.boarded_at)}</p>
						</div>
					</button>
				{/each}
			</div>
		{/if}

		<!-- Pagination -->
		{#if totalPages > 1}
			<div class="mt-6 flex items-center justify-between" in:fly={{ y: 20, duration: 400, delay: 300 }}>
				<button
					onclick={() => currentPage = Math.max(1, currentPage - 1)}
					disabled={currentPage === 1}
					class="btn-secondary disabled:opacity-50 disabled:cursor-not-allowed flex items-center gap-2"
				>
					<svg class="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
						<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 19l-7-7 7-7" />
					</svg>
					Previous
				</button>

				<div class="flex items-center gap-2">
					{#each Array.from({ length: Math.min(5, totalPages) }, (_, i) => {
						const pageNum = Math.max(1, Math.min(totalPages - 4, currentPage - 2)) + i;
						return pageNum <= totalPages ? pageNum : null;
					}).filter((n): n is number => n !== null) as pageNum}
						<button
							onclick={() => currentPage = pageNum}
							class="w-10 h-10 rounded-lg font-medium transition-all duration-200 {currentPage === pageNum ? 'bg-brand-600 text-white' : 'bg-white text-gray-700 hover:bg-gray-100'}"
						>
							{pageNum}
						</button>
					{/each}
				</div>

				<button
					onclick={() => currentPage = Math.min(totalPages, currentPage + 1)}
					disabled={currentPage === totalPages}
					class="btn-secondary disabled:opacity-50 disabled:cursor-not-allowed flex items-center gap-2"
				>
					Next
					<svg class="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
						<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5l7 7-7 7" />
					</svg>
				</button>
			</div>
		{/if}
	</div>
</div>

<!-- Detail Modal -->
{#if selectedBoarding}
	<div
		class="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/50 backdrop-blur-sm"
		onclick={() => selectedBoarding = null}
		role="dialog"
		aria-modal="true"
		tabindex="-1"
		onkeydown={(e) => e.key === 'Escape' && (selectedBoarding = null)}
		transition:fade
	>
		<div
			class="glass-card max-w-lg w-full p-6 relative"
			onclick={(e) => e.stopPropagation()}
			role="presentation"
			in:scale={{ duration: 300, start: 0.9 }}
		>
			<button
			aria-label="Close modal"
				onclick={() => selectedBoarding = null}
				class="absolute top-4 right-4 text-gray-400 hover:text-gray-600"
			>
				<svg class="w-6 h-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
					<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
				</svg>
			</button>

			<h2 class="text-2xl font-black text-gray-900 mb-6">Boarding Details</h2>

			<div class="space-y-4">
				<div>
					<div class="block text-sm font-medium text-gray-500 mb-1">Employee Name</div>
					<p class="text-lg font-semibold text-gray-900">{selectedBoarding.employee.full_name}</p>
				</div>

				<div>
					<div class="block text-sm font-medium text-gray-500 mb-1">Employee ID</div>
					<p class="text-gray-900">{selectedBoarding.employee.id}</p>
				</div>

				<div>
					<div class="block text-sm font-medium text-gray-500 mb-1">Email</div>
					<p class="text-gray-900">{selectedBoarding.employee.email}</p>
				</div>

				<div>
					<div class="block text-sm font-medium text-gray-500 mb-1">Phone Number</div>
					<p class="text-gray-900">{selectedBoarding.employee.phone_number || 'Not provided'}</p>
				</div>

				<div>
					<div class="block text-sm font-medium text-gray-500 mb-1">NFC UID</div>
					<p class="text-gray-900 font-mono">{selectedBoarding.employee.nfc_uid || 'Not assigned'}</p>
				</div>

				<div>
					<div class="block text-sm font-medium text-gray-500 mb-1">Boarded At</div>
					<p class="text-gray-900">{formatDateTime(selectedBoarding.boarded_at)}</p>
					<p class="text-sm text-gray-500 mt-1">{getRelativeTime(selectedBoarding.boarded_at)}</p>
				</div>

				<div>
					<div class="block text-sm font-medium text-gray-500 mb-1">Trip ID</div>
					<span class="inline-flex items-center px-3 py-1 rounded-full text-sm font-semibold bg-brand-100 text-brand-800">
						Trip #{selectedBoarding.trip}
					</span>
				</div>

				<div>
					<div class="block text-sm font-medium text-gray-500 mb-1">Boarding ID</div>
					<p class="text-gray-900 font-mono">#{selectedBoarding.id}</p>
				</div>
			</div>

			<div class="mt-6 flex gap-3">
				<button onclick={() => selectedBoarding = null} class="btn-secondary flex-1">
					Close
				</button>
			</div>
		</div>
	</div>
{/if}
