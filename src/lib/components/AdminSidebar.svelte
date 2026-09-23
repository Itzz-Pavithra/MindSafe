<script>
  import { page } from '$app/state';
  import Logo from './Logo.svelte';
  import { appState } from '$lib/state/appState.svelte.js';

  let { mobileOpen = false, closeMobile } = $props();

  const navItems = [
    {
      href: '/admin',
      label: 'Dashboard',
      icon: 'M3.75 6A2.25 2.25 0 016 3.75h2.25A2.25 2.25 0 0110.5 6v2.25a2.25 2.25 0 01-2.25 2.25H6a2.25 2.25 0 01-2.25-2.25V6zM3.75 15.75A2.25 2.25 0 016 13.5h2.25a2.25 2.25 0 012.25 2.25V18a2.25 2.25 0 01-2.25 2.25H6A2.25 2.25 0 013.75 18v-2.25zM13.5 6a2.25 2.25 0 012.25-2.25H18A2.25 2.25 0 0120.25 6v2.25A2.25 2.25 0 0118 10.5h-2.25a2.25 2.25 0 01-2.25-2.25V6zM13.5 15.75a2.25 2.25 0 012.25-2.25H18a2.25 2.25 0 012.25 2.25V18A2.25 2.25 0 0118 20.25h-2.25A2.25 2.25 0 0113.5 18v-2.25z'
    },
    {
      href: '/admin/statistics',
      label: 'Survey Statistics',
      icon: 'M3 13.125C3 12.504 3.504 12 4.125 12h2.25c.621 0 1.125.504 1.125 1.125v6.75C7.5 20.496 6.996 21 6.375 21h-2.25A1.125 1.125 0 013 19.875v-6.75zM9.75 8.625c0-.621.504-1.125 1.125-1.125h2.25c.621 0 1.125.504 1.125 1.125v11.25c0 .621-.504 1.125-1.125 1.125h-2.25a1.125 1.125 0 01-1.125-1.125V8.625zM16.5 4.125c0-.621.504-1.125 1.125-1.125h2.25C20.496 3 21 3.504 21 4.125v15.75c0 .621-.504 1.125-1.125 1.125h-2.25a1.125 1.125 0 01-1.125-1.125V4.125z'
    },
    {
      href: '/admin/mental-health',
      label: 'Mental Health Analysis',
      icon: 'M21 8.25c0-2.485-2.099-4.5-4.688-4.5-1.935 0-3.597 1.126-4.312 2.733-.715-1.607-2.377-2.733-4.313-2.733C5.1 3.75 3 5.765 3 8.25c0 7.22 9 12 9 12s9-4.78 9-12z'
    },
    {
      href: '/admin/relationships',
      label: 'Relationship Analysis',
      icon: 'M7.5 14.25v2.25m3-4.5v4.5m3-6.75v6.75m3-9v9M6 20.25h12A2.25 2.25 0 0020.25 18V6A2.25 2.25 0 0018 3.75H6A2.25 2.25 0 003.75 6v12A2.25 2.25 0 006 20.25z'
    },
    {
      href: '/admin/statistical-analysis',
      label: 'Statistical Analysis',
      icon: 'M12 6v12m-3-2.818l.879.659c1.171.879 3.07.879 4.242 0 1.172-.879 1.172-2.303 0-3.182C13.536 12.219 12.768 12 12 12c-.725 0-1.45-.22-2.003-.659-1.106-.879-1.106-2.303 0-3.182s2.9-.879 4.006 0l.415.33M21 12a9 9 0 11-18 0 9 9 0 0118 0z'
    },
    {
      href: '/admin/findings',
      label: 'Key Findings',
      icon: 'M12 18v-5.25m0 0a6.01 6.01 0 001.5-.189m-1.5.189a6.01 6.01 0 01-1.5-.189m3.75 7.478a12.06 12.06 0 01-4.5 0m3.75 2.383a14.406 14.406 0 01-3 0M14.25 18v-.192c0-.983.658-1.823 1.508-2.316a7.5 7.5 0 10-7.516 0c.85.493 1.509 1.333 1.509 2.316V18'
    }
  ];

  function isActive(href) {
    if (href === '/admin') {
      return page.url.pathname === '/admin';
    }
    return page.url.pathname.startsWith(href);
  }

  async function handleLogout() {
    await appState.logout(true);
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

  <!-- Role Badge -->
  <div class="px-5 pt-3.5 pb-2 flex items-center justify-between">
    <span class="text-[10px] font-bold text-[#EA9D9D] uppercase tracking-widest">
      Research Administration
    </span>
    <span class="px-2 py-0.5 rounded text-[10px] font-semibold bg-[#BD5579]/40 text-[#FFEBB8] border border-[#BD5579]/50">
      Admin
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

    <!-- Logout Action -->
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
        A
      </div>
      <div class="min-w-0 flex-1">
        <span class="text-xs font-bold text-white block truncate leading-tight">
          Lead Researcher
        </span>
        <span class="text-[10px] text-[#EA9D9D] block truncate">
          admin@mindsafe.org
        </span>
      </div>
    </div>
  </div>
</aside>
