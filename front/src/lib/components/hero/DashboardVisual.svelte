<script lang="ts">
  // DashboardVisual.svelte - Advanced Styling
</script>

<div class="relative w-full max-w-[550px] aspect-[4/3] mx-auto z-10 select-none">
  
  <!-- Main Container -->
  <div class="relative w-full h-full transform-style-3d hover:scale-[1.02] transition-transform duration-700 ease-[cubic-bezier(0.23,1,0.32,1)]">
    
    <!-- Shadow for depth -->
    <div class="absolute inset-x-12 bottom-[-40px] h-20 bg-brand-900/20 blur-[50px] transform rotate-x-90 translate-z-[-80px] rounded-[100%]"></div>

    <!-- Layer 1: Backplane (Dark Glass) -->
    <div class="absolute inset-0 bg-[#0f172a] rounded-[2rem] transform translate-z-[-30px] shadow-2xl border border-gray-700 ring-1 ring-white/10 overflow-hidden">
        <!-- Abstract data grid -->
        <div class="absolute inset-0 opacity-20 bg-[linear-gradient(rgba(142,202,230,0.1)_1px,transparent_1px),linear-gradient(90deg,rgba(142,202,230,0.1)_1px,transparent_1px)] bg-[length:30px_30px]"></div>
        <div class="absolute top-0 right-0 w-[300px] h-[300px] bg-brand-500/20 blur-[80px] rounded-full"></div>
    </div>

    <!-- Layer 2: Main Interface Surface -->
    <div class="absolute inset-4 bg-gray-900/90 backdrop-blur-xl rounded-[1.5rem] transform translate-z-[10px] shadow-xl border border-white/10 flex flex-col overflow-hidden">
        <!-- Header -->
        <div class="h-12 border-b border-white/5 flex items-center px-6 justify-between">
            <div class="flex gap-2">
                <div class="w-2.5 h-2.5 rounded-full bg-gray-600"></div>
                <div class="w-2.5 h-2.5 rounded-full bg-gray-600"></div>
            </div>
            <div class="text-[10px] text-brand-300 font-mono tracking-widest uppercase">Live_Feed_01</div>
        </div>
        
        <!-- Content Area -->
        <div class="flex-1 relative p-6">
            <!-- Map Simulation -->
            <svg class="w-full h-full opacity-80" viewBox="0 0 400 200" preserveAspectRatio="none">
                 <!-- Route Path -->
                 <path d="M40,160 Q120,100 200,140 T360,80" stroke="url(#gradientLine)" stroke-width="4" fill="none" stroke-linecap="round" />
                 
                 <!-- Gradient definition -->
                 <defs>
                    <linearGradient id="gradientLine" x1="0%" y1="0%" x2="100%" y2="0%">
                        <stop offset="0%" stop-color="#219ebc" /> <!-- brand-500 -->
                        <stop offset="100%" stop-color="#ffafcc" /> <!-- accent-pink -->
                    </linearGradient>
                 </defs>

                 <!-- Moving vehicle node -->
                 <circle cx="0" cy="0" r="6" fill="#f0f9ff" stroke="#219ebc" stroke-width="2">
                    <animateMotion dur="5s" repeatCount="indefinite" path="M40,160 Q120,100 200,140 T360,80" keyPoints="0;1" keyTimes="0;1" calcMode="linear" />
                 </circle>
            </svg>

            <!-- Overlay Stats -->
            <div class="absolute bottom-6 left-6 right-6 flex justify-between items-end">
                <div>
                    <div class="text-xs text-gray-400 mb-1">Coordinates</div>
                    <div class="text-sm font-mono text-brand-200">34.0522° N, 118.2437° W</div>
                </div>
            </div>
        </div>
    </div>

    <!-- Layer 3: Floating Elements (High Z) -->
    
    <!-- Float Card 1: Driver Profile -->
    <div class="glass-card absolute top-12 -right-8 w-44 p-3 flex items-center gap-3 transform translate-z-[50px] animate-float">
        <div class="w-10 h-10 rounded-full bg-gray-200 overflow-hidden border-2 border-brand-300">
             <img src="https://ui-avatars.com/api/?name=Alex+R&background=random" alt="Driver" class="w-full h-full object-cover" />
        </div>
        <div>
            <div class="text-[10px] text-gray-500 font-bold uppercase">Driver</div>
            <div class="text-sm font-black text-gray-900">Alex R.</div>
        </div>
    </div>

    <!-- Float Card 2: Status Pill -->
    <div class="glass-card absolute bottom-20 -left-6 px-4 py-2 flex items-center gap-2 transform translate-z-[70px] animate-float" style="animation-delay: 1s;">
         <div class="relative flex h-2 w-2">
            <span class="animate-ping absolute inline-flex h-full w-full rounded-full bg-accent-pink opacity-75"></span>
            <span class="relative inline-flex rounded-full h-2 w-2 bg-accent-pink"></span>
         </div>
         <span class="text-xs font-bold text-gray-800">ETA: 12m</span>
    </div>

    <!-- Layer 4: Reflection -->
    <div class="absolute inset-0 rounded-[2rem] bg-gradient-to-tr from-white/20 via-transparent to-transparent pointer-events-none transform translate-z-[40px] border border-white/20"></div>

  </div>
</div>