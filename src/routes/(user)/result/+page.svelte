<script>
  import { onMount } from 'svelte';
  import Card from '$lib/components/Card.svelte';
  import Button from '$lib/components/Button.svelte';
  import EmptyState from '$lib/components/EmptyState.svelte';

  let isLoading = $state(true);
  let hasAssessment = $state(false);
  let submittedAt = $state(null);
  let hasResult = $state(false);
  let classification = $state(null);
  let indicators = $state([]);
  let mlMessage = $state('Prediction will be available after the ML model is connected.');

  onMount(async () => {
    try {
      const res = await fetch('/api/survey/my-result');
      if (res.ok) {
        const data = await res.json();
        hasAssessment = data.hasAssessment;
        submittedAt = data.submittedAt;
        hasResult = data.hasResult;
        if (data.hasResult && data.result) {
          classification = data.result.classification;
          indicators = data.result.indicators || [];
        }
        if (data.mlStatus) {
          mlMessage = data.mlStatus.message;
        }
      }
    } catch (e) {
      console.error('Failed to load user result:', e);
    } finally {
      isLoading = false;
    }
  });

  function handlePrint() {
    window.print();
  }

  const targetClasses = ['Not at all', 'Slightly', 'Moderately', 'Severely'];
</script>

<svelte:head>
  <style>
    @media print {
      aside, header, nav, button, .no-print {
        display: none !important;
      }
      body {
        background: #FFFFFF !important;
        color: #601D49 !important;
      }
      .printable-card {
        border: 1px solid #EA9D9D !important;
        box-shadow: none !important;
      }
    }
  </style>
</svelte:head>

<div class="max-w-4xl mx-auto space-y-6 page-fade-in font-sans">
  
  {#if isLoading}
    <div class="p-12 text-center">
      <div class="w-8 h-8 border-3 border-[#BD5579] border-t-transparent rounded-full animate-spin mx-auto"></div>
      <p class="text-xs text-[#82476B] mt-3">Loading assessment records...</p>
    </div>

  {:else if !hasAssessment}
    <!-- Empty State: No Assessment Taken Yet -->
    <EmptyState 
      title="No Assessment Found"
      description="You have not submitted a survey response yet. Please complete the unified mental health assessment to record your response."
      actionText="Start Assessment"
      actionHref="/assessment"
      icon="survey"
    />

  {:else}
    
    <!-- Assessment Recorded Header Banner -->
    <div class="bg-white border border-[#F0D5DD] rounded-2xl p-6 sm:p-7 shadow-xs flex flex-col sm:flex-row sm:items-center justify-between gap-4 printable-card">
      <div class="space-y-1">
        <div class="flex items-center gap-2">
          <span class="px-2.5 py-0.5 rounded text-[10px] font-bold bg-[#FFEBB8] text-[#601D49] border border-[#EA9D9D]/60">
            Recorded in Database
          </span>
          {#if submittedAt}
            <span class="text-[11px] text-[#82476B]">
              Recorded on {new Date(submittedAt).toLocaleDateString()}
            </span>
          {/if}
        </div>
        <h1 class="page-title text-xl sm:text-2xl text-[#601D49]">
          Mental Health Impact Analysis
        </h1>
        <p class="text-xs text-[#82476B]">
          AI-Based Supervised Multiclass Outcome Architecture (MindSafe Research Platform)
        </p>
      </div>

      <div class="no-print shrink-0 flex items-center gap-2">
        <Button variant="outline" onclick={handlePrint} class="px-3.5 py-2 text-xs font-semibold">
          <svg class="w-4 h-4 text-[#601D49]" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" d="M6.72 13.829c-.24-1.22.42-2.457 1.62-2.829l5.06-1.572a2.316 2.316 0 012.87 1.57l1.54 4.962m-9.47-2.131v6.75a1.5 1.5 0 001.5 1.5h6a1.5 1.5 0 001.5-1.5v-6.75m-9 0h9" />
          </svg>
          <span>Print Summary</span>
        </Button>
      </div>
    </div>

    <!-- 1. Classification Result Section -->
    <Card class="p-6 sm:p-8 space-y-6 printable-card">
      <div class="flex items-center justify-between border-b border-[#F0D5DD] pb-4">
        <div>
          <span class="text-[11px] font-bold uppercase tracking-wider text-[#BD5579]">
            Primary ML Outcome Variable
          </span>
          <h2 class="card-heading text-lg">Mental Health Impact Classification</h2>
        </div>
        <div class="px-3 py-1 rounded-xl text-xs font-bold bg-[#FAF7F8] text-[#601D49] border border-[#EA9D9D]/60">
          Target: Mental Health Impact
        </div>
      </div>

      <!-- Result State or Zero Fake Data State -->
      {#if hasResult && classification}
        <div class="p-4 rounded-xl bg-[#FAF7F8] border border-[#EA9D9D] space-y-2">
          <div class="flex items-center justify-between">
            <span class="text-xs font-bold text-[#601D49]">Classified Outcome:</span>
            <span class="text-sm font-extrabold text-[#BD5579]">{classification}</span>
          </div>
        </div>
      {:else}
        <!-- Calm Empty State per Section 10: Zero fake predictions -->
        <div class="p-6 rounded-xl bg-[#FAF7F8] border border-[#EA9D9D]/60 text-center space-y-2">
          <div class="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-[#FFEBB8] text-[#601D49] text-xs font-semibold border border-[#EA9D9D]/60">
            <svg class="w-3.5 h-3.5 text-[#BD5579]" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" d="M11.25 11.25l.041-.02a.75.75 0 011.063.852l-.708 2.836a.75.75 0 001.063.853l.041-.021M21 12a9 9 0 11-18 0 9 9 0 0118 0zm-9-3.75h.008v.008H12V8.25z" />
            </svg>
            <span>Model Status: Pending Connection</span>
          </div>
          <h3 class="text-base font-bold text-[#601D49] mt-2">
            Prediction will be available after the ML model is connected.
          </h3>
          <p class="text-xs text-[#82476B] max-w-lg mx-auto">
            Your survey responses are securely recorded in MongoDB. The trained multiclass classification pipeline (Random Forest) will be integrated in Phase 2 to compute analytical classifications.
          </p>
        </div>
      {/if}

      <!-- Four-Level Indicator Architecture -->
      <div class="space-y-3 pt-2">
        <div class="flex items-center justify-between text-xs font-semibold text-[#601D49]">
          <span>Supervised Multiclass Scale:</span>
          <span class="text-[#82476B]">4 Discrete Target Classes</span>
        </div>

        <div class="grid grid-cols-2 sm:grid-cols-4 gap-3">
          {#each targetClasses as tClass}
            <div class="p-3.5 rounded-xl border text-center transition-all
              {classification === tClass 
                ? 'bg-[#FFEBB8] border-[#BD5579] font-bold text-[#601D49] shadow-xs' 
                : 'bg-white border-[#F0D5DD] text-[#82476B]'}">
              <span class="text-xs block font-bold">{tClass}</span>
              <span class="text-[10px] block opacity-75 mt-0.5">
                {tClass === 'Not at all' ? 'Class 1' : tClass === 'Slightly' ? 'Class 2' : tClass === 'Moderately' ? 'Class 3' : 'Class 4'}
              </span>
            </div>
          {/each}
        </div>
      </div>
    </Card>

    <!-- 2. Explainability & Interpretability Section (SHAP Placeholder) -->
    <Card class="p-6 sm:p-8 space-y-4 printable-card">
      <div class="border-b border-[#F0D5DD] pb-3">
        <span class="text-[11px] font-bold uppercase tracking-wider text-[#BD5579]">
          Model Interpretability Architecture
        </span>
        <h2 class="card-heading text-base sm:text-lg">Why was this result predicted?</h2>
        <p class="text-xs text-[#82476B] mt-0.5">
          Feature contribution breakdown via SHAP (SHapley Additive exPlanations) & feature importance
        </p>
      </div>

      <!-- Clean empty state per Section 11 -->
      <div class="p-6 rounded-xl bg-[#FAF7F8] border border-[#F0D5DD] text-center space-y-2">
        <svg class="w-8 h-8 text-[#BD5579] mx-auto opacity-70" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" d="M3 13.125C3 12.504 3.504 12 4.125 12h2.25c.621 0 1.125.504 1.125 1.125v6.75C7.5 20.496 6.996 21 6.375 21h-2.25A1.125 1.125 0 013 19.875v-6.75zM9.75 8.625c0-.621.504-1.125 1.125-1.125h2.25c.621 0 1.125.504 1.125 1.125v11.25c0 .621-.504 1.125-1.125 1.125h-2.25a1.125 1.125 0 01-1.125-1.125V8.625zM16.5 4.125c0-.621.504-1.125 1.125-1.125h2.25C20.496 3 21 3.504 21 4.125v15.75c0 .621-.504 1.125-1.125 1.125h-2.25a1.125 1.125 0 01-1.125-1.125V4.125z" />
        </svg>
        <h4 class="text-sm font-semibold text-[#601D49]">
          Model explanation will appear after the trained model is connected.
        </h4>
        <p class="text-xs text-[#82476B] max-w-md mx-auto">
          SHAP-based feature importance, local explanations, and contributing behavioral weights will be rendered dynamically once the ML model pipeline is linked.
        </p>
      </div>
    </Card>

    <!-- 3. Recommendations & Awareness Section -->
    <Card class="p-6 sm:p-8 space-y-4 printable-card">
      <div class="border-b border-[#F0D5DD] pb-3">
        <span class="text-[11px] font-bold uppercase tracking-wider text-[#BD5579]">
          Supportive Guidance
        </span>
        <h2 class="card-heading text-base sm:text-lg">Recommendations & Digital Safety Awareness</h2>
        <p class="text-xs text-[#82476B] mt-0.5">
          General non-diagnostic resources for student wellness and cyber safety
        </p>
      </div>

      <div class="grid grid-cols-1 md:grid-cols-3 gap-4 pt-1">
        <div class="p-4 rounded-xl bg-[#FAF7F8] border border-[#F0D5DD] space-y-1.5">
          <h4 class="text-xs font-bold text-[#601D49]">Curate Screen Engagement</h4>
          <p class="text-xs text-[#82476B] leading-relaxed">
            Establish healthy screen limits. Take structured breaks from social feeds to mitigate continuous emotional fatigue.
          </p>
        </div>

        <div class="p-4 rounded-xl bg-[#FAF7F8] border border-[#F0D5DD] space-y-1.5">
          <h4 class="text-xs font-bold text-[#601D49]">Evidence Preservation</h4>
          <p class="text-xs text-[#82476B] leading-relaxed">
            Preserve unedited screenshots with timestamps, account handles, and message URLs prior to muting or blocking perpetrators.
          </p>
        </div>

        <div class="p-4 rounded-xl bg-[#FAF7F8] border border-[#F0D5DD] space-y-1.5">
          <h4 class="text-xs font-bold text-[#601D49]">National Helpline (1930)</h4>
          <p class="text-xs text-[#82476B] leading-relaxed">
            Report serious cyber offenses through cybercrime.gov.in or dial national helpline 1930 for official statutory grievance redressal.
          </p>
        </div>
      </div>

      <!-- Ethical / Medical Disclaimer -->
      <div class="p-3.5 rounded-xl bg-[#FFEBB8]/40 border border-[#EA9D9D]/60 flex items-start gap-2.5 mt-2">
        <svg class="w-4 h-4 text-[#BD5579] shrink-0 mt-0.5" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" d="M11.25 11.25l.041-.02a.75.75 0 011.063.852l-.708 2.836a.75.75 0 001.063.853l.041-.021M21 12a9 9 0 11-18 0 9 9 0 0118 0zm-9-3.75h.008v.008H12V8.25z" />
        </svg>
        <span class="text-xs text-[#601D49] leading-relaxed font-medium">
          <strong>Academic Disclaimer:</strong> This is an analytical result from the research project model and is not a medical or psychiatric diagnosis. If you are experiencing distress, please reach out to qualified campus counseling or healthcare professionals.
        </span>
      </div>
    </Card>

  {/if}

</div>
