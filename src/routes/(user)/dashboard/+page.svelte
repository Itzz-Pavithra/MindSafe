<script>
  import { onMount } from 'svelte';
  import Card from '$lib/components/Card.svelte';
  import Button from '$lib/components/Button.svelte';
  import { appState } from '$lib/state/appState.svelte.js';

  let hasSubmitted = $state(false);
  let submittedAt = $state(null);
  let isLoading = $state(true);

  onMount(async () => {
    try {
      const res = await fetch('/api/survey/my-response');
      if (res.ok) {
        const data = await res.json();
        if (data.success && data.hasResponse) {
          hasSubmitted = true;
          submittedAt = data.response.submittedAt;
        }
      }
    } catch (e) {
      console.error('Failed to load assessment status:', e);
    } finally {
      isLoading = false;
    }
  });
</script>

<div class="max-w-4xl mx-auto space-y-6 page-fade-in font-sans">
  
  <!-- Welcome Banner -->
  <div class="bg-gradient-to-r from-[#601D49] to-[#80255F] rounded-2xl p-6 sm:p-8 text-white shadow-sm flex flex-col md:flex-row items-start md:items-center justify-between gap-6 border border-[#601D49]">
    <div class="space-y-2 max-w-xl">
      <span class="inline-block px-3 py-1 rounded-full bg-[#FFEBB8] text-[#601D49] text-xs font-semibold tracking-wide">
        Research Participant Portal
      </span>
      <h1 class="page-title text-white">
        Welcome, {appState.user?.name || 'Participant'}
      </h1>
      <p class="text-xs sm:text-sm text-[#FFEBB8] font-normal leading-relaxed">
        MindSafe – An AI-Based Cyberbullying and Its Impact on Mental Health. Your responses contribute to academic inquiry examining the relationship between digital harassment and psychological well-being.
      </p>
    </div>

    <!-- Main CTA Button -->
    <a href="/assessment" class="shrink-0">
      <Button variant="accent" class="px-6 py-3 text-xs sm:text-sm font-bold shadow-md">
        <span>{hasSubmitted ? 'Retake Assessment' : 'Start Mental Health Assessment'}</span>
        <svg class="w-4 h-4" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" d="M13.5 4.5L21 12m0 0l-7.5 7.5M21 12H3" />
        </svg>
      </Button>
    </a>
  </div>

  <!-- Status & Assessment History -->
  <div class="grid grid-cols-1 md:grid-cols-3 gap-5">
    
    <!-- Assessment Status Card -->
    <Card class="p-5 space-y-3">
      <div class="flex items-center justify-between">
        <span class="label-text">Assessment Status</span>
        <span class="px-2 py-0.5 rounded text-[10px] font-bold 
          {hasSubmitted ? 'bg-[#FFEBB8] text-[#601D49] border border-[#EA9D9D]' : 'bg-[#FAF7F8] text-[#82476B] border border-[#F0D5DD]'}">
          {hasSubmitted ? 'Completed' : 'Pending'}
        </span>
      </div>

      <div>
        <h3 class="card-heading">
          {hasSubmitted ? 'Survey Recorded' : 'Assessment Not Started'}
        </h3>
        <p class="small-supporting-text mt-1">
          {hasSubmitted && submittedAt 
            ? `Submitted on ${new Date(submittedAt).toLocaleDateString()} at ${new Date(submittedAt).toLocaleTimeString()}`
            : 'Participate in the unified survey to record your responses for empirical evaluation.'}
        </p>
      </div>

      <div class="pt-2">
        {#if hasSubmitted}
          <a href="/result" class="text-xs font-semibold text-[#BD5579] hover:underline flex items-center gap-1">
            <span>View Result Architecture</span>
            <svg class="w-3.5 h-3.5" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" d="M8.25 4.5l7.5 7.5-7.5 7.5" />
            </svg>
          </a>
        {:else}
          <a href="/assessment" class="text-xs font-semibold text-[#BD5579] hover:underline flex items-center gap-1">
            <span>Start Now</span>
            <svg class="w-3.5 h-3.5" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" d="M8.25 4.5l7.5 7.5-7.5 7.5" />
            </svg>
          </a>
        {/if}
      </div>
    </Card>

    <!-- Research Framework Card -->
    <Card class="p-5 space-y-3">
      <div class="flex items-center justify-between">
        <span class="label-text">Study Variable</span>
        <span class="px-2 py-0.5 rounded text-[10px] font-bold bg-[#FFEBB8] text-[#601D49] border border-[#EA9D9D]">
          ML Target
        </span>
      </div>

      <div>
        <h3 class="card-heading">Mental Health Impact</h3>
        <p class="small-supporting-text mt-1">
          4 Discrete Target Classes: Not at all, Slightly, Moderately, Severely. Designed for supervised multiclass classification.
        </p>
      </div>

      <div class="pt-2">
        <span class="text-[11px] text-[#82476B]">Non-causal empirical framework</span>
      </div>
    </Card>

    <!-- Confidentiality & Ethics Card -->
    <Card class="p-5 space-y-3">
      <div class="flex items-center justify-between">
        <span class="label-text">Confidentiality</span>
        <span class="px-2 py-0.5 rounded text-[10px] font-bold bg-[#FAF7F8] text-[#601D49] border border-[#F0D5DD]">
          Academic
        </span>
      </div>

      <div>
        <h3 class="card-heading">Anonymized Processing</h3>
        <p class="small-supporting-text mt-1">
          Responses are aggregated strictly for academic research and statistical modeling. No personal data is commercialized.
        </p>
      </div>

      <div class="pt-2">
        <span class="text-[11px] text-[#82476B]">Ethical research compliance</span>
      </div>
    </Card>

  </div>

  <!-- Assessment Structure Guidance -->
  <Card class="p-6 space-y-4">
    <div class="border-b border-[#F0D5DD] pb-3">
      <h2 class="section-heading">Assessment Structure & Instructions</h2>
      <p class="small-supporting-text mt-0.5">Please review the survey parameters before commencing the assessment</p>
    </div>

    <div class="grid grid-cols-1 md:grid-cols-3 gap-4 pt-1">
      <div class="p-4 rounded-xl bg-[#FAF7F8] border border-[#F0D5DD] space-y-1.5">
        <span class="text-xs font-bold text-[#601D49] block">1. Unified Questionnaire</span>
        <p class="text-xs text-[#82476B] leading-relaxed">
          12 comprehensive questions addressing demographics, screen time, direct cyberbullying exposure, frequency, and psychological impact.
        </p>
      </div>

      <div class="p-4 rounded-xl bg-[#FAF7F8] border border-[#F0D5DD] space-y-1.5">
        <span class="text-xs font-bold text-[#601D49] block">2. Single-Step Flow</span>
        <p class="text-xs text-[#82476B] leading-relaxed">
          Questions are presented one at a time with clear progress indicators, previous/next controls, and validation.
        </p>
      </div>

      <div class="p-4 rounded-xl bg-[#FAF7F8] border border-[#F0D5DD] space-y-1.5">
        <span class="text-xs font-bold text-[#601D49] block">3. Review & Submission</span>
        <p class="text-xs text-[#82476B] leading-relaxed">
          Review all selections before final submission. Results are saved securely to the MongoDB database.
        </p>
      </div>
    </div>
  </Card>

</div>
