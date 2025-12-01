<script lang="ts">
  import { goto } from '$app/navigation';
  import { page } from '$app/state';
  import { auth } from '$lib/stores/auth.svelte';
  import { fade, slide } from 'svelte/transition';
  import { onMount, onDestroy } from 'svelte';
  import { tripService } from '$lib/services/trip';
  import { t, loading } from '$lib/i18n';
  import LanguageToggle from '$lib/components/shared/LanguageToggle.svelte';

  // Helper to get translated text with fallback
  function getNavLabel(key: string): string {
    const translation = $t('common.nav.' + key);
    // If translation is the same as the key, return a capitalized version of the key
    return translation && translation !== 'common.nav.' + key ? translation : key.charAt(0).toUpperCase() + key.slice(1).replace(/([A-Z])/g, ' $1').trim();
  }

  // Mobile menu state
  let isMobileMenuOpen = $state(false);
  let isProfileMenuOpen = $state(false);
  let scrollY = $state(0);

  // Active trips count
  let activeTripsCount = $state(0);
  let activeTripsInterval: ReturnType<typeof setInterval>;

  async function fetchActiveTripsCount() {
    if (!auth.isAuthenticated) return;
    try {
      const trips = await tripService.getLiveTracking();
      activeTripsCount = trips.length;
    } catch {
      // Silently fail
    }
  }

  // Navigation items based on role
  let navItems = $derived.by(() => {
    if (!auth.isAuthenticated || !auth.user) {
      return [
        { href: '/checkin', labelKey: 'checkin', badge: 0 },
        { href: '/auth/login', labelKey: 'login', badge: 0 },
        { href: '/auth/register', labelKey: 'register', badge: 0 },
      ];
    }

    const items: { href: string; labelKey: string; badge: number }[] = [];

    switch (auth.user.role) {
      case 'admin':
        items.push(
          { href: '/dashboard', labelKey: 'dashboard', badge: 0 },
          { href: '/buses', labelKey: 'buses', badge: 0 },
          { href: '/routes', labelKey: 'routes', badge: 0 },
          { href: '/trips', labelKey: 'trips', badge: 0 },
          { href: '/boardings', labelKey: 'boardings', badge: 0 },
          { href: '/live-tracking', labelKey: 'activeTrips', badge: activeTripsCount }
        );
        break;
      case 'driver':
        items.push(
          { href: '/driver', labelKey: 'myTrips', badge: 0 },
          { href: '/checkin', labelKey: 'checkin', badge: 0 },
          { href: '/live-tracking', labelKey: 'activeTrips', badge: activeTripsCount }
        );
        break;
      case 'employee':
        items.push(
          { href: '/my-boardings', labelKey: 'myBoardings', badge: 0 }
        );
        break;
    }

    return items;
  });

  // Check if link is active
  function isActive(href: string): boolean {
    return page.url.pathname === href || page.url.pathname.startsWith(href + '/');
  }

  let isHomePage = $derived(page.url.pathname === '/');

  // Handle logout
  async function handleLogout() {
    await auth.logout();
    await goto('/auth/login');
    isProfileMenuOpen = false;
  }

  // Toggle mobile menu
  function toggleMobileMenu() {
    isMobileMenuOpen = !isMobileMenuOpen;
    if (isMobileMenuOpen) isProfileMenuOpen = false;
  }

  // Close mobile menu
  function closeMobileMenu() {
    isMobileMenuOpen = false;
  }

  // Toggle profile menu
  function toggleProfileMenu() {
    isProfileMenuOpen = !isProfileMenuOpen;
  }

  // Close menus on click outside
  function handleClickOutside(event: MouseEvent) {
    const target = event.target as HTMLElement;
    if (!target.closest('.profile-menu-container') && isProfileMenuOpen) {
      isProfileMenuOpen = false;
    }
  }

  onMount(() => {
    window.addEventListener('click', handleClickOutside);

    // Fetch active trips count
    fetchActiveTripsCount();
    activeTripsInterval = setInterval(fetchActiveTripsCount, 30000); // Every 30 seconds

    return () => {
      window.removeEventListener('click', handleClickOutside);
    };
  });

  onDestroy(() => {
    if (activeTripsInterval) {
      clearInterval(activeTripsInterval);
    }
  });
</script>

<svelte:window bind:scrollY />

<nav 
  class="fixed top-0 left-0 right-0 z-50 transition-all duration-300 border-b border-transparent"
  class:bg-white={!isHomePage && scrollY > 20}
  class:shadow-md={!isHomePage && scrollY > 20}
  class:bg-transparent={isHomePage || scrollY <= 20}
  class:py-2={scrollY > 20}
  class:py-4={scrollY <= 20}
>
  <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
    <div class="flex justify-between items-center h-16">
      <!-- Logo -->
      <div class="flex-shrink-0 flex items-center">
        <a href="/" class="flex items-center gap-3 group">
          <div class="w-10 h-10 rounded-xl bg-gradient-to-br from-brand-300 to-accent-pink flex items-center justify-center text-gray-900 shadow-lg shadow-brand-300/30 group-hover:scale-105 transition-transform duration-300">
            <svg xmlns="http://www.w3.org/2000/svg" class="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8 7h12m0 0l-4-4m4 4l-4 4m0 6H4m0 0l4 4m-4-4l4-4" />

            </svg>
          </div>
          <span class="font-display font-black text-2xl tracking-tight transition-colors text-gray-900 group-hover:text-brand-400">
            Bus<span class="text-brand-400">Tracker</span>
          </span>
        </a>
      </div>

      <!-- Desktop Menu -->
      <div class="hidden md:flex items-center space-x-1">
        {#each navItems as item}
          <a
            href={item.href}
            class="px-4 py-2 rounded-lg text-sm font-bold transition-all duration-200 relative {isActive(item.href) ? 'bg-brand-50 text-brand-700 shadow-sm' : 'text-gray-600 hover:text-brand-600 hover:bg-gray-50/50'}"
          >
            {getNavLabel(item.labelKey)}
            {#if item.badge > 0}
              <span class="absolute -top-1 -right-1 bg-red-500 text-white text-xs rounded-full w-5 h-5 flex items-center justify-center font-bold animate-pulse">
                {item.badge}
              </span>
            {/if}
          </a>
        {/each}

        <!-- Language Toggle -->
        <div class="ml-2">
          <LanguageToggle />
        </div>

        {#if auth.isAuthenticated && auth.user}
          <div class="ml-4 pl-4 border-l border-gray-200 relative profile-menu-container">
            <button 
              onclick={toggleProfileMenu}
              class="flex items-center gap-3 p-1.5 rounded-xl hover:bg-gray-50 transition-colors focus:outline-none"
            >
              <div class="flex flex-col items-end">
                <span class="text-sm font-bold text-gray-900">{auth.user.full_name}</span>
                <span class="text-xs font-bold text-gray-500 uppercase tracking-wider">{auth.user.role}</span>
              </div>
              <div class="w-10 h-10 rounded-full bg-brand-100 flex items-center justify-center text-brand-700 font-bold border-2 border-white shadow-sm">
                {auth.user.full_name.charAt(0)}
              </div>
            </button>

            {#if isProfileMenuOpen}
              <div 
                transition:slide={{ duration: 200 }}
                class="absolute right-0 mt-2 w-48 bg-white rounded-xl shadow-xl border border-gray-100 py-2 overflow-hidden"
              >
                <div class="px-4 py-2 border-b border-gray-50 mb-1">
                  <p class="text-xs text-gray-500">Signed in as</p>
                  <p class="text-sm font-bold text-gray-900 truncate">{auth.user.email}</p>
                </div>
                <a
                  href="/profile"
                  class="w-full text-left px-4 py-2 text-sm font-medium text-gray-700 hover:bg-gray-50 transition-colors flex items-center gap-2"
                  onclick={() => isProfileMenuOpen = false}
                >
                  <svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z" />
                  </svg>
                  {getNavLabel('profile')}
                </a>
                <button
                  onclick={handleLogout}
                  class="w-full text-left px-4 py-2 text-sm font-medium text-red-600 hover:bg-red-50 transition-colors flex items-center gap-2"
                >
                  <svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M17 16l4-4m0 0l-4-4m4 4H7m6 4v1a3 3 0 01-3 3H6a3 3 0 01-3-3V7a3 3 0 013-3h4a3 3 0 013 3v1" />
                  </svg>
                  {getNavLabel('logout')}
                </button>
              </div>
            {/if}
          </div>
        {/if}
      </div>

      <!-- Mobile Menu Button -->
      <div class="md:hidden flex items-center">
        <button
          onclick={toggleMobileMenu}
          class="p-2 rounded-lg text-gray-600 hover:bg-gray-100 focus:outline-none transition-colors"
          aria-label="Toggle menu"
        >
          <div class="w-6 h-5 relative flex flex-col justify-between">
            <span class="w-full h-0.5 bg-current transform transition-all duration-300 {isMobileMenuOpen ? 'rotate-45 translate-y-2' : ''}"></span>
            <span class="w-full h-0.5 bg-current transition-all duration-300 {isMobileMenuOpen ? 'opacity-0' : ''}"></span>
            <span class="w-full h-0.5 bg-current transform transition-all duration-300 {isMobileMenuOpen ? '-rotate-45 -translate-y-2.5' : ''}"></span>
          </div>
        </button>
      </div>
    </div>
  </div>

  <!-- Mobile Menu -->
  {#if isMobileMenuOpen}
    <div
      class="md:hidden absolute w-full left-0 shadow-xl border-t bg-white border-gray-100"
      transition:slide={{ duration: 300 }}
    >
      <div class="px-4 pt-2 pb-6 space-y-1">
        {#if auth.isAuthenticated && auth.user}
          <div class="px-4 py-3 mb-2 rounded-xl border bg-brand-50/50 border-brand-100">
            <div class="flex items-center gap-3">
              <div class="w-10 h-10 rounded-full bg-brand-200 flex items-center justify-center text-brand-700 font-bold text-lg border-2 border-white shadow-sm">
                {auth.user.full_name.charAt(0)}
              </div>
              <div>
                <div class="font-bold text-gray-900">{auth.user.full_name}</div>
                <div class="text-xs text-brand-600 font-bold uppercase tracking-wider">{auth.user.role}</div>
              </div>
            </div>
          </div>
        {/if}

        <!-- Language Toggle (Mobile) -->
        <div class="mb-3">
          <LanguageToggle mobile={true} />
        </div>

        {#each navItems as item}
          <a
            href={item.href}
            class="block px-4 py-3 rounded-xl text-base font-bold transition-all duration-200 relative {isActive(item.href) ? 'bg-brand-300 text-gray-900 shadow-lg shadow-brand-300/30' : 'text-gray-600 hover:bg-gray-50 hover:text-brand-600'}"
            onclick={closeMobileMenu}
          >
            <span class="flex items-center justify-between">
              {getNavLabel(item.labelKey)}
              {#if item.badge > 0}
                <span class="bg-red-500 text-white text-xs rounded-full px-2 py-0.5 font-bold">
                  {item.badge}
                </span>
              {/if}
            </span>
          </a>
        {/each}

        {#if auth.isAuthenticated}
          <a
            href="/profile"
            class="block px-4 py-3 rounded-xl text-base font-bold text-gray-600 hover:bg-gray-50 hover:text-brand-600 transition-all duration-200 flex items-center gap-2"
            onclick={closeMobileMenu}
          >
            <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z" />
            </svg>
            {getNavLabel('profile')}
          </a>
          <button
            onclick={() => {
              handleLogout();
              closeMobileMenu();
            }}
            class="w-full mt-4 px-4 py-3 rounded-xl text-base font-bold text-red-600 bg-red-50 hover:bg-red-100 transition-colors flex items-center justify-center gap-2"
          >
            <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M17 16l4-4m0 0l-4-4m4 4H7m6 4v1a3 3 0 01-3 3H6a3 3 0 01-3-3V7a3 3 0 013-3h4a3 3 0 013 3v1" />
            </svg>
            {getNavLabel('logout')}
          </button>
        {/if}
      </div>
    </div>
  {/if}
</nav>

<!-- Spacer for fixed navbar -->
{#if !isHomePage}
  <div class="h-20"></div>
{/if}
