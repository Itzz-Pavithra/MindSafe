<script>
  import { onMount, onDestroy } from 'svelte';
  import { browser } from '$app/environment';

  let { type = 'bar', data, options = {}, height = 260 } = $props();

  let canvasEl;
  let chartInstance = null;
  let ChartJS = null;

  async function getChartJS() {
    if (!browser) return null;
    if (!ChartJS) {
      const c = await import('chart.js');
      ChartJS = c.Chart;
      ChartJS.register(
        c.Title,
        c.Tooltip,
        c.Legend,
        c.BarElement,
        c.CategoryScale,
        c.LinearScale,
        c.PointElement,
        c.LineElement,
        c.ArcElement,
        c.BarController,
        c.DoughnutController,
        c.LineController,
        c.PieController
      );
    }
    return ChartJS;
  }

  async function renderChart() {
    if (!browser || !canvasEl) return;
    const Chart = await getChartJS();
    if (!Chart || !canvasEl) return;

    if (chartInstance) {
      chartInstance.destroy();
      chartInstance = null;
    }
    if (!data || !data.datasets || data.datasets.length === 0) {
      return;
    }

    const defaultOptions = {
      responsive: true,
      maintainAspectRatio: false,
      plugins: {
        legend: {
          display: true,
          position: 'bottom',
          labels: {
            boxWidth: 12,
            boxHeight: 12,
            font: { family: 'Inter', size: 11, weight: '500' },
            color: '#601D49',
            padding: 14
          }
        },
        tooltip: {
          backgroundColor: '#601D49',
          titleColor: '#FFEBB8',
          bodyColor: '#FFFFFF',
          borderColor: '#EA9D9D',
          borderWidth: 1,
          titleFont: { family: 'Inter', size: 12, weight: '600' },
          bodyFont: { family: 'Inter', size: 11 },
          padding: 10,
          cornerRadius: 8
        }
      },
      scales: type === 'doughnut' || type === 'pie' ? {} : {
        x: {
          grid: { display: false },
          ticks: { font: { family: 'Inter', size: 11 }, color: '#82476B' }
        },
        y: {
          grid: { color: 'rgba(240, 213, 221, 0.7)' },
          ticks: { font: { family: 'Inter', size: 11 }, color: '#82476B' }
        }
      },
      ...options
    };

    chartInstance = new Chart(canvasEl, {
      type,
      data,
      options: defaultOptions
    });
  }

  onMount(() => {
    renderChart();
  });

  $effect(() => {
    if (browser && data && canvasEl) {
      renderChart();
    }
  });

  onDestroy(() => {
    if (chartInstance) {
      chartInstance.destroy();
      chartInstance = null;
    }
  });
</script>

<div class="relative w-full" style="height: {height}px;">
  <canvas bind:this={canvasEl}></canvas>
</div>
