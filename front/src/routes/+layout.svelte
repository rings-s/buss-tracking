<script lang="ts">
	import { Navbar, Footer } from '$lib/components';
	import type { Snippet } from 'svelte';
	import { auth } from '$lib/stores/auth.svelte';
	import { language } from '$lib/stores/language.svelte';
	import { setLocale, loadTranslations } from '$lib/i18n';
	import { browser } from '$app/environment';

	import './layout.css';

	let { children }: { children: Snippet } = $props();

	// PWA State
	let deferredPrompt: any = $state(null);
	let showInstallPrompt = $state(false);
	let updateAvailable = $state(false);

	// Initialize and watch for language changes with $effect
	$effect(() => {
		if (!browser) return;

		const currentLocale = language.locale;

		// Load translations when locale changes
		setLocale(currentLocale);
		loadTranslations(currentLocale, '/');
	});

	// PWA setup with $effect
	$effect(() => {
		if (!browser) return;

		// PWA Install Prompt
		const handleBeforeInstall = (e: Event) => {
			e.preventDefault();
			deferredPrompt = e;
			showInstallPrompt = true;
		};

		window.addEventListener('beforeinstallprompt', handleBeforeInstall);

		// Service Worker Update Handler
		if ('serviceWorker' in navigator) {
			navigator.serviceWorker.ready.then((registration) => {
				registration.addEventListener('updatefound', () => {
					const newWorker = registration.installing;
					if (newWorker) {
						newWorker.addEventListener('statechange', () => {
							if (newWorker.state === 'installed' && navigator.serviceWorker.controller) {
								updateAvailable = true;
							}
						});
					}
				});
			});
		}

		// Cleanup
		return () => {
			window.removeEventListener('beforeinstallprompt', handleBeforeInstall);
		};
	});

	async function installPWA() {
		if (!deferredPrompt) return;

		deferredPrompt.prompt();
		const { outcome } = await deferredPrompt.userChoice;

		if (outcome === 'accepted') {
			showInstallPrompt = false;
		}
		deferredPrompt = null;
	}

	function reloadApp() {
		window.location.reload();
	}
</script>

{#if showInstallPrompt}
	<div
		class="fixed bottom-4 left-4 right-4 md:left-auto md:right-4 md:max-w-sm bg-white border border-gray-200 rounded-xl shadow-lg p-4 z-50"
	>
		<div class="flex items-start gap-3">
			<div
				class="w-12 h-12 rounded-xl bg-brand-100 flex items-center justify-center flex-shrink-0"
			>
				<svg
					xmlns="http://www.w3.org/2000/svg"
					class="h-6 w-6 text-brand-600"
					fill="none"
					viewBox="0 0 24 24"
					stroke="currentColor"
				>
					<path
						stroke-linecap="round"
						stroke-linejoin="round"
						stroke-width="2"
						d="M12 10v6m0 0l-3-3m3 3l3-3m2 8H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z"
					/>
				</svg>
			</div>
			<div class="flex-1">
				<h3 class="font-bold text-gray-900 mb-1">Install App</h3>
				<p class="text-sm text-gray-600 mb-3">
					Install Bus Tracker for faster access and offline support
				</p>
				<div class="flex gap-2">
					<button
						onclick={installPWA}
						class="px-4 py-2 bg-brand-600 text-white rounded-lg text-sm font-medium hover:bg-brand-700 transition-colors"
					>
						Install
					</button>
					<button
						onclick={() => (showInstallPrompt = false)}
						class="px-4 py-2 text-gray-600 rounded-lg text-sm font-medium hover:bg-gray-100 transition-colors"
					>
						Not Now
					</button>
				</div>
			</div>
		</div>
	</div>
{/if}

{#if updateAvailable}
	<div
		class="fixed top-20 left-4 right-4 md:left-auto md:right-4 md:max-w-sm bg-blue-600 text-white rounded-xl shadow-lg p-4 z-50"
	>
		<div class="flex items-center justify-between gap-3">
			<p class="text-sm font-medium">A new version is available!</p>
			<button
				onclick={reloadApp}
				class="px-4 py-2 bg-white text-blue-600 rounded-lg text-sm font-bold hover:bg-blue-50 transition-colors"
			>
				Update
			</button>
		</div>
	</div>
{/if}

<Navbar />
<main>
	{@render children()}
</main>
<Footer />
