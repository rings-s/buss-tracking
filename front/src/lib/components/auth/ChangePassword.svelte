<script lang="ts">
  import { authService } from '$lib/services/auth';
  import { changePasswordSchema } from '$lib/schemas';
  import { ApiClientError } from '$lib/services/api-client';
  import { ZodError } from 'zod';
  import { fade, fly } from 'svelte/transition';

  // Form state
  let old_password = $state('');
  let new_password = $state('');
  let new_password_confirm = $state('');
  let isSubmitting = $state(false);
  let errors = $state<Record<string, string>>({});
  let generalError = $state('');
  let successMessage = $state('');

  // Form validation
  function validateForm(): boolean {
    errors = {};
    generalError = '';

    try {
      changePasswordSchema.parse({
        old_password,
        new_password,
        new_password_confirm,
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

  // Reset form
  function resetForm() {
    old_password = '';
    new_password = '';
    new_password_confirm = '';
    errors = {};
  }

  // Handle form submission
  async function handleSubmit(e: Event) {
    e.preventDefault();

    if (!validateForm()) return;

    isSubmitting = true;
    generalError = '';
    successMessage = '';

    try {
      const response = await authService.changePassword({
        old_password,
        new_password,
        new_password_confirm,
      });

      successMessage = response.message || 'Password changed successfully!';
      resetForm();
    } catch (err) {
      if (err instanceof ApiClientError) {
        if (err.data.detail) {
          generalError = err.data.detail;
        } else if (err.data.old_password) {
          errors.old_password = Array.isArray(err.data.old_password)
            ? err.data.old_password[0]
            : String(err.data.old_password);
        } else if (err.data.new_password) {
          errors.new_password = Array.isArray(err.data.new_password)
            ? err.data.new_password[0]
            : String(err.data.new_password);
        } else if (err.data.new_password_confirm) {
          errors.new_password_confirm = Array.isArray(err.data.new_password_confirm)
            ? err.data.new_password_confirm[0]
            : String(err.data.new_password_confirm);
        } else {
          generalError = err.message;
        }
      } else {
        generalError = 'An unexpected error occurred';
      }
    } finally {
      isSubmitting = false;
    }
  }
</script>

<div class="w-full max-w-md mx-auto" in:fly={{ y: 20, duration: 600, delay: 200 }}>
  <div class="glass p-8 rounded-2xl">
    <div class="text-center mb-8">
      <h2 class="text-2xl font-bold text-gray-900 mb-2">Change Password</h2>
      <p class="text-gray-600">Update your security credentials</p>
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
        <label for="old_password" class="block text-sm font-medium text-gray-700 ml-1">Current Password</label>
        <input
          type="password"
          id="old_password"
          bind:value={old_password}
          disabled={isSubmitting}
          autocomplete="current-password"
          class="input-field {errors.old_password ? 'border-red-300 focus:border-red-500 focus:ring-red-500/20' : ''}"
          placeholder="••••••••"
        />
        {#if errors.old_password}
          <span class="text-red-500 text-xs ml-1" transition:fade>{errors.old_password}</span>
        {/if}
      </div>

      <div class="space-y-2">
        <label for="new_password" class="block text-sm font-medium text-gray-700 ml-1">New Password</label>
        <input
          type="password"
          id="new_password"
          bind:value={new_password}
          disabled={isSubmitting}
          autocomplete="new-password"
          class="input-field {errors.new_password ? 'border-red-300 focus:border-red-500 focus:ring-red-500/20' : ''}"
          placeholder="••••••••"
        />
        {#if errors.new_password}
          <span class="text-red-500 text-xs ml-1" transition:fade>{errors.new_password}</span>
        {/if}
      </div>

      <div class="space-y-2">
        <label for="new_password_confirm" class="block text-sm font-medium text-gray-700 ml-1">Confirm New Password</label>
        <input
          type="password"
          id="new_password_confirm"
          bind:value={new_password_confirm}
          disabled={isSubmitting}
          autocomplete="new-password"
          class="input-field {errors.new_password_confirm ? 'border-red-300 focus:border-red-500 focus:ring-red-500/20' : ''}"
          placeholder="••••••••"
        />
        {#if errors.new_password_confirm}
          <span class="text-red-500 text-xs ml-1" transition:fade>{errors.new_password_confirm}</span>
        {/if}
      </div>

      <button type="submit" disabled={isSubmitting} class="btn-primary w-full mt-4 relative overflow-hidden group">
        <span class="relative z-10 flex items-center justify-center gap-2">
          {#if isSubmitting}
            <svg class="animate-spin h-5 w-5 text-white" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
              <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
              <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
            </svg>
            <span>Changing Password...</span>
          {:else}
            Change Password
          {/if}
        </span>
      </button>
    </form>
  </div>
</div>
