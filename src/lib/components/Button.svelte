<script>
  let { 
    children, 
    onclick, 
    type = 'button', 
    variant = 'primary', 
    disabled = false, 
    class: className = '' 
  } = $props();

  const baseStyles = 'px-4 py-2.5 rounded-xl font-medium text-sm tracking-normal transition-all duration-150 active:scale-[0.99] disabled:opacity-50 disabled:pointer-events-none flex items-center justify-center gap-2 cursor-pointer';
  
  const variants = {
    // Primary #BD5579 (Primary action)
    primary: 'bg-[#BD5579] hover:bg-[#A84466] text-white font-semibold shadow-xs border border-[#BD5579]',
    // Secondary #EA9D9D (Soft card / secondary action)
    secondary: 'bg-[#EA9D9D] hover:bg-[#E38B8B] text-[#601D49] font-semibold border border-[#EA9D9D]',
    // Dark Primary #601D49
    dark: 'bg-[#601D49] hover:bg-[#4B1639] text-white font-semibold border border-[#601D49]',
    // Accent #FFEBB8
    accent: 'bg-[#FFEBB8] hover:bg-[#FADC8C] text-[#601D49] font-semibold border border-[#EA9D9D]/60',
    // Outline
    outline: 'bg-white hover:bg-[#FAF7F8] text-[#601D49] border border-[#EA9D9D] hover:border-[#BD5579]',
    // Subtle
    subtle: 'bg-[#FAF7F8] hover:bg-[#FFEBB8]/50 text-[#601D49] border border-[#F0D5DD]',
    // Danger
    danger: 'bg-[#BD5579] hover:bg-[#601D49] text-white border border-[#BD5579]',
    // Ghost
    ghost: 'bg-transparent text-[#601D49] hover:bg-[#FFEBB8]/40'
  };
</script>

<button
  {type}
  {disabled}
  {onclick}
  class="{baseStyles} {variants[variant] || variants.primary} {className}"
>
  {@render children()}
</button>
