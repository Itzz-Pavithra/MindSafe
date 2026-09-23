<script>
  let { size = 'md', showText = true, className = '', dark = false } = $props();

  const iconSizes = {
    sm: 'w-7 h-7',
    md: 'w-9 h-9',
    lg: 'w-11 h-11'
  };

  const textSizes = {
    sm: 'text-base',
    md: 'text-lg',
    lg: 'text-2xl'
  };
</script>

<div class="flex items-center gap-2.5 {className}">
  <!-- Academic Shield & Research SVG Icon -->
  <div class="{iconSizes[size]} shrink-0 rounded-xl bg-[#601D49] text-white flex items-center justify-center border border-[#BD5579]/30 shadow-xs">
    <svg class="w-5 h-5 text-[#FFEBB8]" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24">
      <path stroke-linecap="round" stroke-linejoin="round" d="M9 12.75L11.25 15 15 9.75m-3-7.036A11.959 11.959 0 013.598 6 11.99 11.99 0 003 9.749c0 5.592 3.824 10.29 9 11.623 5.176-1.332 9-6.03 9-11.622 0-1.31-.21-2.571-.598-3.751A11.959 11.959 0 0112 2.714z" />
    </svg>
  </div>

  {#if showText}
    <div class="flex flex-col text-left select-none">
      <div class="{textSizes[size]} font-bold tracking-tight leading-none {dark ? 'text-white' : 'text-[#601D49]'} flex items-center gap-0.5">
        <span>Mind</span><span class="text-[#BD5579]">Safe</span>
      </div>
      <span class="text-[10.5px] font-medium {dark ? 'text-[#EA9D9D]' : 'text-[#82476B]'} tracking-wide mt-0.5">
        Cyberbullying & Mental Health Analytics
      </span>
    </div>
  {/if}
</div>
