<script>
  import Logo from '$lib/components/Logo.svelte';
  import Button from '$lib/components/Button.svelte';
  import Card from '$lib/components/Card.svelte';
  import { appState } from '$lib/state/appState.svelte.js';

  let email = $state('');
  let password = $state('');
  let isSubmitting = $state(false);
  let errorMessage = $state('');

  async function handleLogin(e) {
    e.preventDefault();
    isSubmitting = true;
    errorMessage = '';

    try {
      const res = await fetch('/api/auth/login', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ email, password })
      });

      const data = await res.json();

      if (res.ok && data.success) {
        appState.setUser(data.user);
        appState.addToast('success', 'Sign In Successful', `Welcome, ${data.user.name}!`);
        
        // Role-based redirection per specification
        if (data.user.role === 'admin') {
          window.location.href = '/admin';
        } else {
          window.location.href = '/dashboard';
        }
      } else {
        errorMessage = data.error || 'Invalid credentials. Please verify your email and password.';
      }
    } catch (err) {
      console.error('Login error:', err);
      errorMessage = 'Network error. Please verify server and database connectivity.';
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
      <p class="text-xs text-[#82476B] font-normal pt-1 max-w-xs leading-relaxed">
        Academic research platform analyzing cyberbullying patterns and self-reported mental health impact.
      </p>
    </div>

    <!-- Login Container Card -->
    <Card class="p-6 sm:p-7 space-y-5 bg-white border border-[#F0D5DD] shadow-sm">
      <div class="border-b border-[#F0D5DD] pb-3">
        <h2 class="text-base font-bold text-[#601D49]">Participant Sign In</h2>
        <p class="text-xs text-[#82476B] mt-0.5">Enter your participant credentials to access your assessment workspace</p>
      </div>

      {#if errorMessage}
        <div class="p-3 rounded-xl bg-[#FAF7F8] border border-[#BD5579] text-[#601D49] text-xs font-semibold flex items-center gap-2">
          <svg class="w-4 h-4 text-[#BD5579] shrink-0" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" d="M12 9v3.75m9-.75a9 9 0 11-18 0 9 9 0 0118 0zm-9 3.75h.008v.008H12v-.008z" />
          </svg>
          <span>{errorMessage}</span>
        </div>
      {/if}

      <form onsubmit={handleLogin} class="space-y-4">
        <!-- Email Field -->
        <div class="space-y-1.5">
          <label for="login-email" class="label-text block">
            Email Address
          </label>
          <div class="relative">
            <div class="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none text-[#82476B]">
              <svg class="w-4 h-4" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" d="M15.75 6a3.75 3.75 0 11-7.5 0 3.75 3.75 0 017.5 0zM4.501 20.118a7.5 7.5 0 0114.998 0A17.933 17.933 0 0112 21.75c-2.676 0-5.216-.584-7.499-1.632z" />
              </svg>
            </div>
            <input 
              type="email" 
              id="login-email"
              bind:value={email}
              required
              placeholder="name@example.com"
              class="w-full pl-9 pr-3 py-2.5 rounded-xl bg-[#FAF7F8] border border-[#EA9D9D]/60 text-xs text-[#601D49] placeholder-[#82476B]/60 focus:outline-none focus:border-[#BD5579] font-medium"
            />
          </div>
        </div>

        <!-- Password Field -->
        <div class="space-y-1.5">
          <label for="login-password" class="label-text block">
            Password
          </label>
          <div class="relative">
            <div class="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none text-[#82476B]">
              <svg class="w-4 h-4" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" d="M16.5 10.5V6.75a4.5 4.5 0 10-9 0v3.75m-.75 11.25h10.5a2.25 2.25 0 002.25-2.25v-6.75a2.25 2.25 0 00-2.25-2.25H6.75a2.25 2.25 0 00-2.25 2.25v6.75a2.25 2.25 0 002.25 2.25z" />
              </svg>
            </div>
            <input 
              type="password" 
              id="login-password"
              bind:value={password}
              required
              placeholder="••••••••"
              class="w-full pl-9 pr-3 py-2.5 rounded-xl bg-[#FAF7F8] border border-[#EA9D9D]/60 text-xs text-[#601D49] placeholder-[#82476B]/60 focus:outline-none focus:border-[#BD5579] font-medium"
            />
          </div>
        </div>

        <!-- Sign In Button -->
        <Button 
          type="submit" 
          disabled={isSubmitting} 
          variant="primary" 
          class="w-full py-2.5 text-xs font-semibold"
        >
          {#if isSubmitting}
            <span class="w-3.5 h-3.5 border-2 border-white border-t-transparent rounded-full animate-spin"></span>
            <span>Signing In...</span>
          {:else}
            <svg class="w-4 h-4" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" d="M15.75 9V5.25A2.25 2.25 0 0013.5 3h-6a2.25 2.25 0 00-2.25 2.25v13.5A2.25 2.25 0 007.5 21h6a2.25 2.25 0 002.25-2.25V15m3 0l3-3m0 0l-3-3m3 3H9" />
            </svg>
            <span>Sign In</span>
          {/if}
        </Button>
      </form>

      <!-- Registration link for survey users -->
      <div class="text-center pt-2 border-t border-[#F0D5DD]">
        <p class="text-xs text-[#82476B]">
          New participant? 
          <a href="/register" class="text-[#BD5579] font-semibold hover:underline">
            Register account
          </a>
        </p>
      </div>
    </Card>

    <!-- Subtle Administrative Access Link -->
    <div class="text-center pt-1">
      <a 
        href="/admin-login" 
        class="text-[11px] text-[#82476B]/70 hover:text-[#601D49] transition-colors inline-flex items-center gap-1.5 font-medium hover:underline"
      >
        <svg class="w-3.5 h-3.5 text-[#BD5579]/70" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" d="M16.5 10.5V6.75a4.5 4.5 0 10-9 0v3.75m-.75 11.25h10.5a2.25 2.25 0 002.25-2.25v-6.75a2.25 2.25 0 00-2.25-2.25H6.75a2.25 2.25 0 00-2.25 2.25v6.75a2.25 2.25 0 002.25 2.25z" />
        </svg>
        <span>Admin Login</span>
      </a>
    </div>

  </div>
</div>
