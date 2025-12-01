# Translation System Guide

## Overview

This project uses `sveltekit-i18n` for internationalization with support for English (en) and Arabic (ar).

## Translation Namespaces

The translations are organized into domain-specific namespaces:

- **common**: Navigation, shared UI elements
- **auth**: Login, register, profile
- **dashboard**: Dashboard greetings, stats, status
- **buses**: Fleet management
- **trips**: Trip management and details
- **home**: Landing page hero section
- **routes**: Route management
- **attendance**: Attendance records
- **checkin**: NFC check-in
- **drivers**: Driver portal and trips
- **reports**: Absence reports
- **errors**: Validation and API errors
- **ui**: Common UI buttons, states, confirmations
- **tracking**: Live GPS tracking
- **footer**: Footer links and contact info

## Usage in Components

### 1. Import the translation function

```svelte
<script lang="ts">
  import { t } from '$lib/i18n';
</script>
```

### 2. Use translations in templates

**Simple translation:**
```svelte
<h1>{$t('auth.login.title')}</h1>
<!-- English: "Welcome Back" -->
<!-- Arabic: "مرحباً بعودتك" -->
```

**With fallback:**
```svelte
<button>{$t('ui.buttons.save')}</button>
<!-- English: "Save" -->
<!-- Arabic: "حفظ" -->
```

### 3. Using translations with parameters

For dynamic values, you can use string interpolation:

```svelte
<p>{$t('footer.copyright').replace('{{year}}', new Date().getFullYear())}</p>
```

### 4. Translation key patterns

Translation keys follow the pattern: `namespace.category.key`

Examples:
- `auth.login.title` → Authentication → Login → Title
- `buses.form.busName` → Buses → Form → Bus Name
- `ui.buttons.save` → UI → Buttons → Save
- `errors.validation.required` → Errors → Validation → Required

## Language Switching

The language can be changed using the `LanguageToggle` component or programmatically:

```svelte
<script lang="ts">
  import { language } from '$lib/stores/language.svelte';

  // Switch to Arabic
  language.setLocale('ar');

  // Toggle between languages
  language.toggleLanguage();

  // Check current language
  const isArabic = language.isArabic;
  const isEnglish = language.isEnglish;
</script>
```

## RTL Support

Arabic automatically enables RTL (Right-to-Left) layout through:
- HTML `dir` attribute
- CSS direction property
- Tailwind RTL utilities (use `rtl:` prefix)

```svelte
<div class="ml-4 rtl:mr-4 rtl:ml-0">
  <!-- Margin-left in LTR, margin-right in RTL -->
</div>
```

## Adding New Translations

### 1. Create translation files

Add to both `en/` and `ar/` directories:

```json
// en/new-feature.json
{
  "title": "New Feature",
  "description": "Feature description"
}

// ar/new-feature.json
{
  "title": "ميزة جديدة",
  "description": "وصف الميزة"
}
```

### 2. Register in i18n config

Update `src/lib/i18n/index.ts`:

```typescript
{
  locale: 'en',
  key: 'newFeature',
  loader: async () => (await import('../translations/en/new-feature.json')).default
},
{
  locale: 'ar',
  key: 'newFeature',
  loader: async () => (await import('../translations/ar/new-feature.json')).default
}
```

### 3. Use in components

```svelte
<h1>{$t('newFeature.title')}</h1>
```

## Best Practices

1. **Keep translations organized**: Use clear, hierarchical namespaces
2. **Consistent naming**: Use camelCase for keys
3. **Avoid hardcoded text**: Always use translation keys
4. **Provide context**: Use descriptive keys that indicate purpose
5. **Test both languages**: Verify layouts work in both LTR and RTL
6. **Handle missing translations**: The fallback helper prevents blank text

## Common Translation Patterns

### Form Labels
```svelte
<label for="email">{$t('auth.login.email')}</label>
<input id="email" type="email" placeholder="{$t('auth.login.email')}" />
```

### Button States
```svelte
<button disabled={isSubmitting}>
  {isSubmitting ? $t('ui.actions.saving') : $t('ui.buttons.save')}
</button>
```

### Error Messages
```svelte
{#if errors.email}
  <span class="text-red-500">{$t('errors.validation.email')}</span>
{/if}
```

### Status Badges
```svelte
<span class="badge">
  {trip.is_active ? $t('ui.states.active') : $t('ui.states.completed')}
</span>
```

### Confirmations
```svelte
<button onclick={() => {
  if (confirm($t('ui.confirmations.deleteConfirm'))) {
    handleDelete();
  }
}}>
  {$t('ui.buttons.delete')}
</button>
```

## File Structure

```
src/lib/translations/
├── README.md (this file)
├── en/
│   ├── common.json
│   ├── auth.json
│   ├── dashboard.json
│   ├── buses.json
│   ├── trips.json
│   ├── home.json
│   ├── routes.json
│   ├── attendance.json
│   ├── checkin.json
│   ├── drivers.json
│   ├── reports.json
│   ├── errors.json
│   ├── ui.json
│   ├── tracking.json
│   └── footer.json
└── ar/
    ├── common.json
    ├── auth.json
    ├── dashboard.json
    ├── buses.json
    ├── trips.json
    ├── home.json
    ├── routes.json
    ├── attendance.json
    ├── checkin.json
    ├── drivers.json
    ├── reports.json
    ├── errors.json
    ├── ui.json
    ├── tracking.json
    └── footer.json
```

## Troubleshooting

### Translation not showing
1. Check if the key exists in the JSON file
2. Verify the namespace is registered in `i18n/index.ts`
3. Ensure translations are loaded with `loadTranslations()`
4. Check browser console for "No locale provided" errors

### RTL layout issues
1. Verify `language.svelte.ts` sets `dir` attribute correctly
2. Use Tailwind RTL utilities (`rtl:` prefix)
3. Check that CSS doesn't force LTR direction

### Missing translations
The fallback helper in `Navbar.svelte` can be used as a pattern:
```typescript
function getTranslation(key: string): string {
  const translation = $t(key);
  return translation && translation !== key
    ? translation
    : formatFallback(key);
}
```
