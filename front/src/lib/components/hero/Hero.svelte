<script lang="ts">
  import { onMount } from 'svelte';
  import DashboardVisual from './DashboardVisual.svelte';
  import { t } from '$lib/i18n';

  let mounted = $state(false);
  let mousePos = $state({ x: 0, y: 0 });

  // Mock auth state
  const isAuthenticated = false; 

  onMount(() => {
    mounted = true;
    const handleMouseMove = (e: MouseEvent) => {
      mousePos = {
        x: (e.clientX / window.innerWidth) * 20,
        y: (e.clientY / window.innerHeight) * 20,
      };
    };
    window.addEventListener('mousemove', handleMouseMove);
    return () => window.removeEventListener('mousemove', handleMouseMove);
  });
</script>

<div class="relative min-h-screen bg-gray-50 text-gray-900 overflow-hidden font-sans selection:bg-brand-300/30">
  
  <!-- Background Effects -->
  <div class="hero-dots"></div>


  <!-- Main Content Container -->
  <div class="relative z-20 w-full max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 pt-12 lg:pt-20 pb-20">
    <div class="flex flex-col lg:flex-row items-center gap-12 lg:gap-20">
      
      <!-- Left Column: Content -->
      <div class="w-full lg:w-1/2 flex flex-col items-start text-left">
        
        <!-- Badge -->
       

        <!-- Heading -->
        <h1 class="text-5xl sm:text-6xl md:text-7xl lg:text-7xl font-black text-gray-900 tracking-tighter leading-[0.85] mb-8 animate-slide-up" style="animation-delay: 0.2s;">
          <span class="block">{$t('home.hero.title1')}</span>
          <span class="block text-transparent bg-clip-text bg-gradient-to-r from-brand-500 to-brand-300">{$t('home.hero.title2')}</span>
        </h1>

        <!-- Description -->
        <p class="text-lg text-gray-600 font-medium leading-relaxed max-w-lg mb-10 animate-slide-up" style="animation-delay: 0.3s;">
          {$t('home.hero.description')}
        </p>

        <!-- Buttons / Actions -->
        <div class="flex flex-wrap gap-4 w-full animate-slide-up" style="animation-delay: 0.4s;">
          {#if isAuthenticated}
            <a href="/dashboard" class="group relative px-8 py-4 bg-gray-900 text-white rounded-2xl font-bold text-lg shadow-xl shadow-gray-900/20 hover:bg-gray-800 hover:-translate-y-1 transition-all duration-300 overflow-hidden">
               <span class="relative z-10 flex items-center gap-3">
                 {$t('home.hero.openCommandCenter')}
                 <svg class="w-5 h-5 transition-transform group-hover:translate-x-1" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M14 5l7 7m0 0l-7 7m7-7H3"></path></svg>
               </span>
            </a>
          {:else}
            <a href="/auth/login" class="group px-8 py-4 bg-gray-900 text-white rounded-2xl font-bold text-lg shadow-xl shadow-gray-900/20 hover:bg-gray-800 hover:-translate-y-1 transition-all duration-300 flex items-center gap-3">
              <span>{$t('home.hero.authenticate')}</span>
              <svg class="w-5 h-5 text-gray-400 group-hover:text-white transition-colors" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 15v2m-6 4h12a2 2 0 002-2v-6a2 2 0 00-2-2H6a2 2 0 00-2 2v6a2 2 0 002 2zm10-10V7a4 4 0 00-8 0v4h8z"></path></svg>
            </a>
            <button class="px-8 py-4 bg-white/80 backdrop-blur-sm text-gray-900 border border-gray-200 rounded-2xl font-bold text-lg shadow-sm hover:bg-white hover:shadow-md transition-all duration-300">
              {$t('home.hero.systemStatus')}
            </button>
          {/if}
        </div>

      </div>

      <!-- Right Column: Visual -->
      <div class="w-full lg:w-1/2 relative perspective-[2000px] h-[500px] lg:h-[600px] flex items-center justify-center">
         <div 
            class="transform-style-3d transition-transform duration-200 ease-out w-full"
            style="transform: rotateX({10 + mousePos.y * 0.3}deg) rotateY({-10 + mousePos.x * 0.3}deg)"
         >
            <DashboardVisual />
         </div>
      </div>

    </div>
  </div>
</div>