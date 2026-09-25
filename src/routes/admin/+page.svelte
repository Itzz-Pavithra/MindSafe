<script>
  import Logo from '$lib/components/Logo.svelte';
  import Button from '$lib/components/Button.svelte';
  import Card from '$lib/components/Card.svelte';
  import { appState } from '$lib/state/appState.svelte.js';

  let { data } = $props();

  const summary = $derived(data?.summary || {
    totalRespondents: 0,
    distribution: {
      'Not at all': 0,
      'Slightly': 0,
      'Moderately': 0,
      'Severely': 0
    },
    mostCommonClass: 'None'
  });

  const targetClasses = ['Not at all', 'Slightly', 'Moderately', 'Severely'];

  async function handleLogout() {
    await appState.logout();
  }
</script>

<svelte:head>
  <title>Admin Respondent Summary | MindSafe</title>
</svelte:head>

<div class="min-h-screen bg-[#FAF7F8] font-sans text-[#601D49] flex flex-col">
  
  <!-- Admin Header -->
  <header class="bg-white border-b border-[#F0D5DD] px-4 sm:px-6 py-3.5 sticky top-0 z-30 shadow-xs">
    <div class="max-w-5xl mx-auto flex items-center justify-between">
      <div class="flex items-center gap-3">
        <Logo size="md" />
        <span class="px-2.5 py-0.5 rounded text-[10px] font-bold bg-[#FFEBB8] text-[#601D49] border border-[#EA9D9D]/60 uppercase tracking-wider">
          Admin Portal
        </span>
      </div>

      <div class="flex items-center gap-4">
        <div class="hidden sm:block text-right">
          <span class="text-xs font-bold text-[#601D49] block leading-tight">
            {data?.adminUser?.name || 'Administrator'}
          </span>
          <span class="text-[10px] text-[#82476B] block">
            {data?.adminUser?.email || 'admin'}
          </span>
        </div>

        <Button 
          variant="outline" 
          onclick={handleLogout}
          class="px-3 py-1.5 text-xs font-semibold text-[#BD5579] border-[#EA9D9D] hover:bg-[#FFEBB8]/40"
        >
          <svg class="w-3.5 h-3.5 mr-1" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" d="M15.75 9V5.25A2.25 2.25 0 0013.5 3h-6a2.25 2.25 0 00-2.25 2.25v13.5A2.25 2.25 0 007.5 21h6a2.25 2.25 0 002.25-2.25V15m3 0l3-3m0 0l-3-3m3 3H9" />
          </svg>
          <span>Sign Out</span>
        </Button>
      </div>
    </div>
  </header>

  <!-- Main Content Container -->
  <main class="flex-1 max-w-5xl w-full mx-auto px-4 sm:px-6 py-8 space-y-6">
    
    <!-- Title & Purpose Banner -->
    <div class="space-y-1">
      <h1 class="page-title text-2xl sm:text-3xl font-extrabold text-[#601D49]">
        Respondent Prediction Summary
      </h1>
      <p class="text-xs sm:text-sm text-[#82476B]">
        Real-time monitoring of submitted survey responses and model classification outcomes.
      </p>
    </div>

    <!-- Summary KPI Cards: Total Respondents & Most Common Class -->
    <div class="grid grid-cols-1 sm:grid-cols-2 gap-4">
      
      <!-- Card A: Total Respondents -->
      <Card class="p-6 bg-white border border-[#F0D5DD] shadow-xs space-y-2">
        <div class="flex items-center justify-between">
          <span class="text-xs font-bold uppercase tracking-wider text-[#BD5579]">
            Total Submissions
          </span>
          <div class="w-8 h-8 rounded-lg bg-[#FFEBB8]/60 text-[#BD5579] flex items-center justify-center border border-[#EA9D9D]/50">
            <svg class="w-4 h-4" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" d="M18 18.72a9.094 9.094 0 003.741-.479 3 3 0 00-4.682-2.72m.94 3.198l.001.031c0 .225-.012.447-.037.666A11.944 11.944 0 0112 21c-2.17 0-4.207-.576-5.963-1.584A6.062 6.062 0 016 18.719m12 0a5.971 5.971 0 00-.941-3.197m0 0A5.995 5.995 0 0012 12.75a5.995 5.995 0 00-5.058 2.772m0 0a3 3 0 00-4.681 2.72 8.986 8.986 0 003.74.477m.94-3.197a5.971 5.971 0 00-.94 3.197M15 6.75a3 3 0 11-6 0 3 3 0 016 0zm6 3a2.25 2.25 0 11-4.5 0 2.25 2.25 0 014.5 0zm-13.5 0a2.25 2.25 0 11-4.5 0 2.25 2.25 0 014.5 0z" />
            </svg>
          </div>
        </div>
        <div class="text-3xl sm:text-4xl font-extrabold text-[#601D49]">
          {summary.totalRespondents}
        </div>
        <p class="text-xs text-[#82476B]">
          Total respondents who submitted responses
        </p>
      </Card>

      <!-- Card C: Most Common Predicted Class -->
      <Card class="p-6 bg-white border border-[#F0D5DD] shadow-xs space-y-2">
        <div class="flex items-center justify-between">
          <span class="text-xs font-bold uppercase tracking-wider text-[#BD5579]">
            Dominant Class
          </span>
          <div class="w-8 h-8 rounded-lg bg-[#EBF7EE] text-[#22543D] flex items-center justify-center border border-[#48BB78]/40">
            <svg class="w-4 h-4" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" d="M3 13.125C3 12.504 3.504 12 4.125 12h2.25c.621 0 1.125.504 1.125 1.125v6.75C7.5 20.496 6.996 21 6.375 21h-2.25A1.125 1.125 0 013 19.875v-6.75zM9.75 8.625c0-.621.504-1.125 1.125-1.125h2.25c.621 0 1.125.504 1.125 1.125v11.25c0 .621-.504 1.125-1.125 1.125h-2.25a1.125 1.125 0 01-1.125-1.125V8.625zM16.5 4.125c0-.621.504-1.125 1.125-1.125h2.25C20.496 3 21 3.504 21 4.125v15.75c0 .621-.504 1.125-1.125 1.125h-2.25a1.125 1.125 0 01-1.125-1.125V4.125z" />
            </svg>
          </div>
        </div>
        <div class="text-2xl sm:text-3xl font-extrabold text-[#601D49]">
          {summary.mostCommonClass}
        </div>
        <p class="text-xs text-[#82476B]">
          Prediction class with the highest number of respondents
        </p>
      </Card>

    </div>

    <!-- Card B: Prediction Class Distribution -->
    <Card class="p-6 sm:p-7 bg-white border border-[#F0D5DD] shadow-xs space-y-4">
      <div class="border-b border-[#F0D5DD] pb-3 flex flex-col sm:flex-row sm:items-center justify-between gap-1">
        <div>
          <h2 class="text-base font-bold text-[#601D49]">
            Mental Health Impact Distribution
          </h2>
          <p class="text-xs text-[#82476B]">
            Number of respondents classified into each Mental Health Impact class
          </p>
        </div>
        <span class="text-xs text-[#82476B] font-medium">
          Total Classified: <strong class="text-[#601D49]">{summary.totalClassified}</strong>
        </span>
      </div>

      <!-- Clean Distribution Table -->
      <div class="overflow-x-auto">
        <table class="w-full text-left border-collapse">
          <thead>
            <tr class="border-b border-[#F0D5DD] text-xs font-bold text-[#82476B] uppercase tracking-wider">
              <th class="py-3 px-4">Mental Health Impact Class</th>
              <th class="py-3 px-4 text-right">Number of Respondents</th>
              <th class="py-3 px-4 text-right">Percentage</th>
            </tr>
          </thead>
          <tbody class="divide-y divide-[#F0D5DD] text-xs sm:text-sm">
            {#each targetClasses as cls}
              {@const count = summary.distribution[cls] || 0}
              {@const pct = summary.totalClassified > 0 ? ((count / summary.totalClassified) * 100).toFixed(1) : '0.0'}
              <tr class="hover:bg-[#FAF7F8]/80 transition-colors">
                <td class="py-3.5 px-4 font-semibold text-[#601D49] flex items-center gap-2">
                  <span class="w-2.5 h-2.5 rounded-full 
                    {cls === 'Not at all' ? 'bg-[#48BB78]' : 
                     cls === 'Slightly' ? 'bg-[#ECC94B]' : 
                     cls === 'Moderately' ? 'bg-[#ED8936]' : 'bg-[#E53E3E]'}">
                  </span>
                  <span>{cls}</span>
                </td>
                <td class="py-3.5 px-4 text-right font-bold text-[#601D49] text-base">
                  {count}
                </td>
                <td class="py-3.5 px-4 text-right text-xs font-semibold text-[#82476B]">
                  {pct}%
                </td>
              </tr>
            {/each}
          </tbody>
        </table>
      </div>
    </Card>

    <!-- Simple Operational Note -->
    <div class="p-4 rounded-xl bg-white border border-[#F0D5DD] flex items-center justify-between text-xs text-[#82476B]">
      <span>
        Database counts update automatically whenever a new respondent submits an assessment.
      </span>
      <span class="text-[11px] text-[#82476B]">
        Academic Research Monitoring
      </span>
    </div>

  </main>
</div>
