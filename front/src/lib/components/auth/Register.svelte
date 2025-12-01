<script lang="ts">
  import { goto } from '$app/navigation';
  import { auth } from '$lib/stores/auth.svelte';
  import { registerDataSchema } from '$lib/schemas';
  import { ApiClientError } from '$lib/services/api-client';
  import { ZodError } from 'zod';
  import { fade, fly } from 'svelte/transition';
  import { t } from '$lib/i18n';

  // Props
  let { redirectTo = '/auth/login' }: { redirectTo?: string } = $props();

  // Form state
  let email = $state('');
  let password = $state('');
  let password_confirm = $state('');
  let full_name = $state('');
  let phone_number = $state('');
  let isSubmitting = $state(false);
  let errors = $state<Record<string, string>>({});
  let generalError = $state('');
  let successMessage = $state('');

  // Form validation
  function validateForm(): boolean {
    errors = {};
    generalError = '';

    try {
      registerDataSchema.parse({
        email,
        password,
        password_confirm,
        full_name,
        phone_number: phone_number || undefined,
      });
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
    successMessage = '';

    try {
      await auth.register({
        email,
        password,
        password_confirm,
        full_name,
        phone_number: phone_number || undefined,
      });

      successMessage = $t('auth.register.successMessage');

      setTimeout(() => {
        goto(redirectTo);
      }, 2000);
    } catch (err) {
      if (err instanceof ApiClientError) {
        if (err.data.detail) {
          generalError = err.data.detail;
        } else if (err.data.email) {
          errors.email = Array.isArray(err.data.email)
            ? err.data.email[0]
            : String(err.data.email);
        } else if (err.data.password) {
          errors.password = Array.isArray(err.data.password)
            ? err.data.password[0]
            : String(err.data.password);
        } else if (err.data.password_confirm) {
          errors.password_confirm = Array.isArray(err.data.password_confirm)
            ? err.data.password_confirm[0]
            : String(err.data.password_confirm);
        } else if (err.data.full_name) {
          errors.full_name = Array.isArray(err.data.full_name)
            ? err.data.full_name[0]
            : String(err.data.full_name);
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
      <h2 class="text-3xl font-bold text-gray-900 mb-2">{$t('auth.register.title')}</h2>
      <p class="text-gray-600">{$t('auth.register.subtitle')}</p>
    </div>

    <form onsubmit={handleSubmit} class="space-y-5">
      {#if generalError}
        <div class="bg-red-50 text-red-600 p-4 rounded-xl text-sm font-medium border border-red-100 animate-shake" transition:fade>
          {generalError}
        </div>
      {/if}

      {#if successMessage}
        <div class="bg-green-50 text-green-600 p-4 rounded-xl text-sm font-medium border border-green-100" transition:fade>
          {successMessage}
        </div>
      {/if}

      <div class="space-y-2">
        <label for="full_name" class="block text-sm font-medium text-gray-700 ml-1">{$t('auth.register.fullName')}</label>
        <input
          type="text"
          id="full_name"
          bind:value={full_name}
          disabled={isSubmitting}
          autocomplete="name"
          class="input-field {errors.full_name ? 'border-red-300 focus:border-red-500 focus:ring-red-500/20' : ''}"
          placeholder="John Doe"
        />
        {#if errors.full_name}
          <span class="text-red-500 text-xs ml-1" transition:fade>{errors.full_name}</span>
        {/if}
      </div>

      <div class="space-y-2">
        <label for="email" class="block text-sm font-medium text-gray-700 ml-1">{$t('auth.register.email')}</label>
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
        <label for="phone_number" class="block text-sm font-medium text-gray-700 ml-1">{$t('auth.register.phoneNumber')} <span class="text-gray-400 font-normal">{$t('auth.register.optional')}</span></label>
        <input
          type="tel"
          id="phone_number"
          bind:value={phone_number}
          disabled={isSubmitting}
          autocomplete="tel"
          class="input-field {errors.phone_number ? 'border-red-300 focus:border-red-500 focus:ring-red-500/20' : ''}"
          placeholder="+1 (555) 000-0000"
        />
        {#if errors.phone_number}
          <span class="text-red-500 text-xs ml-1" transition:fade>{errors.phone_number}</span>
        {/if}
      </div>

      <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
        <div class="space-y-2">
          <label for="password" class="block text-sm font-medium text-gray-700 ml-1">{$t('auth.register.password')}</label>
          <input
            type="password"
            id="password"
            bind:value={password}
            disabled={isSubmitting}
            autocomplete="new-password"
            class="input-field {errors.password ? 'border-red-300 focus:border-red-500 focus:ring-red-500/20' : ''}"
            placeholder="••••••••"
          />
          {#if errors.password}
            <span class="text-red-500 text-xs ml-1" transition:fade>{errors.password}</span>
          {/if}
        </div>

        <div class="space-y-2">
          <label for="password_confirm" class="block text-sm font-medium text-gray-700 ml-1">{$t('auth.register.confirmPassword')}</label>
          <input
            type="password"
            id="password_confirm"
            bind:value={password_confirm}
            disabled={isSubmitting}
            autocomplete="new-password"
            class="input-field {errors.password_confirm ? 'border-red-300 focus:border-red-500 focus:ring-red-500/20' : ''}"
            placeholder="••••••••"
          />
          {#if errors.password_confirm}
            <span class="text-red-500 text-xs ml-1" transition:fade>{errors.password_confirm}</span>
          {/if}
        </div>
      </div>

      <button type="submit" disabled={isSubmitting} class="btn-primary w-full mt-4 relative overflow-hidden group">
        <span class="relative z-10 flex items-center justify-center gap-2">
          {#if isSubmitting}
            <svg class="animate-spin h-5 w-5 text-white" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
              <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
              <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
            </svg>
            <span>{$t('auth.register.creatingAccount')}</span>
          {:else}
            {$t('auth.register.createAccount')}
          {/if}
        </span>
      </button>

      <p class="text-center text-sm text-gray-600 mt-6">
        {$t('auth.register.alreadyHaveAccount')}
        <a href="/auth/login" class="font-semibold text-brand-600 hover:text-brand-700 transition-colors">
          {$t('auth.register.signIn')}
        </a>
      </p>
    </form>
  </div>
</div>
