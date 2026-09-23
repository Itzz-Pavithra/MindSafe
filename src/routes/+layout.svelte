<script>
  import '../app.css';
  import Toast from '$lib/components/Toast.svelte';

  let { children } = $props();
</script>

<Toast />

<div class="min-h-screen bg-[#FAF7F8] font-sans antialiased text-[#601D49] flex flex-col">
  {@render children()}
</div>
