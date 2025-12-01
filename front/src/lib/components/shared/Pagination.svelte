<script lang="ts">
	let {
		currentPage,
		totalPages,
		onPageChange
	}: {
		currentPage: number;
		totalPages: number;
		onPageChange: (page: number) => void;
	} = $props();

	const hasPrevious = $derived(currentPage > 1);
	const hasNext = $derived(currentPage < totalPages);
</script>

<nav class="flex items-center justify-center gap-4 py-4">
	<button 
		type="button" 
		class="px-4 py-2 rounded-xl bg-white text-gray-700 font-bold border border-gray-200 hover:bg-gray-50 disabled:opacity-50 disabled:cursor-not-allowed transition-all"
		disabled={!hasPrevious} 
		onclick={() => onPageChange(currentPage - 1)}
	>
		Previous
	</button>
	<span class="text-sm font-bold text-gray-600">
		Page <span class="text-gray-900">{currentPage}</span> of <span class="text-gray-900">{totalPages}</span>
	</span>
	<button 
		type="button" 
		class="px-4 py-2 rounded-xl bg-white text-gray-700 font-bold border border-gray-200 hover:bg-gray-50 disabled:opacity-50 disabled:cursor-not-allowed transition-all"
		disabled={!hasNext} 
		onclick={() => onPageChange(currentPage + 1)}
	>
		Next
	</button>
</nav>
