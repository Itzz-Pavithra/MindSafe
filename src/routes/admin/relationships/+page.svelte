<script>
  import { onMount } from 'svelte';
  import Card from '$lib/components/Card.svelte';
  import ChartCanvas from '$lib/components/ChartCanvas.svelte';
  import EmptyState from '$lib/components/EmptyState.svelte';

  let varX = $state('frequency');
  let varY = $state('mentalHealthImpact');
  let relData = $state(null);
  let isLoading = $state(true);
  let hasData = $derived(relData && relData.hasData && relData.totalResponses > 0);

  const varXOptions = [
    { value: 'frequency', label: 'Cyberbullying Encounter Frequency' },
    { value: 'usage', label: 'Social Media Daily Usage Hours' },
    { value: 'experience', label: 'Direct Cyberbullying Experience (Yes / No)' },
    { value: 'platform', label: 'Primary Social Media Platform' }
  ];

  async function loadData() {
    isLoading = true;
    try {
      const res = await fetch(`/api/admin/relationships?varX=${varX}&varY=${varY}`);
      if (res.ok) {
        relData = await res.json();
      }
    } catch (e) {
      console.error('Failed to load relationship explorer data:', e);
    } finally {
      isLoading = false;
    }
  }

  onMount(() => {
    loadData();
  });

  function handleVarXChange(e) {
    varX = e.target.value;
    loadData();
  }

  let chartData = $derived.by(() => {
    if (!hasData || !relData.labels || !relData.datasets) return null;
    return {
      labels: relData.labels,
      datasets: relData.datasets
    };
  });
</script>

<div class="max-w-6xl mx-auto space-y-6 page-fade-in font-sans">
  
  <div class="border-b border-[#F0D5DD] pb-4">
    <h1 class="page-title text-2xl text-[#601D49]">Relationship Explorer</h1>
    <p class="text-xs text-[#82476B] mt-0.5">
      Interactive bivariate cross-tabulation and non-causal association analysis
    </p>
  </div>

  <!-- Interactive Controls Card -->
  <Card class="p-5 bg-white border border-[#F0D5DD] space-y-4">
    <div class="grid grid-cols-1 sm:grid-cols-2 gap-4">
      
      <!-- Variable X Dropdown -->
      <div class="space-y-1.5">
        <label for="var-x-select" class="label-text block">
          Independent Variable (Variable X)
        </label>
        <select 
          id="var-x-select"
          value={varX}
          onchange={handleVarXChange}
          class="w-full px-3.5 py-2.5 rounded-xl bg-[#FAF7F8] border border-[#EA9D9D]/60 text-xs font-semibold text-[#601D49] focus:outline-none focus:border-[#BD5579]"
        >
          {#each varXOptions as opt}
            <option value={opt.value}>{opt.label}</option>
          {/each}
        </select>
      </div>

      <!-- Variable Y (Locked to Mental Health Impact) -->
      <div class="space-y-1.5">
        <label for="var-y-select" class="label-text block">
          Outcome Variable (Variable Y)
        </label>
        <div 
          id="var-y-select"
          class="w-full px-3.5 py-2.5 rounded-xl bg-[#FFEBB8]/40 border border-[#EA9D9D]/60 text-xs font-bold text-[#601D49] flex items-center justify-between"
        >
          <span>Mental Health Impact (Multiclass Outcome)</span>
          <span class="text-[10px] text-[#BD5579] font-bold uppercase">Main Target</span>
        </div>
      </div>

    </div>
  </Card>

  {#if !hasData}
    <EmptyState 
      title="No Survey Data Available Yet"
      description="Cross-tabulation and association matrices will compute dynamically once real survey data is collected. No simulated data is inserted."
      icon="chart"
    />
  {:else}
    <!-- Visualization & Association Matrix -->
    <div class="grid grid-cols-1 lg:grid-cols-3 gap-6">
      
      <!-- Grouped Bar Chart -->
      <Card class="p-6 lg:col-span-2 space-y-4">
        <div class="flex items-center justify-between border-b border-[#F0D5DD] pb-3">
          <h3 class="card-heading">Observed Bivariate Distribution</h3>
          <span class="text-xs text-[#82476B]">Non-causal cross-tabulation</span>
        </div>
        {#if chartData}
          <ChartCanvas type="bar" data={chartData} height={300} />
        {/if}
      </Card>

      <!-- Statistical Result & Academic Interpretation -->
      <Card class="p-6 space-y-4">
        <h3 class="card-heading border-b border-[#F0D5DD] pb-3">Association Metrics</h3>

        <div class="space-y-3">
          <div class="p-3.5 rounded-xl bg-[#FAF7F8] border border-[#F0D5DD] space-y-1">
            <span class="text-[11px] font-semibold text-[#82476B]">Test of Independence</span>
            <p class="text-xs font-bold text-[#601D49]">Chi-Square Contingency Test</p>
            {#if relData.associationStats}
              <div class="pt-1 text-[11px] text-[#601D49] space-y-0.5">
                <div>Chi-Square: <span class="font-bold text-[#BD5579]">{relData.associationStats.chiSquare}</span></div>
                <div>df: <span class="font-bold">{relData.associationStats.degreesOfFreedom}</span></div>
                <div>Cramér's V: <span class="font-bold text-[#BD5579]">{relData.associationStats.cramersV}</span></div>
              </div>
            {/if}
          </div>

          <div class="p-3.5 rounded-xl bg-[#FFEBB8]/40 border border-[#EA9D9D]/60 space-y-1">
            <span class="text-[11px] font-bold text-[#601D49]">Academic Interpretation</span>
            <p class="text-xs text-[#601D49] leading-relaxed">
              {relData.interpretation}
            </p>
          </div>

          <div class="p-3 rounded-lg border border-[#F0D5DD] text-[11px] text-[#82476B] leading-relaxed">
            <strong>Methodology Note:</strong> Analyzed variables evaluate empirical associations and observed patterns without asserting direct causal relationships.
          </div>
        </div>
      </Card>

    </div>
  {/if}

</div>
