<script lang="ts">
	import { tripService } from '$lib/services/trip';
	import { checkInDataSchema } from '$lib/schemas';
	import type { EmployeeBoarding } from '$lib/types';

	let { tripId }: { tripId: number } = $props();

	let nfcUid = $state('');
	let isLoading = $state(false);
	let lastBoarding = $state<EmployeeBoarding | null>(null);
	let error = $state('');

	async function handleScan(e: Event) {
		e.preventDefault();
		if (!nfcUid.trim()) return;

		isLoading = true;
		error = '';
		lastBoarding = null;

		try {
			const data = { nfc_uid: nfcUid.trim(), trip_id: tripId };
			checkInDataSchema.parse(data);
			
			const response = await tripService.checkIn(data);
			lastBoarding = response.boarding;
			nfcUid = '';
		} catch (err) {
			error = err instanceof Error ? err.message : 'Check-in failed';
		} finally {
			isLoading = false;
		}
	}
</script>

<div class="glass-card p-8 animate-slide-up">
	<h2 class="text-2xl font-black mb-6 text-gray-900 flex items-center gap-3">
		<svg xmlns="http://www.w3.org/2000/svg" class="h-8 w-8 text-brand-500" fill="none" viewBox="0 0 24 24" stroke="currentColor">
			<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 4v1m6 11h2m-6 0h-2v4m0-11v3m0 0h.01M12 12h4.01M16 20h4M4 12h4m12 0h.01M5 8h2a1 1 0 001-1V5a1 1 0 00-1-1H5a1 1 0 00-1 1v2a1 1 0 001 1zm12 0h2a1 1 0 001-1V5a1 1 0 00-1-1h-2a1 1 0 00-1 1v2a1 1 0 001 1zM5 20h2a1 1 0 001-1v-2a1 1 0 00-1-1H5a1 1 0 00-1 1v2a1 1 0 001 1z" />
		</svg>
		NFC Check-in
	</h2>

	<form onsubmit={handleScan} class="space-y-6">
		<div>
			<label for="nfc-uid" class="block text-sm font-bold text-gray-700 mb-2">
				NFC UID
			</label>
			<div class="relative">
				<input 
					id="nfc-uid"
					type="text" 
					class="input-field pl-10 font-mono"
					bind:value={nfcUid} 
					placeholder="Scan or enter NFC UID"
					disabled={isLoading}
				/>
				<div class="pointer-events-none absolute inset-y-0 left-0 flex items-center px-3 text-gray-400">
					<svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
						<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 11c0 3.517-1.009 6.799-2.753 9.571m-3.44-2.04l.054-.09A13.916 13.916 0 008 11a4 4 0 118 0c0 1.017-.07 2.019-.203 3m-2.118 6.844A21.88 21.88 0 0015.171 17m3.839 1.132c.645-2.266.99-4.659.99-7.131A8 8 0 008 4.07M3 15.364c.64-1.319 1-2.8 1-4.364 0-1.457.2-2.85.577-4.147" />
					</svg>
				</div>
			</div>
		</div>
		<button type="submit" class="btn-primary flex justify-center items-center gap-2" disabled={isLoading || !nfcUid.trim()}>
			{#if isLoading}
				<div class="animate-spin rounded-full h-5 w-5 border-b-2 border-gray-900"></div>
				Processing...
			{:else}
				Check In
			{/if}
		</button>
	</form>

	{#if error}
		<div role="alert" class="mt-6 p-4 rounded-xl bg-red-50 text-red-600 border border-red-100 flex items-center gap-3 animate-slide-down">
			<svg xmlns="http://www.w3.org/2000/svg" class="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
				<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
			</svg>
			<span class="font-medium">{error}</span>
		</div>
	{/if}

	{#if lastBoarding}
		<div class="mt-6 p-6 rounded-2xl bg-green-50 border border-green-100 animate-scale-in">
			<div class="flex items-center gap-3 mb-4">
				<div class="w-10 h-10 rounded-full bg-green-100 flex items-center justify-center text-green-600">
					<svg xmlns="http://www.w3.org/2000/svg" class="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
						<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7" />
					</svg>
				</div>
				<h3 class="text-xl font-black text-gray-900">Check-in Successful</h3>
			</div>
			<div class="space-y-2 pl-13">
				<div>
					<span class="text-xs font-bold text-gray-500 uppercase tracking-wider">Employee</span>
					<p class="font-bold text-gray-900">{lastBoarding.employee.full_name}</p>
				</div>
				<div>
					<span class="text-xs font-bold text-gray-500 uppercase tracking-wider">Time</span>
					<p class="font-mono text-green-700">{new Date(lastBoarding.boarded_at).toLocaleString()}</p>
				</div>
			</div>
		</div>
	{/if}
</div>
