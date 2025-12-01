<script lang="ts">
	let {
		value,
		onChange,
		label,
		placeholder = 'Select date'
	}: {
		value: string;
		onChange: (value: string) => void;
		label?: string;
		placeholder?: string;
	} = $props();
</script>

<div>
	{#if label}
		<label class="block text-sm font-bold text-gray-700 mb-2">
			{label}
			<input
				type="date"
				class="input-field mt-1"
				{value}
				{placeholder}
				onchange={(e) => onChange(e.currentTarget.value)}
			/>
		</label>
	{:else}
		<input
			type="date"
			class="input-field"
			{value}
			{placeholder}
			onchange={(e) => onChange(e.currentTarget.value)}
		/>
	{/if}
</div>
