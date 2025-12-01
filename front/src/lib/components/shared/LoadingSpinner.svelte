<script lang="ts">
	let { message = 'Loading...' }: { message?: string } = $props();
</script>

<div class="flex flex-col items-center justify-center p-4">
	<div class="animate-spin rounded-full h-8 w-8 border-b-2 border-brand-500 mb-2"></div>
	{#if message}
		<span class="text-sm font-bold text-gray-500 animate-pulse">{message}</span>
	{/if}
</div>
