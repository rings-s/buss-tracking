<script lang="ts">
	let { message, onDismiss }: { message: string; onDismiss?: () => void } = $props();
</script>

<div role="alert" class="p-4 rounded-xl bg-red-50 text-red-600 border border-red-100 flex items-center justify-between gap-3 animate-slide-down">
	<div class="flex items-center gap-3">
		<svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5 flex-shrink-0" fill="none" viewBox="0 0 24 24" stroke="currentColor">
			<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
		</svg>
		<span class="font-medium">{message}</span>
	</div>
	{#if onDismiss}
		<button type="button" class="p-1 hover:bg-red-100 rounded-lg transition-colors" onclick={onDismiss} aria-label="Dismiss">
			<svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5" viewBox="0 0 20 20" fill="currentColor">
				<path fill-rule="evenodd" d="M4.293 4.293a1 1 0 011.414 0L10 8.586l4.293-4.293a1 1 0 111.414 1.414L11.414 10l4.293 4.293a1 1 0 01-1.414 1.414L10 11.414l-4.293 4.293a1 1 0 01-1.414-1.414L8.586 10 4.293 5.707a1 1 0 010-1.414z" clip-rule="evenodd" />
			</svg>
		</button>
	{/if}
</div>
