// simulator.js — "What If" budget simulator

const sliderEl = document.getElementById('budget-slider');
const sliderVal = document.getElementById('slider-value');
const predSpend = document.getElementById('pred-spend');
const predClicks = document.getElementById('pred-clicks');
const predConv = document.getElementById('pred-conv');
const predROI = document.getElementById('pred-roi');

if (sliderEl) {
  // Base values from data attributes
  const baseBudget  = parseFloat(sliderEl.dataset.base  || 1000);
  const baseClicks  = parseFloat(sliderEl.dataset.clicks  || 100);
  const baseConv    = parseFloat(sliderEl.dataset.conv    || 10);
  const baseROI     = parseFloat(sliderEl.dataset.roi     || 2.5);

  function updateSimulator() {
    const pct = parseInt(sliderEl.value);
    const mult = 1 + pct / 100;

    const newBudget = baseBudget * mult;
    const newClicks = Math.round(baseClicks * mult * 0.92); // slight diminishing returns
    const newConv   = Math.round(baseConv * mult * 0.88);
    const newROI    = (baseROI * (pct >= 0 ? 0.97 : 1.03)).toFixed(2);

    if (sliderVal)  sliderVal.textContent = (pct >= 0 ? '+' : '') + pct + '%';
    if (predSpend)  predSpend.textContent  = '₹' + newBudget.toLocaleString('en-IN', { maximumFractionDigits: 0 });
    if (predClicks) predClicks.textContent = newClicks.toLocaleString();
    if (predConv)   predConv.textContent   = newConv.toLocaleString();
    if (predROI)    predROI.textContent    = newROI + 'x';

    // Color the slider value
    if (sliderVal) {
      sliderVal.style.color = pct > 0 ? 'var(--green)' : pct < 0 ? 'var(--red)' : 'var(--text-muted)';
    }
  }

  sliderEl.addEventListener('input', updateSimulator);
  updateSimulator();
}