<script>
  import { page } from '$app/state';
  import Logo from './Logo.svelte';
  import { appState } from '$lib/state/appState.svelte.js';

  let { mobileOpen = false, closeMobile } = $props();

  const navItems = [
    {
      href: '/dashboard',
      label: 'Dashboard',
      icon: 'M3.75 6A2.25 2.25 0 016 3.75h2.25A2.25 2.25 0 0110.5 6v2.25a2.25 2.25 0 01-2.25 2.25H6a2.25 2.25 0 01-2.25-2.25V6zM3.75 15.75A2.25 2.25 0 016 13.5h2.25a2.25 2.25 0 012.25 2.25V18a2.25 2.25 0 01-2.25 2.25H6A2.25 2.25 0 013.75 18v-2.25zM13.5 6a2.25 2.25 0 012.25-2.25H18A2.25 2.25 0 0120.25 6v2.25A2.25 2.25 0 0118 10.5h-2.25a2.25 2.25 0 01-2.25-2.25V6zM13.5 15.75a2.25 2.25 0 012.25-2.25H18a2.25 2.25 0 012.25 2.25V18A2.25 2.25 0 0118 20.25h-2.25A2.25 2.25 0 0113.5 18v-2.25z'
    },
    {
      href: '/assessment',
      label: 'Mental Health Assessment',
      icon: 'M9 12h3.75M9 15h3.75M9 18h3.75m3 .75H18a2.25 2.25 0 002.25-2.25V6.108c0-1.135-.845-2.098-1.976-2.192a48.424 48.424 0 00-1.123-.08m-5.801 0c-.065.21-.1.433-.1.664 0 .414.336.75.75.75h4.5a.75.75 0 00.75-.75 2.25 2.25 0 00-.1-.664m-5.8 0A2.251 2.251 0 0113.5 2.25H15c1.012 0 1.867.668 2.15 1.586m-5.8 0c-.376.023-.75.05-1.124.08C9.095 4.01 8.25 4.973 8.25 6.108V8.25m0 0H4.875c-.621 0-1.125.504-1.125 1.125v11.25c0 .621.504 1.125 1.125 1.125h9.75c.621 0 1.125-.504 1.125-1.125V9.375c0-.621-.504-1.125-1.125-1.125H8.25zM6.75 12h.008v.008H6.75V12zm0 3h.008v.008H6.75V15zm0 3h.008v.008H6.75V18z'
    },
    {
      href: '/result',
      label: 'My Result',
      icon: 'M21 8.25c0-2.485-2.099-4.5-4.688-4.5-1.935 0-3.597 1.126-4.312 2.733-.715-1.607-2.377-2.733-4.313-2.733C5.1 3.75 3 5.765 3 8.25c0 7.22 9 12 9 12s9-4.78 9-12z'
    },
    {
      href: '/profile',
      label: 'Profile',
      icon: 'M15.75 6a3.75 3.75 0 11-7.5 0 3.75 3.75 0 017.5 0zM4.501 20.118a7.5 7.5 0 0114.998 0A17.933 17.933 0 0112 21.75c-2.676 0-5.216-.584-7.499-1.632z'
    }
  ];

  function isActive(href) {
    if (href === '/dashboard') {
      return page.url.pathname === '/dashboard';
    }
    return page.url.pathname.startsWith(href);
  }

  async function handleLogout() {
    await appState.logout();
  }
</script>

<aside 
  class="fixed lg:static top-0 left-0 bottom-0 z-40 w-64 bg-[#601D49] text-white flex flex-col transition-transform duration-200 border-r border-[#601D49] shadow-lg lg:shadow-none
    {mobileOpen ? 'translate-x-0' : '-translate-x-full lg:translate-x-0'}"
>
  <!-- Sidebar Header -->
  <div class="p-4 border-b border-[#BD5579]/30 flex items-center justify-between">
    <Logo size="sm" dark={true} />
    {#if closeMobile}
      <button 
        onclick={closeMobile} 
        class="lg:hidden p-1.5 rounded-lg text-[#EA9D9D] hover:text-white hover:bg-[#BD5579]/30 cursor-pointer" 
        aria-label="Close navigation"
      >
        <svg class="w-5 h-5" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" d="M6 18L18 6M6 6l12 12" />
        </svg>
      </button>
    {/if}
  </div>

  <!-- Role Indicator -->
  <div class="px-5 pt-3.5 pb-2 flex items-center justify-between">
    <span class="text-[10px] font-bold text-[#EA9D9D] uppercase tracking-widest">
      Survey Workspace
    </span>
    <span class="px-2 py-0.5 rounded text-[10px] font-semibold bg-[#BD5579]/40 text-[#FFEBB8] border border-[#BD5579]/50">
      Respondent
    </span>
  </div>

  <!-- Navigation Links -->
  <nav class="flex-1 px-3 py-2 space-y-1 overflow-y-auto">
    {#each navItems as item}
      <a 
        href={item.href}
        onclick={() => { if (closeMobile) closeMobile(); }}
        class="w-full flex items-center gap-3 px-3 py-2.5 rounded-xl text-xs font-medium transition-all duration-150 text-left
          {isActive(item.href) 
            ? 'bg-[#BD5579] text-white font-bold shadow-xs' 
            : 'text-[#EA9D9D] hover:bg-[#BD5579]/20 hover:text-white'}"
      >
        <svg class="w-4 h-4 shrink-0 {isActive(item.href) ? 'text-white' : 'text-[#EA9D9D]'}" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" d={item.icon} />
        </svg>
        <span>{item.label}</span>
      </a>
    {/each}

    <div class="pt-3 pb-1">
      <div class="h-px bg-[#BD5579]/20"></div>
    </div>

    <!-- Logout Item -->
    <button 
      onclick={handleLogout}
      class="w-full flex items-center gap-3 px-3 py-2.5 rounded-xl text-xs font-medium text-[#FFEBB8] hover:bg-[#BD5579]/30 transition-colors text-left cursor-pointer"
    >
      <svg class="w-4 h-4 shrink-0 text-[#FFEBB8]" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24">
        <path stroke-linecap="round" stroke-linejoin="round" d="M15.75 9V5.25A2.25 2.25 0 0013.5 3h-6a2.25 2.25 0 00-2.25 2.25v13.5A2.25 2.25 0 007.5 21h6a2.25 2.25 0 002.25-2.25V15M12 9l-3 3m0 0l3 3m-3-3h12.75" />
      </svg>
      <span>Logout</span>
    </button>
  </nav>

  <!-- User Profile Badge -->
  <div class="p-3.5 border-t border-[#BD5579]/30 bg-[#4D1439]/50">
    <div class="flex items-center gap-2.5">
      <div class="w-7 h-7 rounded-full bg-[#BD5579] text-white flex items-center justify-center font-bold text-xs shrink-0">
        {appState.user?.name ? appState.user.name.charAt(0).toUpperCase() : 'U'}
      </div>
      <div class="min-w-0 flex-1">
        <span class="text-xs font-bold text-white block truncate leading-tight">
          {appState.user?.name || 'Participant'}
        </span>
        <span class="text-[10px] text-[#EA9D9D] block truncate">
          {appState.user?.email || 'survey@mindsafe.org'}
        </span>
      </div>
    </div>
  </div>
</aside>
