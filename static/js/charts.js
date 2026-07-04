// charts.js — Chart.js initialization

const CHART_DEFAULTS = {
  color: {
    accent:  '#6366f1',
    green:   '#10b981',
    amber:   '#f59e0b',
    red:     '#f43f5e',
    blue:    '#3b82f6',
    purple:  '#a855f7',
    google:  '#4285F4',
    meta:    '#1877F2',
    bing:    '#00a4c8',
    text:    '#64748b',
    border:  'rgba(15,23,42,0.08)',
    grid:    'rgba(15,23,42,0.06)',
  }
};

// Common chart options
function baseOptions(opts = {}) {
  return {
    responsive: true,
    maintainAspectRatio: false,
    plugins: {
      legend: {
        display: opts.legend ?? false,
        labels: { color: CHART_DEFAULTS.color.text, font: { size: 12, family: 'Inter' }, boxWidth: 10, padding: 16 }
      },
      tooltip: {
        backgroundColor: '#0F172A',
        borderColor: 'rgba(255,255,255,0.1)',
        borderWidth: 1,
        titleColor: '#F8FAFC',
        bodyColor: '#CBD5E1',
        padding: 12,
        cornerRadius: 8,
        callbacks: opts.callbacks || {}
      }
    },
    scales: opts.scales !== false ? {
      x: {
        grid: { color: CHART_DEFAULTS.color.grid, drawBorder: false },
        ticks: { color: CHART_DEFAULTS.color.text, font: { size: 11, family: 'Inter' }, maxTicksLimit: 8 }
      },
      y: {
        grid: { color: CHART_DEFAULTS.color.grid, drawBorder: false },
        ticks: { color: CHART_DEFAULTS.color.text, font: { size: 11, family: 'Inter' },
          callback: opts.yFmt || ((v) => v >= 1000 ? (v/1000).toFixed(0)+'K' : v)
        },
        border: { display: false }
      }
    } : false,
    elements: {
      point: { radius: 3, hoverRadius: 5, borderWidth: 2 },
      line:  { tension: 0.4 }
    }
  };
}

// ── SPEND TREND LINE CHART ──
function initSpendChart(canvasId, labels, spendData, revenueData) {
  const ctx = document.getElementById(canvasId);
  if (!ctx) return;
  return new Chart(ctx, {
    type: 'line',
    data: {
      labels,
      datasets: [
        {
          label: 'Revenue',
          data: revenueData,
          borderColor: CHART_DEFAULTS.color.green,
          backgroundColor: 'rgba(16,185,129,0.08)',
          fill: true, borderWidth: 2,
        },
        {
          label: 'Spend',
          data: spendData,
          borderColor: CHART_DEFAULTS.color.accent,
          backgroundColor: 'rgba(99,102,241,0.08)',
          fill: true, borderWidth: 2,
        }
      ]
    },
    options: {
      ...baseOptions({ legend: true, callbacks: { label: (c) => ` ${c.dataset.label}: ₹${c.raw.toLocaleString()}` } }),
    }
  });
}

// ── PLATFORM DONUT CHART ──
function initPlatformDonut(canvasId, labels, data) {
  const ctx = document.getElementById(canvasId);
  if (!ctx) return;
  return new Chart(ctx, {
    type: 'doughnut',
    data: {
      labels,
      datasets: [{
        data,
        backgroundColor: [
          CHART_DEFAULTS.color.google,
          CHART_DEFAULTS.color.meta,
          CHART_DEFAULTS.color.bing
        ],
        borderColor: '#FFFFFF',
        borderWidth: 3,
        hoverOffset: 4
      }]
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      cutout: '72%',
      plugins: {
        legend: {
          display: true, position: 'bottom',
          labels: { color: CHART_DEFAULTS.color.text, font: { size: 12, family: 'Inter' }, boxWidth: 10, padding: 14 }
        },
        tooltip: {
          backgroundColor: '#0F172A',
          borderColor: 'rgba(255,255,255,0.1)',
          borderWidth: 1,
          titleColor: '#F8FAFC',
          bodyColor: '#CBD5E1',
          padding: 12,
          callbacks: { label: (c) => ` ${c.label}: ₹${c.raw.toLocaleString()}` }
        }
      }
    }
  });
}

// ── CLICKS BAR CHART ──
function initClicksChart(canvasId, labels, clicksData) {
  const ctx = document.getElementById(canvasId);
  if (!ctx) return;
  return new Chart(ctx, {
    type: 'bar',
    data: {
      labels,
      datasets: [{
        label: 'Clicks',
        data: clicksData,
        backgroundColor: 'rgba(99,102,241,0.6)',
        borderColor: CHART_DEFAULTS.color.accent,
        borderWidth: 1,
        borderRadius: 4,
        borderSkipped: false,
      }]
    },
    options: baseOptions({ callbacks: { label: (c) => ` Clicks: ${c.raw.toLocaleString()}` } })
  });
}

// ── PLATFORM BAR COMPARISON ──
function initPlatformBar(canvasId, labels, googleData, metaData, bingData) {
  const ctx = document.getElementById(canvasId);
  if (!ctx) return;
  return new Chart(ctx, {
    type: 'bar',
    data: {
      labels,
      datasets: [
        { label: 'Google', data: googleData, backgroundColor: 'rgba(66,133,244,0.75)', borderRadius: 4 },
        { label: 'Meta',   data: metaData,   backgroundColor: 'rgba(24,119,242,0.75)', borderRadius: 4 },
        { label: 'Bing',   data: bingData,   backgroundColor: 'rgba(0,164,200,0.75)',  borderRadius: 4 },
      ]
    },
    options: { ...baseOptions({ legend: true }), scales: { x: { stacked: false }, y: { stacked: false } } }
  });
}

// ── ROI LINE CHART ──
function initROIChart(canvasId, labels, roiData) {
  const ctx = document.getElementById(canvasId);
  if (!ctx) return;
  return new Chart(ctx, {
    type: 'line',
    data: {
      labels,
      datasets: [{
        label: 'ROI',
        data: roiData,
        borderColor: CHART_DEFAULTS.color.amber,
        backgroundColor: 'rgba(245,158,11,0.08)',
        fill: true, borderWidth: 2,
      }]
    },
    options: baseOptions({
      yFmt: (v) => v.toFixed(1) + 'x',
      callbacks: { label: (c) => ` ROI: ${c.raw.toFixed(2)}x` }
    })
  });
}

// ── CAMPAIGN DETAIL CHART ──
function initCampaignDetailChart(canvasId, labels, spendData, clicksData) {
  const ctx = document.getElementById(canvasId);
  if (!ctx) return;
  return new Chart(ctx, {
    type: 'line',
    data: {
      labels,
      datasets: [
        {
          label: 'Spend (₹)',
          data: spendData,
          borderColor: CHART_DEFAULTS.color.accent,
          backgroundColor: 'rgba(99,102,241,0.08)',
          fill: true, borderWidth: 2, yAxisID: 'y'
        },
        {
          label: 'Clicks',
          data: clicksData,
          borderColor: CHART_DEFAULTS.color.green,
          backgroundColor: 'transparent',
          borderWidth: 2, yAxisID: 'y1'
        }
      ]
    },
    options: {
      ...baseOptions({ legend: true }),
      scales: {
        x: { grid: { color: CHART_DEFAULTS.color.grid }, ticks: { color: CHART_DEFAULTS.color.text, font: { size: 11 } } },
        y: {
          type: 'linear', position: 'left',
          grid: { color: CHART_DEFAULTS.color.grid },
          ticks: { color: CHART_DEFAULTS.color.text, font: { size: 11 }, callback: (v) => '₹' + v.toLocaleString() }
        },
        y1: {
          type: 'linear', position: 'right',
          grid: { drawOnChartArea: false },
          ticks: { color: CHART_DEFAULTS.color.text, font: { size: 11 } }
        }
      }
    }
  });
}