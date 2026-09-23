<script>
  import Logo from '$lib/components/Logo.svelte';
  import Button from '$lib/components/Button.svelte';
  import Card from '$lib/components/Card.svelte';
  import { appState } from '$lib/state/appState.svelte.js';

  let email = $state('');
  let password = $state('');
  let isSubmitting = $state(false);
  let errorMessage = $state('');

  async function handleAdminLogin(e) {
    e.preventDefault();
    isSubmitting = true;
    errorMessage = '';

    try {
      const res = await fetch('/api/auth/admin-login', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ email, password })
      });

      const data = await res.json();

      if (res.ok && data.success) {
        appState.setUser(data.user);
        appState.addToast('success', 'Admin Session Initialized', 'Welcome to the Research Administration Workspace.');
        window.location.href = '/admin';
      } else {
        errorMessage = data.error || 'Invalid administrator credentials. Access restricted.';
      }
    } catch (err) {
      console.error('Admin login error:', err);
      errorMessage = 'Network or server error. Please check MongoDB service status.';
    } finally {
      isSubmitting = false;
    }
  }
</script>

<div class="min-h-screen bg-[#FAF7F8] flex flex-col justify-center items-center px-4 py-12 font-sans text-[#601D49]">
  <div class="w-full max-w-sm space-y-6">
    
    <!-- Branding Header -->
    <div class="text-center space-y-2 flex flex-col items-center">
      <Logo size="lg" />
      <div class="inline-flex items-center gap-1.5 px-3 py-1 rounded-full bg-[#FFEBB8] border border-[#EA9D9D]/70 text-[#601D49] text-xs font-semibold mt-2 shadow-xs">
        <svg class="w-3.5 h-3.5 text-[#BD5579]" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" d="M16.5 10.5V6.75a4.5 4.5 0 10-9 0v3.75m-.75 11.25h10.5a2.25 2.25 0 002.25-2.25v-6.75a2.25 2.25 0 00-2.25-2.25H6.75a2.25 2.25 0 00-2.25 2.25v6.75a2.25 2.25 0 002.25 2.25z" />
        </svg>
        <span>Protected Administrative Portal</span>
      </div>
    </div>

    <!-- Login Container Card -->
    <Card class="p-6 sm:p-7 space-y-5 bg-white border border-[#F0D5DD] shadow-sm">
      <div class="border-b border-[#F0D5DD] pb-3">
        <h2 class="text-base font-bold text-[#601D49]">Lead Researcher / Admin Access</h2>
        <p class="text-xs text-[#82476B] mt-0.5">Secure authentication for survey administration & analytics</p>
      </div>

      {#if errorMessage}
        <div class="p-3 rounded-xl bg-[#FAF7F8] border border-[#BD5579] text-[#601D49] text-xs font-semibold flex items-center gap-2">
          <svg class="w-4 h-4 text-[#BD5579] shrink-0" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" d="M12 9v3.75m9-.75a9 9 0 11-18 0 9 9 0 0118 0zm-9 3.75h.008v.008H12v-.008z" />
          </svg>
          <span>{errorMessage}</span>
        </div>
      {/if}

      <form onsubmit={handleAdminLogin} class="space-y-4">
        <!-- Admin Email Field -->
        <div class="space-y-1.5">
          <label for="admin-email" class="label-text block">
            Admin Email Address
          </label>
          <div class="relative">
            <div class="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none text-[#82476B]">
              <svg class="w-4 h-4" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" d="M15.75 6a3.75 3.75 0 11-7.5 0 3.75 3.75 0 017.5 0zM4.501 20.118a7.5 7.5 0 0114.998 0A17.933 17.933 0 0112 21.75c-2.676 0-5.216-.584-7.499-1.632z" />
              </svg>
            </div>
            <input 
              type="email" 
              id="admin-email"
              bind:value={email}
              required
              placeholder="admin@mindsafe.org"
              class="w-full pl-9 pr-3 py-2.5 rounded-xl bg-[#FAF7F8] border border-[#EA9D9D]/60 text-xs text-[#601D49] placeholder-[#82476B]/60 focus:outline-none focus:border-[#BD5579] font-medium"
            />
          </div>
        </div>

        <!-- Admin Password Field -->
        <div class="space-y-1.5">
          <label for="admin-password" class="label-text block">
            Admin Password
          </label>
          <div class="relative">
            <div class="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none text-[#82476B]">
              <svg class="w-4 h-4" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" d="M16.5 10.5V6.75a4.5 4.5 0 10-9 0v3.75m-.75 11.25h10.5a2.25 2.25 0 002.25-2.25v-6.75a2.25 2.25 0 00-2.25-2.25H6.75a2.25 2.25 0 00-2.25 2.25v6.75a2.25 2.25 0 002.25 2.25z" />
              </svg>
            </div>
            <input 
              type="password" 
              id="admin-password"
              bind:value={password}
              required
              placeholder="••••••••"
              class="w-full pl-9 pr-3 py-2.5 rounded-xl bg-[#FAF7F8] border border-[#EA9D9D]/60 text-xs text-[#601D49] placeholder-[#82476B]/60 focus:outline-none focus:border-[#BD5579] font-medium"
            />
          </div>
        </div>

        <!-- Authenticate Admin Button -->
        <Button 
          type="submit" 
          disabled={isSubmitting} 
          variant="dark" 
          class="w-full py-2.5 text-xs font-semibold"
        >
          {#if isSubmitting}
            <span class="w-3.5 h-3.5 border-2 border-white border-t-transparent rounded-full animate-spin"></span>
            <span>Verifying Admin Credentials...</span>
          {:else}
            <svg class="w-4 h-4" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" d="M9 12.75L11.25 15 15 9.75m-3-7.036A11.959 11.959 0 013.598 6 11.99 11.99 0 003 9.749c0 5.592 3.824 10.29 9 11.623 5.176-1.332 9-6.03 9-11.622 0-1.31-.21-2.571-.598-3.751A11.959 11.959 0 0112 2.714z" />
            </svg>
            <span>Admin Sign In</span>
          {/if}
        </Button>
      </form>
    </Card>

  </div>
</div>
