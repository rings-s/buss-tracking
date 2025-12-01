<script lang="ts">
  import { goto } from '$app/navigation';
  import { auth } from '$lib/stores/auth.svelte';
  import { loginCredentialsSchema } from '$lib/schemas';
  import { ApiClientError } from '$lib/services/api-client';
  import { ZodError } from 'zod';
  import { fade, fly } from 'svelte/transition';
  import { t } from '$lib/i18n';

  // Props
  let { redirectTo }: { redirectTo?: string } = $props();

  // Form state
  let email = $state('');
  let password = $state('');
  let isSubmitting = $state(false);
  let errors = $state<Record<string, string>>({});
  let generalError = $state('');

  // Form validation
  function validateForm(): boolean {
    errors = {};
    generalError = '';

    try {
      loginCredentialsSchema.parse({ email, password });
      return true;
    } catch (err) {
      if (err instanceof ZodError) {
        err.issues.forEach((issue) => {
          const field = issue.path[0] as string;
          errors[field] = issue.message;
        });
      }
      return false;
    }
  }

  // Handle form submission
  async function handleSubmit(e: Event) {
    e.preventDefault();

    if (!validateForm()) return;

    isSubmitting = true;
    generalError = '';

    try {
      const user = await auth.login({ email, password });
      const target = redirectTo || auth.getRedirectPath(user);
      await goto(target);
    } catch (err) {
      if (err instanceof ApiClientError) {
        if (err.status === 401) {
          generalError = $t('auth.errors.invalidCredentials');
        } else if (err.data.detail) {
          generalError = err.data.detail;
        } else if (err.data.email) {
          errors.email = Array.isArray(err.data.email)
            ? err.data.email[0]
            : String(err.data.email);
        } else if (err.data.password) {
          errors.password = Array.isArray(err.data.password)
            ? err.data.password[0]
            : String(err.data.password);
        } else {
          generalError = err.message;
        }
      } else {
        generalError = $t('auth.errors.unexpectedError');
      }
    } finally {
      isSubmitting = false;
    }
  }
</script>

<div class="w-full max-w-md mx-auto" in:fly={{ y: 20, duration: 600, delay: 200 }}>
  <div class="glass p-8 rounded-2xl">
    <div class="text-center mb-8">
      <h2 class="text-3xl font-bold text-gray-900 mb-2">{$t('auth.login.title')}</h2>
      <p class="text-gray-600">{$t('auth.login.subtitle')}</p>
    </div>

    <form onsubmit={handleSubmit} class="space-y-6">
      {#if generalError}
        <div class="bg-red-50 text-red-600 p-4 rounded-xl text-sm font-medium border border-red-100 animate-shake" transition:fade>
          {generalError}
        </div>
      {/if}

      <div class="space-y-2">
        <label for="email" class="block text-sm font-medium text-gray-700 ml-1">{$t('auth.login.email')}</label>
        <input
          type="email"
          id="email"
          bind:value={email}
          disabled={isSubmitting}
          autocomplete="email"
          class="input-field {errors.email ? 'border-red-300 focus:border-red-500 focus:ring-red-500/20' : ''}"
          placeholder="you@example.com"
        />
        {#if errors.email}
          <span class="text-red-500 text-xs ml-1" transition:fade>{errors.email}</span>
        {/if}
      </div>

      <div class="space-y-2">
        <div class="flex justify-between items-center ml-1">
          <label for="password" class="block text-sm font-medium text-gray-700">{$t('auth.login.password')}</label>
          <a href="/auth/forgot-password" class="text-xs font-medium text-brand-600 hover:text-brand-700 transition-colors">
            {$t('auth.login.forgotPassword')}
          </a>
        </div>
        <input
          type="password"
          id="password"
          bind:value={password}
          disabled={isSubmitting}
          autocomplete="current-password"
          class="input-field {errors.password ? 'border-red-300 focus:border-red-500 focus:ring-red-500/20' : ''}"
          placeholder="••••••••"
        />
        {#if errors.password}
          <span class="text-red-500 text-xs ml-1" transition:fade>{errors.password}</span>
        {/if}
      </div>

      <button type="submit" disabled={isSubmitting} class="btn-primary w-full relative overflow-hidden group">
        <span class="relative z-10 flex items-center justify-center gap-2">
          {#if isSubmitting}
            <svg class="animate-spin h-5 w-5 text-white" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
              <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
              <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
            </svg>
            <span>{$t('auth.login.signingIn')}</span>
          {:else}
            {$t('auth.login.signIn')}
          {/if}
        </span>
      </button>

      <div class="relative my-6">
        <div class="absolute inset-0 flex items-center">
          <div class="w-full border-t border-gray-200"></div>
        </div>
        <div class="relative flex justify-center text-sm">
          <span class="px-2 bg-white text-gray-500">{$t('auth.login.orContinueWith')}</span>
        </div>
      </div>

      {#await import('./GoogleLogin.svelte') then { default: GoogleLogin }}
        <div class="transition-all duration-300 hover:scale-[1.02]">
          <GoogleLogin />
        </div>
      {/await}

      <p class="text-center text-sm text-gray-600 mt-8">
        {$t('auth.login.noAccount')}
        <a href="/auth/register" class="font-semibold text-brand-600 hover:text-brand-700 transition-colors">
          {$t('auth.login.createAccount')}
        </a>
      </p>
    </form>
  </div>
</div>
