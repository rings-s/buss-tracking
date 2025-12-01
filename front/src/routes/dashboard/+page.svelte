<script lang="ts">
  import { auth } from '$lib/stores/auth.svelte';
  import AdminDashboard from '$lib/components/dashboard/AdminDashboard.svelte';
  import DriverDashboard from '$lib/components/dashboard/DriverDashboard.svelte';
  import EmployeeDashboard from '$lib/components/dashboard/EmployeeDashboard.svelte';
  import { t } from '$lib/i18n';

  const getGreeting = $derived.by(() => {
    const hour = new Date().getHours();
    if (hour < 12) return $t('dashboard.greeting.morning');
    if (hour < 18) return $t('dashboard.greeting.afternoon');
    return $t('dashboard.greeting.evening');
  });
</script>

<div class="min-h-screen bg-gray-50 relative overflow-hidden">
  <!-- Background Elements -->
  <div class="hero-dots fixed inset-0 opacity-30 pointer-events-none"></div>
  <div class="fixed top-0 left-0 w-full h-96 bg-gradient-to-b from-brand-50/80 to-transparent pointer-events-none"></div>
  
  <!-- Main Content -->
  <div class="relative z-10 max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8 md:py-12 space-y-8">
    
    <!-- Header Section -->
    <div class="flex flex-col md:flex-row md:items-center justify-between gap-4 animate-fade-in">
      <div>
        <p class="text-brand-600 font-bold uppercase tracking-wider text-sm mb-1">{new Date().toLocaleDateString(undefined, { weekday: 'long', year: 'numeric', month: 'long', day: 'numeric' })}</p>
        <h1 class="text-4xl md:text-5xl font-black text-gray-900 tracking-tight">
          {getGreeting}, <span class="text-transparent bg-clip-text bg-gradient-to-r from-brand-600 to-brand-400">{auth.user?.full_name?.split(' ')[0] || 'User'}</span>
        </h1>
      </div>
      
      <div class="flex items-center gap-3">
        <div class="glass px-4 py-2 rounded-full flex items-center gap-2 text-sm font-bold text-gray-600 shadow-sm">
          <span class="w-2 h-2 rounded-full bg-green-500 animate-pulse"></span>
          {$t('dashboard.status.systemOnline')}
        </div>
        {#if auth.user?.role}
          <div class="glass px-4 py-2 rounded-full text-sm font-bold text-brand-700 shadow-sm uppercase tracking-wider border-brand-100 bg-brand-50/50">
            {$t(`dashboard.status.${auth.user.role}Portal`)}
          </div>
        {/if}
      </div>
    </div>

    <!-- Dashboard Content -->
    <div class="animate-slide-up" style="animation-delay: 100ms;">
      {#if auth.user?.role === 'admin'}
        <AdminDashboard />
      {:else if auth.user?.role === 'driver'}
        <DriverDashboard />
      {:else if auth.user?.role === 'employee'}
        <EmployeeDashboard />
      {:else}
        <div class="glass-card p-12 text-center max-w-2xl mx-auto mt-12">
          <div class="w-24 h-24 mx-auto rounded-full bg-brand-50 flex items-center justify-center text-brand-300 mb-6">
            <svg xmlns="http://www.w3.org/2000/svg" class="h-12 w-12" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 15v2m-6 4h12a2 2 0 002-2v-6a2 2 0 00-2-2H6a2 2 0 00-2 2v6a2 2 0 002 2zm10-10V7a4 4 0 00-8 0v4h8z" />
            </svg>
          </div>
          <h2 class="text-3xl font-black text-gray-900 mb-4">{$t('dashboard.pending.title')}</h2>
          <p class="text-gray-500 text-lg mb-8">{$t('dashboard.pending.message')}</p>
          <button class="btn-primary max-w-xs mx-auto">{$t('dashboard.pending.contactSupport')}</button>
        </div>
      {/if}
    </div>
  </div>
</div>
