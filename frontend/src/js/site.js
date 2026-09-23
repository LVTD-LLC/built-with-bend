(() => {
  const root = document.documentElement;
  try {
    const saved = localStorage.getItem('bend-theme');
    if (saved === 'dark' || (!saved && matchMedia('(prefers-color-scheme: dark)').matches)) root.dataset.theme = 'dark';
  } catch { /* Color controls still work when storage is unavailable. */ }
  document.querySelector('.theme-toggle')?.addEventListener('click', () => {
    root.dataset.theme = root.dataset.theme === 'dark' ? 'light' : 'dark';
    try { localStorage.setItem('bend-theme', root.dataset.theme); } catch { /* Optional preference. */ }
  });
})();
