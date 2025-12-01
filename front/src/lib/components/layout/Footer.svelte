<script lang="ts">
  // Get current year
  const currentYear = new Date().getFullYear();
</script>

<footer class="bg-gray-900 text-white border-t border-gray-800 mt-auto">
  <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-16">
    <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-12">
      <!-- Brand -->
      <div class="space-y-6">
        <div class="flex items-center gap-3">
          <div class="w-10 h-10 rounded-xl bg-gradient-to-br from-brand-500 to-brand-700 flex items-center justify-center text-white shadow-lg shadow-brand-500/20">
            <svg xmlns="http://www.w3.org/2000/svg" class="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8 7h12m0 0l-4-4m4 4l-4 4m0 6H4m0 0l4 4m-4-4l4-4" />
            </svg>
          </div>
          <span class="font-display font-bold text-2xl tracking-tight">
            Bus<span class="text-brand-400">Tracker</span>
          </span>
        </div>
        <p class="text-gray-400 text-sm leading-relaxed">
          Advanced NFC-based employee attendance and bus tracking system for modern enterprises. Streamline your fleet management today.
        </p>
        <div class="flex gap-4">
          <!-- Social Icons -->
          {#each ['twitter', 'github', 'linkedin'] as social}
            <a href="/" class="w-10 h-10 rounded-lg bg-gray-800 flex items-center justify-center text-gray-400 hover:bg-brand-600 hover:text-white transition-all duration-300">
              <span class="sr-only">{social}</span>
              <svg class="w-5 h-5" fill="currentColor" viewBox="0 0 24 24" aria-hidden="true">
                <path fill-rule="evenodd" d="M12 2C6.477 2 2 6.484 2 12.017c0 4.425 2.865 8.18 6.839 9.504.5.092.682-.217.682-.483 0-.237-.008-.868-.013-1.703-2.782.605-3.369-1.343-3.369-1.343-.454-1.158-1.11-1.466-1.11-1.466-.908-.62.069-.608.069-.608 1.003.07 1.531 1.032 1.531 1.032.892 1.53 2.341 1.088 2.91.832.092-.647.35-1.088.636-1.338-2.22-.253-4.555-1.113-4.555-4.951 0-1.093.39-1.988 1.029-2.688-.103-.253-.446-1.272.098-2.65 0 0 .84-.27 2.75 1.026A9.564 9.564 0 0112 6.844c.85.004 1.705.115 2.504.337 1.909-1.296 2.747-1.027 2.747-1.027.546 1.379.202 2.398.1 2.651.64.7 1.028 1.595 1.028 2.688 0 3.848-2.339 4.695-4.566 4.943.359.309.678.92.678 1.855 0 1.338-.012 2.419-.012 2.747 0 .268.18.58.688.482A10.019 10.019 0 0022 12.017C22 6.484 17.522 2 12 2z" clip-rule="evenodd" />
              </svg>
            </a>
          {/each}
        </div>
      </div>

      <!-- Quick Links -->
      <div>
        <h3 class="font-display font-bold text-lg mb-6 text-white">Quick Links</h3>
        <ul class="space-y-4">
          <li><a href="/about" class="text-gray-400 hover:text-brand-400 transition-colors text-sm flex items-center gap-2 group">
            <span class="w-1.5 h-1.5 rounded-full bg-brand-500 opacity-0 group-hover:opacity-100 transition-opacity"></span>
            About Us
          </a></li>
          <li><a href="/features" class="text-gray-400 hover:text-brand-400 transition-colors text-sm flex items-center gap-2 group">
            <span class="w-1.5 h-1.5 rounded-full bg-brand-500 opacity-0 group-hover:opacity-100 transition-opacity"></span>
            Features
          </a></li>
          <li><a href="/pricing" class="text-gray-400 hover:text-brand-400 transition-colors text-sm flex items-center gap-2 group">
            <span class="w-1.5 h-1.5 rounded-full bg-brand-500 opacity-0 group-hover:opacity-100 transition-opacity"></span>
            Pricing
          </a></li>
          <li><a href="/contact" class="text-gray-400 hover:text-brand-400 transition-colors text-sm flex items-center gap-2 group">
            <span class="w-1.5 h-1.5 rounded-full bg-brand-500 opacity-0 group-hover:opacity-100 transition-opacity"></span>
            Contact Support
          </a></li>
        </ul>
      </div>

      <!-- Legal -->
      <div>
        <h3 class="font-display font-bold text-lg mb-6 text-white">Legal</h3>
        <ul class="space-y-4">
          <li><a href="/privacy" class="text-gray-400 hover:text-brand-400 transition-colors text-sm flex items-center gap-2 group">
            <span class="w-1.5 h-1.5 rounded-full bg-brand-500 opacity-0 group-hover:opacity-100 transition-opacity"></span>
            Privacy Policy
          </a></li>
          <li><a href="/terms" class="text-gray-400 hover:text-brand-400 transition-colors text-sm flex items-center gap-2 group">
            <span class="w-1.5 h-1.5 rounded-full bg-brand-500 opacity-0 group-hover:opacity-100 transition-opacity"></span>
            Terms of Service
          </a></li>
          <li><a href="/cookies" class="text-gray-400 hover:text-brand-400 transition-colors text-sm flex items-center gap-2 group">
            <span class="w-1.5 h-1.5 rounded-full bg-brand-500 opacity-0 group-hover:opacity-100 transition-opacity"></span>
            Cookie Policy
          </a></li>
        </ul>
      </div>

      <!-- Newsletter -->
      <div>
        <h3 class="font-display font-bold text-lg mb-6 text-white">Stay Updated</h3>
        <p class="text-gray-400 text-sm mb-4">Subscribe to our newsletter for the latest updates and features.</p>
        <form class="space-y-3" onsubmit={(e) => e.preventDefault()}>
          <div class="relative">
            <input 
              type="email" 
              placeholder="Enter your email" 
              class="w-full bg-gray-800 border border-gray-700 rounded-xl px-4 py-3 text-sm text-white placeholder-gray-500 focus:outline-none focus:border-brand-500 focus:ring-1 focus:ring-brand-500 transition-all"
            />
          </div>
          <button type="submit" class="w-full bg-brand-600 hover:bg-brand-700 text-white font-semibold py-3 px-4 rounded-xl transition-colors text-sm shadow-lg shadow-brand-500/20">
            Subscribe
          </button>
        </form>
      </div>
    </div>

    <div class="border-t border-gray-800 mt-16 pt-8 flex flex-col md:flex-row justify-between items-center gap-4">
      <p class="text-gray-500 text-sm">
        &copy; {currentYear} Bus Tracker. All rights reserved.
      </p>
      <p class="text-gray-500 text-sm flex items-center gap-1">
        Developed by <a href="https://ringo-solutions.com" class="font-medium text-brand-400 hover:text-brand-300 transition-colors">Ringo-solutions - Ahmed Bashir</a>
      </p>
    </div>
  </div>
</footer>
