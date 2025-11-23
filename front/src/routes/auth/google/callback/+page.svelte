<script lang="ts">
  import { OAuthCallback } from '$lib/components/auth';
</script>

<svelte:head>
  <title>Authenticating... - Bus Tracker</title>
</svelte:head>

<div class="min-h-screen flex items-center justify-center py-12 px-4 sm:px-6 lg:px-8 bg-gradient-to-br from-gray-50 to-gray-100">
  <OAuthCallback />
</div>
