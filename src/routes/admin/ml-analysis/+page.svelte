<script>
  import Card from '$lib/components/Card.svelte';

  let { data } = $props();

  const modelInfo = $derived(data.modelInfo);
  const primaryMetrics = $derived(data.metrics?.primary_model || {
    Accuracy: 0.4854,
    Macro_Precision: 0.3700,
    Macro_Recall: 0.3498,
    Macro_F1: 0.3275,
    Weighted_Precision: 0.4134,
    Weighted_Recall: 0.4854,
    Weighted_F1: 0.4177
  });

  const shapImportance = $derived(data.shapImportance || []);
  const maxShap = $derived(
    shapImportance.length > 0
      ? Math.max(...shapImportance.map(s => Number(s.Mean_Abs_SHAP_Overall) || 0))
      : 1
  );

  const featureImportance = $derived(data.featureImportance || []);
  const maxFeatImp = $derived(
    featureImportance.length > 0
      ? Math.max(...featureImportance.map(f => Number(f.Importance) || 0))
      : 1
  );

  function cleanLabel(raw) {
    if (!raw) return '';
    return raw
      .replace(/_Binary$/, '')
      .replace(/_Ordinal$/, '')
      .replace(/Platform_Used_/, 'Uses: ')
      .replace(/Bullying_Type_/, 'Type: ')
      .replace(/Context_Area_/, 'Area: ')
      .replace(/Action_Taken_/, 'Action: ')
      .replace(/Sought_Help_/, 'Help: ')
      .replace(/Incident_Platform_/, 'Platform: ')
      .replace(/Posted_Offensive_/, 'Posted: ')
      .replace(/_/g, ' ');
  }
</script>

<svelte:head>
  <title>ML Model & SHAP Analytics • MindSafe Admin</title>
</svelte:head>

<div class="space-y-6 max-w-6xl mx-auto page-fade-in font-sans">
  
  <!-- Page Header -->
  <div class="flex flex-col sm:flex-row sm:items-center justify-between gap-3">
    <div class="space-y-1">
      <div class="flex items-center gap-2">
        <span class="px-2.5 py-0.5 rounded text-[10px] font-bold bg-[#FFEBB8] text-[#601D49] border border-[#EA9D9D]/60">
          Phase 3 Research Artifacts
        </span>
        <span class="text-xs text-[#82476B]">Scenario B (Leakage-Controlled)</span>
      </div>
      <h1 class="page-title text-2xl sm:text-3xl text-[#601D49]">
        Machine Learning Model & SHAP Analytics
      </h1>
      <p class="text-xs text-[#82476B]">
        Comprehensive empirical evaluation of the primary Random Forest classifier and Tree SHAP interpretability engine.
      </p>
    </div>

    <div class="shrink-0 flex items-center gap-2">
      <div class="px-3.5 py-2 rounded-xl bg-white border border-[#F0D5DD] shadow-xs text-xs">
        <span class="text-[#82476B]">Primary Predictors:</span>
        <span class="font-bold text-[#601D49] ml-1">54 Features</span>
      </div>
    </div>
  </div>

  <!-- Research Notice Banner -->
  <div class="p-4 rounded-xl bg-[#FAF7F8] border border-[#EA9D9D] flex items-start gap-3">
    <svg class="w-5 h-5 text-[#BD5579] shrink-0 mt-0.5" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24">
      <path stroke-linecap="round" stroke-linejoin="round" d="M11.25 11.25l.041-.02a.75.75 0 011.063.852l-.708 2.836a.75.75 0 001.063.853l.041-.021M21 12a9 9 0 11-18 0 9 9 0 0118 0zm-9-3.75h.008v.008H12V8.25z" />
    </svg>
    <div class="space-y-0.5 text-xs text-[#601D49] leading-relaxed">
      <span class="font-bold">Academic Evaluation Integrity Notice:</span>
      <p class="text-[#82476B]">
        These performance figures represent empirical scikit-learn test evaluation metrics from Phase 3 on the held-out test cohort (N=103) and 5-fold cross-validation on training records (N=411). They are documented model evaluation results and do not represent medical diagnostic accuracy.
      </p>
    </div>
  </div>

  <!-- Model Overview & Hyperparameters Card -->
  <Card class="p-6 bg-white border border-[#F0D5DD]">
    <div class="border-b border-[#F0D5DD] pb-3 mb-4">
      <span class="text-[11px] font-bold uppercase tracking-wider text-[#BD5579]">
        Model Architecture Specification
      </span>
      <h2 class="card-heading text-lg text-[#601D49]">{modelInfo.modelName}</h2>
    </div>

    <div class="grid grid-cols-2 sm:grid-cols-4 gap-4 text-xs">
      <div class="p-3.5 rounded-xl bg-[#FAF7F8] border border-[#F0D5DD] space-y-1">
        <span class="text-[11px] font-semibold text-[#82476B]">Algorithm</span>
        <p class="font-bold text-[#601D49]">Random Forest Classifier</p>
        <span class="text-[10px] text-[#82476B] block">100 Trees • Balanced Weights</span>
      </div>

      <div class="p-3.5 rounded-xl bg-[#FAF7F8] border border-[#F0D5DD] space-y-1">
        <span class="text-[11px] font-semibold text-[#82476B]">Target Outcome</span>
        <p class="font-bold text-[#601D49]">{modelInfo.targetVariable}</p>
        <span class="text-[10px] text-[#82476B] block">4 Multiclass Categories</span>
      </div>

      <div class="p-3.5 rounded-xl bg-[#FAF7F8] border border-[#F0D5DD] space-y-1">
        <span class="text-[11px] font-semibold text-[#82476B]">Data Partitioning</span>
        <p class="font-bold text-[#601D49]">Train N=411 • Test N=103</p>
        <span class="text-[10px] text-[#82476B] block">80/20 Stratified Split</span>
      </div>

      <div class="p-3.5 rounded-xl bg-[#FAF7F8] border border-[#F0D5DD] space-y-1">
        <span class="text-[11px] font-semibold text-[#82476B]">Feature Scenario</span>
        <p class="font-bold text-[#601D49]">Scenario B (Leakage-Controlled)</p>
        <span class="text-[10px] text-[#82476B] block">Excludes Q13 & Q14 tautology</span>
      </div>
    </div>
  </Card>

  <!-- Documented Model Performance Cards -->
  <div class="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-6 gap-3.5">
    <div class="p-4 rounded-2xl bg-white border border-[#F0D5DD] shadow-xs space-y-1">
      <span class="text-[11px] font-semibold text-[#82476B] block">Test Accuracy</span>
      <div class="text-xl sm:text-2xl font-black text-[#601D49]">
        {(primaryMetrics.Accuracy * 100).toFixed(2)}%
      </div>
      <span class="text-[10px] text-[#82476B] block">N = 103 test records</span>
    </div>

    <div class="p-4 rounded-2xl bg-white border border-[#F0D5DD] shadow-xs space-y-1">
      <span class="text-[11px] font-semibold text-[#82476B] block">Macro Precision</span>
      <div class="text-xl sm:text-2xl font-black text-[#601D49]">
        {primaryMetrics.Macro_Precision.toFixed(4)}
      </div>
      <span class="text-[10px] text-[#82476B] block">Unweighted class avg</span>
    </div>

    <div class="p-4 rounded-2xl bg-white border border-[#F0D5DD] shadow-xs space-y-1">
      <span class="text-[11px] font-semibold text-[#82476B] block">Macro Recall</span>
      <div class="text-xl sm:text-2xl font-black text-[#601D49]">
        {primaryMetrics.Macro_Recall.toFixed(4)}
      </div>
      <span class="text-[10px] text-[#82476B] block">Sensitivity balance</span>
    </div>

    <div class="p-4 rounded-2xl bg-white border border-[#F0D5DD] shadow-xs space-y-1">
      <span class="text-[11px] font-semibold text-[#82476B] block">Macro F1-Score</span>
      <div class="text-xl sm:text-2xl font-black text-[#BD5579]">
        {primaryMetrics.Macro_F1.toFixed(4)}
      </div>
      <span class="text-[10px] text-[#82476B] block">Core benchmark metric</span>
    </div>

    <div class="p-4 rounded-2xl bg-white border border-[#F0D5DD] shadow-xs space-y-1">
      <span class="text-[11px] font-semibold text-[#82476B] block">Weighted F1</span>
      <div class="text-xl sm:text-2xl font-black text-[#601D49]">
        {primaryMetrics.Weighted_F1.toFixed(4)}
      </div>
      <span class="text-[10px] text-[#82476B] block">Support weighted</span>
    </div>

    <div class="p-4 rounded-2xl bg-white border border-[#F0D5DD] shadow-xs space-y-1">
      <span class="text-[11px] font-semibold text-[#82476B] block">5-Fold CV Accuracy</span>
      <div class="text-xl sm:text-2xl font-black text-[#601D49]">
        49.88%
      </div>
      <span class="text-[10px] text-[#82476B] block">± 1.74% standard dev</span>
    </div>
  </div>

  <!-- Global SHAP Feature Importance (Horizontal Bar Chart) -->
  <Card class="p-6 sm:p-8 bg-white border border-[#F0D5DD] space-y-5">
    <div class="flex flex-col sm:flex-row sm:items-center justify-between border-b border-[#F0D5DD] pb-4 gap-2">
      <div>
        <span class="text-[11px] font-bold uppercase tracking-wider text-[#BD5579]">
          Explainability Engine
        </span>
        <h2 class="card-heading text-lg text-[#601D49]">Global SHAP Feature Importance</h2>
      </div>
      <div class="px-3 py-1 rounded-xl text-xs font-semibold bg-[#FAF7F8] text-[#82476B] border border-[#F0D5DD]">
        Top 15 Predictor Dimensions
      </div>
    </div>

    <p class="text-xs text-[#82476B] leading-relaxed">
      <strong>Research Definition:</strong> Mean absolute SHAP values indicate the average magnitude of each feature's contribution to model predictions across all test instances. SHAP values quantify algorithm reliance and decision attribution, not medical or behavioral causation.
    </p>

    <!-- Horizontal Bar Chart -->
    <div class="space-y-3 pt-2">
      {#each shapImportance as item, idx}
        {@const val = Number(item.Mean_Abs_SHAP_Overall) || 0}
        {@const pct = maxShap > 0 ? (val / maxShap) * 100 : 0}
        <div class="space-y-1">
          <div class="flex items-center justify-between text-xs">
            <span class="font-semibold text-[#601D49] flex items-center gap-2">
              <span class="w-4 text-[10px] text-[#82476B] font-mono">{idx + 1}.</span>
              <span>{cleanLabel(item.Feature)}</span>
            </span>
            <span class="font-mono text-xs font-bold text-[#BD5579]">
              {val.toFixed(4)}
            </span>
          </div>

          <!-- Bar -->
          <div class="w-full h-3 bg-[#FAF7F8] rounded-full overflow-hidden border border-[#F0D5DD]">
            <div 
              class="h-full bg-[#BD5579] rounded-full transition-all duration-500 ease-out"
              style="width: {pct}%;"
            ></div>
          </div>
        </div>
      {/each}
    </div>
  </Card>

  <!-- Detailed Tables Grid: Per-Class Report & Model Comparison -->
  <div class="grid grid-cols-1 lg:grid-cols-2 gap-6">
    
    <!-- Per-Class Classification Report -->
    <Card class="p-6 bg-white border border-[#F0D5DD] space-y-4">
      <div class="border-b border-[#F0D5DD] pb-3">
        <span class="text-[11px] font-bold uppercase tracking-wider text-[#BD5579]">
          Test Set Breakdown (N=103)
        </span>
        <h3 class="text-base font-bold text-[#601D49]">Per-Class Classification Metrics</h3>
      </div>

      <div class="overflow-x-auto">
        <table class="w-full text-left text-xs">
          <thead>
            <tr class="border-b border-[#F0D5DD] text-[#82476B] uppercase font-bold text-[10px]">
              <th class="py-2.5 px-2">Target Class</th>
              <th class="py-2.5 px-2 text-right">Precision</th>
              <th class="py-2.5 px-2 text-right">Recall</th>
              <th class="py-2.5 px-2 text-right">F1-Score</th>
              <th class="py-2.5 px-2 text-right">Support</th>
            </tr>
          </thead>
          <tbody class="divide-y divide-[#F0D5DD]">
            {#each data.classificationReport as row}
              <tr class="hover:bg-[#FAF7F8]">
                <td class="py-2.5 px-2 font-bold text-[#601D49]">{row.Class}</td>
                <td class="py-2.5 px-2 text-right font-mono">{Number(row.Precision).toFixed(4)}</td>
                <td class="py-2.5 px-2 text-right font-mono">{Number(row.Recall).toFixed(4)}</td>
                <td class="py-2.5 px-2 text-right font-mono font-bold text-[#BD5579]">{Number(row.F1_Score).toFixed(4)}</td>
                <td class="py-2.5 px-2 text-right font-mono text-[#82476B]">{row.Support}</td>
              </tr>
            {/each}
          </tbody>
        </table>
      </div>
    </Card>

    <!-- Cross-Validation & Scenario Comparison -->
    <Card class="p-6 bg-white border border-[#F0D5DD] space-y-4">
      <div class="border-b border-[#F0D5DD] pb-3">
        <span class="text-[11px] font-bold uppercase tracking-wider text-[#BD5579]">
          5-Fold Stratified Cross-Validation
        </span>
        <h3 class="text-base font-bold text-[#601D49]">Cross-Validation Results</h3>
      </div>

      <div class="overflow-x-auto">
        <table class="w-full text-left text-xs">
          <thead>
            <tr class="border-b border-[#F0D5DD] text-[#82476B] uppercase font-bold text-[10px]">
              <th class="py-2.5 px-2">Model Scenario</th>
              <th class="py-2.5 px-2 text-right">CV Accuracy</th>
              <th class="py-2.5 px-2 text-right">CV Weighted F1</th>
              <th class="py-2.5 px-2 text-right">CV Macro F1</th>
            </tr>
          </thead>
          <tbody class="divide-y divide-[#F0D5DD]">
            {#each data.cvResults as cv}
              <tr class="hover:bg-[#FAF7F8]">
                <td class="py-2.5 px-2 font-bold text-[#601D49]">{cv.Model}</td>
                <td class="py-2.5 px-2 text-right font-mono">
                  {(Number(cv.CV_Accuracy_Mean) * 100).toFixed(2)}% ± {(Number(cv.CV_Accuracy_Std) * 100).toFixed(2)}%
                </td>
                <td class="py-2.5 px-2 text-right font-mono font-bold text-[#BD5579]">
                  {Number(cv.CV_Weighted_F1_Mean).toFixed(4)}
                </td>
                <td class="py-2.5 px-2 text-right font-mono">
                  {Number(cv.CV_Macro_F1_Mean).toFixed(4)}
                </td>
              </tr>
            {/each}
          </tbody>
        </table>
      </div>

      <div class="p-3 rounded-xl bg-[#FAF7F8] border border-[#F0D5DD] text-[11px] text-[#82476B]">
        <strong>5-Fold CV Summary:</strong> Primary Model B achieves mean cross-validation accuracy of 49.88% ± 1.74% and mean weighted F1 of 0.4387 ± 0.0226 across all folds.
      </div>
    </Card>

  </div>

  <!-- Model Comparison Benchmark Table -->
  <Card class="p-6 bg-white border border-[#F0D5DD] space-y-4">
    <div class="border-b border-[#F0D5DD] pb-3">
      <span class="text-[11px] font-bold uppercase tracking-wider text-[#BD5579]">
        Comparative Research Framework
      </span>
      <h3 class="text-base font-bold text-[#601D49]">Model Benchmark Comparison</h3>
    </div>

    <div class="overflow-x-auto">
      <table class="w-full text-left text-xs">
        <thead>
          <tr class="border-b border-[#F0D5DD] text-[#82476B] uppercase font-bold text-[10px]">
            <th class="py-3 px-3">Model Candidate</th>
            <th class="py-3 px-3 text-right">Accuracy</th>
            <th class="py-3 px-3 text-right">Macro Precision</th>
            <th class="py-3 px-3 text-right">Macro Recall</th>
            <th class="py-3 px-3 text-right">Macro F1</th>
            <th class="py-3 px-3 text-right">Weighted F1</th>
          </tr>
        </thead>
        <tbody class="divide-y divide-[#F0D5DD]">
          {#each data.modelComparison as comp}
            <tr class="hover:bg-[#FAF7F8]">
              <td class="py-3 px-3 font-bold text-[#601D49]">{comp.Model}</td>
              <td class="py-3 px-3 text-right font-mono">{(Number(comp.Accuracy) * 100).toFixed(2)}%</td>
              <td class="py-3 px-3 text-right font-mono">{Number(comp.Macro_Precision).toFixed(4)}</td>
              <td class="py-3 px-3 text-right font-mono">{Number(comp.Macro_Recall).toFixed(4)}</td>
              <td class="py-3 px-3 text-right font-mono font-bold text-[#BD5579]">{Number(comp.Macro_F1).toFixed(4)}</td>
              <td class="py-3 px-3 text-right font-mono font-bold">{Number(comp.Weighted_F1).toFixed(4)}</td>
            </tr>
          {/each}
        </tbody>
      </table>
    </div>
  </Card>

</div>
