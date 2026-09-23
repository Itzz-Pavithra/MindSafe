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
  let probabilities = $state(null);
  let topFeatures = $state([]);
  let modelVersion = $state('MindSafe Primary Random Forest (Scenario B)');
  let disclaimer = $state('This is an analytical result from the project ML model and is not a medical diagnosis.');
  let showDetailedProbabilities = $state(false);

  const targetClasses = ['Not at all', 'Slightly', 'Moderately', 'Severely'];

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
          probabilities = data.result.probabilities || null;
          topFeatures = data.result.topFeatures || [];
          modelVersion = data.result.modelVersion || modelVersion;
          if (data.result.disclaimer) disclaimer = data.result.disclaimer;
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

  function getBadgeClass(tClass) {
    if (classification !== tClass) {
      return 'bg-white border-[#F0D5DD] text-[#82476B] opacity-60';
    }
    switch (tClass) {
      case 'Not at all':
        return 'bg-[#EBF7EE] border-[#48BB78] text-[#22543D] ring-2 ring-[#48BB78]/30 font-bold shadow-xs';
      case 'Slightly':
        return 'bg-[#FFFBEB] border-[#F6E05E] text-[#744210] ring-2 ring-[#F6E05E]/30 font-bold shadow-xs';
      case 'Moderately':
        return 'bg-[#FFEBB8] border-[#BD5579] text-[#601D49] ring-2 ring-[#BD5579]/30 font-bold shadow-xs';
      case 'Severely':
        return 'bg-[#FFF5F5] border-[#E53E3E] text-[#742A2A] ring-2 ring-[#E53E3E]/30 font-bold shadow-xs';
      default:
        return 'bg-[#FFEBB8] border-[#BD5579] text-[#601D49] font-bold';
    }
  }
</script>

<svelte:head>
  <title>Assessment Result • MindSafe</title>
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
    <div class="p-16 text-center space-y-3">
      <div class="w-10 h-10 border-3 border-[#BD5579] border-t-transparent rounded-full animate-spin mx-auto"></div>
      <p class="text-xs font-semibold text-[#82476B]">Retrieving assessment result from research database...</p>
    </div>

  {:else if !hasAssessment}
    <!-- Empty State: No Assessment Taken Yet -->
    <EmptyState 
      title="No Assessment Found"
      description="You have not submitted a survey assessment yet. Please complete the assessment to view your model analysis."
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
            Research Evaluation
          </span>
          {#if submittedAt}
            <span class="text-[11px] text-[#82476B]">
              Recorded on {new Date(submittedAt).toLocaleDateString()} at {new Date(submittedAt).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
            </span>
          {/if}
        </div>
        <h1 class="page-title text-xl sm:text-2xl text-[#601D49]">
          Mental Health Impact Analysis
        </h1>
        <p class="text-xs text-[#82476B]">
          Predicted via Supervised Multiclass Random Forest ({modelVersion})
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

    <!-- 1. Classification Result Section with 4-Level Visual Indicator -->
    <Card class="p-6 sm:p-8 space-y-6 printable-card bg-white border border-[#F0D5DD]">
      <div class="flex items-center justify-between border-b border-[#F0D5DD] pb-4">
        <div>
          <span class="text-[11px] font-bold uppercase tracking-wider text-[#BD5579]">
            Target Outcome Classification
          </span>
          <h2 class="card-heading text-lg text-[#601D49]">Mental Health Impact</h2>
        </div>
        <div class="px-3 py-1 rounded-xl text-xs font-bold bg-[#FAF7F8] text-[#601D49] border border-[#EA9D9D]/60">
          Supervised Multiclass
        </div>
      </div>

      {#if hasResult && classification}
        <!-- Prominent Highlight of the Classified Outcome -->
        <div class="p-5 rounded-2xl bg-[#FAF7F8] border border-[#EA9D9D] flex flex-col sm:flex-row sm:items-center justify-between gap-4">
          <div class="space-y-1">
            <span class="text-xs font-semibold text-[#82476B]">Model Classified Category:</span>
            <div class="text-2xl font-extrabold text-[#601D49] flex items-center gap-2.5">
              <span>{classification}</span>
              <span class="text-xs px-2.5 py-0.5 rounded-full font-bold {getBadgeClass(classification)}">
                Predicted Class
              </span>
            </div>
            <p class="text-xs text-[#82476B]">
              The classification reflects the model's prediction based on the submitted survey responses.
            </p>
          </div>

          <a href="/assessment" class="no-print shrink-0">
            <Button variant="outline" class="px-4 py-2 text-xs font-semibold">
              <span>Retake Assessment</span>
            </Button>
          </a>
        </div>

        <!-- 4-Level Visual Indicator Scale (Highlighting ONLY the predicted class) -->
        <div class="space-y-3 pt-1">
          <div class="flex items-center justify-between text-xs font-semibold text-[#601D49]">
            <span>4-Level Empirical Outcome Scale:</span>
            <span class="text-[#82476B]">Highlighting active predicted category</span>
          </div>

          <div class="grid grid-cols-2 sm:grid-cols-4 gap-3">
            {#each targetClasses as tClass}
              <div class="p-4 rounded-xl border text-center transition-all {getBadgeClass(tClass)}">
                <div class="flex items-center justify-center gap-1.5 mb-1">
                  {#if classification === tClass}
                    <svg class="w-4 h-4 text-[#BD5579]" fill="none" stroke="currentColor" stroke-width="2.5" viewBox="0 0 24 24">
                      <path stroke-linecap="round" stroke-linejoin="round" d="M4.5 12.75l6 6 9-13.5" />
                    </svg>
                  {/if}
                  <span class="text-sm font-bold block">{tClass}</span>
                </div>
                <span class="text-[10px] block opacity-75">
                  {tClass === 'Not at all' ? 'Minimal / None' : tClass === 'Slightly' ? 'Mild Friction' : tClass === 'Moderately' ? 'Noticeable Stress' : 'Substantial Distress'}
                </span>
              </div>
            {/each}
          </div>
        </div>

      {:else}
        <!-- Fallback if prediction is still processing -->
        <div class="p-6 rounded-xl bg-[#FAF7F8] border border-[#EA9D9D]/60 text-center space-y-2">
          <p class="text-xs font-semibold text-[#601D49]">
            Your assessment responses have been recorded in MongoDB. The model analysis is processing.
          </p>
        </div>
      {/if}
    </Card>

    <!-- 2. "Why did the model make this prediction?" Section (Actual SHAP Output) -->
    <Card class="p-6 sm:p-8 space-y-5 printable-card bg-white border border-[#F0D5DD]">
      <div class="border-b border-[#F0D5DD] pb-3 space-y-0.5">
        <span class="text-[11px] font-bold uppercase tracking-wider text-[#BD5579]">
          Local Model Explainability (SHAP TreeExplainer)
        </span>
        <h2 class="card-heading text-lg text-[#601D49]">Why did the model make this prediction?</h2>
        <p class="text-xs text-[#82476B]">
          The features below contributed most heavily to the algorithm's decision for your specific response profile.
        </p>
      </div>

      {#if topFeatures && topFeatures.length > 0}
        <div class="space-y-3">
          {#each topFeatures as item, idx}
            <div class="p-4 rounded-xl bg-[#FAF7F8] border border-[#F0D5DD] flex items-start justify-between gap-3">
              <div class="flex items-start gap-3 min-w-0">
                <span class="w-6 h-6 rounded-full bg-[#FFEBB8] text-[#601D49] font-bold text-xs flex items-center justify-center shrink-0 border border-[#EA9D9D]/60 mt-0.5">
                  {idx + 1}
                </span>
                <div class="space-y-0.5 min-w-0">
                  <h4 class="text-xs sm:text-sm font-bold text-[#601D49]">
                    {item.feature}
                  </h4>
                  <p class="text-xs text-[#82476B] leading-relaxed">
                    {item.description}
                  </p>
                </div>
              </div>

              <div class="shrink-0 text-right space-y-0.5">
                <span class="inline-block px-2 py-0.5 rounded text-[10px] font-bold
                  {item.direction === 'increased' 
                    ? 'bg-[#EBF7EE] text-[#22543D] border border-[#48BB78]/40' 
                    : 'bg-[#FFF5F5] text-[#742A2A] border border-[#E53E3E]/40'}">
                  {item.direction === 'increased' ? '+ Positive Weight' : 'Countervailing'}
                </span>
                <span class="block text-[10px] text-[#82476B] font-mono">
                  SHAP: {item.shap_value > 0 ? '+' : ''}{item.shap_value}
                </span>
              </div>
            </div>
          {/each}
        </div>

        <div class="p-3 rounded-xl bg-[#FAF7F8] border border-[#F0D5DD] text-[11px] text-[#82476B] leading-relaxed">
          <strong>Methodological note:</strong> SHAP (SHapley Additive exPlanations) values quantify how much each survey response pushed the tree ensemble toward or away from the predicted class. They explain model decision behavior, not medical causality.
        </div>

      {:else}
        <div class="p-6 rounded-xl bg-[#FAF7F8] border border-[#F0D5DD] text-center text-xs text-[#82476B]">
          Feature attribution weights are available immediately upon completing the online assessment.
        </div>
      {/if}
    </Card>

    <!-- 3. Model Class Probabilities (Optional Toggle & Explicit Labeling) -->
    {#if probabilities}
      <Card class="p-6 sm:p-8 space-y-4 printable-card bg-white border border-[#F0D5DD]">
        <div class="flex items-center justify-between border-b border-[#F0D5DD] pb-3">
          <div>
            <span class="text-[11px] font-bold uppercase tracking-wider text-[#BD5579]">
              Analytical Metrics
            </span>
            <h3 class="text-sm sm:text-base font-bold text-[#601D49]">Model Class Probabilities</h3>
          </div>
          <button 
            type="button"
            onclick={() => showDetailedProbabilities = !showDetailedProbabilities}
            class="text-xs font-semibold text-[#BD5579] hover:underline cursor-pointer"
          >
            {showDetailedProbabilities ? 'Hide Probabilities' : 'View Class Probabilities'}
          </button>
        </div>

        {#if showDetailedProbabilities}
          <div class="space-y-3 pt-1">
            <p class="text-xs text-[#82476B] leading-relaxed">
              These values represent the model's estimated probabilities across the four predefined survey outcome classes. They are not medical probabilities or diagnostic probabilities.
            </p>

            <div class="grid grid-cols-2 sm:grid-cols-4 gap-3">
              {#each targetClasses as cName}
                {@const prob = probabilities[cName] ?? 0}
                <div class="p-3.5 rounded-xl bg-[#FAF7F8] border border-[#F0D5DD] space-y-1">
                  <span class="text-[11px] font-semibold text-[#82476B] block">{cName}</span>
                  <div class="text-base font-extrabold text-[#601D49]">
                    {(prob * 100).toFixed(1)}%
                  </div>
                  <!-- Mini Progress Bar -->
                  <div class="w-full h-1.5 bg-white rounded-full overflow-hidden border border-[#F0D5DD]">
                    <div 
                      class="h-full bg-[#BD5579] rounded-full" 
                      style="width: {Math.min(100, Math.round(prob * 100))}%;"
                    ></div>
                  </div>
                </div>
              {/each}
            </div>
          </div>
        {/if}
      </Card>
    {/if}

    <!-- 4. Recommendations & Official Helplines -->
    <Card class="p-6 sm:p-8 space-y-4 printable-card bg-white border border-[#F0D5DD]">
      <div class="border-b border-[#F0D5DD] pb-3">
        <span class="text-[11px] font-bold uppercase tracking-wider text-[#BD5579]">
          Supportive Guidance & Resources
        </span>
        <h2 class="card-heading text-base sm:text-lg text-[#601D49]">Cyber Safety & Student Wellness</h2>
      </div>

      <div class="grid grid-cols-1 md:grid-cols-3 gap-4 pt-1">
        <div class="p-4 rounded-xl bg-[#FAF7F8] border border-[#F0D5DD] space-y-1.5">
          <h4 class="text-xs font-bold text-[#601D49]">Curate Digital Screen Time</h4>
          <p class="text-xs text-[#82476B] leading-relaxed">
            Establish healthy screen boundaries. Take structured breaks from social media feeds to mitigate continuous digital friction.
          </p>
        </div>

        <div class="p-4 rounded-xl bg-[#FAF7F8] border border-[#F0D5DD] space-y-1.5">
          <h4 class="text-xs font-bold text-[#601D49]">Systematic Evidence Logging</h4>
          <p class="text-xs text-[#82476B] leading-relaxed">
            Preserve unedited screenshots with timestamps, account handles, and message URLs prior to muting or blocking offending profiles.
          </p>
        </div>

        <div class="p-4 rounded-xl bg-[#FAF7F8] border border-[#F0D5DD] space-y-1.5">
          <h4 class="text-xs font-bold text-[#601D49]">National Helpline (1930)</h4>
          <p class="text-xs text-[#82476B] leading-relaxed">
            Report statutory cyber offenses via cybercrime.gov.in or dial the national helpline 1930 for official grievance redressal.
          </p>
        </div>
      </div>

      <!-- Prominent Medical / Analytical Disclaimer -->
      <div class="p-4 rounded-xl bg-[#FFEBB8]/50 border border-[#EA9D9D] flex items-start gap-3 mt-3">
        <svg class="w-5 h-5 text-[#BD5579] shrink-0 mt-0.5" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" d="M12 9v3.75m9-.75a9 9 0 11-18 0 9 9 0 0118 0zm-9 3.75h.008v.008H12v-.008z" />
        </svg>
        <div class="space-y-1 text-xs text-[#601D49] leading-relaxed font-medium">
          <p>
            <strong>Medical & Analytical Disclaimer:</strong> {disclaimer}
          </p>
          <p class="text-[#82476B]">
            The classification reflects the model's prediction based on the submitted survey responses. This computational output is intended for academic research purposes and is not a clinical psychiatric evaluation. If you are experiencing distress, please reach out to qualified campus counseling or mental health professionals.
          </p>
        </div>
      </div>
    </Card>

  {/if}

</div>
