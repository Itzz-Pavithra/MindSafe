<script>
  import Logo from '$lib/components/Logo.svelte';
  import Button from '$lib/components/Button.svelte';
  import Card from '$lib/components/Card.svelte';
  import { appState } from '$lib/state/appState.svelte.js';

  let { data } = $props();

  $effect(() => {
    if (data?.user) {
      appState.init(data.user);
    }
  });

  let dashboardHref = '/dashboard';
</script>

<div class="min-h-screen bg-[#FAF7F8] flex flex-col justify-between font-sans text-[#601D49]">
  
  <!-- Header Navigation -->
  <header class="bg-white border-b border-[#F0D5DD] px-6 py-4 shadow-xs sticky top-0 z-30">
    <div class="max-w-6xl mx-auto flex items-center justify-between">
      <Logo size="md" />

      <div class="flex items-center gap-3">
        {#if appState.isLoggedIn}
          <a href={dashboardHref}>
            <Button variant="primary" class="px-4 py-2 text-xs font-semibold">
              <span>Go to Workspace</span>
              <svg class="w-3.5 h-3.5" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" d="M13.5 4.5L21 12m0 0l-7.5 7.5M21 12H3" />
              </svg>
            </Button>
          </a>
        {:else}
          <a href="/login">
            <Button variant="outline" class="px-4 py-2 text-xs font-semibold">
              <svg class="w-3.5 h-3.5 text-[#BD5579]" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" d="M15.75 9V5.25A2.25 2.25 0 0013.5 3h-6a2.25 2.25 0 00-2.25 2.25v13.5A2.25 2.25 0 007.5 21h6a2.25 2.25 0 002.25-2.25V15m3 0l3-3m0 0l-3-3m3 3H9" />
              </svg>
              <span>Sign In</span>
            </Button>
          </a>
          <a href="/register">
            <Button variant="primary" class="px-4 py-2 text-xs font-semibold">
              <span>Register</span>
              <svg class="w-3.5 h-3.5" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" d="M13.5 4.5L21 12m0 0l-7.5 7.5M21 12H3" />
              </svg>
            </Button>
          </a>
        {/if}
      </div>
    </div>
  </header>

  <!-- Hero Section -->
  <main class="flex-1 max-w-5xl mx-auto px-6 py-12 md:py-16 flex flex-col items-center text-center justify-center space-y-8">
    
    <!-- Academic Badge -->
    <div class="inline-flex items-center gap-2 px-3.5 py-1.5 rounded-full bg-[#FFEBB8] border border-[#EA9D9D]/70 text-[#601D49] text-xs font-semibold shadow-xs">
      <svg class="w-3.5 h-3.5 text-[#BD5579]" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24">
        <path stroke-linecap="round" stroke-linejoin="round" d="M4.26 10.147a60.436 60.436 0 00-.491 6.347A48.627 48.627 0 0112 20.904a48.627 48.627 0 018.232-4.41 60.46 60.46 0 00-.491-6.347m-15.482 0a50.57 50.57 0 00-2.658-.813A59.905 59.905 0 0112 3.493a59.902 59.902 0 0110.399 5.84c-.896.248-1.783.52-2.658.814m-15.482 0A50.697 50.697 0 0112 13.489a50.702 50.702 0 017.74-3.342" />
      </svg>
      <span>Academic College Research Platform</span>
    </div>

    <!-- Title & Abstract -->
    <div class="space-y-4 max-w-3xl">
      <h1 class="page-title text-3xl sm:text-4xl md:text-5xl leading-tight text-[#601D49]">
        MindSafe – An AI-Based Cyberbullying & Its Impact on <span class="text-[#BD5579]">Mental Health</span>
      </h1>

      <p class="body-text text-sm sm:text-base text-[#82476B] max-w-2xl mx-auto leading-relaxed">
        An academic research platform analyzing primary survey data on digital harassment exposure, psychological well-being, and screen usage. Built with a statistical-analysis backend and architecture prepared for supervised multiclass machine learning classification.
      </p>
    </div>

    <!-- Action Buttons -->
    <div class="flex flex-wrap items-center justify-center gap-3 pt-2">
      <a href="/login">
        <Button variant="primary" class="px-6 py-3 text-xs sm:text-sm font-semibold">
          <svg class="w-4 h-4" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" d="M15.75 6a3.75 3.75 0 11-7.5 0 3.75 3.75 0 017.5 0zM4.501 20.118a7.5 7.5 0 0114.998 0A17.933 17.933 0 0112 21.75c-2.676 0-5.216-.584-7.499-1.632z" />
          </svg>
          <span>Participate in Assessment</span>
        </Button>
      </a>

      <a href="/register">
        <Button variant="outline" class="px-6 py-3 text-xs sm:text-sm font-semibold">
          <svg class="w-4 h-4 text-[#BD5579]" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" d="M19 7.5v3m0 0v3m0-3h3m-3 0h-3m-2.25-4.125a3.375 3.375 0 11-6.75 0 3.375 3.375 0 016.75 0zM4 19.235v-.11a6.375 6.375 0 0112.75 0v.109A12.318 12.318 0 0110.374 21c-2.331 0-4.512-.645-6.374-1.765z" />
          </svg>
          <span>Register Account</span>
        </Button>
      </a>
    </div>

    <!-- Research Pillar Cards -->
    <div class="grid grid-cols-1 md:grid-cols-3 gap-5 w-full pt-4 text-left">
      <Card class="p-6 space-y-3 bg-white" hover={true}>
        <div class="w-10 h-10 rounded-xl bg-[#FFEBB8]/50 text-[#BD5579] border border-[#EA9D9D]/60 font-bold flex items-center justify-center shadow-xs">
          <svg class="w-5 h-5" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" d="M3.75 3v11.25A2.25 2.25 0 006 16.5h2.25M3.75 3h-1.5m1.5 0h16.5m0 0h1.5m-1.5 0v11.25A2.25 2.25 0 0118 16.5h-2.25m-7.5 0h7.5m-7.5 0l-1 3m8.5-3l1 3m0 0l.5 1.5m-.5-1.5h-9.5m0 0l-.5 1.5" />
          </svg>
        </div>
        <div class="space-y-1">
          <h3 class="card-heading text-sm">Empirical Primary Data</h3>
          <p class="text-xs text-[#82476B] leading-relaxed">
            Real survey collection addressing demographics, screen time, harassment frequency, and psychological impact indicators.
          </p>
        </div>
      </Card>

      <Card class="p-6 space-y-3 bg-white" hover={true}>
        <div class="w-10 h-10 rounded-xl bg-[#FFEBB8]/50 text-[#BD5579] border border-[#EA9D9D]/60 font-bold flex items-center justify-center shadow-xs">
          <svg class="w-5 h-5" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" d="M21 8.25c0-2.485-2.099-4.5-4.688-4.5-1.935 0-3.597 1.126-4.312 2.733-.715-1.607-2.377-2.733-4.313-2.733C5.1 3.75 3 5.765 3 8.25c0 7.22 9 12 9 12s9-4.78 9-12z" />
          </svg>
        </div>
        <div class="space-y-1">
          <h3 class="card-heading text-sm">Mental Health Target</h3>
          <p class="text-xs text-[#82476B] leading-relaxed">
            Architected for Supervised Multiclass Classification across 4 target classes: Not at all, Slightly, Moderately, Severely.
          </p>
        </div>
      </Card>

      <Card class="p-6 space-y-3 bg-white" hover={true}>
        <div class="w-10 h-10 rounded-xl bg-[#FFEBB8]/50 text-[#BD5579] border border-[#EA9D9D]/60 font-bold flex items-center justify-center shadow-xs">
          <svg class="w-5 h-5" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" d="M9 12.75L11.25 15 15 9.75m-3-7.036A11.959 11.959 0 013.598 6 11.99 11.99 0 003 9.749c0 5.592 3.824 10.29 9 11.623 5.176-1.332 9-6.03 9-11.622 0-1.31-.21-2.571-.598-3.751A11.959 11.959 0 0112 2.714z" />
          </svg>
        </div>
        <div class="space-y-1">
          <h3 class="card-heading text-sm">Statistical Foundation</h3>
          <p class="text-xs text-[#82476B] leading-relaxed">
            Real descriptive and inferential tests (Mean, Median, Mode, Chi-square, T-test, Correlation) with non-causal association metrics.
          </p>
        </div>
      </Card>
    </div>

  </main>

  <!-- Footer -->
  <footer class="border-t border-[#F0D5DD] bg-white py-5 px-6 text-center text-xs text-[#82476B]">
    <div class="max-w-6xl mx-auto flex flex-col sm:flex-row items-center justify-between gap-2">
      <span>MindSafe • An AI-Based Cyberbullying and Its Impact on Mental Health</span>
      <span class="text-[11px] text-[#82476B]">Academic Research Tool • Not a medical diagnosis system</span>
    </div>
  </footer>

</div>
