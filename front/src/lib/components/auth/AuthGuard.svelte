<script lang="ts">
  import { goto } from '$app/navigation';
  import { auth } from '$lib/stores/auth.svelte';
  import type { Snippet } from 'svelte';
  import type { UserRole } from '$lib/types';
  import { fade } from 'svelte/transition';

  // Props
  let {
    children,
    roles = [],
    redirectTo = '/auth/login',
    fallback,
  }: {
    children: Snippet;
    roles?: UserRole[];
    redirectTo?: string;
    fallback?: Snippet;
  } = $props();

  // Check if user has required role
  let hasAccess = $derived(() => {
    if (!auth.isAuthenticated || !auth.user) return false;
    if (roles.length === 0) return true;
    return roles.includes(auth.user.role);
  });

  // Redirect if not authenticated
  $effect(() => {
    if (!auth.isLoading && !auth.isAuthenticated) {
      goto(redirectTo);
    }
  });

  // Redirect if no access (role check)
  $effect(() => {
    if (!auth.isLoading && auth.isAuthenticated && roles.length > 0 && !hasAccess()) {
      goto('/unauthorized');
    }
  });
</script>

{#if auth.isLoading}
  {#if fallback}
    {@render fallback()}
  {:else}
    <div class="min-h-[50vh] flex items-center justify-center" transition:fade>
      <div class="relative">
        <div class="w-12 h-12 rounded-full border-4 border-brand-200 animate-spin"></div>
        <div class="absolute top-0 left-0 w-12 h-12 rounded-full border-4 border-brand-600 border-t-transparent animate-spin"></div>
      </div>
    </div>
  {/if}
{:else if hasAccess()}
  {@render children()}
{:else if fallback}
  {@render fallback()}
{:else}
  <div class="min-h-[50vh] flex items-center justify-center" transition:fade>
    <div class="text-center">
      <h2 class="text-2xl font-bold text-gray-900 mb-2">Unauthorized Access</h2>
      <p class="text-gray-600">You do not have permission to view this page.</p>
    </div>
  </div>
{/if}
