<script lang="ts">
	import { language } from '$lib/stores/language.svelte';
	import type { SupportedLocale } from '$lib/stores/language.svelte';

	let { mobile = false } = $props<{ mobile?: boolean }>();

	// Simply update the language store - the $effect in +layout.svelte will handle the rest
	function changeLanguage(locale: SupportedLocale) {
		language.setLocale(locale);
	}
</script>

{#if mobile}
	<!-- Mobile Toggle -->
	<div class="flex justify-center gap-1 p-2 bg-gray-50 rounded-xl border border-gray-200">
		<button
			onclick={() => changeLanguage('en')}
			class="flex-1 px-4 py-2 rounded-lg text-sm font-bold transition-all duration-200 {language.isEnglish
				? 'bg-brand-300 text-gray-900 shadow-md'
				: 'text-gray-600 hover:bg-gray-100'}"
			aria-label="Switch to English"
			aria-pressed={language.isEnglish}
		>
			EN
		</button>
		<button
			onclick={() => changeLanguage('ar')}
			class="flex-1 px-4 py-2 rounded-lg text-sm font-bold transition-all duration-200 {language.isArabic
				? 'bg-brand-300 text-gray-900 shadow-md'
				: 'text-gray-600 hover:bg-gray-100'}"
			aria-label="Switch to Arabic"
			aria-pressed={language.isArabic}
		>
			AR
		</button>
	</div>
{:else}
	<!-- Desktop Toggle -->
	<div class="flex items-center gap-1 px-2 py-1 bg-gray-50 rounded-lg border border-gray-200">
		<button
			onclick={() => changeLanguage('en')}
			class="px-3 py-1 rounded text-xs font-bold transition-all duration-200 {language.isEnglish
				? 'bg-brand-300 text-gray-900'
				: 'text-gray-600 hover:bg-gray-100'}"
			aria-label="Switch to English"
			aria-pressed={language.isEnglish}
		>
			EN
		</button>
		<div class="w-px h-4 bg-gray-300"></div>
		<button
			onclick={() => changeLanguage('ar')}
			class="px-3 py-1 rounded text-xs font-bold transition-all duration-200 {language.isArabic
				? 'bg-brand-300 text-gray-900'
				: 'text-gray-600 hover:bg-gray-100'}"
			aria-label="Switch to Arabic"
			aria-pressed={language.isArabic}
		>
			AR
		</button>
	</div>
{/if}
