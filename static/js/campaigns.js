// campaigns.js — Campaign list filters, search, platform toggle

// ── Platform filter buttons ──
document.querySelectorAll('[data-platform-filter]').forEach(btn => {
  btn.addEventListener('click', () => {
    const platform = btn.dataset.platformFilter;
    const url = new URL(window.location);
    if (platform === 'all') {
      url.searchParams.delete('platform');
    } else {
      url.searchParams.set('platform', platform);
    }
    url.searchParams.delete('page');
    window.location = url.toString();
  });
});

// ── Status filter ──
document.querySelectorAll('[data-status-filter]').forEach(btn => {
  btn.addEventListener('click', () => {
    const status = btn.dataset.statusFilter;
    const url = new URL(window.location);
    if (status === 'all') {
      url.searchParams.delete('status');
    } else {
      url.searchParams.set('status', status);
    }
    window.location = url.toString();
  });
});

// ── Search with debounce ──
const searchInput = document.getElementById('campaign-search');
if (searchInput) {
  let timeout;
  searchInput.addEventListener('input', (e) => {
    clearTimeout(timeout);
    timeout = setTimeout(() => {
      const url = new URL(window.location);
      const q = e.target.value.trim();
      if (q) { url.searchParams.set('q', q); }
      else   { url.searchParams.delete('q'); }
      window.location = url.toString();
    }, 400);
  });
}

// ── Sort table columns ──
document.querySelectorAll('[data-sort]').forEach(th => {
  th.style.cursor = 'pointer';
  th.addEventListener('click', () => {
    const col = th.dataset.sort;
    const tbody = document.querySelector('tbody');
    if (!tbody) return;
    const rows = Array.from(tbody.querySelectorAll('tr'));
    const idx = Array.from(th.parentElement.children).indexOf(th);
    const asc = th.dataset.sortDir !== 'asc';
    th.dataset.sortDir = asc ? 'asc' : 'desc';
    rows.sort((a, b) => {
      const av = a.cells[idx]?.textContent.trim() || '';
      const bv = b.cells[idx]?.textContent.trim() || '';
      const an = parseFloat(av.replace(/[^0-9.-]/g, ''));
      const bn = parseFloat(bv.replace(/[^0-9.-]/g, ''));
      if (!isNaN(an) && !isNaN(bn)) return asc ? an - bn : bn - an;
      return asc ? av.localeCompare(bv) : bv.localeCompare(av);
    });
    rows.forEach(r => tbody.appendChild(r));
  });
});