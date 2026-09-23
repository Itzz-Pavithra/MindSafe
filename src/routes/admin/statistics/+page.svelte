<script>
  import { onMount } from 'svelte';
  import Card from '$lib/components/Card.svelte';
  import ChartCanvas from '$lib/components/ChartCanvas.svelte';
  import EmptyState from '$lib/components/EmptyState.svelte';

  let stats = $state(null);
  let isLoading = $state(true);
  let hasData = $derived(stats && stats.hasData && stats.totalResponses > 0);

  onMount(async () => {
    try {
      const res = await fetch('/api/admin/survey-statistics');
      if (res.ok) {
        stats = await res.json();
      }
    } catch (e) {
      console.error('Failed to load survey statistics:', e);
    } finally {
      isLoading = false;
    }
  });

  // Chart data definitions from real MongoDB survey statistics
  let ageChartData = $derived.by(() => {
    if (!hasData || !stats.ageDistribution) return null;
    const labels = Object.keys(stats.ageDistribution);
    return {
      labels,
      datasets: [{
        label: 'Respondents',
        data: labels.map(l => stats.ageDistribution[l]),
        backgroundColor: '#601D49',
        borderRadius: 4
      }]
    };
  });

  let genderChartData = $derived.by(() => {
    if (!hasData || !stats.genderDistribution) return null;
    const labels = Object.keys(stats.genderDistribution);
    return {
      labels,
      datasets: [{
        data: labels.map(l => stats.genderDistribution[l]),
        backgroundColor: ['#601D49', '#BD5579', '#EA9D9D', '#FFEBB8']
      }]
    };
  });

  let platformChartData = $derived.by(() => {
    if (!hasData || !stats.platformUsage) return null;
    const labels = Object.keys(stats.platformUsage);
    return {
      labels,
      datasets: [{
        label: 'Platform Users',
        data: labels.map(l => stats.platformUsage[l]),
        backgroundColor: '#BD5579',
        borderRadius: 4
      }]
    };
  });

  let usageChartData = $derived.by(() => {
    if (!hasData || !stats.usageDuration) return null;
    const labels = ['< 2.5 hrs', '2.5–4.5 hrs', '4.5–6.5 hrs', '> 6.5 hrs'];
    return {
      labels,
      datasets: [{
        label: 'Respondents',
        data: labels.map(l => stats.usageDuration[l] || 0),
        backgroundColor: '#EA9D9D',
        borderRadius: 4
      }]
    };
  });

  let frequencyChartData = $derived.by(() => {
    if (!hasData || !stats.cyberbullyingFrequency) return null;
    const labels = ['Never', 'Rarely', 'Sometimes', 'Often', 'Very Often'];
    return {
      labels,
      datasets: [{
        label: 'Incident Frequency',
        data: labels.map(l => stats.cyberbullyingFrequency[l] || 0),
        backgroundColor: '#601D49',
        borderRadius: 4
      }]
    };
  });
</script>

<div class="max-w-6xl mx-auto space-y-6 page-fade-in font-sans">
  
  <div class="border-b border-[#F0D5DD] pb-4">
    <h1 class="page-title text-2xl text-[#601D49]">Survey Statistics</h1>
    <p class="text-xs text-[#82476B] mt-0.5">
      Empirical demographic, screen usage, and digital harassment exposure distributions
    </p>
  </div>

  {#if !hasData}
    <EmptyState 
      title="No Survey Data Available Yet"
      description="Survey distribution charts will populate dynamically once survey responses are logged into the MongoDB database. No fake chart data is simulated."
      icon="chart"
    />
  {:else}
    <!-- Demographic Distributions Grid -->
    <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
      
      <!-- Age Distribution -->
      <Card class="p-6 space-y-4">
        <h3 class="card-heading">Age Distribution</h3>
        {#if ageChartData}
          <ChartCanvas type="bar" data={ageChartData} height={240} />
        {/if}
      </Card>

      <!-- Gender Distribution -->
      <Card class="p-6 space-y-4">
        <h3 class="card-heading">Gender Distribution</h3>
        {#if genderChartData}
          <ChartCanvas type="doughnut" data={genderChartData} height={240} />
        {/if}
      </Card>

      <!-- Platform Usage -->
      <Card class="p-6 space-y-4">
        <h3 class="card-heading">Social Media Platform Usage</h3>
        {#if platformChartData}
          <ChartCanvas type="bar" data={platformChartData} height={240} />
        {/if}
      </Card>

      <!-- Usage Duration -->
      <Card class="p-6 space-y-4">
        <h3 class="card-heading">Daily Social Media Usage Duration</h3>
        {#if usageChartData}
          <ChartCanvas type="bar" data={usageChartData} height={240} />
        {/if}
      </Card>

      <!-- Cyberbullying Frequency -->
      <Card class="p-6 space-y-4 md:col-span-2">
        <h3 class="card-heading">Cyberbullying Encounter Frequency</h3>
        {#if frequencyChartData}
          <ChartCanvas type="bar" data={frequencyChartData} height={240} />
        {/if}
      </Card>

    </div>
  {/if}

</div>
