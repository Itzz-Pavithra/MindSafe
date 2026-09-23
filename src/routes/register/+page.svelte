<script>
  import Logo from '$lib/components/Logo.svelte';
  import Button from '$lib/components/Button.svelte';
  import Card from '$lib/components/Card.svelte';
  import { appState } from '$lib/state/appState.svelte.js';

  let fullName = $state('');
  let email = $state('');
  let password = $state('');
  let confirmPassword = $state('');
  let errorMessage = $state('');
  let isSubmitting = $state(false);

  async function handleRegister(e) {
    e.preventDefault();
    errorMessage = '';

    if (!fullName.trim()) {
      errorMessage = 'Please enter your full name.';
      return;
    }
    if (!email.trim() || !email.includes('@')) {
      errorMessage = 'Please enter a valid email address.';
      return;
    }
    if (password.length < 6) {
      errorMessage = 'Password must be at least 6 characters.';
      return;
    }
    if (password !== confirmPassword) {
      errorMessage = 'Passwords do not match.';
      return;
    }

    isSubmitting = true;

    try {
      const res = await fetch('/api/auth/register', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          name: fullName.trim(),
          email: email.trim(),
          password
        })
      });

      const data = await res.json();

      if (res.ok && data.success) {
        appState.setUser(data.user);
        appState.addToast('success', 'Account Registered', `Welcome, ${data.user.name}!`);
        window.location.href = '/dashboard';
      } else {
        errorMessage = data.error || 'Registration failed. Please try again.';
      }
    } catch (err) {
      console.error('Registration error:', err);
      errorMessage = 'Network error. Please ensure server and database are operational.';
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
        Register to access the survey assessment workspace.
      </p>
    </div>

    <!-- Registration Card -->
    <Card class="bg-white border border-[#F0D5DD] shadow-sm p-6 sm:p-7 space-y-5">
      <div class="border-b border-[#F0D5DD] pb-3">
        <h2 class="text-base font-bold text-[#601D49]">Create Participant Account</h2>
        <p class="text-xs text-[#82476B] mt-0.5">Participate in academic cyberbullying & mental health survey</p>
      </div>

      {#if errorMessage}
        <div class="p-3 bg-[#FAF7F8] border border-[#BD5579] text-[#601D49] text-xs font-semibold rounded-xl flex items-center gap-2">
          <svg class="w-4 h-4 text-[#BD5579] shrink-0" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" d="M12 9v3.75m9-.75a9 9 0 11-18 0 9 9 0 0118 0zm-9 3.75h.008v.008H12v-.008z" />
          </svg>
          <span>{errorMessage}</span>
        </div>
      {/if}

      <form onsubmit={handleRegister} class="space-y-3.5">
        <div class="space-y-1">
          <label for="reg-name" class="label-text block">
            Full Name
          </label>
          <input 
            type="text" 
            id="reg-name"
            bind:value={fullName}
            required
            placeholder="e.g. Sarah Jenkins"
            class="w-full px-3 py-2.5 rounded-xl bg-[#FAF7F8] border border-[#EA9D9D]/60 text-xs text-[#601D49] placeholder-[#82476B]/60 focus:outline-none focus:border-[#BD5579] font-medium"
          />
        </div>

        <div class="space-y-1">
          <label for="reg-email" class="label-text block">
            Email Address
          </label>
          <input 
            type="email" 
            id="reg-email"
            bind:value={email}
            required
            placeholder="sarah@university.edu"
            class="w-full px-3 py-2.5 rounded-xl bg-[#FAF7F8] border border-[#EA9D9D]/60 text-xs text-[#601D49] placeholder-[#82476B]/60 focus:outline-none focus:border-[#BD5579] font-medium"
          />
        </div>

        <div class="space-y-1">
          <label for="reg-password" class="label-text block">
            Password
          </label>
          <input 
            type="password" 
            id="reg-password"
            bind:value={password}
            required
            minlength="6"
            placeholder="••••••••"
            class="w-full px-3 py-2.5 rounded-xl bg-[#FAF7F8] border border-[#EA9D9D]/60 text-xs text-[#601D49] placeholder-[#82476B]/60 focus:outline-none focus:border-[#BD5579] font-medium"
          />
          <span class="text-[10px] text-[#82476B]">At least 6 characters</span>
        </div>

        <div class="space-y-1">
          <label for="reg-confirm" class="label-text block">
            Confirm Password
          </label>
          <input 
            type="password" 
            id="reg-confirm"
            bind:value={confirmPassword}
            required
            placeholder="••••••••"
            class="w-full px-3 py-2.5 rounded-xl bg-[#FAF7F8] border border-[#EA9D9D]/60 text-xs text-[#601D49] placeholder-[#82476B]/60 focus:outline-none focus:border-[#BD5579] font-medium"
          />
        </div>

        <Button 
          type="submit" 
          disabled={isSubmitting} 
          variant="primary" 
          class="w-full py-2.5 text-xs font-semibold mt-2"
        >
          {#if isSubmitting}
            <span class="w-3.5 h-3.5 border-2 border-white border-t-transparent rounded-full animate-spin"></span>
            <span>Creating Account...</span>
          {:else}
            <svg class="w-4 h-4" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" d="M19 7.5v3m0 0v3m0-3h3m-3 0h-3m-2.25-4.125a3.375 3.375 0 11-6.75 0 3.375 3.375 0 016.75 0zM4 19.235v-.11a6.375 6.375 0 0112.75 0v.109A12.318 12.318 0 0110.374 21c-2.331 0-4.512-.645-6.374-1.765z" />
            </svg>
            <span>Create Participant Account</span>
          {/if}
        </Button>
      </form>

      <div class="text-center pt-2 border-t border-[#F0D5DD]">
        <p class="text-xs text-[#82476B]">
          Already have an account? 
          <a href="/login" class="text-[#BD5579] font-semibold hover:underline">
            Sign In
          </a>
        </p>
      </div>
    </Card>

  </div>
</div>
