import { browser } from '$app/environment';

// Storage key
const LOCALE_KEY = 'app_locale';

// Supported locales
export const supportedLocales = ['en', 'ar'] as const;
export type SupportedLocale = (typeof supportedLocales)[number];

// Language state using Svelte 5 runes
let currentLocale = $state<SupportedLocale>('en');
let isRTL = $state(false);
let isInitialized = $state(false);

// Browser language detection
function detectBrowserLanguage(): SupportedLocale {
	if (!browser) return 'en';

	const browserLang = navigator.language.split('-')[0]; // 'en-US' → 'en'

	// Check if browser language is supported
	if (supportedLocales.includes(browserLang as SupportedLocale)) {
		return browserLang as SupportedLocale;
	}

	return 'en'; // Fallback
}

// Load saved locale or detect browser language
function loadLocale(): SupportedLocale {
	if (!browser) return 'en';

	const savedLocale = localStorage.getItem(LOCALE_KEY);

	if (savedLocale && supportedLocales.includes(savedLocale as SupportedLocale)) {
		return savedLocale as SupportedLocale;
	}

	// First visit: detect browser language
	return detectBrowserLanguage();
}

// Save locale to localStorage
function saveLocale(locale: SupportedLocale): void {
	if (!browser) return;
	localStorage.setItem(LOCALE_KEY, locale);
}

// Set locale and update RTL state
function setLocale(locale: SupportedLocale): void {
	currentLocale = locale;
	isRTL = locale === 'ar';
	saveLocale(locale);

	// Update HTML attributes
	if (browser) {
		document.documentElement.lang = locale;
		document.documentElement.dir = isRTL ? 'rtl' : 'ltr';
	}
}

// Toggle between languages
function toggleLanguage(): void {
	const newLocale = currentLocale === 'en' ? 'ar' : 'en';
	setLocale(newLocale);
}

// Initialize on browser
function initialize(): void {
	if (!browser || isInitialized) return;

	const locale = loadLocale();
	setLocale(locale);
	isInitialized = true;
}

// Auto-initialize
if (browser) {
	initialize();
}

// Export language store
export const language = {
	get locale() {
		return currentLocale;
	},
	get isRTL() {
		return isRTL;
	},
	get isInitialized() {
		return isInitialized;
	},

	setLocale,
	toggleLanguage,
	initialize,

	// Utility getters
	get isEnglish() {
		return currentLocale === 'en';
	},
	get isArabic() {
		return currentLocale === 'ar';
	},

	// Get locale config for i18n
	getLocaleConfig() {
		return {
			locale: currentLocale,
			dir: isRTL ? 'rtl' : 'ltr'
		};
	}
};

export default language;
