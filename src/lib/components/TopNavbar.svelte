<script>
  import { appState } from '$lib/state/appState.svelte.js';

  let { toggleMobile, title = '' } = $props();
</script>

<header class="bg-white border-b border-[#F0D5DD] px-4 sm:px-6 py-3 flex items-center justify-between sticky top-0 z-30 shadow-xs">
  <div class="flex items-center gap-3">
    {#if toggleMobile}
      <button 
        onclick={toggleMobile}
        class="lg:hidden p-2 rounded-xl text-[#601D49] hover:bg-[#FAF7F8] border border-[#F0D5DD] cursor-pointer"
        aria-label="Toggle Navigation"
      >
        <svg class="w-5 h-5" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" d="M3.75 6.75h16.5M3.75 12h16.5m-16.5 5.25h16.5" />
        </svg>
      </button>
    {/if}

    <div>
      <div class="flex items-center gap-2.5">
        <h2 class="text-sm sm:text-base font-bold text-[#601D49] tracking-tight leading-tight">
          {title || 'MindSafe Workspace'}
        </h2>
        <span class="px-2 py-0.5 rounded text-[10px] font-semibold bg-[#FFEBB8] text-[#601D49] border border-[#EA9D9D]/60">
          Survey Respondent
        </span>
      </div>
      <p class="text-[11px] text-[#82476B] hidden md:block mt-0.5">
        MindSafe • Academic Research on Cyberbullying & Mental Health Impact
      </p>
    </div>
  </div>

  <div class="flex items-center gap-2.5 sm:gap-3">
    <!-- User Badge -->
    <div class="flex items-center gap-2 pl-2 sm:pl-3">
      <div class="w-8 h-8 rounded-full bg-[#BD5579] text-white flex items-center justify-center font-bold text-xs shadow-xs">
        {appState.user?.name ? appState.user.name.charAt(0).toUpperCase() : 'U'}
      </div>
      <div class="hidden sm:block text-left">
        <span class="text-xs font-bold text-[#601D49] block leading-tight">{appState.user?.name || 'User'}</span>
        <span class="text-[10px] text-[#82476B] block">{appState.user?.roleLabel || 'Survey User'}</span>
      </div>
    </div>
  </div>
</header>
