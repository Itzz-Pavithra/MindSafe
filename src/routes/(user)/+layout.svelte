<script>
  import UserSidebar from '$lib/components/UserSidebar.svelte';
  import TopNavbar from '$lib/components/TopNavbar.svelte';
  import { appState } from '$lib/state/appState.svelte.js';

  let { data, children } = $props();

  $effect(() => {
    if (data?.user) {
      appState.setUser(data.user);
    }
  });

  let mobileOpen = $state(false);

  function toggleMobile() {
    mobileOpen = !mobileOpen;
  }

  function closeMobile() {
    mobileOpen = false;
  }
</script>

<div class="flex h-screen bg-[#FAF7F8] overflow-hidden font-sans text-[#601D49]">
  <!-- Survey User Sidebar Navigation -->
  <UserSidebar {mobileOpen} {closeMobile} />

  <!-- Main Content Canvas -->
  <div class="flex-1 flex flex-col min-w-0 overflow-hidden bg-[#FAF7F8]">
    <TopNavbar {toggleMobile} title="Survey Assessment Workspace" />

    <main class="flex-1 overflow-y-auto p-4 sm:p-6 lg:p-8 bg-[#FAF7F8]">
      {@render children()}
    </main>
  </div>
</div>
