<script lang="ts">
	import type { EmployeeBoarding } from '$lib/types';

	let {
		boarding,
		error,
		onReset
	}: {
		boarding: EmployeeBoarding | null;
		error: string | null;
		onReset: () => void;
	} = $props();
</script>

<div class="glass-card p-8 max-w-md mx-auto text-center animate-scale-in">
	{#if error}
		<div role="alert" class="space-y-4">
			<div class="w-16 h-16 bg-red-100 rounded-full flex items-center justify-center mx-auto mb-4">
				<svg xmlns="http://www.w3.org/2000/svg" class="h-8 w-8 text-red-600" fill="none" viewBox="0 0 24 24" stroke="currentColor">
					<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
				</svg>
			</div>
			<h3 class="text-2xl font-black text-gray-900">Check-in Failed</h3>
			<p class="text-gray-600 bg-red-50 p-3 rounded-xl border border-red-100">{error}</p>
			<button type="button" class="btn-primary w-full mt-6" onclick={onReset}>Try Again</button>
		</div>
	{:else if boarding}
		<div class="space-y-4">
			<div class="w-16 h-16 bg-green-100 rounded-full flex items-center justify-center mx-auto mb-4">
				<svg xmlns="http://www.w3.org/2000/svg" class="h-8 w-8 text-green-600" fill="none" viewBox="0 0 24 24" stroke="currentColor">
					<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7" />
				</svg>
			</div>
			<h3 class="text-2xl font-black text-gray-900">Check-in Successful</h3>
			
			<div class="bg-brand-50/50 p-6 rounded-2xl border border-brand-100/50 text-left space-y-3">
				<div>
					<span class="text-xs font-bold text-gray-400 uppercase tracking-wider">Employee</span>
					<p class="text-lg font-bold text-gray-900">{boarding.employee.full_name}</p>
				</div>
				<div>
					<span class="text-xs font-bold text-gray-400 uppercase tracking-wider">Email</span>
					<p class="text-gray-700">{boarding.employee.email}</p>
				</div>
				<div>
					<span class="text-xs font-bold text-gray-400 uppercase tracking-wider">Time</span>
					<p class="font-mono text-brand-600">{new Date(boarding.boarded_at).toLocaleString()}</p>
				</div>
			</div>

			<button type="button" class="btn-primary w-full mt-6" onclick={onReset}>Next Check-in</button>
		</div>
	{/if}
</div>
