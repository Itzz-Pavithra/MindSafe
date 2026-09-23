<script>
  import { onMount } from 'svelte';
  import Card from '$lib/components/Card.svelte';
  import Button from '$lib/components/Button.svelte';
  import EmptyState from '$lib/components/EmptyState.svelte';

  let statData = $state(null);
  let isLoading = $state(true);

  // Variable Selection State
  let selectedVar1 = $state('frequency');
  let selectedVar2 = $state('emotionalWellbeing');
  let selectedTest = $state('chi_square');
  let isRunningTest = $state(false);
  let customResult = $state(null);
  let testError = $state('');

  // Active tab for categorical descriptives
  let activeCatTab = $state('ageGroup');

  let hasData = $derived(statData && statData.hasData && statData.totalResponses > 0);
  let variableCatalogue = $derived(statData?.variableCatalogue || []);

  onMount(async () => {
    await loadInitialData();
  });

  async function loadInitialData() {
    isLoading = true;
    try {
      const res = await fetch('/api/admin/statistical-analysis');
      if (res.ok) {
        statData = await res.json();
        // Load default test into customResult
        if (statData?.defaultTests?.chiSquare) {
          customResult = statData.defaultTests.chiSquare;
        }
      }
    } catch (e) {
      console.error('Failed to load statistical analysis:', e);
    } finally {
      isLoading = false;
    }
  }

  async function handleRunAnalysis() {
    isRunningTest = true;
    testError = '';
    customResult = null;

    try {
      const res = await fetch('/api/admin/statistical-analysis', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          testType: selectedTest,
          var1: selectedVar1,
          var2: selectedVar2
        })
      });

      const data = await res.json();
      if (res.ok && data.success) {
        customResult = data.result;
      } else {
        testError = data.error || 'Failed to compute statistical analysis.';
      }
    } catch (err) {
      console.error('Statistical test error:', err);
      testError = 'Network error while executing statistical test.';
    } finally {
      isRunningTest = false;
    }
  }
</script>

<div class="max-w-6xl mx-auto space-y-7 page-fade-in font-sans text-[#601D49]">
  
  <!-- Header Banner -->
  <div class="border-b border-[#F0D5DD] pb-4 flex flex-col sm:flex-row sm:items-center justify-between gap-3">
    <div>
      <div class="inline-flex items-center gap-1.5 px-2.5 py-0.5 rounded-full bg-[#FFEBB8] text-[10px] font-bold text-[#601D49] border border-[#EA9D9D]/70 uppercase tracking-wider mb-1">
        Academic Empirical Analysis
      </div>
      <h1 class="page-title text-2xl text-[#601D49]">Statistical Analysis & Hypothesis Testing</h1>
      <p class="text-xs text-[#82476B] mt-0.5">
        Descriptive metrics (Mean, Median, Mode) and inferential hypothesis testing (Chi-Square, T-Test, Correlation) computed dynamically from real MongoDB survey records.
      </p>
    </div>
    {#if hasData}
      <div class="px-3.5 py-2 rounded-xl bg-white border border-[#F0D5DD] shadow-xs text-right shrink-0">
        <span class="text-[10px] uppercase font-bold text-[#82476B] block">Analyzed Sample</span>
        <span class="text-sm font-bold text-[#601D49]">N = {statData.totalResponses} Responses</span>
      </div>
    {/if}
  </div>

  {#if isLoading}
    <div class="p-12 text-center">
      <div class="w-8 h-8 border-3 border-[#BD5579] border-t-transparent rounded-full animate-spin mx-auto"></div>
      <p class="text-xs text-[#82476B] font-medium mt-3">Loading statistical models from MongoDB...</p>
    </div>
  {:else if !hasData}
    <EmptyState 
      title="No survey data available yet."
      description="Statistical analyses and hypothesis tests will automatically compute once participants submit questionnaire responses. Zero synthetic or placeholder estimates are generated."
      icon="chart"
    />
  {:else}
    
    <!-- ======================================================== -->
    <!-- 1. VARIABLE SELECTION & INFERENTIAL TEST WORKSPACE       -->
    <!-- ======================================================== -->
    <Card class="p-6 sm:p-7 space-y-6 bg-white border border-[#F0D5DD] shadow-sm">
      <div class="border-b border-[#F0D5DD] pb-3 flex items-center justify-between">
        <div>
          <h2 class="text-base font-bold text-[#601D49]">Inferential Testing & Variable Selection Workspace</h2>
          <p class="text-xs text-[#82476B] mt-0.5">
            Select two variables from the questionnaire and choose an inferential statistical test. The system validates mathematical suitability before running.
          </p>
        </div>
      </div>

      <!-- Variable & Test Selection Form -->
      <div class="grid grid-cols-1 md:grid-cols-3 gap-4 p-4 rounded-2xl bg-[#FAF7F8] border border-[#F0D5DD]">
        
        <!-- Variable 1 Selection -->
        <div class="space-y-1.5">
          <label for="var1-select" class="text-xs font-bold text-[#601D49] flex items-center gap-1.5">
            <span class="w-4 h-4 rounded-full bg-[#BD5579] text-white flex items-center justify-center text-[10px]">1</span>
            Variable 1
          </label>
          <select 
            id="var1-select"
            bind:value={selectedVar1}
            class="w-full px-3 py-2 text-xs rounded-xl bg-white border border-[#EA9D9D]/60 text-[#601D49] font-medium focus:outline-none focus:border-[#BD5579]"
          >
            {#each variableCatalogue as v}
              <option value={v.key}>{v.label} ({v.type})</option>
            {/each}
          </select>
          <span class="text-[10px] text-[#82476B] block">First variable factor or group</span>
        </div>

        <!-- Variable 2 Selection -->
        <div class="space-y-1.5">
          <label for="var2-select" class="text-xs font-bold text-[#601D49] flex items-center gap-1.5">
            <span class="w-4 h-4 rounded-full bg-[#BD5579] text-white flex items-center justify-center text-[10px]">2</span>
            Variable 2
          </label>
          <select 
            id="var2-select"
            bind:value={selectedVar2}
            class="w-full px-3 py-2 text-xs rounded-xl bg-white border border-[#EA9D9D]/60 text-[#601D49] font-medium focus:outline-none focus:border-[#BD5579]"
          >
            {#each variableCatalogue as v}
              <option value={v.key}>{v.label} ({v.type})</option>
            {/each}
          </select>
          <span class="text-[10px] text-[#82476B] block">Second variable factor or target</span>
        </div>

        <!-- Statistical Method Selection -->
        <div class="space-y-1.5">
          <label for="test-select" class="text-xs font-bold text-[#601D49] flex items-center gap-1.5">
            <span class="w-4 h-4 rounded-full bg-[#601D49] text-white flex items-center justify-center text-[10px]">3</span>
            Statistical Test
          </label>
          <select 
            id="test-select"
            bind:value={selectedTest}
            class="w-full px-3 py-2 text-xs rounded-xl bg-white border border-[#EA9D9D]/60 text-[#601D49] font-medium focus:outline-none focus:border-[#BD5579]"
          >
            <option value="chi_square">Chi-Square Test (Categorical × Categorical)</option>
            <option value="t_test">Independent T-Test (Binary Group × Continuous)</option>
            <option value="correlation">Pearson Correlation (Numerical/Ordinal × Numerical/Ordinal)</option>
          </select>
          <span class="text-[10px] text-[#82476B] block">Analytical hypothesis test method</span>
        </div>

      </div>

      <!-- Action Button -->
      <div class="flex items-center justify-between pt-1">
        <span class="text-[11px] text-[#82476B]">
          Calculation adheres to strict variable type validation (Nominal, Ordinal, Interval).
        </span>
        <Button 
          onclick={handleRunAnalysis} 
          disabled={isRunningTest} 
          variant="primary" 
          class="px-5 py-2 text-xs font-semibold"
        >
          {#if isRunningTest}
            <span class="w-3.5 h-3.5 border-2 border-white border-t-transparent rounded-full animate-spin"></span>
            <span>Computing Test...</span>
          {:else}
            <svg class="w-4 h-4" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" d="M3.75 3v11.25A2.25 2.25 0 006 16.5h2.25M3.75 3h-1.5m1.5 0h16.5m0 0h1.5m-1.5 0v11.25A2.25 2.25 0 0118 16.5h-2.25m-7.5 0h7.5m-7.5 0l-1 3m8.5-3l1 3m0 0l.5 1.5m-.5-1.5h-9.5m0 0l-.5 1.5m.75-9l3-3 2.25 2.25L17.25 6" />
            </svg>
            <span>Run Analysis</span>
          {/if}
        </Button>
      </div>

      <!-- Analysis Results Area -->
      {#if testError}
        <div class="p-3.5 rounded-xl bg-[#FAF7F8] border border-[#BD5579] text-[#601D49] text-xs font-semibold flex items-center gap-2">
          <svg class="w-4 h-4 text-[#BD5579] shrink-0" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" d="M12 9v3.75m9-.75a9 9 0 11-18 0 9 9 0 0118 0zm-9 3.75h.008v.008H12v-.008z" />
          </svg>
          <span>{testError}</span>
        </div>
      {:else if customResult}

        <!-- CASE A: TEST NOT APPLICABLE FOR SELECTED VARIABLE TYPES -->
        {#if !customResult.applicable}
          <div class="p-5 rounded-2xl bg-[#FFEBB8]/50 border border-[#EA9D9D] space-y-2">
            <div class="flex items-center gap-2 text-[#601D49] font-bold text-sm">
              <svg class="w-5 h-5 text-[#BD5579] shrink-0" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" d="M12 9v3.75m-9.303 3.376c-.866 1.5.217 3.374 1.948 3.374h14.71c1.73 0 2.813-1.874 1.948-3.374L13.949 3.378c-.866-1.5-3.032-1.5-3.898 0L2.697 16.126zM12 15.75h.007v.008H12v-.008z" />
              </svg>
              <span>Test not applicable for the selected variable types.</span>
            </div>
            <p class="text-xs text-[#601D49] leading-relaxed">
              {customResult.reason}
            </p>
            <div class="pt-2 text-[11px] text-[#82476B] border-t border-[#EA9D9D]/40 grid grid-cols-1 md:grid-cols-3 gap-2">
              <div><strong>Chi-Square:</strong> Requires 2 categorical factors.</div>
              <div><strong>T-Test:</strong> Requires 1 binary group & 1 numerical score.</div>
              <div><strong>Correlation:</strong> Requires 2 numerical or ordinal metrics.</div>
            </div>
          </div>

        <!-- CASE B: TEST IS APPLICABLE AND EXECUTED -->
        {:else}
          <div class="p-5 rounded-2xl bg-[#FAF7F8] border border-[#F0D5DD] space-y-5">
            
            <!-- Result Meta Bar -->
            <div class="flex flex-wrap items-center justify-between gap-3 border-b border-[#F0D5DD] pb-3">
              <div>
                <span class="text-[10px] font-bold text-[#82476B] uppercase tracking-wider block">Hypothesis Test Result</span>
                <h3 class="text-sm font-bold text-[#601D49]">{customResult.testName}</h3>
                <span class="text-xs text-[#82476B]">Variables: {customResult.variables}</span>
              </div>
              <div class="flex items-center gap-2">
                <span class="px-2.5 py-1 rounded-full text-xs font-semibold {customResult.isSignificant ? 'bg-[#BD5579] text-white' : 'bg-[#FFEBB8] text-[#601D49] border border-[#EA9D9D]/60'}">
                  {customResult.isSignificant ? 'Statistically Significant (p < 0.05)' : 'Not Significant (p ≥ 0.05)'}
                </span>
                <span class="px-2.5 py-1 rounded-full bg-white border border-[#F0D5DD] text-xs font-bold text-[#601D49]">
                  N = {customResult.sampleSize}
                </span>
              </div>
            </div>

            <!-- Key Test Metrics Grid -->
            <div class="grid grid-cols-2 sm:grid-cols-4 gap-3 text-xs">
              
              <!-- Metric 1: Test Statistic -->
              <div class="p-3 rounded-xl bg-white border border-[#F0D5DD]">
                <span class="text-[11px] text-[#82476B] block truncate">{customResult.statisticName}</span>
                <span class="text-base font-bold text-[#BD5579]">{customResult.testStatistic}</span>
              </div>

              <!-- Metric 2: Degrees of Freedom -->
              <div class="p-3 rounded-xl bg-white border border-[#F0D5DD]">
                <span class="text-[11px] text-[#82476B] block">Degrees of Freedom</span>
                <span class="text-base font-bold text-[#601D49]">{customResult.degreesOfFreedom}</span>
              </div>

              <!-- Metric 3: p-value -->
              <div class="p-3 rounded-xl bg-white border border-[#F0D5DD]">
                <span class="text-[11px] text-[#82476B] block">p-value (Two-tailed)</span>
                <span class="text-base font-bold {customResult.isSignificant ? 'text-[#BD5579]' : 'text-[#601D49]'}">
                  {customResult.pValue < 0.0001 ? '< 0.0001' : customResult.pValue}
                </span>
              </div>

              <!-- Metric 4: Effect Size -->
              <div class="p-3 rounded-xl bg-white border border-[#F0D5DD]">
                <span class="text-[11px] text-[#82476B] block truncate">{customResult.effectSizeName}</span>
                <span class="text-base font-bold text-[#601D49]">{customResult.effectSize}</span>
              </div>

            </div>

            <!-- Detailed Breakdown by Test Type -->
            {#if customResult.testType === 'chi_square'}
              <div class="space-y-3 pt-2">
                <div class="text-xs font-bold text-[#601D49]">Contingency Frequency Matrix (Observed vs Expected)</div>
                <div class="overflow-x-auto border border-[#F0D5DD] rounded-xl bg-white">
                  <table class="w-full text-left text-xs border-collapse">
                    <thead>
                      <tr class="bg-[#FAF7F8] border-b border-[#F0D5DD] text-[#82476B] text-[11px]">
                        <th class="p-2.5 font-bold">Category Level</th>
                        {#each customResult.colLabels as col}
                          <th class="p-2.5 font-bold text-center">{col}</th>
                        {/each}
                      </tr>
                    </thead>
                    <tbody class="divide-y divide-[#F0D5DD]">
                      {#each customResult.rowLabels as row, rIdx}
                        <tr class="hover:bg-[#FAF7F8]/50">
                          <td class="p-2.5 font-semibold text-[#601D49]">{row}</td>
                          {#each customResult.colLabels as col, cIdx}
                            <td class="p-2.5 text-center">
                              <span class="font-bold text-[#601D49]">{customResult.observedMatrix[rIdx][cIdx]}</span>
                              <span class="text-[10px] text-[#82476B] block">(Exp: {customResult.expectedMatrix[rIdx][cIdx]})</span>
                            </td>
                          {/each}
                        </tr>
                      {/each}
                    </tbody>
                  </table>
                </div>
              </div>

            {:else if customResult.testType === 't_test'}
              <div class="space-y-3 pt-2">
                <div class="text-xs font-bold text-[#601D49]">Cohort Group Comparison Summary</div>
                <div class="grid grid-cols-1 sm:grid-cols-2 gap-3 text-xs">
                  <div class="p-3.5 rounded-xl bg-white border border-[#F0D5DD] space-y-1">
                    <span class="text-[10px] font-bold text-[#82476B] uppercase">Group 1: {customResult.group1.name}</span>
                    <div class="grid grid-cols-3 gap-2 pt-1">
                      <div><span class="text-[11px] text-[#82476B] block">Sample</span><span class="font-bold text-[#601D49]">{customResult.group1.sampleSize}</span></div>
                      <div><span class="text-[11px] text-[#82476B] block">Mean</span><span class="font-bold text-[#BD5579]">{customResult.group1.mean}</span></div>
                      <div><span class="text-[11px] text-[#82476B] block">Std Dev</span><span class="font-bold text-[#601D49]">{customResult.group1.stdDev}</span></div>
                    </div>
                  </div>
                  <div class="p-3.5 rounded-xl bg-white border border-[#F0D5DD] space-y-1">
                    <span class="text-[10px] font-bold text-[#82476B] uppercase">Group 2: {customResult.group2.name}</span>
                    <div class="grid grid-cols-3 gap-2 pt-1">
                      <div><span class="text-[11px] text-[#82476B] block">Sample</span><span class="font-bold text-[#601D49]">{customResult.group2.sampleSize}</span></div>
                      <div><span class="text-[11px] text-[#82476B] block">Mean</span><span class="font-bold text-[#BD5579]">{customResult.group2.mean}</span></div>
                      <div><span class="text-[11px] text-[#82476B] block">Std Dev</span><span class="font-bold text-[#601D49]">{customResult.group2.stdDev}</span></div>
                    </div>
                  </div>
                </div>
              </div>

            {:else if customResult.testType === 'correlation'}
              <div class="space-y-2 pt-2">
                <div class="text-xs font-bold text-[#601D49]">Correlation Parameters</div>
                <div class="grid grid-cols-3 gap-3 text-xs">
                  <div class="p-3 rounded-xl bg-white border border-[#F0D5DD]">
                    <span class="text-[11px] text-[#82476B] block">Direction</span>
                    <span class="font-bold text-[#601D49] capitalize">{customResult.direction}</span>
                  </div>
                  <div class="p-3 rounded-xl bg-white border border-[#F0D5DD]">
                    <span class="text-[11px] text-[#82476B] block">Linear Strength</span>
                    <span class="font-bold text-[#601D49] capitalize">{customResult.strength}</span>
                  </div>
                  <div class="p-3 rounded-xl bg-white border border-[#F0D5DD]">
                    <span class="text-[11px] text-[#82476B] block">Variance Explained (r²)</span>
                    <span class="font-bold text-[#BD5579]">{(customResult.effectSize * 100).toFixed(1)}%</span>
                  </div>
                </div>
              </div>
            {/if}

            <!-- Academic Interpretation Banner -->
            <div class="p-4 rounded-xl bg-[#FFEBB8]/40 border border-[#EA9D9D]/60 space-y-1">
              <span class="text-[10px] font-bold text-[#601D49] uppercase tracking-wider block">Academic Statistical Interpretation</span>
              <p class="text-xs text-[#601D49] leading-relaxed font-medium">
                {customResult.interpretation}
              </p>
              <p class="text-[11px] text-[#82476B] pt-1">
                Note: Statistical tests establish observed mathematical association within sample data and do not confirm or imply causal mechanisms.
              </p>
            </div>

          </div>
        {/if}

      {/if}

    </Card>

    <!-- ======================================================== -->
    <!-- 2. DESCRIPTIVE STATISTICS SECTION                        -->
    <!-- ======================================================== -->
    <div class="space-y-6 pt-2">
      
      <!-- Section A: Numerical & Ordinal Metrics (Mean, Median, Mode) -->
      <div class="space-y-4">
        <div class="border-b border-[#F0D5DD] pb-2">
          <h2 class="text-base font-bold text-[#601D49]">Continuous & Ordinal Descriptive Metrics</h2>
          <p class="text-xs text-[#82476B] mt-0.5">
            Calculated numerical properties (Mean, Median, Mode, Std Deviation) for scaled survey variables.
          </p>
        </div>

        <div class="grid grid-cols-1 md:grid-cols-3 gap-5">
          {#each Object.values(statData.descriptive.numerical) as numItem}
            <Card class="p-5 space-y-3 bg-white border border-[#F0D5DD] shadow-sm">
              <div class="border-b border-[#F0D5DD] pb-2">
                <span class="text-[10px] text-[#82476B] uppercase font-bold tracking-wider">Numerical Variable</span>
                <h3 class="card-heading text-sm mt-0.5">{numItem.variable}</h3>
                <span class="text-[11px] text-[#BD5579] font-medium">{numItem.unit}</span>
              </div>

              <div class="grid grid-cols-2 gap-2 pt-1 text-xs">
                <div class="p-2.5 rounded-lg bg-[#FAF7F8] border border-[#F0D5DD]">
                  <span class="text-[11px] text-[#82476B] block">Mean (μ)</span>
                  <span class="text-sm font-bold text-[#BD5579]">{numItem.mean}</span>
                </div>
                <div class="p-2.5 rounded-lg bg-[#FAF7F8] border border-[#F0D5DD]">
                  <span class="text-[11px] text-[#82476B] block">Median</span>
                  <span class="text-sm font-bold text-[#601D49]">{numItem.median}</span>
                </div>
                <div class="p-2.5 rounded-lg bg-[#FAF7F8] border border-[#F0D5DD]">
                  <span class="text-[11px] text-[#82476B] block">Mode</span>
                  <span class="text-sm font-bold text-[#601D49]">{numItem.mode}</span>
                </div>
                <div class="p-2.5 rounded-lg bg-[#FAF7F8] border border-[#F0D5DD]">
                  <span class="text-[11px] text-[#82476B] block">Std Dev (σ)</span>
                  <span class="text-sm font-bold text-[#601D49]">{numItem.stdDev}</span>
                </div>
              </div>

              <div class="pt-1 flex items-center justify-between text-[11px] text-[#82476B]">
                <span>Sample Size: <strong>{numItem.sampleSize}</strong></span>
                <span>Range: <strong>[{numItem.min} – {numItem.max}]</strong></span>
              </div>
            </Card>
          {/each}
        </div>
      </div>

      <!-- Section B: Categorical Variable Descriptives (Frequency, %, Mode) -->
      <div class="space-y-4 pt-4">
        <div class="border-b border-[#F0D5DD] pb-2">
          <h2 class="text-base font-bold text-[#601D49]">Categorical Variable Frequency & Mode Distributions</h2>
          <p class="text-xs text-[#82476B] mt-0.5">
            Frequency, percentage distributions, and mode category for nominal survey dimensions. Continuous metrics (Mean/Median) are omitted as mathematically non-applicable.
          </p>
        </div>

        <!-- Categorical Variables Tabs -->
        <div class="flex flex-wrap gap-1.5 border-b border-[#F0D5DD] pb-2">
          {#each Object.values(statData.descriptive.categorical) as catItem}
            <button 
              onclick={() => activeCatTab = catItem.key}
              class="px-3 py-1.5 rounded-xl text-xs font-semibold transition-all cursor-pointer
                {activeCatTab === catItem.key 
                  ? 'bg-[#BD5579] text-white shadow-xs' 
                  : 'bg-white text-[#82476B] border border-[#F0D5DD] hover:bg-[#FAF7F8]'}"
            >
              {catItem.variable}
            </button>
          {/each}
        </div>

        <!-- Selected Categorical Detail Table -->
        {#if statData.descriptive.categorical[activeCatTab]}
          {@const cat = statData.descriptive.categorical[activeCatTab]}
          <Card class="p-5 space-y-4 bg-white border border-[#F0D5DD] shadow-sm">
            <div class="flex flex-col sm:flex-row sm:items-center justify-between gap-2 border-b border-[#F0D5DD] pb-3">
              <div>
                <h3 class="text-sm font-bold text-[#601D49]">{cat.variable}</h3>
                <span class="text-xs text-[#82476B]">Sample Size: N = {cat.sampleSize}</span>
              </div>
              <div class="px-3 py-1 rounded-xl bg-[#FFEBB8]/60 border border-[#EA9D9D]/60 text-xs text-[#601D49] font-medium">
                Mode Category: <strong class="text-[#BD5579]">{cat.modeCategory}</strong> ({cat.modePercentage}% of cohort)
              </div>
            </div>

            <div class="overflow-x-auto border border-[#F0D5DD] rounded-xl">
              <table class="w-full text-left text-xs">
                <thead>
                  <tr class="bg-[#FAF7F8] border-b border-[#F0D5DD] text-[#82476B] text-[11px]">
                    <th class="p-3 font-bold">Category</th>
                    <th class="p-3 font-bold text-center">Frequency (Count)</th>
                    <th class="p-3 font-bold text-center">Percentage (%)</th>
                    <th class="p-3 font-bold">Cohort Distribution</th>
                  </tr>
                </thead>
                <tbody class="divide-y divide-[#F0D5DD]">
                  {#each Object.entries(cat.frequencies) as [optName, count]}
                    {@const pct = cat.percentages[optName] || 0}
                    <tr class="hover:bg-[#FAF7F8]/50 {optName === cat.modeCategory ? 'bg-[#FFEBB8]/20' : ''}">
                      <td class="p-3 font-semibold text-[#601D49] flex items-center gap-2">
                        <span>{optName}</span>
                        {#if optName === cat.modeCategory}
                          <span class="px-1.5 py-0.5 rounded text-[9px] font-bold bg-[#BD5579] text-white">Mode</span>
                        {/if}
                      </td>
                      <td class="p-3 text-center font-bold text-[#601D49]">{count}</td>
                      <td class="p-3 text-center font-bold text-[#BD5579]">{pct}%</td>
                      <td class="p-3 w-48">
                        <div class="w-full bg-[#FAF7F8] border border-[#F0D5DD] rounded-full h-2 overflow-hidden">
                          <div class="bg-[#BD5579] h-2 rounded-full transition-all duration-300" style="width: {pct}%"></div>
                        </div>
                      </td>
                    </tr>
                  {/each}
                </tbody>
              </table>
            </div>
          </Card>
        {/if}

      </div>

    </div>

  {/if}

</div>
