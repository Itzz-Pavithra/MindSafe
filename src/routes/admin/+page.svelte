<script>
  import { onMount } from 'svelte';
  import Card from '$lib/components/Card.svelte';
  import Button from '$lib/components/Button.svelte';
  import EmptyState from '$lib/components/EmptyState.svelte';

  let stats = $state(null);
  let mlStatus = $state(null);
  let isLoading = $state(true);
  let hasData = $derived(stats && stats.hasData && stats.totalResponses > 0);

  onMount(async () => {
    try {
      const [statsRes, mlRes] = await Promise.all([
        fetch('/api/admin/statistics'),
        fetch('/api/ml/status')
      ]);

      if (statsRes.ok) {
        stats = await statsRes.json();
      }
      if (mlRes.ok) {
        mlStatus = await mlRes.json();
      }
    } catch (e) {
      console.error('Failed to load admin overview:', e);
    } finally {
      isLoading = false;
    }
  });
</script>

<div class="max-w-6xl mx-auto space-y-6 page-fade-in font-sans">
  
  <!-- Dashboard Page Header -->
  <div class="flex flex-col sm:flex-row sm:items-center justify-between gap-4 border-b border-[#F0D5DD] pb-4">
    <div>
      <h1 class="page-title text-2xl text-[#601D49]">Survey Analytics Overview</h1>
      <p class="text-xs text-[#82476B] mt-0.5">
        Population-level monitoring of cyberbullying incidents, screen engagement, and mental health impact
      </p>
    </div>

    <!-- Live Status Indicator -->
    <div class="flex items-center gap-2">
      <div class="w-2.5 h-2.5 rounded-full {hasData ? 'bg-[#BD5579]' : 'bg-[#EA9D9D]'} animate-pulse"></div>
      <span class="text-xs font-semibold text-[#601D49]">
        {hasData ? `${stats.totalResponses} Survey Responses Logged` : 'Dataset Awaiting Ingestion'}
      </span>
    </div>
  </div>

  <!-- A. Overview KPI Summary Cards -->
  <div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
    
    <!-- Total Survey Responses -->
    <Card class="p-5 space-y-2">
      <div class="flex items-center justify-between">
        <span class="label-text">Total Responses</span>
        <div class="w-7 h-7 rounded-lg bg-[#FFEBB8]/50 text-[#BD5579] flex items-center justify-center">
          <svg class="w-4 h-4" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" d="M15 19.128a9.38 9.38 0 002.625.372 9.337 9.337 0 004.121-.952 4.125 4.125 0 00-7.533-2.493M15 19.128v-.003c0-1.113-.285-2.16-.786-3.07M15 19.128v.106A12.318 12.318 0 018.624 21c-2.331 0-4.512-.645-6.374-1.766l-.001-.109a6.375 6.375 0 0111.964-3.07M12 6.375a3.375 3.375 0 11-6.75 0 3.375 3.375 0 016.75 0zm8.25 2.25a2.625 2.625 0 11-5.25 0 2.625 2.625 0 015.25 0z" />
          </svg>
        </div>
      </div>
      <div>
        <span class="text-2xl font-bold text-[#601D49]">
          {hasData ? stats.totalResponses : '—'}
        </span>
        <p class="text-[11px] text-[#82476B] mt-1">
          {hasData ? 'Verified MongoDB records' : 'No survey data available'}
        </p>
      </div>
    </Card>

    <!-- Cyberbullying Exposure -->
    <Card class="p-5 space-y-2">
      <div class="flex items-center justify-between">
        <span class="label-text">Cyberbullying Exposure</span>
        <div class="w-7 h-7 rounded-lg bg-[#FFEBB8]/50 text-[#BD5579] flex items-center justify-center">
          <svg class="w-4 h-4" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" d="M12 9v3.75m9-.75a9 9 0 11-18 0 9 9 0 0118 0zm-9 3.75h.008v.008H12v-.008z" />
          </svg>
        </div>
      </div>
      <div>
        <span class="text-2xl font-bold text-[#601D49]">
          {hasData ? `${stats.cyberbullyingExposurePct}%` : '—'}
        </span>
        <p class="text-[11px] text-[#82476B] mt-1">
          {hasData ? `${stats.experiencedCount} respondents exposed` : 'No survey data available'}
        </p>
      </div>
    </Card>

    <!-- Social Media Usage -->
    <Card class="p-5 space-y-2">
      <div class="flex items-center justify-between">
        <span class="label-text">Social Media Engagement</span>
        <div class="w-7 h-7 rounded-lg bg-[#FFEBB8]/50 text-[#BD5579] flex items-center justify-center">
          <svg class="w-4 h-4" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" d="M12 6v6h4.5m4.5 0a9 9 0 11-18 0 9 9 0 0118 0z" />
          </svg>
        </div>
      </div>
      <div>
        <span class="text-2xl font-bold text-[#601D49]">
          {hasData ? 'Active Cohort' : '—'}
        </span>
        <p class="text-[11px] text-[#82476B] mt-1">
          {hasData ? 'Screen time patterns mapped' : 'No survey data available'}
        </p>
      </div>
    </Card>

    <!-- Mental Health Impact -->
    <Card class="p-5 space-y-2">
      <div class="flex items-center justify-between">
        <span class="label-text">Elevated Impact Cohort</span>
        <div class="w-7 h-7 rounded-lg bg-[#FFEBB8]/50 text-[#BD5579] flex items-center justify-center">
          <svg class="w-4 h-4" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" d="M21 8.25c0-2.485-2.099-4.5-4.688-4.5-1.935 0-3.597 1.126-4.312 2.733-.715-1.607-2.377-2.733-4.313-2.733C5.1 3.75 3 5.765 3 8.25c0 7.22 9 12 9 12s9-4.78 9-12z" />
          </svg>
        </div>
      </div>
      <div>
        <span class="text-2xl font-bold text-[#601D49]">
          {hasData ? `${stats.mentalHealthImpactPct}%` : '—'}
        </span>
        <p class="text-[11px] text-[#82476B] mt-1">
          {hasData ? `${stats.moderateSevereCount} moderate/severe ratings` : 'No survey data available'}
        </p>
      </div>
    </Card>

  </div>

  <!-- F. ML MODEL STATUS PANEL -->
  <Card class="p-6 space-y-4 bg-white border border-[#F0D5DD]">
    <div class="flex flex-col sm:flex-row sm:items-center justify-between gap-3 border-b border-[#F0D5DD] pb-3">
      <div>
        <span class="text-[11px] font-bold uppercase tracking-wider text-[#BD5579]">
          Phase 4 Machine Learning Architecture
        </span>
        <h2 class="section-heading text-lg">Mental Health Impact Prediction & Explainability Pipeline</h2>
      </div>

      <!-- Status Badge -->
      <span class="px-3 py-1 rounded-full text-xs font-bold border self-start sm:self-auto
        {mlStatus?.connected 
          ? 'bg-[#EBF7EE] text-[#22543D] border-[#48BB78]/50' 
          : 'bg-[#FFEBB8] text-[#601D49] border-[#EA9D9D]/60'}">
        {mlStatus?.connected ? 'ML Service: Connected & Active' : 'ML Service: Offline'}
      </span>
    </div>

    <!-- Informational Message -->
    <div class="p-4 rounded-xl bg-[#FAF7F8] border border-[#F0D5DD] flex flex-col sm:flex-row sm:items-center justify-between gap-4">
      <div class="space-y-1">
        <div class="flex items-center gap-2">
          <svg class="w-4 h-4 text-[#BD5579] shrink-0" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" d="M9 12.75L11.25 15 15 9.75m-3-7.036A11.959 11.959 0 013.598 6 11.99 11.99 0 003 9.749c0 5.592 3.824 10.29 9 11.623 5.176-1.332 9-6.03 9-11.622 0-1.31-.21-2.571-.598-3.751h-.152c-3.196 0-6.1-1.248-8.25-3.285z" />
          </svg>
          <span class="text-xs font-bold text-[#601D49]">
            {mlStatus?.connected ? 'Primary Random Forest Classifier & SHAP Engine Operational' : 'ML Service Offline'}
          </span>
        </div>
        <p class="text-xs text-[#82476B] leading-relaxed">
          Trained on empirical survey data (Scenario B, Leakage-Controlled). Computes multiclass outcome probabilities and Tree SHAP feature attributions on participant submissions.
        </p>
      </div>

      <a href="/admin/ml-analysis" class="shrink-0">
        <Button variant="primary" class="px-4 py-2 text-xs font-semibold">
          <span>View ML & SHAP Analytics</span>
          <svg class="w-3.5 h-3.5" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" d="M13.5 4.5L21 12m0 0l-7.5 7.5M21 12H3" />
          </svg>
        </Button>
      </a>
    </div>

    <div class="grid grid-cols-1 sm:grid-cols-4 gap-3 pt-1">
      <div class="p-3 rounded-lg bg-[#FAF7F8] border border-[#F0D5DD]">
        <span class="text-[10px] text-[#82476B] uppercase font-bold block">Target Variable</span>
        <span class="text-xs font-bold text-[#601D49] mt-0.5 block">Mental Health Impact</span>
      </div>
      <div class="p-3 rounded-lg bg-[#FAF7F8] border border-[#F0D5DD]">
        <span class="text-[10px] text-[#82476B] uppercase font-bold block">Classification Task</span>
        <span class="text-xs font-bold text-[#601D49] mt-0.5 block">Multiclass (4 Classes)</span>
      </div>
      <div class="p-3 rounded-lg bg-[#FAF7F8] border border-[#F0D5DD]">
        <span class="text-[10px] text-[#82476B] uppercase font-bold block">Test Accuracy</span>
        <span class="text-xs font-bold text-[#BD5579] mt-0.5 block">48.54% (Macro F1: 0.3275)</span>
      </div>
      <div class="p-3 rounded-lg bg-[#FAF7F8] border border-[#F0D5DD]">
        <span class="text-[10px] text-[#82476B] uppercase font-bold block">Explainability</span>
        <span class="text-xs font-bold text-[#601D49] mt-0.5 block">SHAP TreeExplainer</span>
      </div>
    </div>
  </Card>

  <!-- Empty State Banner if no survey data is present in database -->
  {#if !hasData}
    <EmptyState 
      title="No Survey Data Available Yet"
      description="Data will appear after the survey dataset is connected or respondents complete the assessment. The application does not generate or display fake/synthetic survey values."
      icon="database"
    />
  {/if}

</div>
