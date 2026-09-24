<script>
  import { onMount } from 'svelte';
  import Card from '$lib/components/Card.svelte';
  import Button from '$lib/components/Button.svelte';
  import { appState } from '$lib/state/appState.svelte.js';

  let hasResponse = $state(false);
  let submittedAt = $state(null);
  let history = $state([]);
  let isLoading = $state(true);

  onMount(async () => {
    try {
      const res = await fetch('/api/survey/my-response');
      if (res.ok) {
        const data = await res.json();
        if (data.success && data.hasResponse) {
          hasResponse = true;
          submittedAt = data.response.submittedAt;
        }
        if (data.history && Array.isArray(data.history)) {
          history = data.history;
        }
      }
    } catch (e) {
      console.error('Failed to load profile assessment history:', e);
    } finally {
      isLoading = false;
    }
  });

  async function handleLogout() {
    await appState.logout();
  }

  function getBadgeClass(cls) {
    switch (cls) {
      case 'Not at all':
        return 'bg-[#EBF7EE] text-[#22543D] border-[#48BB78]/40';
      case 'Slightly':
        return 'bg-[#FFFBEB] text-[#744210] border-[#F6E05E]/40';
      case 'Moderately':
        return 'bg-[#FFEBB8] text-[#601D49] border-[#BD5579]/40';
      case 'Severely':
        return 'bg-[#FFF5F5] text-[#742A2A] border-[#E53E3E]/40';
      default:
        return 'bg-[#FAF7F8] text-[#601D49] border-[#F0D5DD]';
    }
  }
</script>

<svelte:head>
  <title>Participant Profile • MindSafe</title>
</svelte:head>

<div class="max-w-4xl mx-auto space-y-6 page-fade-in font-sans">
  
  <div class="space-y-1">
    <h1 class="page-title text-2xl text-[#601D49]">Participant Profile & Assessment History</h1>
    <p class="text-xs text-[#82476B]">Manage your account details and view documented ML assessment classifications</p>
  </div>

  <!-- Profile Details Card -->
  <Card class="p-6 sm:p-8 space-y-6 bg-white border border-[#F0D5DD]">
    <div class="flex items-center gap-4 border-b border-[#F0D5DD] pb-5">
      <div class="w-14 h-14 rounded-2xl bg-[#BD5579] text-white flex items-center justify-center font-bold text-xl shadow-xs">
        {appState.user?.name ? appState.user.name.charAt(0).toUpperCase() : 'P'}
      </div>
      <div>
        <h2 class="text-lg font-bold text-[#601D49]">{appState.user?.name || 'Survey Participant'}</h2>
        <span class="inline-block px-2.5 py-0.5 rounded text-[10px] font-semibold bg-[#FFEBB8] text-[#601D49] border border-[#EA9D9D]/60 mt-1">
          {appState.user?.roleLabel || 'Survey Respondent'}
        </span>
      </div>
    </div>

    <!-- Account Details Grid -->
    <div class="grid grid-cols-1 sm:grid-cols-2 gap-4">
      <div class="p-4 rounded-xl bg-[#FAF7F8] border border-[#F0D5DD] space-y-1">
        <span class="text-[11px] font-semibold text-[#82476B]">Registered Email</span>
        <p class="text-xs font-bold text-[#601D49]">{appState.user?.email || 'N/A'}</p>
      </div>

      <div class="p-4 rounded-xl bg-[#FAF7F8] border border-[#F0D5DD] space-y-1">
        <span class="text-[11px] font-semibold text-[#82476B]">Account Role</span>
        <p class="text-xs font-bold text-[#601D49]">Survey Participant</p>
      </div>

      <div class="p-4 rounded-xl bg-[#FAF7F8] border border-[#F0D5DD] space-y-1">
        <span class="text-[11px] font-semibold text-[#82476B]">Assessment Status</span>
        <p class="text-xs font-bold {hasResponse ? 'text-[#BD5579]' : 'text-[#82476B]'}">
          {hasResponse ? 'Completed & Recorded' : 'Not yet submitted'}
        </p>
      </div>

      <div class="p-4 rounded-xl bg-[#FAF7F8] border border-[#F0D5DD] space-y-1">
        <span class="text-[11px] font-semibold text-[#82476B]">Latest Submission Date</span>
        <p class="text-xs font-bold text-[#601D49]">
          {hasResponse && submittedAt ? new Date(submittedAt).toLocaleString() : 'Pending completion'}
        </p>
      </div>
    </div>

    <!-- Actions -->
    <div class="flex items-center justify-between pt-4 border-t border-[#F0D5DD]">
      <div class="flex items-center gap-3">
        <a href="/assessment">
          <Button variant="primary" class="px-5 py-2.5 text-xs font-semibold">
            <span>{hasResponse ? 'Retake Assessment' : 'Start Assessment'}</span>
            <svg class="w-3.5 h-3.5" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" d="M13.5 4.5L21 12m0 0l-7.5 7.5M21 12H3" />
            </svg>
          </Button>
        </a>

        {#if hasResponse}
          <a href="/result">
            <Button variant="outline" class="px-4 py-2.5 text-xs font-semibold text-[#601D49]">
              <span>View Latest Result</span>
            </Button>
          </a>
        {/if}
      </div>

      <Button variant="outline" onclick={handleLogout} class="px-4 py-2.5 text-xs font-semibold text-[#601D49]">
        <span>Sign Out</span>
      </Button>
    </div>
  </Card>

  <!-- Assessment & ML Prediction History Card -->
  <Card class="p-6 sm:p-8 space-y-5 bg-white border border-[#F0D5DD]">
    <div class="border-b border-[#F0D5DD] pb-4 flex items-center justify-between">
      <div>
        <span class="text-[11px] font-bold uppercase tracking-wider text-[#BD5579]">
          Recorded Assessment Submissions
        </span>
        <h2 class="text-base sm:text-lg font-bold text-[#601D49]">Assessment & ML Prediction History</h2>
      </div>
      <span class="text-xs text-[#82476B] font-semibold">
        {history.length} {history.length === 1 ? 'Record' : 'Records'}
      </span>
    </div>

    {#if isLoading}
      <div class="p-8 text-center text-xs text-[#82476B]">
        Loading assessment history...
      </div>
    {:else if history.length === 0}
      <div class="p-8 text-center rounded-xl bg-[#FAF7F8] border border-[#F0D5DD] space-y-2">
        <p class="text-xs font-semibold text-[#601D49]">No assessment records found.</p>
        <p class="text-xs text-[#82476B]">Complete the research questionnaire to generate your first ML outcome classification.</p>
      </div>
    {:else}
      <div class="overflow-x-auto">
        <table class="w-full text-left text-xs">
          <thead>
            <tr class="border-b border-[#F0D5DD] text-[#82476B] uppercase font-bold text-[10px]">
              <th class="py-3 px-3">Assessment Date</th>
              <th class="py-3 px-3">Predicted Mental Health Impact</th>
              <th class="py-3 px-3">Model Version</th>
              <th class="py-3 px-3 text-right">Action</th>
            </tr>
          </thead>
          <tbody class="divide-y divide-[#F0D5DD]">
            {#each history as rec}
              <tr class="hover:bg-[#FAF7F8] transition-colors">
                <td class="py-3.5 px-3 font-semibold text-[#601D49]">
                  {new Date(rec.createdAt).toLocaleDateString()} at {new Date(rec.createdAt).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
                </td>
                <td class="py-3.5 px-3">
                  <span class="inline-block px-2.5 py-0.5 rounded-full font-bold border text-[11px] {getBadgeClass(rec.classification)}">
                    {rec.classification || 'Evaluating'}
                  </span>
                </td>
                <td class="py-3.5 px-3 text-[#82476B] font-mono text-[11px]">
                  {rec.modelVersion || 'MindSafe Primary RF (Scenario B)'}
                </td>
                <td class="py-3.5 px-3 text-right">
                  <a href="/result" class="text-xs font-bold text-[#BD5579] hover:underline">
                    View Explanation →
                  </a>
                </td>
              </tr>
            {/each}
          </tbody>
        </table>
      </div>
    {/if}
  </Card>

</div>
