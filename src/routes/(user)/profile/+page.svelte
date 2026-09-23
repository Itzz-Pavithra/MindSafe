<script>
  import { onMount } from 'svelte';
  import Card from '$lib/components/Card.svelte';
  import Button from '$lib/components/Button.svelte';
  import { appState } from '$lib/state/appState.svelte.js';

  let hasResponse = $state(false);
  let submittedAt = $state(null);
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
</script>

<div class="max-w-3xl mx-auto space-y-6 page-fade-in font-sans">
  
  <div class="space-y-1">
    <h1 class="page-title text-2xl text-[#601D49]">Participant Profile</h1>
    <p class="text-xs text-[#82476B]">Manage your account details and view survey submission records</p>
  </div>

  <!-- Profile Details Card -->
  <Card class="p-6 sm:p-8 space-y-6 bg-white border border-[#F0D5DD]">
    <div class="flex items-center gap-4 border-b border-[#F0D5DD] pb-5">
      <div class="w-14 h-14 rounded-2xl bg-[#BD5579] text-white flex items-center justify-center font-bold text-xl shadow-xs">
        {appState.user?.name ? appState.user.name.charAt(0).toUpperCase() : 'U'}
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
        <p class="text-xs font-bold text-[#601D49]">{appState.role === 'admin' ? 'Administrator' : 'Survey User'}</p>
      </div>

      <div class="p-4 rounded-xl bg-[#FAF7F8] border border-[#F0D5DD] space-y-1">
        <span class="text-[11px] font-semibold text-[#82476B]">Assessment Status</span>
        <p class="text-xs font-bold {hasResponse ? 'text-[#BD5579]' : 'text-[#82476B]'}">
          {hasResponse ? 'Completed & Recorded' : 'Not yet submitted'}
        </p>
      </div>

      <div class="p-4 rounded-xl bg-[#FAF7F8] border border-[#F0D5DD] space-y-1">
        <span class="text-[11px] font-semibold text-[#82476B]">Submission Timestamp</span>
        <p class="text-xs font-bold text-[#601D49]">
          {hasResponse && submittedAt ? new Date(submittedAt).toLocaleString() : 'Pending completion'}
        </p>
      </div>
    </div>

    <!-- Actions -->
    <div class="flex items-center justify-between pt-4 border-t border-[#F0D5DD]">
      <a href="/assessment">
        <Button variant="primary" class="px-5 py-2.5 text-xs font-semibold">
          <span>{hasResponse ? 'Retake Assessment' : 'Start Assessment'}</span>
          <svg class="w-3.5 h-3.5" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" d="M13.5 4.5L21 12m0 0l-7.5 7.5M21 12H3" />
          </svg>
        </Button>
      </a>

      <Button variant="outline" onclick={handleLogout} class="px-4 py-2.5 text-xs font-semibold text-[#601D49]">
        <span>Sign Out</span>
      </Button>
    </div>
  </Card>

</div>
