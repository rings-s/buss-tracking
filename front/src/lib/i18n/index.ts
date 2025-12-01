import i18n from 'sveltekit-i18n';
import type { Config } from 'sveltekit-i18n';

const config: Config = {
	loaders: [
		// Common translations
		{
			locale: 'en',
			key: 'common',
			loader: async () => (await import('../translations/en/common.json')).default
		},
		{
			locale: 'ar',
			key: 'common',
			loader: async () => (await import('../translations/ar/common.json')).default
		},
		// Auth translations
		{
			locale: 'en',
			key: 'auth',
			loader: async () => (await import('../translations/en/auth.json')).default
		},
		{
			locale: 'ar',
			key: 'auth',
			loader: async () => (await import('../translations/ar/auth.json')).default
		},
		// Dashboard translations
		{
			locale: 'en',
			key: 'dashboard',
			loader: async () => (await import('../translations/en/dashboard.json')).default
		},
		{
			locale: 'ar',
			key: 'dashboard',
			loader: async () => (await import('../translations/ar/dashboard.json')).default
		},
		// Buses translations
		{
			locale: 'en',
			key: 'buses',
			loader: async () => (await import('../translations/en/buses.json')).default
		},
		{
			locale: 'ar',
			key: 'buses',
			loader: async () => (await import('../translations/ar/buses.json')).default
		},
		// Trips translations
		{
			locale: 'en',
			key: 'trips',
			loader: async () => (await import('../translations/en/trips.json')).default
		},
		{
			locale: 'ar',
			key: 'trips',
			loader: async () => (await import('../translations/ar/trips.json')).default
		},
		// Home translations
		{
			locale: 'en',
			key: 'home',
			loader: async () => (await import('../translations/en/home.json')).default
		},
		{
			locale: 'ar',
			key: 'home',
			loader: async () => (await import('../translations/ar/home.json')).default
		},
		// Routes translations
		{
			locale: 'en',
			key: 'routes',
			loader: async () => (await import('../translations/en/routes.json')).default
		},
		{
			locale: 'ar',
			key: 'routes',
			loader: async () => (await import('../translations/ar/routes.json')).default
		},
		// Attendance translations
		{
			locale: 'en',
			key: 'attendance',
			loader: async () => (await import('../translations/en/attendance.json')).default
		},
		{
			locale: 'ar',
			key: 'attendance',
			loader: async () => (await import('../translations/ar/attendance.json')).default
		},
		// Check-in translations
		{
			locale: 'en',
			key: 'checkin',
			loader: async () => (await import('../translations/en/checkin.json')).default
		},
		{
			locale: 'ar',
			key: 'checkin',
			loader: async () => (await import('../translations/ar/checkin.json')).default
		},
		// Drivers translations
		{
			locale: 'en',
			key: 'drivers',
			loader: async () => (await import('../translations/en/drivers.json')).default
		},
		{
			locale: 'ar',
			key: 'drivers',
			loader: async () => (await import('../translations/ar/drivers.json')).default
		},
		// Reports translations
		{
			locale: 'en',
			key: 'reports',
			loader: async () => (await import('../translations/en/reports.json')).default
		},
		{
			locale: 'ar',
			key: 'reports',
			loader: async () => (await import('../translations/ar/reports.json')).default
		},
		// Errors translations
		{
			locale: 'en',
			key: 'errors',
			loader: async () => (await import('../translations/en/errors.json')).default
		},
		{
			locale: 'ar',
			key: 'errors',
			loader: async () => (await import('../translations/ar/errors.json')).default
		},
		// UI translations
		{
			locale: 'en',
			key: 'ui',
			loader: async () => (await import('../translations/en/ui.json')).default
		},
		{
			locale: 'ar',
			key: 'ui',
			loader: async () => (await import('../translations/ar/ui.json')).default
		},
		// Tracking translations
		{
			locale: 'en',
			key: 'tracking',
			loader: async () => (await import('../translations/en/tracking.json')).default
		},
		{
			locale: 'ar',
			key: 'tracking',
			loader: async () => (await import('../translations/ar/tracking.json')).default
		},
		// Footer translations
		{
			locale: 'en',
			key: 'footer',
			loader: async () => (await import('../translations/en/footer.json')).default
		},
		{
			locale: 'ar',
			key: 'footer',
			loader: async () => (await import('../translations/ar/footer.json')).default
		}
	],
	fallbackLocale: 'en'
};

export const { t, locale, locales, loading, loadTranslations, setLocale, setRoute } =
	new i18n(config);

export default { t, locale, locales, loading, loadTranslations, setLocale };
