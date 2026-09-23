<script>
  let { children, class: className = '', hover = false, elevated = false, accent = false } = $props();
</script>

<div class="{accent ? 'bg-[#FFEBB8]/20 border-[#EA9D9D]' : elevated ? 'bg-[#FAF7F8] border-[#EA9D9D]/60' : 'bg-white border-[#F0D5DD]'} rounded-2xl p-5 border text-[#601D49] shadow-xs transition-all duration-150
  {hover ? 'hover:border-[#BD5579] hover:shadow-sm' : ''}
  {className}">
  {@render children()}
</div>
