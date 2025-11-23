<script lang="ts">
  import { auth } from '$lib/stores/auth.svelte';
</script>

<div class="page">
  <h1>Dashboard</h1>
  <p>Welcome, {auth.user?.full_name}</p>
</div>
