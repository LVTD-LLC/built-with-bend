(() => {
  document.querySelectorAll('.project-monogram img').forEach((image) => {
    const fallback = () => { image.hidden = true; };
    image.addEventListener('error', fallback);
    if (image.complete && !image.naturalWidth) fallback();
  });
  const root = document.documentElement;
  try {
    const saved = localStorage.getItem('bend-theme');
    if (saved === 'dark' || (!saved && matchMedia('(prefers-color-scheme: dark)').matches)) root.dataset.theme = 'dark';
  } catch { /* Color controls still work when storage is unavailable. */ }
  root.classList.toggle('dark', root.dataset.theme === 'dark');
  document.querySelector('.theme-toggle')?.addEventListener('click', () => {
    root.dataset.theme = root.dataset.theme === 'dark' ? 'light' : 'dark';
    root.classList.toggle('dark', root.dataset.theme === 'dark');
    try { localStorage.setItem('bend-theme', root.dataset.theme); } catch { /* Optional preference. */ }
  });
})();
