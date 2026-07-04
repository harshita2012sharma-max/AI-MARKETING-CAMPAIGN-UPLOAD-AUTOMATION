// main.js — Global UI logic

// ── Sidebar toggle (mobile) ──
function toggleSidebar() {
  document.getElementById('sidebar').classList.toggle('open');
}

// Close sidebar on outside click (mobile)
document.addEventListener('click', (e) => {
  const sb = document.getElementById('sidebar');
  const hb = document.getElementById('hamburger');
  if (sb && sb.classList.contains('open') && !sb.contains(e.target) && e.target !== hb) {
    sb.classList.remove('open');
  }
});

// ── Auto-dismiss toasts ──
document.querySelectorAll('.toast').forEach(t => {
  setTimeout(() => {
    t.style.opacity = '0';
    t.style.transform = 'translateX(16px)';
    t.style.transition = 'all .3s ease';
    setTimeout(() => t.remove(), 300);
  }, 4000);
});

// ── Active nav highlight ──
const currentPath = window.location.pathname;
document.querySelectorAll('.nav-item').forEach(item => {
  const href = item.getAttribute('href');
  if (href && currentPath === href) {
    item.classList.add('active');
  } else if (href && href !== '/' && currentPath.startsWith(href)) {
    item.classList.add('active');
  }
});

// ── Keyboard shortcuts ──
document.addEventListener('keydown', (e) => {
  if ((e.metaKey || e.ctrlKey) && e.key === 'k') {
    e.preventDefault();
    document.querySelector('.topbar-search input')?.focus();
  }
  if (e.key === 'Escape') {
    document.querySelector('.topbar-search input')?.blur();
    document.getElementById('sidebar')?.classList.remove('open');
  }
});

// ── Live notification count refresh ──
async function refreshNotifCount() {
  try {
    const res = await fetch('/api/notifications/unread');
    if (!res.ok) return;
    const data = await res.json();
    const dot = document.querySelector('.notif-dot');
    const badge = document.querySelector('.nav-badge');
    if (data.count > 0) {
      if (dot) dot.style.display = 'block';
      if (badge) badge.textContent = data.count;
    } else {
      if (dot) dot.style.display = 'none';
      if (badge) badge.style.display = 'none';
    }
  } catch (_) {}
}

// Refresh every 60 seconds
setInterval(refreshNotifCount, 60000);

// ── Mark all notifications read ──
async function markAllRead() {
  await fetch('/notifications/mark-all-read', { method: 'POST' });
  document.querySelectorAll('.notif-item.unread').forEach(el => el.classList.remove('unread'));
  document.querySelectorAll('.notif-dot-ind').forEach(el => el.style.background = 'var(--border-2)');
  refreshNotifCount();
}

// ── Confirm delete ──
function confirmDelete(formId, msg) {
  if (confirm(msg || 'Are you sure? This cannot be undone.')) {
    document.getElementById(formId).submit();
  }
}

// ── Format numbers ──
function fmtNum(n) {
  if (n >= 1000000) return (n/1000000).toFixed(1) + 'M';
  if (n >= 1000) return (n/1000).toFixed(1) + 'K';
  return n.toLocaleString();
}

function fmtCurrency(n) {
  return '₹' + n.toLocaleString('en-IN', { minimumFractionDigits: 0, maximumFractionDigits: 0 });
}