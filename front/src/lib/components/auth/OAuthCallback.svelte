<script lang="ts">
  import { goto } from '$app/navigation';
  import { page } from '$app/state';
  import { auth } from '$lib/stores/auth.svelte';
  import { ApiClientError } from '$lib/services/api-client';

  // Props
  let { redirectTo }: { redirectTo?: string } = $props();

  // State
  let isProcessing = $state(true);
  let error = $state('');

  // Process OAuth callback on mount
  $effect(() => {
    processCallback();
  });

  async function processCallback() {
    const code = page.url.searchParams.get('code');
    const errorParam = page.url.searchParams.get('error');

    if (errorParam) {
      error = `Authentication failed: ${errorParam}`;
      isProcessing = false;
      return;
    }

    if (!code) {
      error = 'No authorization code received';
      isProcessing = false;
      return;
    }

    try {
      const user = await auth.googleLogin(code);
      const target = redirectTo || auth.getRedirectPath(user);
      await goto(target);
    } catch (err) {
      if (err instanceof ApiClientError) {
        error = err.data.detail || err.message || 'Authentication failed';
      } else {
        error = 'An unexpected error occurred';
      }
      isProcessing = false;
    }
  }

  function goToLogin() {
    goto('/auth/login');
  }
</script>

<div class="oauth-callback">
  {#if isProcessing}
    <div class="processing">
      <p>Processing authentication...</p>
    </div>
  {:else if error}
    <div class="error">
      <p>{error}</p>
      <button onclick={goToLogin}>Back to Login</button>
    </div>
  {/if}
</div>
