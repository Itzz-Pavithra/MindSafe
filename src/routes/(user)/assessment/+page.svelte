<script>
  import Card from '$lib/components/Card.svelte';
  import Button from '$lib/components/Button.svelte';
  import { appState } from '$lib/state/appState.svelte.js';

  // 13 Questionnaire Features Expected by MindSafe Primary Model (Scenario B)
  const questions = [
    {
      id: 'age',
      title: 'What is your age category?',
      subtitle: 'Demographic baseline for statistical cohort analysis.',
      type: 'single',
      options: [
        { value: 'Below 18', label: 'Under 18', desc: 'Adolescent cohort' },
        { value: '18–22', label: '18–22 years', desc: 'Undergraduate / College student cohort' },
        { value: '23–30', label: '23–30 years', desc: 'Postgraduate / Early career cohort' },
        { value: 'Above 30', label: 'Above 30 years', desc: 'Adult cohort' }
      ]
    },
    {
      id: 'gender',
      title: 'What is your gender identity?',
      subtitle: 'Demographic grouping for population distribution analysis.',
      type: 'single',
      options: [
        { value: 'Female', label: 'Female', desc: 'Self-identified female respondent' },
        { value: 'Male', label: 'Male', desc: 'Self-identified male respondent' },
        { value: 'Non-binary', label: 'Non-binary', desc: 'Non-binary / Gender diverse' },
        { value: 'Prefer not to say', label: 'Prefer not to say', desc: 'Confidential selection' }
      ]
    },
    {
      id: 'platforms',
      title: 'Which social media platforms do you use regularly?',
      subtitle: 'Select all platforms where you maintain an active digital presence.',
      type: 'multi',
      options: [
        { value: 'Instagram', label: 'Instagram', desc: 'Visual feeds, stories & direct messaging' },
        { value: 'WhatsApp', label: 'WhatsApp', desc: 'Direct, peer & family group messaging' },
        { value: 'YouTube', label: 'YouTube', desc: 'Video content streaming & community comments' },
        { value: 'Facebook', label: 'Facebook', desc: 'Network posts, groups & social connections' },
        { value: 'X (Twitter)', label: 'X (Twitter)', desc: 'Public discourse, micro-blogging & threads' },
        { value: 'Others', label: 'Other Platforms', desc: 'Discord, Snapchat, Reddit, or other social networks' }
      ]
    },
    {
      id: 'usage',
      title: 'How many hours do you spend on social media per day?',
      subtitle: 'Estimate your average daily digital screen engagement.',
      type: 'single',
      options: [
        { value: 'Less than 1 hour', label: 'Less than 1 hour', desc: 'Minimal / Light daily usage' },
        { value: '1–3 hours', label: '1–3 hours', desc: 'Moderate everyday social engagement' },
        { value: '3–5 hours', label: '3–5 hours', desc: 'Substantial daily screen time' },
        { value: 'More than 5 hours', label: 'More than 5 hours', desc: 'Extensive digital immersion' }
      ]
    },
    {
      id: 'q5_exp',
      title: 'Have you personally experienced cyberbullying or online harassment on social media?',
      subtitle: 'Direct personal encounter with abusive or threatening behavior online.',
      type: 'single',
      options: [
        { value: 'Yes', label: 'Yes', desc: 'I have personally experienced online hostility or harassment' },
        { value: 'No', label: 'No', desc: 'I have not personally experienced online harassment' }
      ]
    },
    {
      id: 'q6_wit',
      title: 'Have you ever witnessed someone being cyberbullied online?',
      subtitle: 'Observation of third-party harassment or aggressive behavior.',
      type: 'single',
      options: [
        { value: 'Yes', label: 'Yes', desc: 'I have witnessed someone else being targeted or harassed' },
        { value: 'No', label: 'No', desc: 'I have never witnessed online harassment' }
      ]
    },
    {
      id: 'q7_post',
      title: 'Have you ever posted, shared, or sent a message online that could have hurt or offended someone?',
      subtitle: 'Self-reported communicative friction or conflict behavior.',
      type: 'single',
      options: [
        { value: 'No', label: 'No', desc: 'I have not posted potentially hurtful messages' },
        { value: 'Not Sure', label: 'Not Sure', desc: 'Ambiguous or unintentional communicative impact' },
        { value: 'Yes', label: 'Yes', desc: 'I have sent or posted a message that caused offense' }
      ]
    },
    {
      id: 'q9_types',
      title: 'What type of cyberbullying have you experienced or observed?',
      subtitle: 'Select all categories of hostile conduct encountered (or None).',
      type: 'multi',
      options: [
        { value: 'Offensive Comments', label: 'Offensive Comments', desc: 'Derogatory insults, vulgar remarks, or aggressive baiting' },
        { value: 'Body Shaming', label: 'Body Shaming', desc: 'Targeted criticism of physical appearance' },
        { value: 'Hate Speech', label: 'Hate Speech', desc: 'Hostility directed toward identity, religion, or community' },
        { value: 'Threats', label: 'Direct Threats', desc: 'Threats of physical harm, doxing, or blackmail' },
        { value: 'Fake Rumors', label: 'Fake Rumors', desc: 'Defamatory misinformation or malicious gossip' },
        { value: 'Fake Profile', label: 'Fake Profiles', desc: 'Impersonation accounts created to harass or deceive' },
        { value: 'Sexual Harassment', label: 'Sexual Harassment', desc: 'Unwanted sexual content, non-consensual imagery, or messages' },
        { value: 'Stalking', label: 'Online Stalking', desc: 'Persistent surveillance and unwanted tracking' },
        { value: 'Other', label: 'Other Forms', desc: 'Other varieties of digital friction' }
      ]
    },
    {
      id: 'q10_plat',
      title: 'On which social media platform did the incident most noticeably occur?',
      subtitle: 'Primary platform context for observed or experienced harassment.',
      type: 'single',
      options: [
        { value: 'Instagram', label: 'Instagram', desc: 'DMs, comments, or reels' },
        { value: 'WhatsApp', label: 'WhatsApp', desc: 'Direct messages, status updates, or group chats' },
        { value: 'Facebook', label: 'Facebook', desc: 'Posts, messenger, or group discussions' },
        { value: 'YouTube', label: 'YouTube', desc: 'Video comment sections or livestreams' },
        { value: 'Others', label: 'Other Platforms', desc: 'Discord, gaming platforms, X, or other networks' }
      ]
    },
    {
      id: 'q11_freq',
      title: 'How often have you experienced or encountered cyberbullying online?',
      subtitle: 'Empirical frequency scale of digital hostility.',
      type: 'single',
      options: [
        { value: 'Never', label: 'Never', desc: 'Zero incidents encountered' },
        { value: 'Rarely', label: 'Rarely', desc: 'Infrequent, isolated occurrences' },
        { value: 'Sometimes', label: 'Sometimes', desc: 'Occasional encounters throughout the year' },
        { value: 'Often', label: 'Often', desc: 'Frequent, regular weekly occurrences' },
        { value: 'Very Often', label: 'Very Often', desc: 'Continuous or repetitive online hostility' }
      ]
    },
    {
      id: 'q15_help',
      title: 'Did you seek help from anyone?',
      subtitle: 'Select all sources of support consulted after encountering hostility.',
      type: 'multi',
      options: [
        { value: 'No', label: 'No Help Sought', desc: 'Did not consult external support channels' },
        { value: 'Friends', label: 'Friends / Peers', desc: 'Discussed incident with peer group' },
        { value: 'Family', label: 'Family Members', desc: 'Confided in parents or siblings' },
        { value: 'Teacher', label: 'Teacher / Faculty', desc: 'Reported to academic mentors' },
        { value: 'Counselor', label: 'Counselor', desc: 'Consulted campus or student counselor' },
        { value: 'Psychologist', label: 'Psychologist', desc: 'Sought licensed mental health therapist' },
        { value: 'Helpline', label: 'Official Helpline', desc: 'Contacted cyber crime helpline (1930) or mental health line' }
      ]
    },
    {
      id: 'q17_area',
      title: 'In which area or context did you experience cyberbullying?',
      subtitle: 'Social or environmental domain of the encounter.',
      type: 'single',
      options: [
        { value: 'Social Media Community', label: 'Social Media Community', desc: 'Open social media public forums and comment threads' },
        { value: 'Friends Circle', label: 'Friends Circle', desc: 'Personal friendship or acquaintance network' },
        { value: 'Unknown Stranger', label: 'Unknown Stranger', desc: 'Unidentified or anonymous online accounts' },
        { value: 'School / College', label: 'School / College', desc: 'Educational or campus environment' },
        { value: 'Workplace', label: 'Workplace', desc: 'Professional or workplace digital spaces' },
        { value: 'Online Gaming', label: 'Online Gaming', desc: 'Multiplayer gaming servers and lobbies' },
        { value: 'Family', label: 'Family Network', desc: 'Extended family or kinship communication groups' },
        { value: 'Other', label: 'Other Domain', desc: 'Other interpersonal setting' }
      ]
    },
    {
      id: 'q18_act',
      title: 'What action did you take after experiencing cyberbullying?',
      subtitle: 'Select all behavioral measures or protective steps adopted.',
      type: 'multi',
      options: [
        { value: 'Blocked the user', label: 'Blocked the User', desc: 'Muted or blocked the offending profile' },
        { value: 'Ignored it', label: 'Ignored It', desc: 'Chose not to react or engage' },
        { value: 'Reported the account', label: 'Reported the Account', desc: 'Utilized in-app reporting tools' },
        { value: 'Told Friends / Family', label: 'Told Friends / Family', desc: 'Informed trusted peers or relatives' },
        { value: 'Sought Professional Help', label: 'Sought Professional Help', desc: 'Approached counselor, therapist, or legal authority' },
        { value: 'Took No Action', label: 'Took No Action', desc: 'No intervention or response undertaken' }
      ]
    }
  ];

  let currentIdx = $state(0);
  let answers = $state({});
  let isReviewing = $state(false);
  let isSubmitting = $state(false);
  let validationError = $state('');

  let currentQ = $derived(questions[currentIdx]);
  let currentVal = $derived(answers[currentQ?.id]);
  let progressPct = $derived(Math.round(((currentIdx + 1) / questions.length) * 100));

  function selectSingleOption(val) {
    answers[currentQ.id] = val;
    validationError = '';
  }

  function toggleMultiOption(val) {
    const existing = Array.isArray(answers[currentQ.id]) ? [...answers[currentQ.id]] : [];
    const idx = existing.indexOf(val);
    if (idx >= 0) {
      existing.splice(idx, 1);
    } else {
      existing.push(val);
    }
    answers[currentQ.id] = existing;
    validationError = '';
  }

  function isMultiSelected(val) {
    const existing = answers[currentQ?.id];
    return Array.isArray(existing) && existing.includes(val);
  }

  function handleNext() {
    const val = answers[currentQ.id];
    if (currentQ.type === 'multi') {
      if (!Array.isArray(val) || val.length === 0) {
        validationError = 'Please select at least one option to continue.';
        return;
      }
    } else {
      if (!val) {
        validationError = 'This question is required. Please select an option to continue.';
        return;
      }
    }
    validationError = '';

    if (currentIdx < questions.length - 1) {
      currentIdx++;
    } else {
      isReviewing = true;
    }
  }

  function handleBack() {
    validationError = '';
    if (isReviewing) {
      isReviewing = false;
      return;
    }
    if (currentIdx > 0) {
      currentIdx--;
    }
  }

  function editQuestion(idx) {
    currentIdx = idx;
    isReviewing = false;
  }

  async function submitAssessment() {
    // Validate all 13 questions
    for (let i = 0; i < questions.length; i++) {
      const q = questions[i];
      const val = answers[q.id];
      if (q.type === 'multi') {
        if (!Array.isArray(val) || val.length === 0) {
          currentIdx = i;
          isReviewing = false;
          validationError = `Question ${i + 1} (${q.title}) requires at least one selection.`;
          return;
        }
      } else {
        if (!val) {
          currentIdx = i;
          isReviewing = false;
          validationError = `Question ${i + 1} (${q.title}) requires a response.`;
          return;
        }
      }
    }

    isSubmitting = true;
    validationError = '';

    try {
      const res = await fetch('/api/ml/predict', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ assessment: answers })
      });

      const data = await res.json();
      if (res.ok && data.success) {
        appState.addToast('success', 'Analysis Complete', 'Your assessment was successfully processed by the ML model.');
        window.location.href = '/result';
      } else {
        validationError = data.error || 'Unable to analyze your responses right now. Please try again.';
        appState.addToast('danger', 'Analysis Notice', validationError);
      }
    } catch (err) {
      console.error('Assessment submission network error:', err);
      validationError = 'Unable to analyze your responses right now. Please try again.';
      appState.addToast('danger', 'Connection Notice', validationError);
    } finally {
      isSubmitting = false;
    }
  }
</script>

<div class="max-w-2xl mx-auto space-y-6 page-fade-in font-sans">
  
  {#if isSubmitting}
    <!-- Dedicated Professional ML Loading Screen -->
    <Card class="p-10 sm:p-14 text-center space-y-6 bg-white border border-[#F0D5DD] shadow-sm">
      <div class="w-16 h-16 rounded-full bg-[#FAF7F8] border border-[#EA9D9D] flex items-center justify-center mx-auto shadow-xs">
        <svg class="w-8 h-8 text-[#BD5579] animate-spin" fill="none" viewBox="0 0 24 24">
          <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="3"></circle>
          <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
        </svg>
      </div>

      <div class="space-y-2">
        <h2 class="text-xl font-bold text-[#601D49]">Analyzing your responses...</h2>
        <p class="text-xs text-[#82476B] max-w-md mx-auto leading-relaxed">
          Evaluating survey feature dimensions through the trained Random Forest classifier and computing local SHAP feature attributions.
        </p>
      </div>

      <div class="inline-flex items-center gap-2 px-3 py-1.5 rounded-full bg-[#FAF7F8] border border-[#F0D5DD] text-[11px] font-semibold text-[#82476B]">
        <svg class="w-3.5 h-3.5 text-[#BD5579]" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" d="M9 12.75L11.25 15 15 9.75m-3-7.036A11.959 11.959 0 013.598 6 11.99 11.99 0 003 9.749c0 5.592 3.824 10.29 9 11.623 5.176-1.332 9-6.03 9-11.622 0-1.31-.21-2.571-.598-3.751h-.152c-3.196 0-6.1-1.248-8.25-3.285z" />
        </svg>
        <span>Model Version: Random Forest Scenario B (Leakage-Controlled)</span>
      </div>
    </Card>

  {:else if !isReviewing}
    <!-- Progress Indicator Card -->
    <div class="bg-white border border-[#F0D5DD] rounded-2xl p-5 shadow-xs space-y-3">
      <div class="flex items-center justify-between text-xs font-semibold">
        <span class="text-[#82476B]">Research Assessment Progress</span>
        <span class="text-[#601D49] font-bold">Question {currentIdx + 1} of {questions.length}</span>
      </div>

      <!-- Clean Progress Bar -->
      <div class="w-full h-2 bg-[#FAF7F8] rounded-full overflow-hidden border border-[#F0D5DD]">
        <div 
          class="h-full bg-[#BD5579] rounded-full transition-all duration-300 ease-out"
          style="width: {progressPct}%;"
        ></div>
      </div>
    </div>

    <!-- Active Question Card -->
    <Card class="p-6 sm:p-8 space-y-6 bg-white border border-[#F0D5DD] shadow-sm">
      
      <!-- Question Heading -->
      <div class="space-y-1.5 border-b border-[#F0D5DD] pb-4">
        <div class="flex items-center justify-between">
          <span class="text-[11px] font-bold uppercase tracking-wider text-[#BD5579]">
            Question {currentIdx + 1} of {questions.length} {currentQ.type === 'multi' ? '• Multiselect' : '• Single Choice'}
          </span>
          <span class="text-[11px] font-semibold text-[#82476B]">Required *</span>
        </div>
        <h2 class="text-base sm:text-lg font-bold text-[#601D49] leading-snug">
          {currentQ.title}
        </h2>
        <p class="text-xs text-[#82476B]">
          {currentQ.subtitle}
        </p>
      </div>

      <!-- Error State -->
      {#if validationError}
        <div class="p-3.5 rounded-xl bg-[#FAF7F8] border border-[#BD5579] text-[#601D49] text-xs font-medium flex items-center gap-2.5">
          <svg class="w-4 h-4 text-[#BD5579] shrink-0" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" d="M12 9v3.75m9-.75a9 9 0 11-18 0 9 9 0 0118 0zm-9 3.75h.008v.008H12v-.008z" />
          </svg>
          <span>{validationError}</span>
        </div>
      {/if}

      <!-- Options List -->
      <div class="space-y-2.5">
        {#each currentQ.options as opt}
          {#if currentQ.type === 'multi'}
            <!-- Checkbox Item -->
            <button
              type="button"
              onclick={() => toggleMultiOption(opt.value)}
              class="w-full p-4 rounded-xl border text-left transition-all cursor-pointer flex items-start gap-3.5
                {isMultiSelected(opt.value)
                  ? 'bg-[#FFEBB8]/40 border-[#BD5579] ring-1 ring-[#BD5579] shadow-xs'
                  : 'bg-white border-[#F0D5DD] hover:border-[#EA9D9D] hover:bg-[#FAF7F8]'}"
            >
              <div class="mt-0.5 w-4 h-4 rounded border flex items-center justify-center shrink-0
                {isMultiSelected(opt.value)
                  ? 'border-[#BD5579] bg-[#BD5579]'
                  : 'border-[#EA9D9D] bg-white'}">
                {#if isMultiSelected(opt.value)}
                  <svg class="w-3 h-3 text-white" fill="none" stroke="currentColor" stroke-width="3" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" d="M4.5 12.75l6 6 9-13.5" />
                  </svg>
                {/if}
              </div>

              <div class="space-y-0.5 min-w-0 flex-1">
                <span class="text-xs sm:text-sm font-semibold text-[#601D49] block">
                  {opt.label}
                </span>
                <span class="text-xs text-[#82476B] block">
                  {opt.desc}
                </span>
              </div>
            </button>
          {:else}
            <!-- Radio Item -->
            <button
              type="button"
              onclick={() => selectSingleOption(opt.value)}
              class="w-full p-4 rounded-xl border text-left transition-all cursor-pointer flex items-start gap-3.5
                {currentVal === opt.value
                  ? 'bg-[#FFEBB8]/40 border-[#BD5579] ring-1 ring-[#BD5579] shadow-xs'
                  : 'bg-white border-[#F0D5DD] hover:border-[#EA9D9D] hover:bg-[#FAF7F8]'}"
            >
              <div class="mt-0.5 w-4 h-4 rounded-full border flex items-center justify-center shrink-0
                {currentVal === opt.value
                  ? 'border-[#BD5579] bg-[#BD5579]'
                  : 'border-[#EA9D9D] bg-white'}">
                {#if currentVal === opt.value}
                  <div class="w-1.5 h-1.5 rounded-full bg-white"></div>
                {/if}
              </div>

              <div class="space-y-0.5 min-w-0 flex-1">
                <span class="text-xs sm:text-sm font-semibold text-[#601D49] block">
                  {opt.label}
                </span>
                <span class="text-xs text-[#82476B] block">
                  {opt.desc}
                </span>
              </div>
            </button>
          {/if}
        {/each}
      </div>

      <!-- Navigation Buttons -->
      <div class="flex items-center justify-between pt-4 border-t border-[#F0D5DD]">
        <Button 
          variant="outline" 
          disabled={currentIdx === 0} 
          onclick={handleBack}
          class="px-4 py-2.5 text-xs font-semibold"
        >
          <svg class="w-4 h-4" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" d="M10.5 19.5L3 12m0 0l7.5-7.5M3 12h18" />
          </svg>
          <span>Previous</span>
        </Button>

        <Button 
          variant="primary" 
          onclick={handleNext}
          class="px-6 py-2.5 text-xs font-semibold"
        >
          <span>{currentIdx === questions.length - 1 ? 'Review Responses' : 'Next Question'}</span>
          <svg class="w-4 h-4" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" d="M13.5 4.5L21 12m0 0l-7.5 7.5M21 12H3" />
          </svg>
        </Button>
      </div>

    </Card>

  {:else}
    <!-- Review Before Submission Screen -->
    <Card class="p-6 sm:p-8 space-y-6 bg-white border border-[#F0D5DD] shadow-sm">
      <div class="border-b border-[#F0D5DD] pb-4 space-y-1">
        <span class="text-[11px] font-bold uppercase tracking-wider text-[#BD5579]">
          Final Verification
        </span>
        <h2 class="text-lg font-bold text-[#601D49]">Review Your Survey Responses</h2>
        <p class="text-xs text-[#82476B]">
          Please review your selections. When submitted, the primary Random Forest model will evaluate your responses and generate localized SHAP interpretability weights.
        </p>
      </div>

      {#if validationError}
        <div class="p-3.5 rounded-xl bg-[#FAF7F8] border border-[#BD5579] text-[#601D49] text-xs font-medium">
          {validationError}
        </div>
      {/if}

      <!-- Questions Review Grid -->
      <div class="space-y-3 max-h-96 overflow-y-auto pr-1">
        {#each questions as q, idx}
          {@const ans = answers[q.id]}
          <div class="p-3.5 rounded-xl bg-[#FAF7F8] border border-[#F0D5DD] flex items-center justify-between gap-3">
            <div class="min-w-0 flex-1 space-y-0.5">
              <span class="text-[11px] font-semibold text-[#82476B]">Q{idx + 1}: {q.title}</span>
              <p class="text-xs font-bold text-[#601D49] truncate">
                Answer: 
                <span class="text-[#BD5579]">
                  {Array.isArray(ans) ? ans.join(', ') : (ans || 'Not answered')}
                </span>
              </p>
            </div>
            <button
              type="button"
              onclick={() => editQuestion(idx)}
              class="text-xs font-semibold text-[#BD5579] hover:underline shrink-0 p-1 cursor-pointer"
            >
              Edit
            </button>
          </div>
        {/each}
      </div>

      <!-- Submission Actions -->
      <div class="flex items-center justify-between pt-4 border-t border-[#F0D5DD]">
        <Button 
          variant="outline" 
          onclick={handleBack}
          disabled={isSubmitting}
          class="px-4 py-2.5 text-xs font-semibold"
        >
          <svg class="w-4 h-4" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" d="M10.5 19.5L3 12m0 0l7.5-7.5M3 12h18" />
          </svg>
          <span>Back to Questions</span>
        </Button>

        <Button 
          variant="primary" 
          disabled={isSubmitting}
          onclick={submitAssessment}
          class="px-6 py-2.5 text-xs font-bold"
        >
          <span>Analyze & Submit Assessment</span>
          <svg class="w-4 h-4" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" d="M4.5 12.75l6 6 9-13.5" />
          </svg>
        </Button>
      </div>

    </Card>
  {/if}

</div>
