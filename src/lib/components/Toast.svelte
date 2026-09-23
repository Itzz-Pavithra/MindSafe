<script>
  import { appState } from '../state/appState.svelte.js';

  function remove(id) {
    appState.removeToast(id);
  }
</script>

<div class="fixed top-6 right-6 z-50 flex flex-col gap-2.5 w-full max-w-sm font-sans pointer-events-none">
  {#each appState.toasts as toast (toast.id)}
    <div 
      class="pointer-events-auto flex items-start gap-3 p-4 rounded-xl shadow-md border bg-white transition-all duration-200 animate-slide-in
        {toast.type === 'success' ? 'border-[#EA9D9D] border-l-4 border-l-[#BD5579]' : ''}
        {toast.type === 'danger' || toast.type === 'error' ? 'border-[#EA9D9D] border-l-4 border-l-[#601D49]' : ''}
        {toast.type === 'warning' ? 'border-[#EA9D9D] border-l-4 border-l-[#FFEBB8]' : ''}
        {toast.type === 'info' ? 'border-[#EA9D9D] border-l-4 border-l-[#BD5579]' : ''}"
    >
      <div class="flex-1 min-w-0">
        <h4 class="font-bold text-xs text-[#601D49]">{toast.title}</h4>
        <p class="text-[11px] text-[#82476B] mt-0.5 leading-relaxed">{toast.message}</p>
      </div>
      <button 
        onclick={() => remove(toast.id)}
        class="text-[#82476B] hover:text-[#601D49] p-0.5 rounded cursor-pointer transition-colors"
        aria-label="Close notification"
      >
        <svg class="h-4 w-4" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" d="M6 18L18 6M6 6l12 12" />
        </svg>
      </button>
    </div>
  {/each}
</div>

<style>
  @keyframes slideIn {
    from { opacity: 0; transform: translateY(-8px); }
    to { opacity: 1; transform: translateY(0); }
  }
  .animate-slide-in {
    animation: slideIn 0.2s cubic-bezier(0.16, 1, 0.3, 1) forwards;
  }
</style>
