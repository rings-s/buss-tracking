<script lang="ts" generics="T">
	interface Column<T> {
		key: string;
		label: string;
		render?: (item: T) => string;
	}

	let {
		columns,
		data,
		onRowClick
	}: {
		columns: Column<T>[];
		data: T[];
		onRowClick?: (item: T) => void;
	} = $props();

	function getCellValue(item: T, column: Column<T>): string {
		if (column.render) {
			return column.render(item);
		}
		const value = (item as Record<string, unknown>)[column.key];
		return value != null ? String(value) : '';
	}
</script>

<div class="glass-card overflow-hidden">
	<div class="overflow-x-auto">
		<table class="w-full text-left border-collapse">
			<thead>
				<tr class="bg-gray-50/80 border-b border-gray-200/50 text-xs uppercase tracking-wider text-gray-500">
					{#each columns as column}
						<th class="py-4 px-6 font-bold">{column.label}</th>
					{/each}
				</tr>
			</thead>
			<tbody class="divide-y divide-gray-100/50">
				{#each data as item}
					<tr
						class="hover:bg-brand-50/30 transition-colors duration-200 {onRowClick ? 'cursor-pointer' : ''}"
						onclick={() => onRowClick?.(item)}
						onkeydown={(e) => e.key === 'Enter' && onRowClick?.(item)}
						tabindex={onRowClick ? 0 : -1}
						role={onRowClick ? 'button' : undefined}
					>
						{#each columns as column}
							<td class="py-4 px-6 text-gray-700 text-sm">{getCellValue(item, column)}</td>
						{/each}
					</tr>
				{/each}
			</tbody>
		</table>
	</div>
</div>
