<script>
  import { onMount } from 'svelte';
  import Card from '$lib/components/Card.svelte';
  import ChartCanvas from '$lib/components/ChartCanvas.svelte';
  import EmptyState from '$lib/components/EmptyState.svelte';

  let mentalData = $state(null);
  let isLoading = $state(true);
  let hasData = $derived(mentalData && mentalData.hasData && mentalData.totalResponses > 0);

  onMount(async () => {
    try {
      const res = await fetch('/api/admin/mental-health-analysis');
      if (res.ok) {
        mentalData = await res.json();
      }
    } catch (e) {
      console.error('Failed to load mental health analysis:', e);
    } finally {
      isLoading = false;
    }
  });

  let chartData = $derived.by(() => {
    if (!hasData || !mentalData.distribution) return null;
    return {
      labels: ['Not at all', 'Slightly', 'Moderately', 'Severely'],
      datasets: [{
        label: 'Respondent Count',
        data: [
          mentalData.distribution['Not at all'] || 0,
          mentalData.distribution['Slightly'] || 0,
          mentalData.distribution['Moderately'] || 0,
          mentalData.distribution['Severely'] || 0
        ],
        backgroundColor: ['#601D49', '#BD5579', '#EA9D9D', '#FFEBB8'],
        borderRadius: 6
      }]
    };
  });
</script>

<div class="max-w-5xl mx-auto space-y-6 page-fade-in font-sans">
  
  <div class="border-b border-[#F0D5DD] pb-4">
    <div class="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-[#FFEBB8] text-[#601D49] text-xs font-semibold border border-[#EA9D9D]/60 mb-2">
      <svg class="w-3.5 h-3.5 text-[#BD5579]" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24">
        <path stroke-linecap="round" stroke-linejoin="round" d="M21 8.25c0-2.485-2.099-4.5-4.688-4.5-1.935 0-3.597 1.126-4.312 2.733-.715-1.607-2.377-2.733-4.313-2.733C5.1 3.75 3 5.765 3 8.25c0 7.22 9 12 9 12s9-4.78 9-12z" />
      </svg>
      <span>Primary Research Target</span>
    </div>
    <h1 class="page-title text-2xl text-[#601D49]">Mental Health Impact Distribution</h1>
    <p class="text-xs text-[#82476B] mt-0.5">
      Empirical target distribution across 4 multiclass tiers for the supervised classification framework
    </p>
  </div>

  {#if !hasData}
    <EmptyState 
      title="No Mental Health Impact Data Available"
      description="Mental Health Impact distribution will be calculated from real survey submissions. No artificial distributions are simulated."
      icon="chart"
    />
  {:else}
    <div class="grid grid-cols-1 md:grid-cols-3 gap-6">
      
      <!-- Visualization Canvas -->
      <Card class="p-6 md:col-span-2 space-y-4">
        <div class="flex items-center justify-between border-b border-[#F0D5DD] pb-3">
          <h3 class="card-heading">Target Class Distribution (N = {mentalData.totalResponses})</h3>
          <span class="text-xs font-semibold text-[#BD5579]">Multiclass 4-Tier</span>
        </div>
        {#if chartData}
          <ChartCanvas type="bar" data={chartData} height={280} />
        {/if}
      </Card>

      <!-- Distribution Table & Percentages -->
      <Card class="p-6 space-y-4">
        <h3 class="card-heading border-b border-[#F0D5DD] pb-3">Category Breakdown</h3>
        <div class="space-y-3">
          {#each ['Not at all', 'Slightly', 'Moderately', 'Severely'] as tier}
            <div class="p-3 rounded-xl bg-[#FAF7F8] border border-[#F0D5DD] space-y-1">
              <div class="flex items-center justify-between text-xs font-bold text-[#601D49]">
                <span>{tier}</span>
                <span class="text-[#BD5579]">{mentalData.percentages[tier] || 0}%</span>
              </div>
              <div class="flex items-center justify-between text-[11px] text-[#82476B]">
                <span>{mentalData.distribution[tier] || 0} respondents</span>
                <span class="text-[10px] opacity-75">
                  {tier === 'Not at all' ? 'Tier 1' : tier === 'Slightly' ? 'Tier 2' : tier === 'Moderately' ? 'Tier 3' : 'Tier 4'}
                </span>
              </div>
            </div>
          {/each}
        </div>
      </Card>

    </div>
  {/if}

</div>
