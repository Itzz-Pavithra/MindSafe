<script>
  import { onMount, onDestroy } from 'svelte';
  import {
    Chart as ChartJS,
    Title,
    Tooltip,
    Legend,
    BarElement,
    CategoryScale,
    LinearScale,
    PointElement,
    LineElement,
    ArcElement,
    BarController,
    DoughnutController,
    LineController,
    PieController
  } from 'chart.js';

  ChartJS.register(
    Title,
    Tooltip,
    Legend,
    BarElement,
    CategoryScale,
    LinearScale,
    PointElement,
    LineElement,
    ArcElement,
    BarController,
    DoughnutController,
    LineController,
    PieController
  );

  let { type = 'bar', data, options = {}, height = 260 } = $props();

  let canvasEl;
  let chartInstance = null;

  function renderChart() {
    if (!canvasEl) return;
    if (chartInstance) {
      chartInstance.destroy();
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

    chartInstance = new ChartJS(canvasEl, {
      type,
      data,
      options: defaultOptions
    });
  }

  onMount(() => {
    renderChart();
  });

  $effect(() => {
    if (data && canvasEl) {
      renderChart();
    }
  });

  onDestroy(() => {
    if (chartInstance) {
      chartInstance.destroy();
    }
  });
</script>

<div class="relative w-full" style="height: {height}px;">
  <canvas bind:this={canvasEl}></canvas>
</div>
