<script>
  import Card from '$lib/components/Card.svelte';
  import Button from '$lib/components/Button.svelte';
  import { appState } from '$lib/state/appState.svelte.js';

  // Research Questionnaire Configuration
  const questions = [
    {
      id: 'ageGroup',
      title: 'What is your age category?',
      subtitle: 'Demographic baseline for statistical cohort analysis.',
      options: [
        { value: 'Under 18', label: 'Under 18', desc: 'Adolescent cohort' },
        { value: '18–22', label: '18–22', desc: 'Undergraduate / College student cohort' },
        { value: '23–26', label: '23–26', desc: 'Postgraduate / Early career cohort' },
        { value: '27+', label: '27 and above', desc: 'Adult cohort' }
      ]
    },
    {
      id: 'gender',
      title: 'What is your gender identity?',
      subtitle: 'Demographic grouping for population distribution analysis.',
      options: [
        { value: 'Female', label: 'Female', desc: 'Self-identified female respondent' },
        { value: 'Male', label: 'Male', desc: 'Self-identified male respondent' },
        { value: 'Non-binary', label: 'Non-binary', desc: 'Non-binary / Gender diverse' },
        { value: 'Prefer not to say', label: 'Prefer not to say', desc: 'Confidential selection' }
      ]
    },
    {
      id: 'usageHours',
      title: 'How many hours do you spend on social media per day on average?',
      subtitle: 'Estimate average daily digital engagement across social platforms.',
      options: [
        { value: '< 2.5 hrs', label: '< 2.5 hours', desc: 'Light to moderate daily usage' },
        { value: '2.5–4.5 hrs', label: '2.5–4.5 hours', desc: 'Standard everyday social engagement' },
        { value: '4.5–6.5 hrs', label: '4.5–6.5 hours', desc: 'Substantial daily screen time' },
        { value: '> 6.5 hrs', label: '> 6.5 hours', desc: 'Extensive, prolonged digital immersion' }
      ]
    },
    {
      id: 'socialMediaPlatform',
      title: 'Which primary social media platform do you use most frequently?',
      subtitle: 'Identify the main platform where you spend the largest share of your time.',
      options: [
        { value: 'Instagram', label: 'Instagram', desc: 'Visual feeds, stories & direct messaging' },
        { value: 'YouTube', label: 'YouTube', desc: 'Video content streaming & community comments' },
        { value: 'TikTok / Reels', label: 'Short Video (Reels / Shorts)', desc: 'Algorithmic short-form video streaming' },
        { value: 'X (Twitter)', label: 'X (Twitter)', desc: 'Public discourse, micro-blogging & threads' },
        { value: 'Snapchat', label: 'Snapchat', desc: 'Ephemeral multimedia communication' },
        { value: 'Discord', label: 'Discord', desc: 'Group servers, gaming & interest communities' },
        { value: 'WhatsApp', label: 'WhatsApp', desc: 'Direct, peer & family group messaging' }
      ]
    },
    {
      id: 'cyberbullyingExperience',
      title: 'Have you personally encountered cyberbullying or hostile comments online?',
      subtitle: 'Indicate whether you have directly been subjected to online harassment.',
      options: [
        { value: 'Yes', label: 'Yes', desc: 'I have personally experienced cyberbullying or hostile behavior' },
        { value: 'No', label: 'No', desc: 'I have not directly experienced online harassment' }
      ]
    },
    {
      id: 'frequency',
      title: 'How frequently do you encounter hostile or harassing behavior online?',
      subtitle: 'Specify the observed frequency of digital friction in your interactions.',
      options: [
        { value: 'Never', label: 'Never', desc: 'Zero encounters in typical online activity' },
        { value: 'Rarely', label: 'Rarely', desc: 'Infrequent, isolated occurrences' },
        { value: 'Sometimes', label: 'Sometimes', desc: 'Occasional encounters throughout the month' },
        { value: 'Often', label: 'Often', desc: 'Frequent, regular weekly occurrences' },
        { value: 'Very Often', label: 'Very Often', desc: 'Continuous or daily repetitive hostility' }
      ]
    },
    {
      id: 'activityType',
      title: 'What primary type of online harassment have you observed or experienced?',
      subtitle: 'Identify the category of hostile behavior encountered.',
      options: [
        { value: 'Offensive Comments & Trolling', label: 'Offensive Comments & Trolling', desc: 'Insulting messages, vulgar replies, or baiting' },
        { value: 'Body Shaming', label: 'Body Shaming', desc: 'Derogatory remarks targeting physical appearance' },
        { value: 'Hate Speech', label: 'Hate Speech', desc: 'Hostility directed toward identity, race, or beliefs' },
        { value: 'Threats & Intimidation', label: 'Threats & Intimidation', desc: 'Direct threats of harm, blackmail, or doxing' },
        { value: 'Fake Rumors / Impersonation', label: 'Fake Rumors / Impersonation', desc: 'Defamatory claims, fake profiles, or impersonation' },
        { value: 'None', label: 'None', desc: 'No hostile behavior encountered' }
      ]
    },
    {
      id: 'emotionalWellbeing',
      title: 'How significantly has online interaction affected your mental health & emotional well-being?',
      subtitle: 'Primary ML research target variable (Mental Health Impact).',
      options: [
        { value: 'Not at all', label: 'Not at all', desc: 'No negative psychological impact or emotional strain' },
        { value: 'Slightly', label: 'Slightly', desc: 'Minor, fleeting annoyance or brief irritation' },
        { value: 'Moderately', label: 'Moderately', desc: 'Noticeable stress, worry, or recurring digital fatigue' },
        { value: 'Severely', label: 'Severely', desc: 'Significant anxiety, continuous distress, or sleep disruption' }
      ]
    },
    {
      id: 'emotionalSymptom',
      title: 'Which psychological symptom has been most noticeable during online stress?',
      subtitle: 'Select the prominent psychological symptom experienced.',
      options: [
        { value: 'Minimal Impact', label: 'Minimal Impact', desc: 'No significant negative psychological symptoms' },
        { value: 'Stress', label: 'Stress', desc: 'Feeling overwhelmed, irritable, or tense' },
        { value: 'Anxiety', label: 'Anxiety', desc: 'Persistent apprehension, worry, or nervousness' },
        { value: 'Sleep Loss', label: 'Sleep Loss', desc: 'Disrupted sleep patterns or insomnia' },
        { value: 'Social Withdrawal', label: 'Social Withdrawal', desc: 'Hesitating to post, avoiding messages, or isolating' },
        { value: 'Anger & Frustration', label: 'Anger & Frustration', desc: 'Intense emotional agitation or resentment' }
      ]
    },
    {
      id: 'actionTaken',
      title: 'When encountering online hostility, what response do you typically take?',
      subtitle: 'Reported action or defensive measure adopted.',
      options: [
        { value: 'Blocked User', label: 'Blocked User', desc: 'Muted or blocked the offending profile' },
        { value: 'Reported Account', label: 'Reported Account', desc: 'Utilized platform in-app reporting tools' },
        { value: 'Told Friends/Family', label: 'Told Friends/Family', desc: 'Discussed the incident with trusted peers or mentors' },
        { value: 'Legal Complaint', label: 'Legal Complaint', desc: 'Filed complaint with cyber crime helpline (1930) / police' },
        { value: 'Did Not Report', label: 'Did Not Report', desc: 'Ignored or endured the behavior without formal reporting' }
      ]
    },
    {
      id: 'lawAwareness',
      title: 'How aware are you of statutory cyber crime laws and official helplines?',
      subtitle: 'Knowledge of IT Act provisions and National Cyber Crime Helpline (1930).',
      options: [
        { value: 'Not Aware', label: 'Not Aware', desc: 'Unfamiliar with cyber laws or official reporting channels' },
        { value: 'Slightly Aware', label: 'Slightly Aware', desc: 'Aware laws exist, but unsure of exact complaint steps' },
        { value: 'Moderately Aware', label: 'Moderately Aware', desc: 'Familiar with platform guidelines and helpline 1930' },
        { value: 'Very Aware', label: 'Very Aware', desc: 'Well-informed on legal provisions and evidence preservation' }
      ]
    },
    {
      id: 'privacySetting',
      title: 'Do you actively configure account privacy and maintain evidence hygiene?',
      subtitle: 'General privacy and security practices maintained on digital platforms.',
      options: [
        { value: 'Yes', label: 'Yes — High Privacy', desc: 'Private profiles, 2FA enabled, screenshots preserved with timestamps' },
        { value: 'Partially', label: 'Partially — Moderate', desc: 'Some accounts private, but rarely preserve systematic records' },
        { value: 'No', label: 'No — Public Profiles', desc: 'Public profiles with open messaging and no evidence logging' }
      ]
    }
  ];

  let currentIdx = $state(0);
  let answers = $state({});
  let isReviewing = $state(false);
  let isSubmitting = $state(false);
  let validationError = $state('');

  let currentQ = $derived(questions[currentIdx]);
  let selectedValue = $derived(answers[currentQ?.id] || '');
  let progressPct = $derived(Math.round(((currentIdx + 1) / questions.length) * 100));

  function selectOption(val) {
    answers[currentQ.id] = val;
    validationError = '';
  }

  function handleNext() {
    if (!selectedValue) {
      validationError = 'This question is required. Please select an option to continue.';
      return;
    }
    validationError = '';

    if (currentIdx < questions.length - 1) {
      currentIdx++;
    } else {
      // Transition to Review step before submission
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

  async function submitSurvey() {
    // Validate that all questions are answered
    for (let i = 0; i < questions.length; i++) {
      if (!answers[questions[i].id]) {
        currentIdx = i;
        isReviewing = false;
        validationError = `Question ${i + 1} is required before submission.`;
        return;
      }
    }

    isSubmitting = true;
    try {
      const res = await fetch('/api/survey/submit', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(answers)
      });

      const data = await res.json();
      if (res.ok && data.success) {
        appState.addToast('success', 'Assessment Recorded', 'Your responses have been saved to the database.');
        window.location.href = '/result';
      } else {
        validationError = data.error || 'Failed to record assessment. Please try again.';
        appState.addToast('danger', 'Submission Error', validationError);
      }
    } catch (err) {
      console.error('Survey submission error:', err);
      validationError = 'Network error. Please verify server connection.';
      appState.addToast('danger', 'Network Error', validationError);
    } finally {
      isSubmitting = false;
    }
  }
</script>

<div class="max-w-2xl mx-auto space-y-6 page-fade-in font-sans">
  
  {#if !isReviewing}
    <!-- Progress Indicator Card -->
    <div class="bg-white border border-[#F0D5DD] rounded-2xl p-5 shadow-xs space-y-3">
      <div class="flex items-center justify-between text-xs font-semibold">
        <span class="text-[#82476B]">Overall Assessment Progress</span>
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
            Question {currentIdx + 1} of {questions.length}
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
        <div class="p-3 rounded-xl bg-[#FAF7F8] border border-[#BD5579] text-[#601D49] text-xs font-medium flex items-center gap-2">
          <svg class="w-4 h-4 text-[#BD5579] shrink-0" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" d="M12 9v3.75m9-.75a9 9 0 11-18 0 9 9 0 0118 0zm-9 3.75h.008v.008H12v-.008z" />
          </svg>
          <span>{validationError}</span>
        </div>
      {/if}

      <!-- Options List -->
      <div class="space-y-2.5">
        {#each currentQ.options as opt}
          <button
            type="button"
            onclick={() => selectOption(opt.value)}
            class="w-full p-4 rounded-xl border text-left transition-all cursor-pointer flex items-start gap-3.5
              {selectedValue === opt.value
                ? 'bg-[#FFEBB8]/40 border-[#BD5579] ring-1 ring-[#BD5579] shadow-xs'
                : 'bg-white border-[#F0D5DD] hover:border-[#EA9D9D] hover:bg-[#FAF7F8]'}"
          >
            <!-- Radio Indicator -->
            <div class="mt-0.5 w-4 h-4 rounded-full border flex items-center justify-center shrink-0
              {selectedValue === opt.value
                ? 'border-[#BD5579] bg-[#BD5579]'
                : 'border-[#EA9D9D] bg-white'}">
              {#if selectedValue === opt.value}
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
          Step 2: Review Before Final Submission
        </span>
        <h2 class="text-lg font-bold text-[#601D49]">Review Your Survey Responses</h2>
        <p class="text-xs text-[#82476B]">
          Please review your selections. You may edit any question before submitting your response to the research database.
        </p>
      </div>

      {#if validationError}
        <div class="p-3 rounded-xl bg-[#FAF7F8] border border-[#BD5579] text-[#601D49] text-xs font-medium">
          {validationError}
        </div>
      {/if}

      <!-- Questions Review Grid -->
      <div class="space-y-3 max-h-96 overflow-y-auto pr-1">
        {#each questions as q, idx}
          <div class="p-3.5 rounded-xl bg-[#FAF7F8] border border-[#F0D5DD] flex items-center justify-between gap-3">
            <div class="min-w-0 flex-1 space-y-0.5">
              <span class="text-[11px] font-semibold text-[#82476B]">Q{idx + 1}: {q.title}</span>
              <p class="text-xs font-bold text-[#601D49] truncate">
                Answer: <span class="text-[#BD5579]">{answers[q.id] || 'Not answered'}</span>
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
          onclick={submitSurvey}
          class="px-6 py-2.5 text-xs font-bold"
        >
          {#if isSubmitting}
            <span class="w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin"></span>
            <span>Recording Survey...</span>
          {:else}
            <span>Submit Assessment</span>
            <svg class="w-4 h-4" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" d="M4.5 12.75l6 6 9-13.5" />
            </svg>
          {/if}
        </Button>
      </div>

    </Card>
  {/if}

</div>
