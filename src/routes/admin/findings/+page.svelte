<script>
  import { onMount } from 'svelte';
  import Card from '$lib/components/Card.svelte';
  import EmptyState from '$lib/components/EmptyState.svelte';

  let findingsData = $state(null);
  let isLoading = $state(true);
  let hasData = $derived(findingsData && findingsData.hasData && findingsData.findings?.length > 0);

  onMount(async () => {
    try {
      const res = await fetch('/api/admin/findings');
      if (res.ok) {
        findingsData = await res.json();
      }
    } catch (e) {
      console.error('Failed to load empirical findings:', e);
    } finally {
      isLoading = false;
    }
  });
</script>

<div class="max-w-5xl mx-auto space-y-6 page-fade-in font-sans">
  
  <div class="border-b border-[#F0D5DD] pb-4">
    <h1 class="page-title text-2xl text-[#601D49]">Key Empirical Findings</h1>
    <p class="text-xs text-[#82476B] mt-0.5">
      Synthesized observations derived from statistical distributions and cross-tabulation patterns
    </p>
  </div>

  {#if !hasData}
    <EmptyState 
      title="No Empirical Findings Available Yet"
      description="Research findings will be dynamically synthesized once the real survey dataset is ingested. The system does not invent or fabricate research conclusions."
      icon="database"
    />
  {:else}
    <!-- Dynamic Findings List from Real Data -->
    <div class="space-y-4">
      {#each findingsData.findings as finding}
        <Card class="p-6 space-y-2 border-l-4 border-l-[#BD5579]">
          <div class="flex items-center justify-between">
            <span class="px-2.5 py-0.5 rounded text-[10px] font-bold bg-[#FFEBB8] text-[#601D49] border border-[#EA9D9D]/60 uppercase tracking-wide">
              {finding.category}
            </span>
            <span class="text-[11px] text-[#82476B]">Verified Empirical Signal</span>
          </div>

          <h3 class="card-heading text-base">{finding.title}</h3>
          <p class="text-xs text-[#601D49] leading-relaxed">
            {finding.summary}
          </p>
        </Card>
      {/each}
    </div>
  {/if}

</div>
